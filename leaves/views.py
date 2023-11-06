from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets
from .models import Leave, LeaveAllocation , Employee, LeaveStatus
from .serializers import LeaveSerializer, LeaveAllocationSerializer , EmployeeLeaveAllocationSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

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
    