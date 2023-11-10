from rest_framework import serializers
from .models import Department, PositionLevel, Position, Employee, Address, Dependent ,Signature , EmployeeDocument

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class PositionLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = PositionLevel
        fields = '__all__'

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class DependentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dependent
        fields = '__all__'


class EmployeeNameWithDependentCountSerializer(serializers.ModelSerializer):
    dependents_count = serializers.IntegerField()  # This field gets the annotated count

    class Meta:
        model = Employee
        fields = ['FirstName', 'LastName', 'dependents_count']        



class SignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signature
        fields = '__all__'

class EmployeeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeDocument
        fields = '__all__'