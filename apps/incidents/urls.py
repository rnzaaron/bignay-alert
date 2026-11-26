from django.urls import path

from .views import (
    IncidentDetailView,
    IncidentListCreateView,
    IncidentStatusUpdateView,
)

urlpatterns = [
    path('', IncidentListCreateView.as_view(), name='incident-list-create'),
    path('<str:pk>/', IncidentDetailView.as_view(), name='incident-detail'),
    path(
        '<str:pk>/status/',
        IncidentStatusUpdateView.as_view(),
        name='incident-status-update',
    ),
]
