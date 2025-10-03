from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('clinpro.urls')),
    path('administracion/', include('administracion.urls')),
    path('recepcion/', include('recepcion.urls')),
    path('personal/', include('personal_salud.urls')),
    path("", include('social_django.urls', namespace="social"))
]
