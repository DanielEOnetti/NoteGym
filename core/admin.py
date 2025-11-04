from django.contrib import admin
from .models import PerfilUsuario, Ejercicio, Entrenamiento, DetalleEntrenamiento, SerieEjercicio

# ----------------------------------------
# PERFIL DE USUARIO (Mejorado)
# ----------------------------------------

# Define el "Inline" para mostrar atletas en la página del entrenador
class AtletasAsignadosInline(admin.TabularInline):
    model = PerfilUsuario
    fk_name = 'entrenador'  # Usa el campo 'entrenador' de PerfilUsuario
    verbose_name = 'Atleta Asignado'
    verbose_name_plural = 'Atletas Asignados'
    
    # Muestra estos campos (solo lectura)
    fields = ('nombre', 'email', 'user') 
    readonly_fields = ('nombre', 'email', 'user')
    
    extra = 0  # No muestra filas extra para añadir
    can_delete = False  # No permite borrar desde aquí
    
    # Optimización: solo muestra perfiles que sean 'atleta'
    def get_queryset(self, request):
        return super().get_queryset(request).filter(tipo='atleta')


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "email", "entrenador")
    list_filter = ("tipo", "entrenador") # Ahora podemos filtrar por entrenador
    search_fields = ("nombre", "email")
    ordering = ("nombre",)

    # ¡Añadimos el Inline!
    inlines = [AtletasAsignadosInline]

    # --- Mejoras de UX para el Admin ---

    # 1. Oculta el Inline si estamos viendo un 'atleta'
    def get_inlines(self, request, obj=None):
        if obj and obj.tipo == 'atleta':
            return []
        return self.inlines

    # 2. Oculta campos irrelevantes según el tipo de perfil
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        # Copia la lista para poder modificarla
        fields = list(fields) 
        
        if obj:
            if obj.tipo == 'entrenador':
                # Un entrenador no tiene entrenador ni peso
                if 'entrenador' in fields:
                    fields.remove('entrenador')
                if 'peso' in fields:
                    fields.remove('peso')
            elif obj.tipo == 'atleta':
                # Un atleta tiene entrenador y peso (si los añadiste)
                pass
        return fields


# ----------------------------------------
# EJERCICIOS (Tu código)
# ----------------------------------------
@admin.register(Ejercicio)
class EjercicioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "video", "created_at")
    search_fields = ("nombre",)
    ordering = ("nombre",)


# ----------------------------------------
# ENTRENAMIENTOS (Tu código)
# ----------------------------------------
@admin.register(Entrenamiento)
class EntrenamientoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "entrenador", "atleta", "created_at")
    list_filter = ("entrenador", "atleta", "created_at")
    search_fields = ("nombre", "entrenador__nombre", "atleta__nombre")
    ordering = ("-created_at",)


# ----------------------------------------
# DETALLES DE ENTRENAMIENTO (Tu código)
# ----------------------------------------
@admin.register(DetalleEntrenamiento)
class DetalleEntrenamientoAdmin(admin.ModelAdmin):
    list_display = ("entrenamiento", "ejercicio", "peso_recomendado")
    search_fields = ("entrenamiento__nombre", "ejercicio__nombre")
    ordering = ("entrenamiento", "ejercicio")


# ----------------------------------------
# SERIES DE EJERCICIOS (Tu código)
# ----------------------------------------
@admin.register(SerieEjercicio)
class SerieEjercicioAdmin(admin.ModelAdmin):
    list_display = ("detalle_entrenamiento", "numero_serie", "repeticiones_o_rango", "peso_real", "repeticiones_reales")
    list_filter = ("detalle_entrenamiento",)
    ordering = ("detalle_entrenamiento", "numero_serie")