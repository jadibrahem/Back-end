from django.contrib import admin

from .models import Department, PositionLevel, Position, Employee, Address, Dependent , Signature , EmployeeDocument

admin.site.register(Department)
admin.site.register(PositionLevel)
admin.site.register(Position)
admin.site.register(Employee)
admin.site.register(Address)
admin.site.register(Dependent)
admin.site.register(Signature)
admin.site.register(EmployeeDocument)