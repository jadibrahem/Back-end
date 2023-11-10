from django.urls import path
from .views import ApproveLeaveRequest, CreateLeaveRequest, LeaveViewSet, LeaveAllocationViewSet , EmployeeLeaveViewSet, ListLeaveRequestsByStatus, RejectLeaveRequest, UpdateLeaveRequest ,LeaveRequestAPIView


urlpatterns = [
    # URLs for Leave
    path('leave/', LeaveViewSet.as_view({'get': 'list', 'post': 'create'}), name='leave-list'),
    path('leave/<int:pk>/', LeaveViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='leave-detail'),
    
    path('leave/create/', CreateLeaveRequest.as_view(), name='create_leave_request'),
    path('leave/update/<int:pk>/', UpdateLeaveRequest.as_view(), name='update_leave_request'),
    path('leave/approve/<int:pk>/', ApproveLeaveRequest.as_view(), name='approve_leave_request'),
    path('leave/reject/<int:pk>/', RejectLeaveRequest.as_view(), name='reject_leave_request'),
    path('leave/list-by-status/', ListLeaveRequestsByStatus.as_view(), name='list_leave_requests_by_status'),

    # URLs for LeaveAllocation
    path('leave-allocation/', LeaveAllocationViewSet.as_view({'get': 'list', 'post': 'create'}), name='leaveallocation-list'),
    path('leave-allocation/<int:pk>/', LeaveAllocationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='leaveallocation-detail'),
    
    path('employee-leaves/', EmployeeLeaveViewSet.as_view({'get': 'list'}), name='employee-leaves-list'),

    path('leave-request/', LeaveRequestAPIView.as_view(), name='leave-request'),
    # ... your other url patterns
 


]