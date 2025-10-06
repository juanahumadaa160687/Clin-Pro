from django.urls import path
from .views import calendar_view, pagos_view, reservas_view, modificar_reserva_view, validar_pago_view, \
    editar_reserva_view, delete_reserva_view
from clinpro.views import logout

urlpatterns = [
    path('dashboard_recepcion/', calendar_view, name='dashboard_recepcion'),
    path('reservas/', reservas_view, name='reservas'),
    path('modificar_reserva/', modificar_reserva_view, name='modificar_reserva_view'),
    path('validar_pago/', validar_pago_view, name='validar_pago'),
    path('pagos/', pagos_view, name='pagos'),
    path('edit_reserva/<int:reserva_id>/', editar_reserva_view, name='editar_reserva'),
    path('delete_reserva/<int:reserva_id>/', delete_reserva_view, name='delete_reserva'),
    path('logout/', logout, name='logout')
]