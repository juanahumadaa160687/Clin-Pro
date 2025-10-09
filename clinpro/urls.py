from django.urls import path, include
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('reserva_hora/', reserva_hora, name='reserva_hora'),
    path('pago_exitoso/', pago_exitoso, name='pago_exitoso'),

    path('unauthorized/', no_autorizado, name='no_autorizado'),

]