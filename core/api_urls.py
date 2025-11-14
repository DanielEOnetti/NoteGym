# core/api_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EjercicioViewSet

# Creamos un router de DRF
router = DefaultRouter()

# Registramos nuestro ViewSet.
# DRF creará automáticamente las URLs para list, create, retrieve, update, delete
router.register(r'ejercicios', EjercicioViewSet, basename='ejercicio')

# Las URLs de la API son determinadas automáticamente por el router.
urlpatterns = [
    path('', include(router.urls)),
]