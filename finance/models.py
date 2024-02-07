from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token



@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)



class Profile(models.Model):
    USER_TYPES = [
        ('user', 'Regular User'), 
        ('budget_holder', 'Budget Holder'), 
        ('finance_checker', 'Finance Checker'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=50, choices=USER_TYPES)

    def __str__(self):
        return self.user.username

class PurchaseRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved_budget_holder', 'Approved by Budget Holder'),
        ('approved_finance_checker', 'Approved by Finance Checker'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    programme = models.CharField(max_length=255)
    document_reference = models.CharField(max_length=255, unique=True, editable=False)
    purchase_request_date = models.DateField(default=now)
    location_required = models.CharField(max_length=255)
    date_required = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchase_requests')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    comments = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.document_reference:
            year = now().year
            last_pr = PurchaseRequest.objects.filter(document_reference__endswith=f'/{str(year)[-2:]}').order_by('document_reference').last()
            
            if last_pr:
                last_id_str = last_pr.document_reference[2:6]  # Adjust based on your reference format
                new_id = int(last_id_str) + 1
            else:
                new_id = 1

            new_id_str = str(new_id).zfill(4)  # Pad with zeros to ensure the ID is 4 digits
            self.document_reference = f'PR{new_id_str}/{str(year)[-2:]}'  # Format as PR0008/24
            
        super(PurchaseRequest, self).save(*args, **kwargs)
    def approve(self, user):
        try:
            profile = user.profile  # Assuming a OneToOne relation to the user's profile
            if profile.user_type == 'budget_holder' and self.status == 'pending':
                self.status = 'approved_budget_holder'
                approval_status = 'approved_budget_holder'
            elif profile.user_type == 'finance_checker' and self.status == 'approved_budget_holder':
                self.status = 'approved_finance_checker'
                approval_status = 'approved_finance_checker'
            else:
                return False, "User does not have permission to approve this request or the request is in an invalid state for approval."

            # Save the status change
            self.save()

            # Log the approval in the ApprovalLog
            ApprovalLog.objects.create(
                purchase_request=self,
                approved_by=user,
                approval_status=approval_status
            )

            return True, "Purchase request approved successfully."
        except Profile.DoesNotExist:
            return False, "User does not have an associated profile."
        
    def __str__(self):
        return f"{self.programme} - {self.document_reference}"

class ApprovalLog(models.Model):
    purchase_request = models.ForeignKey(PurchaseRequest, on_delete=models.CASCADE)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE)
    approved_on = models.DateTimeField(auto_now_add=True)
    approval_status = models.CharField(max_length=50, choices=PurchaseRequest.STATUS_CHOICES)

    def __str__(self):
        return f"{self.purchase_request} - {self.approval_status} by {self.approved_by} on {self.approved_on}"


class Item(models.Model):
    UNIT_CHOICES = [
        ('day', 'Day'),
        ('flights', 'Flights'),
        ('number', 'Number'),
        ('months', 'Months'),
        ('times', 'Times'),
        ('liter', 'Liter'),
        ('kg', 'Kg'),
        ('pcs', 'Pieces'),
        ('trip', 'Trip'),
        ('lump_sum', 'Lump Sum'),
        ('none', 'none')
    ]

    name = models.CharField(max_length=255)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=50, choices=UNIT_CHOICES)

    def __str__(self):
        return f"{self.name} - {self.unit_cost} per {self.unit}"

class BudgetLine(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"
class PurchaseRequestItem(models.Model):
    DONOR_CHOICES = [
        ('N62', 'N62'),
        ('donor2', 'Donor 2'),
        # Add more donor choices as needed
    ]

    purchase_request = models.ForeignKey(PurchaseRequest, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.PROTECT)  # Link to the Item catalog
    quantity = models.IntegerField()
    currency = models.CharField(max_length=3)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    donor = models.CharField(max_length=255, choices=DONOR_CHOICES, blank=True, null=True)
    budget_line = models.ForeignKey(BudgetLine, on_delete=models.SET_NULL, null=True, blank=True)  # Allows null values
    comments = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.item.unit_cost  # Calculate total cost
        super().save(*args, **kwargs)  # Call the "real" save() method.

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"
    
