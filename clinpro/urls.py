from django.urls import path, include

from administracion.views import ResetPasswordView
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('registro/', registro, name='registro'),
    path('profile/<int:id>/', profile, name='profile'),
    path('edit_profile/<int:id>/', edit_profile, name='edit_profile'),
    path('delete_profile/<int:id>/', delete_profile, name='delete_profile'),
    path('reserva_hora/', reserva_hora, name='reserva_hora'),
    path('pago_exitoso/', pago_exitoso, name='pago_exitoso'),

    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),

    path('unauthorized/', no_autorizado, name='no_autorizado'),

]