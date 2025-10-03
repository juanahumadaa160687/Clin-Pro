from django.urls import path
from .views import *

urlpatterns = [
    path('dashboard/', dashboard_admin, name='dashboard'),
    path('dashboard_servicios/', dashboard_servicios, name='dashboard_servicios'),
    path('personal_dashboard/', dashboard_personal, name='dashboard_personal'),
    path('editar_pofsalud/<int:user_id>', editar_personal_salud, name='editar_personal_salud'),
    path('editar_usuario/<int:user_id>', editar_usuario, name='editar_usuario'),
    path('eliminar_personal/<int:user_id>', eliminar_usuario, name='eliminar_usuario'),
    path('infome/', generar_pdf_view, name='informe'),
]