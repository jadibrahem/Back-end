from datetime import timezone
import decimal
from MySQLdb import IntegrityError
from django.shortcuts import get_object_or_404
from .models import ApprovalLog, PurchaseRequest, Profile , Item ,PurchaseRequestItem , BudgetLine, QuotationRequest, QuotationItem, Supplier, QuotationTerms, Item
from .serializers import BudgetLineSerializer, PurchaseRequestSerializer , PurchaseRequestItemSerializer , ItemSerializer ,QuotationRequestSerializer
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
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseServerError, JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
import logging
from django.db.models import Sum
from django.template.loader import get_template
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import io
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods
from decimal import Decimal, InvalidOperation

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
    # Filter PurchaseRequests by year suffix and order by document_reference to get the last one
    last_pr = PurchaseRequest.objects.filter(document_reference__endswith=f'/{str(year)[-2:]}').order_by('document_reference').last()
    
    if last_pr:
        # Extract the numeric part of the last document reference
        last_id_str = last_pr.document_reference[2:6]  # Assuming format is PR0008/24, adjust if needed
        new_id = int(last_id_str) + 1
    else:
        new_id = 1

    new_id_str = str(new_id).zfill(4)  # Pad with zeros to make sure the ID part is 4 digits
    new_document_reference = f'PR{new_id_str}/{str(year)[-2:]}'  # Format as PR0008/24

    return Response({'document_reference': new_document_reference})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def budget_lines_list(request):
    budget_lines = BudgetLine.objects.all()
    serializer = BudgetLineSerializer(budget_lines, many=True)
    return Response(serializer.data)


