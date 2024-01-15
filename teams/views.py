from rest_framework.views import APIView
from rest_framework.response import Response
from attendance.models import Attendance
from leaves.models import Leave
from .serializers import AttendanceSerializer
from django.utils import timezone
from rest_framework.generics import ListAPIView
from .models import Team, TeamRole
from .serializers import *
from rest_framework.exceptions import ValidationError

class AttendedEmployeesView(APIView):
    """
    API endpoint that returns a list of employees who have attended on a given date.
    """
    def get(self, request, *args, **kwargs):
        date_query = self.request.query_params.get('date', timezone.now().date())
        attended_employees = Attendance.objects.filter(date=date_query, attendance_status=Attendance.PRESENT)
        serializer = AttendanceSerializer(attended_employees, many=True)
        return Response(serializer.data)


class TeamDetailListView(ListAPIView):
    """
    API endpoint that returns a list of all teams with their members and associated roles.
    """
    queryset = Team.objects.prefetch_related('members__team_role', 'members__employee', 'members__position').all()
    serializer_class = TeamSerializer
class PresentEmployeesNotOnLeaveView(APIView):
    """
    API endpoint that returns a list of employees who are present and not on leave on a given date.
    """
    def get(self, request, *args, **kwargs):
        try:
            date_query = request.query_params.get('date', timezone.now().date())
            # Ensure date is in correct format
            date_query = timezone.datetime.strptime(date_query, '%Y-%m-%d').date()
        except ValueError:
            raise ValidationError('Invalid date format. Please use YYYY-MM-DD format.')

        # Get present employees
        present_employees = Attendance.objects.filter(
            date=date_query,
            attendance_status=Attendance.PRESENT
        ).select_related('employee')

        # Exclude employees who are on leave during the date
        on_leave_employee_ids = Leave.objects.filter(
            StartDate__lte=date_query,
            EndDate__gte=date_query
        ).values_list('Employee__id', flat=True)
        
        eligible_employees = present_employees.exclude(employee__id__in=on_leave_employee_ids)
        
        serializer = EmployeeSerializer(eligible_employees, many=True)
        return Response(serializer.data)


class TeamStructureView(ListAPIView):
    """
    API endpoint that returns the structure of teams along with their required roles.
    """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super(TeamStructureView, self).get_serializer_context()
        context.update({
            'team_roles': TeamRole.objects.all()
        })
        return context