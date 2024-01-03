from django.db.models import Count, Sum ,Q , F
import json, re
from datetime import datetime, timedelta
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
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import AttendanceSerializer
from django.views.decorators.http import require_http_methods
class EmployeeLogin(APIView):
    def post(self, request, format=None):
        insurance_number = request.data.get("insuranceNumber")
        try:
            employee = Employee.objects.get(InsuranceNumber=insurance_number)
            return Response(EmployeeSerializer(employee).data, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)




@api_view(['GET'])
def get_all_attendance(request):
    all_attendance = Attendance.objects.all()
    serializer = AttendanceSerializer(all_attendance, many=True)
    return Response({'status': 'success', 'data': serializer.data})


@api_view(['GET'])
def get_employee_attendance(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    attendance_data = Attendance.objects.filter(employee=employee)
    serializer = AttendanceSerializer(attendance_data, many=True)
    return Response({'status': 'success', 'data': serializer.data})

@api_view(['GET'])
def get_department_attendance(request, department_id):
    employees_in_department = Employee.objects.filter(department=department_id)
    attendance_data = Attendance.objects.filter(employee__in=employees_in_department)
    serializer = AttendanceSerializer(attendance_data, many=True)
    return Response({'status': 'success', 'data': serializer.data})

@api_view(['GET'])
def get_daily_attendance(request, date):
    attendance_data = Attendance.objects.filter(date=date)
    serializer = AttendanceSerializer(attendance_data, many=True)
    return Response({'status': 'success', 'data': serializer.data})

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
            qr_data = json.loads(request.body)
            insurance_number_str = qr_data.get('InsuranceNumber')
            scan_type = qr_data.get('ScanType', 'time_in')

            match = re.search(r'\d+', insurance_number_str)
            if match:
                insurance_number = int(match.group())
            else:
                raise ValueError('Invalid InsuranceNumber format')

            employee = get_object_or_404(Employee, InsuranceNumber=insurance_number)
            current_date = timezone.localdate()

            if scan_type == 'time_in':
                # Time-in scan: create a new Attendance record
                attendance, created = Attendance.objects.get_or_create(
                    employee=employee,
                    date=current_date,
                    defaults={'time_in': timezone.localtime(), 'attendance_status': Attendance.PRESENT}
                )
                if not created:
                    return JsonResponse({'status': 'error', 'message': 'Attendance already marked for today'})
            elif scan_type == 'time_out':
                # Time-out scan: update the existing Attendance record
                try:
                    attendance = Attendance.objects.get(employee=employee, date=current_date)
                    if attendance.time_out is not None:
                        return JsonResponse({'status': 'error', 'message': 'Time-out already recorded'})

                    attendance.time_out = timezone.localtime().time()
                    if attendance.time_in:
                        time_in_datetime = datetime.combine(current_date, attendance.time_in)
                        time_out_datetime = datetime.combine(current_date, attendance.time_out)
                        duration = time_out_datetime - time_in_datetime
                        total_hours_decimal = duration.total_seconds() / 3600.0  # Keep total_hours as decimal
                        attendance.total_hours = round(total_hours_decimal, 2)
                    else:
                        return JsonResponse({'status': 'error', 'message': 'Time-in not recorded for today'})

                    attendance.save()
                except Attendance.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'Attendance not marked for today'})

            return JsonResponse({'status': 'success', 'attendance_id': attendance.id})
        except Employee.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Employee not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def attendance_dashboard(request):
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = datetime(today.year, today.month, 1)

    # Basic aggregations
    daily_data = Attendance.objects.filter(date=today).aggregate(
        total_count=Count('id'),
        total_hours=Sum('total_hours'),
        late_count=Count('id', filter=Q(late_flag=True)),
        early_leave_count=Count('id', filter=Q(early_leave_flag=True)),
        overtime_hours=Sum('overtime_hours')
    )

    weekly_data = Attendance.objects.filter(date__range=[start_of_week, today]).aggregate(
        total_count=Count('id'),
        total_hours=Sum('total_hours'),
        late_count=Count('id', filter=Q(late_flag=True)),
        early_leave_count=Count('id', filter=Q(early_leave_flag=True)),
        overtime_hours=Sum('overtime_hours')
    )

    monthly_data = Attendance.objects.filter(date__gte=start_of_month).aggregate(
        total_count=Count('id'),
        total_hours=Sum('total_hours'),
        late_count=Count('id', filter=Q(late_flag=True)),
        early_leave_count=Count('id', filter=Q(early_leave_flag=True)),
        overtime_hours=Sum('overtime_hours')
    )

    # Additional metrics
    status_breakdown = Attendance.objects.values('attendance_status').annotate(count=Count('id'))
    late_trends = Attendance.objects.filter(late_flag=True).annotate(late_date=F('date')).values('late_date').annotate(count=Count('id'))
    department_summary = Attendance.objects.values('employee__position__Department__Name').annotate(count=Count('id')).order_by('employee__position__Department__Name')

    # Absenteeism rate
    total_employees = Employee.objects.count()
    absentees_today = Attendance.objects.filter(date=today, attendance_status='Absent').count()
    absenteeism_rate = (absentees_today / total_employees) * 100 if total_employees else 0

    most_attended_employees = Attendance.objects.values(
        'employee__FirstName', 'employee__LastName'
    ).annotate(
        total_attendance=Count('id')
    ).order_by('-total_attendance')[:5]  # Adjust the number as needed

    response_data = {
        'daily': daily_data,
        'weekly': weekly_data,
        'monthly': monthly_data,
        'status_breakdown': list(status_breakdown),
        'late_trends': list(late_trends),
        'department_summary': list(department_summary),
        'absenteeism_rate': absenteeism_rate,
        'most_attended_employees': list(most_attended_employees)
    }

    return JsonResponse(response_data)