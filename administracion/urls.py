from django.urls import path
from .views import *

urlpatterns = [
    path('dashboard/', dashboard_admin, name='dashboard'),
    path('login/', login_personal, name='login_personal'),
    path('registro/', registro, name='registro'),
]