from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Department URLs
    path('department/', views.DepartmentListCreateView.as_view(), name='department-list-create'),
    path('department/<int:pk>/', views.DepartmentRetrieveUpdateDestroyView.as_view(), name='department-detail'),

    # PositionLevel URLs
    path('positionlevel/', views.PositionLevelListCreateView.as_view(), name='positionlevel-list-create'),
    path('positionlevel/<int:pk>/', views.PositionLevelRetrieveUpdateDestroyView.as_view(), name='positionlevel-detail'),

    # Position URLs
    path('position/', views.PositionListCreateView.as_view(), name='position-list-create'),
    path('position/<int:pk>/', views.PositionRetrieveUpdateDestroyView.as_view(), name='position-detail'),

    # Employee URLs
    path('employee/', views.EmployeeListCreateView.as_view(), name='employee-list-create'),
    path('employee/<int:pk>/', views.EmployeeRetrieveUpdateDestroyView.as_view(), name='employee-detail'),

    # Address URLs
    path('address/', views.AddressListCreateView.as_view(), name='address-list-create'),
    path('address/<int:pk>/', views.AddressRetrieveUpdateDestroyView.as_view(), name='address-detail'),

    # Dependents URLs
    path('dependents/', views.DependentsListCreateView.as_view(), name='dependents-list-create'),
    path('dependents/<int:pk>/', views.DependentsRetrieveUpdateDestroyView.as_view(), name='dependents-detail'),

    #orgstructure
    path('org-structure/', views.OrgStructureView.as_view(), name='org-structure'),
    
    #to show emoloyee name with their dependent    
    path('employee-dependent-count/', views.EmployeeWithDependentsCountView.as_view(), name='employee-with-dependent-count'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)