from django.urls import path

import administracion
from .views import *

urlpatterns = [
    path('dashboard/', dashboard_admin, name='dashboard'),
    path('dashboard_servicios/', dashboard_servicios, name='dashboard_servicios'),
]