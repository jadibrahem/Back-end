from django.db import models
from base.models import Employee  # Adjust the import path as needed
from django.utils import timezone
from datetime import time

class Attendance(models.Model):
    # Status choices
    PRESENT = 'Present'
    ABSENT = 'Absent'
    LEAVE = 'Leave'
    HALF_DAY = 'Half-day'
    ATTENDANCE_STATUS_CHOICES = [
        (PRESENT, 'Present'),
        (ABSENT, 'Absent'),
        (LEAVE, 'Leave'),
        (HALF_DAY, 'Half-day'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)  # Default to the current date
    time_in = models.TimeField(null=True, blank=True)
    time_out = models.TimeField(null=True, blank=True)
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    late_flag = models.BooleanField(default=False)
    early_leave_flag = models.BooleanField(default=False)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    attendance_status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS_CHOICES, default=PRESENT)

    def calculate_hours(self):
        # Define your standard working hours
        standard_start_time = timezone.datetime.combine(timezone.now().date(), time(9, 0))  # e.g., 9 AM
        standard_end_time = timezone.datetime.combine(timezone.now().date(), time(17, 0))  # e.g., 5 PM
        standard_work_duration = 8  # e.g., 8 hours

        if self.time_in and self.time_out:
            start = timezone.datetime.combine(timezone.now().date(), self.time_in)
            end = timezone.datetime.combine(timezone.now().date(), self.time_out)
            duration = end - start
            self.total_hours = duration.total_seconds() / 3600

            # Calculate LateFlag
            self.late_flag = start > standard_start_time

            # Calculate EarlyLeaveFlag
            self.early_leave_flag = end < standard_end_time

            # Calculate OvertimeHours
            if self.total_hours > standard_work_duration:
                self.overtime_hours = self.total_hours - standard_work_duration
            else:
                self.overtime_hours = 0

            self.save()
    def __str__(self):
        return f"{self.employee.FirstName} {self.employee.LastName} - {self.date}"

    class Meta:
        verbose_name = "Attendance"
        verbose_name_plural = "Attendances"