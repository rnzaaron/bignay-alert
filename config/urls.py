from django.contrib import admin
from django.urls import path, include

from .views import csrf_token_view


urlpatterns = [
    path('admin/', admin.site.urls),

    # CSRF token endpoint
    path('api/csrf/', csrf_token_view, name='csrf-token'),

    # API endpoints
    path('api/users/', include('apps.users.urls')),
    path('api/incidents/', include('apps.incidents.urls')),
    path('api/responders/', include('apps.responders.urls')),
    path('api/announcements/', include('apps.announcements.urls')),
    path('api/activity-logs/', include('apps.activity_logs.urls')),
]