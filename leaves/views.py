from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets
from .models import Leave, LeaveAllocation , Employee, LeaveStatus
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

class UpdateLeaveRequest(APIView):
    def patch(self, request, pk, *args, **kwargs):
        leave = get_object_or_404(Leave, pk=pk)
        if leave.Status in [LeaveStatus.APPROVED, LeaveStatus.REJECTED]:
            return Response({'detail': 'Cannot update a leave that has already been approved or rejected.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = LeaveSerializer(leave, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        print("i get the man")
        # Handle file upload
        signature_file = request.FILES.get('signature_file')
        if signature_file:
            # Save the signature
            signature, created = Signature.objects.get_or_create(employee=employee)
            signature.signature_file.save(name='signature.png', content=signature_file, save=True)
            print("thanks for sinature")
        else:
            print("im stack here")
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
        print("stack here ")
        serializer = LeaveSerializer(data=leave_data)
        print(serializer)
        if serializer.is_valid():
            print("and here two ")
            serializer.save()
            print("im stack here123123")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # If not valid, print the errors to the console and return them in the response
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Don't forget to include the necessary imports at the top of your file