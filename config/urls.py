# core/urls.py

from django.urls import path, include
from django.shortcuts import redirect
from django.contrib import admin
from django.contrib.auth import views as auth_views
from core.views import root_redirect 
from django.contrib.auth import views as auth_views
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
    EjercicioReactListView,MesocicloCreateView, 
    MesocicloDetailView, 
    clonar_semana_view,
    
)

from core.forms import EmailOrUsernameLoginForm, MyPasswordResetForm, MySetPasswordForm, CustomPasswordResetForm

urlpatterns = [
    # --------------------------------------------------------------------
    # Administración y utilidades
    # --------------------------------------------------------------------
    path("admin/", admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
    path('', root_redirect, name='root_redirect'),
    path("login/",auth_views.LoginView.as_view(template_name="core/login.html",authentication_form=EmailOrUsernameLoginForm),name="login"),
    path("logout/", custom_logout_view, name="logout"),
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
    path('ejercicios/', EjercicioReactListView.as_view(), name='ejercicio_lista'),
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


    # Nuevas URLs para Mesociclos
    path('mesociclo/crear/', MesocicloCreateView.as_view(), name='mesociclo_crear'),
    path('mesociclo/<int:pk>/', MesocicloDetailView.as_view(), name='mesociclo_detalle'),
    path('entrenamiento/<int:pk>/clonar/', clonar_semana_view, name='entrenamiento_clonar'),

    # --------------------------------------------------------------------
    # Otros
    # --------------------------------------------------------------------
    path("entrenamientos/actualizar-orden/",ActualizarOrdenEjerciciosView.as_view(),name="actualizar_orden_ejercicios"),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html',form_class=CustomPasswordResetForm, email_template_name='registration/password_reset_email.txt', ),name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html',form_class=MySetPasswordForm),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),name='password_reset_complete'),
    path('api/', include('core.api_urls')),
]