class PurchaseRequestViewSet(viewsets.ModelViewSet):
    queryset = PurchaseRequest.objects.all()
    serializer_class = PurchaseRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_purchase_request(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid request method')

    try:
        data = json.loads(request.body)
     
        # Use the request's user instead of looking up by username
        user = request.user

        # Create the PurchaseRequest instance
        purchase_request = PurchaseRequest.objects.create(
            programme=data['programme'],
            location_required=data['location_required'],
            date_required=data['date_required'],
            comments=data.get('comments', ''),
            created_by=user,
            document_reference=data['document_reference'],
        )

        with transaction.atomic():
            purchase_request.save()
            # Handle items and budget lines
            for item_data in data['items']:
                item, _ = Item.objects.get_or_create(
                    description=item_data['description'],
                    defaults={
                        'unit_cost': item_data['unit_cost'],
                        'unit': item_data['unit'],
                    }
                )

                budget_line_id = item_data.get('budget_line')
                budget_line = None
                if budget_line_id:
                    budget_line = BudgetLine.objects.filter(id=budget_line_id).first()

                PurchaseRequestItem.objects.create(
                    purchase_request=purchase_request,
                    item=item,
                    quantity=item_data['quantity'],
                    currency=item_data['currency'],
                    total_cost=item_data['quantity'] * item_data['unit_cost'],
                    donor=item_data.get('donor', ''),
                    budget_line=budget_line,
                    comments=item_data.get('comments', ''),
                )
               
            total_cost = PurchaseRequestItem.objects.filter(purchase_request=purchase_request).aggregate(Sum('total_cost'))['total_cost__sum']
            purchase_request.total_cost = total_cost or 0
            purchase_request.save()   
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
        purchase_request = PurchaseRequest.objects.prefetch_related('items__item', 'items__budget_line').get(id=request_id)

        items_data = [
            {
                "id": item.id,
                "description": item.item.description,
                "unit_cost": item.item.unit_cost,
                "quantity": item.quantity,
                "currency": item.currency,
                "donor": item.donor,
                "budget_line": item.budget_line.name if item.budget_line else None,
                "comments": item.comments,
                "unit": item.item.unit,
                "total_cost": item.total_cost,
            } for item in purchase_request.items.all()
        ]

        purchase_request_data = {
            "id": purchase_request.id,
            "programme": purchase_request.programme,
            "document_reference": purchase_request.document_reference,
            "purchase_request_date": purchase_request.purchase_request_date.isoformat(),
            "location_required": purchase_request.location_required,
            "date_required": purchase_request.date_required.isoformat(),
            "created_by": purchase_request.created_by.username,
            "status": purchase_request.status,
            "total_cost": purchase_request.total_cost,
            "comments": purchase_request.comments,
            "items": items_data,
        }
    
        return JsonResponse(purchase_request_data)

    except PurchaseRequest.DoesNotExist:
        return HttpResponseNotFound(json.dumps({"error": "Purchase request not found"}), content_type="application/json")

@api_view(['PATCH', 'POST'])
@permission_classes([IsAuthenticated])
def update_item(request, item_id):
    try:
        item_data = json.loads(request.body)
        
        # Fetch the PurchaseRequestItem instance
        purchase_request_item = PurchaseRequestItem.objects.get(id=item_id)
        
        # Access the related Item instance
        item = purchase_request_item.item

        # Check if 'unit_cost' is in the request body and update the related Item instance
        if 'unit_cost' in item_data:
            item.unit_cost = item_data['unit_cost']
            item.save()

        # Update fields on PurchaseRequestItem if needed
        purchase_request_item.quantity = item_data.get('quantity', purchase_request_item.quantity)
        purchase_request_item.comments = item_data.get('comments', purchase_request_item.comments)
        # Add more fields as necessary

        purchase_request_item.save()
        return JsonResponse({'status': 'success', 'message': 'Item updated successfully.'})
    except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return HttpResponseBadRequest(f"Validation error: {e}")
    except Exception as e:
            logger.error(f"Unhandled error: {e}")
            return HttpResponseBadRequest(f"Unhandled error: {e}")
    except PurchaseRequestItem.DoesNotExist:
        return HttpResponseNotFound(json.dumps({"error": "Purchase request item not found"}), content_type="application/json")
    except json.JSONDecodeError:
        return HttpResponseBadRequest('Invalid JSON')
    except Exception as e:
        return HttpResponseBadRequest(f'An error occurred: {str(e)}')

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
    

class ApprovalLogsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, purchase_request_id):
        approval_logs = ApprovalLog.objects.filter(purchase_request_id=purchase_request_id).order_by('approved_on')
        data = [
            {
                "approved_by": log.approved_by.username,
                "approval_status": log.approval_status,
                "approved_on": log.approved_on.strftime("%Y-%m-%d %H:%M:%S")
            } for log in approval_logs
        ]
        return Response(data)
    
