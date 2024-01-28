from django.urls import path
from finance import views  
from finance.views import LoginView , current_user , document_reference , ItemListView , get_purchase_request_details
urlpatterns = [
    # Other URL patterns for your project
    path('finance/login/', LoginView.as_view(), name='login'),
    path('purchase-requests/', views.PurchaseRequestViewSet.as_view({'get': 'list', 'post': 'create'}), name='purchase-request-list'),
    # path('purchase-requests/<int:pk>/', views.PurchaseRequestViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='purchase-request-detail'),
    path('purchase-requests/<int:request_id>/', views.get_purchase_request_details, name='purchase_request_details'),
    path('purchase-requests/<int:request_id>/approve/', views.approve_purchase_request, name='approve_purchase_request'),
    path('purchase-requests/<int:request_id>/reject/', views.reject_purchase_request, name='reject_purchase_request'),
    # ... add other URLs here ...
    path('items/', ItemListView.as_view(), name='item-list'),
    path('current-user/', current_user),
    path('document-reference/', document_reference),
    path('create-purchase-request/', views.create_purchase_request, name='create_purchase_request'),
]