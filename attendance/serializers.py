from rest_framework import serializers
from .models import Attendance, Employee

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['EmployeeID', 'FirstName', 'LastName']
        # Add other necessary fields

class AttendanceSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'date', 'time_in', 'time_out', 'total_hours', 'late_flag', 'early_leave_flag', 'overtime_hours', 'attendance_status', 'employee']