###############################RFQ####################################################



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_quotation_request(request):
    data = json.loads(request.body)
    test_user_id = 1  # Assuming this is a valid user ID

    try:
        with transaction.atomic():
            # Fetch the test user
            test_user = User.objects.get(pk=test_user_id)

            # Create or get the supplier
            supplier_data = data.get('supplier', {})
            supplier, created = Supplier.objects.get_or_create(
                name=supplier_data.get('name'),
                defaults={
                    'address': supplier_data.get('address'),
                    'contact_person': supplier_data.get('contact_person'),
                    'email': supplier_data.get('email'),
                    'telephone': supplier_data.get('telephone'),
                }
            )

            # Prepare the quotation request reference
            reference = f"RFQ{QuotationRequest.objects.count() + 1}/{now().year}"

            # Create the quotation request
            quotation_request = QuotationRequest(
                created_by=test_user,
                programme=data.get('programme'),
                submission_date=data.get('submission_date'),
                quotation_required_by=data.get('quotation_required_by'),
                supplier=supplier,
                reference=reference
            )
            quotation_request.save()

            # Create the quotation items
            items_data = data.get('items', [])
            for item_data in data['items']:
                item, _ = Item.objects.get_or_create(
                    name=item_data['name'],
                    defaults={
                        'unit_cost': item_data['unit_cost'],
                        'unit': item_data['unit'],
                    }
                )

                QuotationItem.objects.create(
                    quotation_request=quotation_request,
                    item=item,
                    quantity=item_data.get('quantity'),
                    unit_rate=item_data.get('unit_rate'),
                    lead_time=item_data.get('lead_time'),
                    comments=item_data.get('comments')
                )

            # Create the quotation terms
            terms_data = data.get('terms', {})
            QuotationTerms.objects.create(
                quotation_request=quotation_request,
                payment_terms=terms_data.get('payment_terms'),
                delivery_or_collection=terms_data.get('delivery_or_collection'),
                delivery_costs=terms_data.get('delivery_costs'),
                warranty_information=terms_data.get('warranty_information'),
                validity=terms_data.get('validity')
            )

            return JsonResponse({'message': 'Quotation Request created successfully'}, status=201)

    except IntegrityError as e:
        if "Duplicate entry" in str(e) and "finance_quotationrequest.reference" in str(e):
            try:
                with transaction.atomic():
                    # Increment the reference count to avoid duplication
                    new_reference_count = QuotationRequest.objects.count() + 2  # Simple increment, might need a more robust solution
                    new_reference = f"RFQ{new_reference_count}/{now().year}"

                    # Update the quotation request with a new reference and save again
                    quotation_request.reference = new_reference
                    quotation_request.save()

                    # Assuming items and terms are still valid, no need to recreate them

                    return JsonResponse({'message': 'Quotation Request created successfully with a new reference'}, status=201)

            except Exception as retry_exception:
                return JsonResponse({'error': f"An error occurred on retry: {str(retry_exception)}"}, status=500)
        else:
            return JsonResponse({'error': f"An unexpected error occurred: {str(e)}"}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_quotation_request_details(request, pk):
    try:
        quotation_request = QuotationRequest.objects.select_related('supplier', 'terms').prefetch_related('items__item').get(id=pk)

        items_data = [
            {
                "id": item.id,
                "name": item.item.name,
                "description": item.item.description,
                "unit_cost": item.unit_rate,
                "quantity": item.quantity,
                "unit": item.item.unit,
                "total_cost": item.total_cost,
                "lead_time": item.lead_time,
                "comments": item.comments
            } for item in quotation_request.items.all()
        ]

        quotation_request_data = {
            "id": quotation_request.id,
            "programme": quotation_request.programme,
            "submission_date": quotation_request.submission_date.isoformat(),
            "quotation_required_by": quotation_request.quotation_required_by.isoformat(),
            "supplier": {
                "name": quotation_request.supplier.name,
                "address": quotation_request.supplier.address,
                "contact_person": quotation_request.supplier.contact_person,
                "email": quotation_request.supplier.email,
                "telephone": quotation_request.supplier.telephone
            },
            "reference": quotation_request.reference,
            "created_by": quotation_request.created_by.username,
            "items": items_data,
            "terms": {
                "payment_terms": quotation_request.terms.payment_terms,
                "delivery_or_collection": quotation_request.terms.delivery_or_collection,
                "delivery_costs": quotation_request.terms.delivery_costs,
                "warranty_information": quotation_request.terms.warranty_information,
                "validity": quotation_request.terms.validity
            }
        }
    
        return JsonResponse(quotation_request_data)

    except QuotationRequest.DoesNotExist:
        return HttpResponseNotFound(json.dumps({"error": "Quotation request not found"}), content_type="application/json")
@api_view(['GET'])

def list_quotation_requests(request):
    quotation_requests = QuotationRequest.objects.all()
    serializer = QuotationRequestSerializer(quotation_requests, many=True)
    return Response(serializer.data)


@api_view(['GET'])

def quotation_request_details(request, pk):
    try:
        quotation_request = QuotationRequest.objects.get(pk=pk)
        serializer = QuotationRequestSerializer(quotation_request)
        return Response(serializer.data)
    except QuotationRequest.DoesNotExist:
        return Response({'error': 'Quotation Request not found'}, status=status.HTTP_404_NOT_FOUND)