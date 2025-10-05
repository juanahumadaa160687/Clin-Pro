from django.urls import path
from .views import calendar_view, pagos_view, reservas_view
from clinpro.views import logout

urlpatterns = [
    path('dashboard/', calendar_view, name='dashboard'),
    path('reservas/', reservas_view, name='reservas'),
    path('pagos/', pagos_view, name='pagos'),
    path('logout/', logout, name='logout')
]