from django.db import models
from base.models import Employee
# Create your models here.



class LeaveType(models.TextChoices):
    SICK_LEAVE = 'sick', 'Sick Leave'
    PAID = 'paid', 'paid leave'
    UNPAID = 'unpaid', 'Unpaid Leave'
    # ... add any other leave types as needed ...

class LeaveStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'

class Leave(models.Model):
    Employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    LeaveType = models.CharField(max_length=50, choices=LeaveType.choices, default=LeaveType.PAID)
    StartDate = models.DateField()
    EndDate = models.DateField()
    Reason = models.TextField(blank=True, null=True)
    Status = models.CharField(max_length=50, choices=LeaveStatus.choices, default=LeaveStatus.PENDING)

    @property
    def duration(self):
        return (self.EndDate - self.StartDate).days + 1

class LeaveAllocation(models.Model):
    Employee = models.OneToOneField(Employee, on_delete=models.CASCADE, primary_key=True)
    total_leaves = models.PositiveIntegerField(default=0)
    used_leaves = models.PositiveIntegerField(default=0)
    remaining_leaves = models.PositiveIntegerField(default=0)
    
    def update_leaves(self):
        approved_leaves = Leave.objects.filter(Employee=self.Employee, Status=LeaveStatus.APPROVED)
        
        leaves_taken = sum([(leave.EndDate - leave.StartDate).days + 1 for leave in approved_leaves])
        
        self.used_leaves = leaves_taken
        self.remaining_leaves = self.total_leaves - self.used_leaves
        print("Updating leaves for:", self.Employee)
        self.save()