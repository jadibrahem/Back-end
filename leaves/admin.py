from django.contrib import admin

# Register your models here.
from .models import Leave , LeaveAllocation

admin.site.register(LeaveAllocation)
admin.site.register(Leave)
