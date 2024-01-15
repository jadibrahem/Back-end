from django.urls import path
from .views import *
urlpatterns = [
   path('teams/', AttendedEmployeesView.as_view(), name= 'attended-employees'),
   path('teams/details/', TeamDetailListView.as_view(), name='team-details-list'),
   path('teams/present-not-on-leave/', PresentEmployeesNotOnLeaveView.as_view(), name='present-employees-not-on-leave'),
   path('teams/structure/', TeamStructureView.as_view(), name='team-structure'),
]