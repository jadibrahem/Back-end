from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
   path('loginnum/',views.EmployeeLogin.as_view(), name='employee_login'),
   path('scan-qr-code/', views.scan_qr_code, name='scan_qr_code'),
   path('scan-qr-code/<str:InsuranceNumber>/', views.scan_qr_code, name='scan_qr_code_employee'),
   path('attendance/', views.get_all_attendance, name='all_attendance'),
   path('attendance/employee/<int:employee_id>/', views.get_employee_attendance, name='employee_attendance'),
   path('attendance/department/<int:department_id>/', views.get_department_attendance, name='department_attendance'),
   path('attendance/daily/<str:date>/', views.get_daily_attendance, name='daily_attendance'),
   path('attendance/monthly-summary/<int:employee_id>/<int:year>/<int:month>/', views.calculate_monthly_summary, name='monthly_summary'),
   
   path('attendance/dash/', views.attendance_dashboard, name='attendance_dashboard'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)