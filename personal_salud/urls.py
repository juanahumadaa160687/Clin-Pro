from django.urls import path
from .views import dashboard_fichas

urlpatterns = [
    path('dashboard_fichas/', dashboard_fichas, name='dashboard_fichas'),
]