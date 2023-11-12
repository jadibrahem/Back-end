from collections import Counter
from rest_framework import generics, permissions, status
from itertools import count
from operator import countOf
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets
from .models import Leave, LeaveAllocation , Employee, LeaveStatus, LeaveType
from .serializers import LeaveSerializer, LeaveAllocationSerializer , EmployeeLeaveAllocationSerializer , LeaveRequestSerializer , SignatureSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from base.models import Signature
from rest_framework.parsers import MultiPartParser, FormParser

class LeaveViewSet(viewsets.ModelViewSet):
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer


class CreateLeaveRequest(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LeaveSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LeaveDetailView(generics.RetrieveUpdateAPIView):
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        leave = self.get_object()

        # Restrict updates to only the 'Status' field and only for admin users
        if request.user.is_staff:
            new_status = request.data.get('Status', None)
            if new_status and new_status in LeaveStatus.choices:
                leave.Status = new_status
                leave.save()
                return Response({'status': new_status}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid or missing 'Status' field."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "You do not have permission to change the leave status."},
                            status=status.HTTP_403_FORBIDDEN)
class ApproveLeaveRequest(APIView):
    def post(self, request, pk, *args, **kwargs):
        leave = get_object_or_404(Leave, pk=pk)
        leave.Status = LeaveStatus.APPROVED
        leave.save()
        return Response({'status': 'approved'}, status=status.HTTP_200_OK)

class RejectLeaveRequest(APIView):
    def post(self, request, pk, *args, **kwargs):
        leave = get_object_or_404(Leave, pk=pk)
        leave.Status = LeaveStatus.REJECTED
        leave.save()
        return Response({'status': 'rejected'}, status=status.HTTP_200_OK)

class ListLeaveRequestsByStatus(APIView):
    def get(self, request, *args, **kwargs):
        status_param = request.query_params.get('status')
        if status_param and status_param in dict(LeaveStatus.choices):
            leaves = Leave.objects.filter(Status=status_param)
            serializer = LeaveSerializer(leaves, many=True)
            return Response(serializer.data)
        return Response({'detail': 'Invalid or missing status parameter.'}, status=status.HTTP_400_BAD_REQUEST)



class LeaveAllocationViewSet(viewsets.ModelViewSet):
    queryset = LeaveAllocation.objects.all()
    serializer_class = LeaveAllocationSerializer

    def list(self, request, *args, **kwargs):
        print("Inside the list method")  # <--- Debugging print statement
        queryset = self.get_queryset()
        for allocation in queryset:
            allocation.update_leaves()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.update_leaves()  # Update the leave allocation before retrieving
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class EmployeeLeaveViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeLeaveAllocationSerializer
    



class LeaveRequestAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)  # Add these parsers to handle file upload
    def post(self, request, *args, **kwargs):
        # Retrieve the insurance number from the request data
        insurance_number = request.data.get('InsuranceNumber')
        # Find the employee with the given insurance number
        employee = get_object_or_404(Employee, InsuranceNumber=insurance_number)
        # Handle file upload
        signature_file = request.FILES.get('signature_file')
        if signature_file:
            # Save the signature
            signature, created = Signature.objects.get_or_create(employee=employee)
            signature.signature_file.save(name='signature.png', content=signature_file, save=True)
            
        else:
            return Response({"error": "Signature file is missing."}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new leave request
        leave_data = {
            'Employee': employee.pk,
            'LeaveType': request.data.get('LeaveType'),
            'StartDate': request.data.get('StartDate'),
            'EndDate': request.data.get('EndDate'),
            'Reason': request.data.get('Reason'),
            # Assume Status is set to PENDING by default in the model
        }
       
        serializer = LeaveSerializer(data=leave_data)
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # If not valid, print the errors to the console and return them in the response
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




def employee_leave_info(request):
    employees_info = []

    for employee in Employee.objects.all():
        leave_allocation = LeaveAllocation.objects.filter(Employee=employee).first()
        approved_leaves = Leave.objects.filter(Employee=employee, Status=LeaveStatus.APPROVED)

        # Initialize leave details with all leave types set to 0
        leave_details = {label: 0 for _, label in LeaveType.choices}

        # Sum the duration of leaves by type
        for leave in approved_leaves:
            leave_type_label = dict(LeaveType.choices)[leave.LeaveType]
            leave_duration = (leave.EndDate - leave.StartDate).days + 1
            leave_details[leave_type_label] += leave_duration

        employee_data = {
            'EmployeeID': employee.EmployeeID,
            'Name': f"{employee.FirstName} {employee.LastName}",
            'LeaveDetails': leave_details
        }

        if leave_allocation:
            employee_data.update({
                'TakenLeaves': leave_allocation.used_leaves,
                'RemainingLeaves': leave_allocation.remaining_leaves
            })
        else:
            employee_data.update({
                'TakenLeaves': 'Not Available',
                'RemainingLeaves': 'Not Available'
            })

        employees_info.append(employee_data)

    return JsonResponse(employees_info, safe=False)