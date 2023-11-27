from django.shortcuts import render
from rest_framework import generics
from .models import Employee , Department, Position , PositionLevel , Address , Dependent , Signature , EmployeeDocument
from .serializers import EmployeeSerializer , DepartmentSerializer  , PositionLevelSerializer , PositionSerializer ,AddressSerializer , DependentsSerializer , EmployeeNameWithDependentCountSerializer , EmployeeDocumentSerializer , SignatureSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import filters
from django.db.models import Q
from django.db.models import Count
from rest_framework import status
from django.http import Http404, JsonResponse
from rest_framework.decorators import api_view

# List and Create View
class EmployeeListCreateView(generics.ListCreateAPIView):
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        queryset = Employee.objects.all()

        # Search by FirstName, LastName, or InsuranceNumber
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(FirstName__icontains=search_query) | 
                Q(LastName__icontains=search_query) |
                Q(InsuranceNumber__icontains=search_query)
            )

        # Filtering by DateHired
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date and end_date:
            queryset = queryset.filter(DateHired__range=[start_date, end_date])

        # Filtering by DateOfBirth
        dob_start = self.request.query_params.get('dob_start', None)
        dob_end = self.request.query_params.get('dob_end', None)
        if dob_start and dob_end:
            queryset = queryset.filter(DateOfBirth__range=[dob_start, dob_end])

        # Filtering by Gender or MaritalStatus
        gender = self.request.query_params.get('gender', None)
        marital_status = self.request.query_params.get('marital_status', None)
        if gender:
            queryset = queryset.filter(Gender=gender)
        if marital_status:
            queryset = queryset.filter(MaritalStatus=marital_status)

        # Filtering by Department or Position
        department = self.request.query_params.get('department', None)
        position = self.request.query_params.get('position', None)
        if department:
            queryset = queryset.filter(Department__Name=department)
        if position:
            queryset = queryset.filter(Position__Name=position)

        return queryset




# Retrieve, Update, and Delete View



@api_view(['GET'])
def employee_detail(request, insurance_number):
    try:
        employee = Employee.objects.get(InsuranceNumber=insurance_number)
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)
    except Employee.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=404)

class DepartmentListCreateView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class DepartmentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer    



class PositionLevelListCreateView(generics.ListCreateAPIView):
    queryset = PositionLevel.objects.all()
    serializer_class = PositionLevelSerializer

class PositionLevelRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PositionLevel.objects.all()
    serializer_class = PositionLevelSerializer    



class PositionListCreateView(generics.ListCreateAPIView):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer

class PositionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer    


class AddressListCreateView(generics.ListCreateAPIView):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

class AddressRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer


class DependentsListCreateView(generics.ListCreateAPIView):
    queryset = Dependent.objects.all()
    serializer_class = DependentsSerializer

class DependentsRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Dependent.objects.all()
    serializer_class = DependentsSerializer


# function to show org structure 

# class OrgStructureView(APIView):
#     def get(self, request):
#         departments = Department.objects.all()

#         org_structure = []

#         for department in departments:
#             # Serialize the department
#             department_data = DepartmentSerializer(department).data

#             # Fetch and serialize positions related to this department
#             positions = Position.objects.filter(Department=department)
#             positions_data = PositionSerializer(positions, many=True).data

#             for position in positions_data:
#                 # Fetch and serialize employees related to this position
#                 employees = Employee.objects.filter(position__Name=position['Name'])
#                 position['employees'] = EmployeeSerializer(employees, many=True).data

#             department_data['positions'] = positions_data

#             org_structure.append(department_data)

#         return Response(org_structure)

#function to show employee names with their dependents number

class EmployeeWithDependentsCountView(APIView):

    def get(self, request):
        # Annotate each employee with their dependents count
        employees_with_counts = Employee.objects.annotate(dependents_count=Count('dependent'))

        # Serialize the data
        serializer = EmployeeNameWithDependentCountSerializer(employees_with_counts, many=True)

        return Response(serializer.data)
    


class SignatureListCreateView(generics.ListCreateAPIView):
    queryset = Signature.objects.all()
    serializer_class = SignatureSerializer

class SignatureDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Signature.objects.all()
    serializer_class = SignatureSerializer

class EmployeeDocumentListCreateView(generics.ListCreateAPIView):
    queryset = EmployeeDocument.objects.all()
    serializer_class = EmployeeDocumentSerializer

class EmployeeDocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EmployeeDocument.objects.all()
    serializer_class = EmployeeDocumentSerializer



def get_org_structure(request):
    org_structure = []
    for department in Department.objects.all():
        department_data = {
            'Department': department.Name,
            'Positions': []
        }

        positions = Position.objects.filter(Department=department)
        for position in positions:
            position_data = {
                'Position': position.Name,
                'Level': position.Level.LevelName,
                'Employees': []
            }

            employees = Employee.objects.filter(position=position)
            for employee in employees:
                employee_data = {
                    'Name': f"{employee.FirstName} {employee.LastName}",
                    'DateHired' : employee.DateHired
                }
                position_data['Employees'].append(employee_data)

            department_data['Positions'].append(position_data)
        org_structure.append(department_data)

    return JsonResponse(org_structure, safe=False)    