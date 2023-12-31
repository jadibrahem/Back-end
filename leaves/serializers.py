
from rest_framework import serializers
from .models import Leave, LeaveAllocation , Employee 
from base.models import Signature
class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class LeaveSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='Employee.FirstName', read_only=True)  # Ensure this matches your model field
    position_name = serializers.CharField(source='Employee.position.Name', read_only=True)  # Ensure this matches your model field

    class Meta:
        model = Leave
        fields = ['id', 'LeaveType', 'StartDate', 'EndDate', 'Reason', 'Status', 'Employee', 'employee_name', 'position_name']
class LeaveAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveAllocation
        fields = '__all__'



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
class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = '__all__'  # List all the fields that you want to include

class SignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signature
        fields =  '__all__'        

class LeavePdfSerializer(serializers.ModelSerializer):
    employee_details = EmployeeSerializer(source='Employee', read_only=True)
    signature_details = SignatureSerializer(source='Employee.signature', read_only=True)

    class Meta:
        model = Leave
        fields = '__all__'  # Use '__all__' to automatically include all model fields

    # Add a SerializerMethodField for the duration property
    duration = serializers.SerializerMethodField()

    def get_duration(self, obj):
        # Assuming the Leave model has a 'duration' property method that calculates the duration
        return obj.duration