from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from base.models import Employee
from base.serializers import EmployeeSerializer  # You need to create this serializer

class EmployeeLogin(APIView):
    def post(self, request, format=None):
        insurance_number = request.data.get("insuranceNumber")
        try:
            employee = Employee.objects.get(InsuranceNumber=insurance_number)
            return Response(EmployeeSerializer(employee).data, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)