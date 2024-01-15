from django.db import models
from base.models import Employee, Position

class TeamType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(max_length=255)
    team_type = models.ForeignKey(TeamType, on_delete=models.CASCADE)
    # Add other fields if necessary, like location, project, etc.

    def __str__(self):
        return self.name

class TeamRole(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    # Other fields can include hierarchy level, responsibilities, etc.

    def __str__(self):
        return self.name

class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    team_role = models.ForeignKey(TeamRole, on_delete=models.CASCADE)
    # Consider adding a 'start_date' and 'end_date' to manage duration of assignments

    def __str__(self):
        return f"{self.employee.FirstName} {self.employee.LastName} - {self.team_role.name} in {self.team.name}"

