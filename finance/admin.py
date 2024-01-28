from django.contrib import admin
from .models import Profile, PurchaseRequest, Item, PurchaseRequestItem
from django import forms
# Register your models here.

# Simple registration for Profile model
admin.site.register(Profile)

# Admin class for PurchaseRequest to customize admin interface

# Register PurchaseRequest with its admin class


# Simple registration for Item model
admin.site.register(Item)

# Admin class for PurchaseRequestItem to customize admin interface
class PurchaseRequestItemAdmin(admin.ModelAdmin):
    list_display = ('purchase_request', 'item', 'quantity', 'total_cost')
    search_fields = ('item__name', 'purchase_request__document_reference')
    list_filter = ('donor', 'currency')

# Register PurchaseRequestItem with its admin class
admin.site.register(PurchaseRequestItem, PurchaseRequestItemAdmin)

# Admin class for Approval to customize admin interface
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ('purchase_request', 'approver', 'approval_type', 'status', 'approval_date')
    search_fields = ('purchase_request__document_reference', 'approver__username')
    list_filter = ('approval_type', 'status')

class PurchaseRequestItemForm(forms.ModelForm):
    total_cost_display = forms.CharField(label='Total Cost', required=False)

    class Meta:
        model = PurchaseRequestItem
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['total_cost_display'].initial = self.instance.total_cost
            self.fields['total_cost_display'].disabled = True

class PurchaseRequestItemInline(admin.TabularInline):
    model = PurchaseRequestItem
    form = PurchaseRequestItemForm
    extra = 1
    fields = ('item', 'quantity', 'donor', 'budget_line', 'comments', 'total_cost_display')


class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ('programme', 'document_reference', 'purchase_request_date', 'status')
    search_fields = ('programme', 'document_reference')
    list_filter = ('status', 'location_required')
    inlines = [PurchaseRequestItemInline]  # Add this line    




admin.site.register(PurchaseRequest, PurchaseRequestAdmin)