from django.contrib import admin
from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('base.urls')),  # Include your  urls here
    path('', include('leaves.urls')),
    path('', include('attendance.urls')),
    path('', include('teams.urls')),
    path('',include('finance.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)