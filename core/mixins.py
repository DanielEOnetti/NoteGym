# En tu archivo core/mixins.py

from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
# Asume que tienes estos modelos que representan los tipos de perfil (Atleta y Entrenador)
from .models import Atleta, Entrenador 

# Mixin de acceso base que permite controlar los permisos y redirecciones.
class EntrenadorRequiredMixin(AccessMixin):
    """
    Verifica que el usuario esté autenticado Y tenga un perfil de Entrenador.
    Si no lo es, lo redirige a la página de inicio de sesión o al dashboard.
    """
    # Método principal de los Mixins de clase de Django que maneja la lógica antes de ejecutar la vista.
    def dispatch(self, request, *args, **kwargs):
        # 1. Chequea si el usuario está logueado
        if not request.user.is_authenticated:
            # Si el usuario no está autenticado, llama al manejador por defecto (típicamente redirige a LOGIN_URL).
            return self.handle_no_permission() 

        # 2. Chequea si el usuario tiene un perfil de Entrenador
        try:
            # Consulta el modelo Entrenador para ver si existe un perfil asociado al usuario actual (request.user).
            if not Entrenador.objects.filter(user=request.user).exists():
                # Si está logueado pero NO tiene un perfil de Entrenador, lo redirigimos al dashboard.
                return redirect(reverse_lazy('dashboard'))
        except Exception:
            # Captura cualquier excepción (ej. error de base de datos o modelo no configurado)
            # y redirige al dashboard como medida de seguridad.
            return redirect(reverse_lazy('dashboard'))
            
        # Si el usuario está autenticado Y es Entrenador, permite que la solicitud continúe a la vista.
        return super().dispatch(request, *args, **kwargs)


class AtletaRequiredMixin(AccessMixin):
    """
    Verifica que el usuario esté autenticado Y tenga un perfil de Atleta.
    Si no lo es, lo redirige a la página de inicio de sesión o al dashboard.
    """
    # Método que se ejecuta antes de la lógica de la vista.
    def dispatch(self, request, *args, **kwargs):
        # 1. Chequea si el usuario está logueado
        if not request.user.is_authenticated:
            # Si no está logueado, se utiliza la gestión de permisos por defecto (redirige a login).
            return self.handle_no_permission() 

        # 2. Chequea si el usuario tiene un perfil de Atleta
        try:
            # Consulta el modelo Atleta para verificar si hay un perfil asociado al usuario actual.
            if not Atleta.objects.filter(user=request.user).exists():
                # Si está logueado pero NO tiene un perfil de Atleta, lo redirigimos al dashboard.
                return redirect(reverse_lazy('dashboard'))
        except Exception:
            # Captura excepciones y redirige al dashboard para evitar errores en producción.
            return redirect(reverse_lazy('dashboard'))

        # Si el usuario está autenticado Y es Atleta, permite que la solicitud continúe.
        return super().dispatch(request, *args, **kwargs)