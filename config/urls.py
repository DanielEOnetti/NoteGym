# core/urls.py

# Importaciones principales de Django para la gestión de rutas y administración.
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib import admin
from django.contrib.auth import views as auth_views
from core.views import root_redirect 
from django.contrib.auth import views as auth_views

# Importación de las vistas utilizadas en la aplicación principal (core).
from core.views import (
    RegistroUsuarioView,
    DashboardView,
    custom_logout_view,
    EntrenamientoCreateView,
    EntrenamientoDetailView,
    EntrenamientoUpdateView,
    ConfigurarSeriesView,
    MisRutinasListView,
    RutinaEditarRegistroView,
    MarcasPersonalesListView,
    ProgresionEjercicioDetailView,
    AtletaProgresionMaxView,
    EjercicioCreateView,
    EntrenamientoDeleteView,
    ListaAtletasView,
    AtletaRecordDetailView,
    ActualizarOrdenEjerciciosView,
    EjercicioListView,
    EjercicioDeleteView
    
)
# Importas tu formulario personalizado (¡esto es correcto!)
from core.forms import EmailOrUsernameLoginForm, MyPasswordResetForm, MySetPasswordForm

# ========================================================================
# Definición de patrones de URL del proyecto.
# ========================================================================
urlpatterns = [
    # --------------------------------------------------------------------
    # Administración y utilidades
    # --------------------------------------------------------------------
    path("admin/", admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
    path('', root_redirect, name='root_redirect'),

    # --------------------------------------------------------------------
    # Autenticación y gestión de usuarios
    # --------------------------------------------------------------------

    # Vista genérica de inicio de sesión (LoginView)
    # --- ¡CORRECCIÓN Y MEJORA DE INDENTACIÓN AQUÍ! ---
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="core/login.html",
            authentication_form=EmailOrUsernameLoginForm  # Le pasamos el formulario
        ),  # <-- La llamada a as_view() se cierra aquí
        name="login"  # <-- La coma faltante se añade antes de 'name'
    ),

    # Vista personalizada de cierre de sesión.
    path("logout/", custom_logout_view, name="logout"),

    # Vista de registro de nuevos usuarios.
    path("registro/", RegistroUsuarioView.as_view(), name="registro"),

    # --------------------------------------------------------------------
    # Dashboard general
    # --------------------------------------------------------------------
    path("", DashboardView.as_view(), name="home"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),

    # --------------------------------------------------------------------
    # Gestión de entrenamientos
    # --------------------------------------------------------------------
    path("entrenamientos/crear/", EntrenamientoCreateView.as_view(), name="entrenamiento_crear"),
    path('entrenamiento/<int:pk>/detalle/', EntrenamientoDetailView.as_view(), name='entrenamiento_detail'),
    path("entrenamientos/<int:pk>/editar/", EntrenamientoUpdateView.as_view(), name="entrenamiento_update"),
    path('entrenamiento/<int:pk>/eliminar/', EntrenamientoDeleteView.as_view(), name='entrenamiento_delete'),

    # --------------------------------------------------------------------
    # Configuración de series
    # --------------------------------------------------------------------
    path('entrenamiento/<int:pk>/series/', ConfigurarSeriesView.as_view(), name='configurar_series'),

    # --------------------------------------------------------------------
    # Gestión de ejercicios
    # --------------------------------------------------------------------
    path("ejercicios/crear/", EjercicioCreateView.as_view(), name="ejercicio_crear"),
    path('ejercicios/', EjercicioListView.as_view(), name='ejercicio_lista'),
    path('ejercicios/<int:pk>/eliminar/', 
         EjercicioDeleteView.as_view(), 
         name='ejercicio_delete'),

    # --------------------------------------------------------------------
    # Sección del atleta
    # --------------------------------------------------------------------
    path("mis-rutinas/", MisRutinasListView.as_view(), name="mis_rutinas"),
    path('rutina/<int:pk>/', RutinaEditarRegistroView.as_view(), name='detalle_rutina'),
    path("marcas-personales/", MarcasPersonalesListView.as_view(), name="marcas_personales"),
    path("progresion/<int:pk>/", ProgresionEjercicioDetailView.as_view(), name="progresion_ejercicio"),
    path('mis-atletas/', ListaAtletasView.as_view(), name='lista_atletas'),
    path('entrenador/atleta/<int:pk>/records/', AtletaRecordDetailView.as_view(), name='atleta_record_detail'),
    path("progreso-maximo/<int:ejercicio_pk>/", AtletaProgresionMaxView.as_view(), name="progresion_maxima"),


    path(
        "entrenamientos/actualizar-orden/", 
        ActualizarOrdenEjerciciosView.as_view(), 
        name="actualizar_orden_ejercicios"
    ),

    # 1. Formulario para solicitar el email (¡CORREGIDO!)
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             form_class=MyPasswordResetForm  # <-- Ahora sí usará tu formulario
         ), 
         name='password_reset'),

    # 2. Página mostrada tras enviar el email
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ), 
         name='password_reset_done'),

    # 3. Formulario para introducir la nueva contraseña (¡CORREGIDO!)
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             form_class=MySetPasswordForm  # <-- AÑADE ESTA LÍNEA
         ), 
         name='password_reset_confirm'),

    # 4. Página final de confirmación
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ), 
         name='password_reset_complete'),

]