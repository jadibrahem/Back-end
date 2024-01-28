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
            last_id = PurchaseRequest.objects.filter(document_reference__startswith=f'PR{year}').count()
            new_id = last_id + 1
            self.document_reference = f'PR{year}{str(new_id).zfill(4)}'
         
        super(PurchaseRequest, self).save(*args, **kwargs)
    def approve(self, user):
        try:
            profile = user.profile  # Assuming a OneToOne relation to the user's profile
            if profile.user_type == 'budget_holder' and self.status == 'pending':
                self.status = 'approved_budget_holder'
            elif profile.user_type == 'finance_checker' and self.status == 'approved_budget_holder':
                self.status = 'approved'
            else:
                return False, "User does not have permission to approve this request or the request is in an invalid state for approval."
            self.save()
            return True, "Purchase request approved successfully."
        except Profile.DoesNotExist:
            return False, "User does not have an associated profile."
        
    def __str__(self):
        return f"{self.programme} - {self.document_reference}"
class Item(models.Model):
    name = models.CharField(max_length=255)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} - {self.unit_cost} per {self.unit}"

class Budget_Line :
    name = models.CharField(max_length = 255)


class PurchaseRequestItem(models.Model):
    DONOR_CHOICES = [
        ('donor1', 'Donor 1'),
        ('donor2', 'Donor 2'),
    ]
    purchase_request = models.ForeignKey(PurchaseRequest, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.PROTECT)  # Link to the Item catalog
    quantity = models.IntegerField()
    currency = models.CharField(max_length=3)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    donor = models.CharField(max_length=255, choices=DONOR_CHOICES, blank=True, null=True)
    budget_line = models.CharField(max_length=255, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.item.unit_cost  # Calculate total cost
        super(PurchaseRequestItem, self).save(*args, **kwargs)  # Call the "real" save() method.

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"
    

# class Approval(models.Model):
#     APPROVAL_TYPES = [                                                                                                  
#     ('first', 'First Approval'),
#     ('second', 'Second Approval'),
#     ]
#     STATUS_CHOICES = [
#     ('pending', 'Pending'),
#     ('approved', 'Approved'),
#     ('rejected', 'Rejected'),
#     ]
#     purchase_request = models.ForeignKey(PurchaseRequest, on_delete=models.CASCADE, related_name='approvals')
#     approver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approvals_made')
#     approval_type = models.CharField(max_length=50, choices=APPROVAL_TYPES)
#     status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
#     comments = models.TextField(blank=True, null=True)
#     approval_date = models.DateField(auto_now_add=True)
#     def save(self, *args, **kwargs):
#         with transaction.atomic():
#             if self.status == 'approved':
#                 # Update the status of the PurchaseRequest depending on the type of approval
#                 if self.approval_type == 'first' and self.approver.profile.user_type == 'type2':
#                     self.purchase_request.status = 'approved_first'
#                 elif self.approval_type == 'second' and self.approver.profile.user_type == 'type3':
#                     self.purchase_request.status = 'approved_second'
#                 self.purchase_request.save()
#             elif self.status == 'rejected':
#                 self.purchase_request.status = 'rejected'
#                 self.purchase_request.save()
            
#             # Optionally, send a notification to the next approver or to the requester
#             # ... [send notification logic here] ...
            
#             # Check for appropriate permission before approval
#             if self.approval_type == 'first' and not self.approver.profile.user_type == 'type2':
#                 raise PermissionError("User does not have permission for first approval.")
#             if self.approval_type == 'second' and not self.approver.profile.user_type == 'type3':
#                 raise PermissionError("User does not have permission for second approval.")
                
#             super(Approval, self).save(*args, **kwargs)
    


