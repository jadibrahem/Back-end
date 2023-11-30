from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Department URLs

    path('login/', views.LoginView.as_view(), name='login'),
    path('org-structure/', views.get_org_structure),

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
   
    path('employee/<str:insurance_number>/', views.employee_detail, name='employee-details-by-insurance'),
    # Address URLs
    path('address/', views.AddressListCreateView.as_view(), name='address-list-create'),
    path('address/<int:pk>/', views.AddressRetrieveUpdateDestroyView.as_view(), name='address-detail'),

    # Dependents URLs
    path('dependents/', views.DependentsListCreateView.as_view(), name='dependents-list-create'),
    path('dependents/<int:pk>/', views.DependentsRetrieveUpdateDestroyView.as_view(), name='dependents-detail'),

    #orgstructure
    #path('org-structure/', views.OrgStructureView.as_view(), name='org-structure'),
    
    #to show emoloyee name with their dependent    
    path('employee-dependent-count/', views.EmployeeWithDependentsCountView.as_view(), name='employee-with-dependent-count'),

    # URLs for Signature model operations
    path('signatures/', views.SignatureListCreateView.as_view(), name='signature-list-create'),
    path('signatures/<int:pk>/', views.SignatureDetailView.as_view(), name='signature-detail'),
    
    # URLs for EmployeeDocument model operations
    path('employee-documents/', views.EmployeeDocumentListCreateView.as_view(), name='employee-document-list-create'),
    path('employee-documents/<int:pk>/', views.EmployeeDocumentDetailView.as_view(), name='employee-document-detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)