from django.urls import include, path, include
from django.views.decorators.cache import cache_page
from django.views.i18n import JavaScriptCatalog

from .views import *

urlpatterns = [
    #paciente y reserva de hora
    path('', index, name='index'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout, name='logout'),
    path('password_reset/', password_reset, name='password_reset'),
    path('profile/', profile, name='profile'),
    path('reserva/', reserva_hora, name='reserva_hora'),

    #recepcion
    path('recepcion/', recepcionista_view, name='recepcion'),

    #profesional
    path('profesional/', profesional_view, name='profesional'),

    #administrador
    path('administrador/', admin_view, name='administrador'),
    path('registro_funcionarios/', registro_funcionarios, name='registro_funcionarios'),

    #Autorizacion denegada
    path('no_autorizado/', no_autorizado, name='no_autorizado'),

    #Pago Exitoso
    path('pago_exitoso/', pago_exitoso, name='pago_exitoso'),

    # Social Auth
    path("", include('social_django.urls', namespace="social")),

    path(
        'jsi18n/',
        cache_page(3600)(JavaScriptCatalog.as_view(packages=['formset'])),
        name='javascript-catalog'
    ),
]