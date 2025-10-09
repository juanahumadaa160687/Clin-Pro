from django.urls import path
from .views import *

urlpatterns = [
    path('dashboard/', dashboard_admin, name='dashboard'),
    path('personal_dashboard/', dashboard_personal, name='dashboard_personal'),
    path('sevicios/', servicios_view, name='servicios'),
    path('editar_servicio/<int:servicio_id>', editar_servicio, name='editar_servicio'),
    path('procedimientos/', procedimientos_view, name='procedimientos'),
    path('editar_procedimiento/<int:procedimiento_id>', editar_procedimiento, name='editar_procedimiento'),
    path('eliminar_servicio/<int:servicio_id>', eliminar_servicio, name='eliminar_servicio'),
    path('eliminar_procedimiento/<int:procedimiento_id>', eliminar_procedimiento, name='eliminar_procedimiento'),
    path('editar_usuario/<int:user_id>', editar_usuario, name='editar_usuario'),
    path('eliminar_personal/<int:user_id>', eliminar_usuario, name='eliminar_usuario'),
    path('infome/', generar_pdf_view, name='informe'),
]