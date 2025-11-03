# core/admin.py
from django.contrib import admin
from .models import PerfilUsuario, Ejercicio, Entrenamiento, DetalleEntrenamiento, SerieEjercicio

# ----------------------------------------
# PERFIL DE USUARIO
# ----------------------------------------
@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "email", "entrenador")
    list_filter = ("tipo",)
    search_fields = ("nombre", "email")
    ordering = ("nombre",)


# ----------------------------------------
# EJERCICIOS
# ----------------------------------------
@admin.register(Ejercicio)
class EjercicioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "video", "created_at")
    search_fields = ("nombre",)
    ordering = ("nombre",)


# ----------------------------------------
# ENTRENAMIENTOS
# ----------------------------------------
@admin.register(Entrenamiento)
class EntrenamientoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "entrenador", "atleta", "created_at")
    list_filter = ("entrenador", "atleta", "created_at")
    search_fields = ("nombre", "entrenador__nombre", "atleta__nombre")
    ordering = ("-created_at",)


# ----------------------------------------
# DETALLES DE ENTRENAMIENTO
# ----------------------------------------
@admin.register(DetalleEntrenamiento)
class DetalleEntrenamientoAdmin(admin.ModelAdmin):
    list_display = ("entrenamiento", "ejercicio", "peso_recomendado")
    search_fields = ("entrenamiento__nombre", "ejercicio__nombre")
    ordering = ("entrenamiento", "ejercicio")


# ----------------------------------------
# SERIES DE EJERCICIOS
# ----------------------------------------
@admin.register(SerieEjercicio)
class SerieEjercicioAdmin(admin.ModelAdmin):
    list_display = ("detalle_entrenamiento", "numero_serie", "repeticiones_o_rango", "peso_real", "repeticiones_reales")
    list_filter = ("detalle_entrenamiento",)
    ordering = ("detalle_entrenamiento", "numero_serie")
