# serializers.py
from rest_framework import serializers
from .models import PurchaseRequest , Item , PurchaseRequestItem



class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('id', 'name', 'unit_cost', 'description', 'unit')



class PurchaseRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseRequest
        fields = '__all__'


class PurchaseRequestItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer(allow_null=True, required=False)

    class Meta:
        model = PurchaseRequestItem
        fields = ['item', 'quantity', 'currency', 'total_cost', 'donor', 'budget_line', 'comments']

class PurchaseRequestSerializer(serializers.ModelSerializer):
    items = PurchaseRequestItemSerializer(many=True)


    class Meta:
        model = PurchaseRequest
        fields = ['id', 'programme', 'document_reference', 'purchase_request_date', 'location_required', 'date_required', 'created_by', 'status', 'total_cost', 'comments', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        purchase_request = PurchaseRequest.objects.create(**validated_data)

        for item_data in items_data:
            item_data = item_data.get('item', None)
            if item_data and not item_data.get('id'):
                # Create a new item if no ID is provided
                item = Item.objects.create(**item_data)
            else:
                item = Item.objects.get(id=item_data['id'])

            PurchaseRequestItem.objects.create(purchase_request=purchase_request, item=item, **item_data)

        return purchase_request


# class PurchaseRequestItemSerializer(serializers.ModelSerializer):
#     item = ItemSerializer(read_only=True)
#     item_id = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all(), write_only=True, source='item')

#     class Meta:
#         model = PurchaseRequestItem
#         fields = ('id', 'item', 'item_id', 'quantity', 'currency', 'total_cost', 'donor', 'budget_line', 'comments')
#         read_only_fields = ('total_cost',)  # total_cost is calculated in the model's save method

#     def create(self, validated_data):
#         # Create the PurchaseRequestItem
#         purchase_request_item = PurchaseRequestItem.objects.create(**validated_data)
#         return purchase_request_item