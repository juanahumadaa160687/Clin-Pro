from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('register/', register, name='register'),
    path('profile/<int:id>', profile, name='profile'),
    path('edit_profile/<int:id>', edit_profile, name='edit_profile'),
    path('delete_profile/<int:id>', delete_profile, name='delete_profile'),
    path('reserva_hora', reserva_hora, name='reserva_hora'),
    path('pago_exitoso', pago_exitoso, name='pago_exitoso'),
    path('accounts/password_reset/', password_reset, name='password_reset'),
    path('accounts/password_reset/done/', password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', password_reset_complete, name='password_reset_complete'),
]