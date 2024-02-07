from rest_framework import serializers
from .models import PurchaseRequest, Item, PurchaseRequestItem, BudgetLine

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('id', 'name', 'unit_cost', 'description', 'unit')

class BudgetLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetLine
        fields = ('id', 'name', 'description')

class PurchaseRequestItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer(allow_null=True, required=False)
    budget_line = BudgetLineSerializer(allow_null=True, required=False)

    class Meta:
        model = PurchaseRequestItem
        fields = ['id', 'item', 'quantity', 'currency', 'total_cost', 'donor', 'budget_line', 'comments']

    def create(self, validated_data):
        item_data = validated_data.pop('item', None)
        budget_line_data = validated_data.pop('budget_line', None)
        budget_line = None

        if item_data:
            item, _ = Item.objects.get_or_create(**item_data)
            validated_data['item'] = item

        if budget_line_data:
            budget_line, _ = BudgetLine.objects.get_or_create(**budget_line_data)
            validated_data['budget_line'] = budget_line

        purchase_request_item = PurchaseRequestItem.objects.create(**validated_data)
        return purchase_request_item
    def update(self, instance, validated_data):
        item_data = validated_data.pop('item', None)
        budget_line_data = validated_data.pop('budget_line', None)

        # Update the simple fields of PurchaseRequestItem
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

        # Update or create the nested Item
        if item_data:
            item_id = item_data.get('id', None)
            if item_id:
                # Update existing Item
                Item.objects.filter(id=item_id).update(**item_data)
            else:
                # Create new Item and associate it with the PurchaseRequestItem
                item = Item.objects.create(**item_data)
                instance.item = item

        # Update or create the nested BudgetLine
        if budget_line_data:
            budget_line_id = budget_line_data.get('id', None)
            if budget_line_id:
                # Update existing BudgetLine
                BudgetLine.objects.filter(id=budget_line_id).update(**budget_line_data)
            else:
                # Create new BudgetLine and associate it with the PurchaseRequestItem
                budget_line = BudgetLine.objects.create(**budget_line_data)
                instance.budget_line = budget_line

        instance.save()
        return instance
class PurchaseRequestSerializer(serializers.ModelSerializer):
    items = PurchaseRequestItemSerializer(many=True)

    class Meta:
        model = PurchaseRequest
        fields = ['id', 'programme', 'document_reference', 'purchase_request_date', 'location_required', 'date_required', 'created_by', 'status', 'total_cost', 'comments', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        purchase_request = PurchaseRequest.objects.create(**validated_data)

        for item_data in items_data:
            PurchaseRequestItemSerializer().create({'purchase_request': purchase_request, **item_data})

        return purchase_request