from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from base.models import Employee 

from base.serializers import EmployeeSerializer  # You need to create this serializer
import qrcode
from django.core.files.base import ContentFile
from io import BytesIO
import datetime
from .models import Attendance

def generate_qr_code():
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data("ATTENDANCE_QR")
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue(), 'qr.png')

class RecordAttendance(APIView):
    def post(self, request):
        insurance_number = request.data.get('insurance_number')
        employee = Employee.objects.get(InsuranceNumber=insurance_number)
        now = datetime.datetime.now()

        # Determine if it's time-in or time-out
        attendance, created = Attendance.objects.get_or_create(
            employee=employee, 
            date=now.date(),
            defaults={'time_in': now}
        )
        if not created and not attendance.time_out:
            attendance.time_out = now
            attendance.save()

        # Implement logic to calculate total hours, late flag, etc.

        return Response({'status': 'success', 'message': 'Attendance recorded'})

class EmployeeLogin(APIView):
    def post(self, request, format=None):
        insurance_number = request.data.get("insuranceNumber")
        try:
            employee = Employee.objects.get(InsuranceNumber=insurance_number)
            return Response(EmployeeSerializer(employee).data, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)