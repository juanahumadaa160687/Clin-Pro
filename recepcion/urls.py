from django.urls import path
from .views import dashboard_view, calendar_view, pagos_view
from clinpro.views import logout

urlpatterns = [
    path('dashboard/', dashboard_view, name='dashboard_view'),
    path('calendar_view/', calendar_view, name='calendar_view'),
    path('reservas/', calendar_view, name='reservas_view'),
    path('pagos/', pagos_view, name='pagos_view'),
    path('logout/', logout, name='logout')
]