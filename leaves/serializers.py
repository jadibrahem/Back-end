from rest_framework import serializers
from .models import Leave, LeaveAllocation , Employee

class LeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = '__all__'

class LeaveAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveAllocation
        fields = '__all__'



# class EmployeeLeaveSerializer(serializers.ModelSerializer):
#     leaves = serializers.SerializerMethodField()

#     class Meta:
#         model = Employee
#         fields = [ 'EmployeeID', 'FirstName', 'position', 'leaves']  # Add any other Employee fields you want

#     def get_leaves(self, obj):
#         leaves = Leave.objects.filter(Employee=obj)
#         return [
#             {
#                 "type": leave.LeaveType,
#                 "start_date": leave.StartDate,
#                 "end_date": leave.EndDate
#             }
#             for leave in leaves
#        ]
class EmployeeLeaveAllocationSerializer(serializers.ModelSerializer):
    leave_allocation = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['EmployeeID', 'FirstName', 'position', 'leave_allocation']  # Add any other Employee fields you want

    def get_leave_allocation(self, obj):
        # Assuming there is a one-to-one relationship between Employee and LeaveAllocation
        try:
            allocation = LeaveAllocation.objects.get(Employee=obj)
            return {
                "total_leaves": allocation.total_leaves,
                "used_leaves": allocation.used_leaves,
                "remaining_leaves": allocation.remaining_leaves
            }
        except LeaveAllocation.DoesNotExist:
            return None  # Or a default representation of no allocation