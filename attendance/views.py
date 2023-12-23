import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from base.models import Employee 
from django.views.decorators.csrf import csrf_exempt
from base.serializers import EmployeeSerializer  
import qrcode
from django.core.files.base import ContentFile
from io import BytesIO
from django.utils import timezone
from datetime import datetime, time
from .models import Attendance
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import re
from django.db.models import Sum
# def generate_qr_code():
#     qr = qrcode.QRCode(
#         version=1,
#         error_correction=qrcode.constants.ERROR_CORRECT_L,
#         box_size=10,
#         border=4,
#     )
#     qr.add_data("ATTENDANCE_QR")
#     qr.make(fit=True)

#     img = qr.make_image(fill='black', back_color='white')
#     buffer = BytesIO()
#     img.save(buffer, format="PNG")
#     return ContentFile(buffer.getvalue(), 'qr.png')

# class RecordAttendance(APIView):
#     def post(self, request):
#         insurance_number = request.data.get('insurance_number')
#         employee = Employee.objects.get(InsuranceNumber=insurance_number)
#         now = datetime.datetime.now()

#         # Determine if it's time-in or time-out
#         attendance, created = Attendance.objects.get_or_create(
#             employee=employee, 
#             date=now.date(),
#             defaults={'time_in': now}
#         )
#         if not created and not attendance.time_out:
#             attendance.time_out = now
#             attendance.save()

#         # Implement logic to calculate total hours, late flag, etc.

#         return Response({'status': 'success', 'message': 'Attendance recorded'})

class EmployeeLogin(APIView):
    def post(self, request, format=None):
        insurance_number = request.data.get("insuranceNumber")
        try:
            employee = Employee.objects.get(InsuranceNumber=insurance_number)
            return Response(EmployeeSerializer(employee).data, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)






def get_employee_attendance(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    attendance_data = Attendance.objects.filter(employee=employee).values()
    return JsonResponse({'status': 'success', 'data': list(attendance_data)})

def get_department_attendance(request, department_id):
    # Assuming you have a Department model and a relationship between Employee and Department
    employees_in_department = Employee.objects.filter(department=department_id)
    attendance_data = Attendance.objects.filter(employee__in=employees_in_department).values()
    return JsonResponse({'status': 'success', 'data': list(attendance_data)})

def get_daily_attendance(request, date):
    attendance_data = Attendance.objects.filter(date=date).values()
    return JsonResponse({'status': 'success', 'data': list(attendance_data)})

# You can add more views as needed

def calculate_monthly_summary(request, employee_id, year, month):
    employee = get_object_or_404(Employee, id=employee_id)
    start_date = f"{year}-{month}-01"
    end_date = f"{year}-{month + 1 if month < 12 else 1}-01"
    
    monthly_summary = Attendance.objects.filter(
        employee=employee, date__gte=start_date, date__lt=end_date
    ).aggregate(
        total_hours=Sum('total_hours'),
        overtime_hours=Sum('overtime_hours'),
        late_count=Sum('late_flag'),
        early_leave_count=Sum('early_leave_flag')
    )

    return JsonResponse({'status': 'success', 'data': monthly_summary})


@csrf_exempt
def scan_qr_code(request):
    if request.method == 'POST':
        try:
            # Decode the QR code data from the JSON request
            qr_data = json.loads(request.body)
            insurance_number_str = qr_data.get('InsuranceNumber')

            # Extract only numeric part using regular expression
            match = re.search(r'\d+', insurance_number_str)
            if match:
                insurance_number = int(match.group())
            else:
                raise ValueError('Invalid InsuranceNumber format')
            print(request.body)
            print(insurance_number)
            # Get the employee based on the insurance number
            employee = get_object_or_404(Employee, InsuranceNumber=insurance_number)
            print(employee)
            
            current_datetime = timezone.now()
            current_time = current_datetime.time()

            standard_start_time = datetime.combine(timezone.now().date(), time(9, 0))
            standard_end_time = datetime.combine(timezone.now().date(), time(17, 0))
            standard_work_duration = 8 

            # Create an Attendance object
            attendance = Attendance.objects.create(
                employee=employee,
                date=timezone.now().date(),
                time_in=current_datetime.time(),
                attendance_status=Attendance.PRESENT,  
            )

            # Calculate hours and set flags
           

            attendance.save()
            print(attendance)
            return JsonResponse({'status': 'success', 'attendance_id': attendance.id})
        except Employee.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Employee not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})