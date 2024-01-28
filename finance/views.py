from django.shortcuts import get_object_or_404
from .models import PurchaseRequest, Profile , Item ,PurchaseRequestItem
from .serializers import PurchaseRequestSerializer , PurchaseRequestItemSerializer , ItemSerializer
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from rest_framework import generics
from django.db import transaction
import json
from django.http import HttpResponseNotFound, HttpResponseServerError, JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
import logging

logger = logging.getLogger(__name__)
class LoginView(APIView):
    def post(self, request, format=None):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:    
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({"error": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = request.user
    profile = Profile.objects.get(user=user)  # Get the related Profile for the user
    return Response({
        'username': user.username,
        'user_type': profile.user_type  # Assuming 'user_type' is a field on the Profile model
    })

class ItemListView(generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
def document_reference(request):
    year = now().year
    last_pr = PurchaseRequest.objects.filter(document_reference__startswith=f'PR{year}').last()
    if last_pr:
        last_id_str = last_pr.document_reference[6:]  # Adjust index based on your reference format
        new_id = int(last_id_str) + 1
    else:
        new_id = 1
    new_id_str = str(new_id).zfill(4)  # Pad with zeros
    new_document_reference = f'PR{year}{new_id_str}'
    return Response({'document_reference': new_document_reference})


class PurchaseRequestViewSet(viewsets.ModelViewSet):
    queryset = PurchaseRequest.objects.all()
    serializer_class = PurchaseRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

# class PurchaseRequestViewSet(viewsets.ModelViewSet):
#     queryset = PurchaseRequest.objects.all()
#     serializer_class = PurchaseRequestSerializer
        
#     permission_classes = [permissions.IsAuthenticated]

#     def create(self, request, *args, **kwargs):
#         # Override the create method to handle nested serialization
#         data = request.data
#         purchase_request_serializer = PurchaseRequestSerializer(data=data)
        
#         if purchase_request_serializer.is_valid():
#             purchase_request = purchase_request_serializer.save(created_by=request.user)
            
#             # Now handle the creation of PurchaseRequestItems
#             items_data = data.get('items')
#             if items_data:
#                 for item_data in items_data:
#                     item_serializer = PurchaseRequestItemSerializer(data=item_data)
#                     if item_serializer.is_valid():
#                         item_serializer.save(purchase_request=purchase_request)
#                     else:
#                         purchase_request.delete()  # Rollback if items are invalid
#                         return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
#             return Response(purchase_request_serializer.data, status=status.HTTP_201_CREATED)
#         else:
#             return Response(purchase_request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def perform_update(self, serializer):
#         # Get the current user and their profile
#         current_user = self.request.user
#         profile = Profile.objects.get(user=current_user)

#         # Determine the approval type based on the user's profile
#         if profile.user_type == 'budget_holder':
#             approval_status = 'approved_budget_holder'
#         elif profile.user_type == 'finance_checker':
#             approval_status = 'approved_finance_checker'
#         else:
#             # If the user does not have the right to approve, raise an error
#             raise permissions.PermissionDenied("You do not have permission to approve this request.")

#         # Check the current status of the purchase request
#         purchase_request = serializer.instance
#         if purchase_request.status == 'pending' and approval_status == 'approved_budget_holder':
#             # Save the instance with the updated status by budget holder
#             serializer.save(status=approval_status)
#         elif purchase_request.status == 'approved_budget_holder' and approval_status == 'approved_finance_checker':
#             # Save the instance with the final approved status by finance checker
#             serializer.save(status='approved')
#         elif approval_status in ['approved_budget_holder', 'approved_finance_checker']:
#             # If the request is already processed, don't allow re-approval
#             raise permissions.PermissionDenied("This request has already been processed.")



@csrf_exempt
@permission_classes([IsAuthenticated])
def create_purchase_request(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid request method')

    try:
        data = json.loads(request.body)

        # Fetch the user (adjust this part as per your User model's configuration)
        try:
            user = User.objects.get(username=data['created_by'])
        except User.DoesNotExist:
            return HttpResponseBadRequest('User not found')

        # Create the PurchaseRequest instance
        purchase_request = PurchaseRequest(
            programme=data['programme'],
            location_required=data['location_required'],
            date_required=data['date_required'],
            comments=data.get('comments', ''),
            created_by=user,
            document_reference=data['document_reference'],
            # You can calculate and set total_cost here if necessary
        )

        with transaction.atomic():
            purchase_request.save()

            # Create Item and PurchaseRequestItem instances
            for item_data in data['items']:
                item = Item.objects.create(
                    name=item_data['name'],
                    unit_cost=item_data['unit_cost'],
                    description=item_data.get('description', ''),
                    unit=item_data.get('unit', 'unit'),
                )

                PurchaseRequestItem.objects.create(
                    purchase_request=purchase_request,
                    item=item,
                    quantity=item_data['quantity'],
                    currency=item_data['currency'],
                    total_cost=item_data['quantity'] * item_data['unit_cost'],  # Calculate total cost
                    donor=item_data.get('donor', ''),
                    budget_line=item_data.get('budget_line', ''),
                    comments=item_data.get('comments', ''),
                )

        return JsonResponse({'status': 'success', 'message': 'Purchase request created successfully.'})

    except json.JSONDecodeError:
        return HttpResponseBadRequest('Invalid JSON')
    except KeyError as e:
        return HttpResponseBadRequest(f'Missing key: {e}')
    except Exception as e:
        # Log the error here for more details
        return HttpResponseBadRequest(f'An error occurred: {str(e)}')




@permission_classes([IsAuthenticated])
def get_purchase_request_details(request, request_id):
    try:
        # Retrieve the specific PurchaseRequest and its related items
        purchase_request = PurchaseRequest.objects.select_related('created_by').get(id=request_id)
        items = PurchaseRequestItem.objects.filter(purchase_request=purchase_request)
        
        # Fetch user profile
        user_profile = Profile.objects.get(user=purchase_request.created_by)
      
        # Prepare the data for the response
        purchase_request_data = {
            "programme": purchase_request.programme,
            "document_reference": purchase_request.document_reference,
            "purchase_request_date": purchase_request.purchase_request_date.isoformat(),
            "location_required": purchase_request.location_required,
            "date_required": purchase_request.date_required.isoformat(),
            "created_by": user_profile.user.username,
            "user_type": user_profile.user_type,
            "status": purchase_request.status,
            "total_cost": purchase_request.total_cost,
            "comments": purchase_request.comments,
            "items": [
                {
                    "name": item.item.name,
                    "description": item.item.description,
                    "unit_cost": item.item.unit_cost,
                    "quantity": item.quantity,
                    "currency": item.currency,
                    "donor": item.donor,
                    "budget_line": item.budget_line,
                    "comments": item.comments,
                    "unit": item.item.unit,
                } for item in items
            ]
        }

        return JsonResponse(purchase_request_data)
    except PurchaseRequest.DoesNotExist:
        return HttpResponseNotFound(json.dumps({"error": "Purchase request not found"}), content_type="application/json")
    except Profile.DoesNotExist:
        return HttpResponseNotFound(json.dumps({"error": "User profile not found"}), content_type="application/json")





@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_purchase_request(request, request_id):
    try:
        purchase_request = get_object_or_404(PurchaseRequest, pk=request_id)
        success, message = purchase_request.approve(request.user)

        if success:
            # Log the successful approval
            logger.info(f"Purchase request {purchase_request.id} approved by {request.user.username}")
            return JsonResponse({'status': 'success', 'new_status': purchase_request.status})
        else:
            # Log the reason why approval was not successful
            logger.warning(f"Failed to approve purchase request {purchase_request.id}: {message}")
            return HttpResponseBadRequest(message)
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Error approving purchase request {request_id}: {e}", exc_info=True)
        return HttpResponseBadRequest(f"An unexpected error occurred: {str(e)}")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_purchase_request(request, request_id):
    purchase_request = get_object_or_404(PurchaseRequest, pk=request_id)

    # Example status validation
    if purchase_request.status not in ['pending', 'approved_budget_holder']:
        return HttpResponseBadRequest('Cannot reject a request in its current state.')

    try:
        purchase_request.status = 'rejected'
        purchase_request.save()
        return JsonResponse({'status': 'success', 'new_status': purchase_request.status})
    except Exception as e:
        # Log the exception e
        return HttpResponseServerError('An error occurred while rejecting the request.')