# serializers.py
from rest_framework import serializers
from attendance.models import Attendance
from base.models import Employee , Position
from .models import Team, TeamRole , TeamMember , TeamType


class TeamRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamRole
        fields = ['id', 'name', 'description']


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ('id', 'Name')

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'time_in', 'time_out', 'attendance_status']
class EmployeeSerializer(serializers.ModelSerializer):
    position = serializers.SlugRelatedField(slug_field='Name', read_only=True)

    class Meta:
        model = Employee
        fields = [ 'FirstName', 'LastName', 'position']


class TeamMemberSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer()
    position = PositionSerializer()
    team_role = TeamRoleSerializer()

    class Meta:
        model = TeamMember
        fields = ('id', 'employee', 'position', 'team_role')

class TeamRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamRole
        fields = ['id', 'name', 'description']


class TeamTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamType
        fields = ('id', 'name', 'description')     



class TeamSerializer(serializers.ModelSerializer):
    team_type = TeamTypeSerializer()
    members = TeamMemberSerializer(many=True)

    class Meta:
        model = Team
        fields = ('id', 'name', 'team_type', 'members')     