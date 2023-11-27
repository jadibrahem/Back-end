from django.urls import path
from .views import LeaveViewSet, LeaveAllocationViewSet , EmployeeLeaveViewSet, ListLeaveRequestsByStatus, LeaveRequestAPIView, employee_leave_info ,LeaveDetailView , employee_leave
from .views import LeavePDFDetail

urlpatterns = [
    # URLs for Leave
    path('leave/', LeaveViewSet.as_view({'get': 'list', 'post': 'create'}), name='leave-list'),
    path('leave/<int:pk>/', LeaveDetailView.as_view(), name='leave-detail'),
    


    path('leave/list-by-status/', ListLeaveRequestsByStatus.as_view(), name='list_leave_requests_by_status'),

    # URLs for LeaveAllocation
    path('leave-allocation/', LeaveAllocationViewSet.as_view({'get': 'list', 'post': 'create'}), name='leaveallocation-list'),
    path('leave-allocation/<int:pk>/', LeaveAllocationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='leaveallocation-detail'),
    
    path('employee-leaves/', EmployeeLeaveViewSet.as_view({'get': 'list'}), name='employee-leaves-list'),
    path('employee-leave-info/', employee_leave_info),
    path('leave-request/', LeaveRequestAPIView.as_view(), name='leave-request'),

    path('employee/<str:insurance_number>/leaves/', employee_leave, name='employee-leave'),

    path('leavepdf/<int:pk>/',LeavePDFDetail.as_view(), name='leave-detail'),
    # ... your other url patterns
 


]