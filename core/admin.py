from django.contrib import admin
from .models import PerfilUsuario, Ejercicio, Entrenamiento, DetalleEntrenamiento, SerieEjercicio

class AtletasAsignadosInline(admin.TabularInline):
    model = PerfilUsuario
    fk_name = 'entrenador'  
    verbose_name = 'Atleta Asignado'
    verbose_name_plural = 'Atletas Asignados'
    fields = ('nombre', 'email', 'user') 
    readonly_fields = ('nombre', 'email', 'user')
    extra = 0  
    can_delete = False  
    def get_queryset(self, request):
        return super().get_queryset(request).filter(tipo='atleta')


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "email", "entrenador")
    list_filter = ("tipo", "entrenador") 
    search_fields = ("nombre", "email")
    ordering = ("nombre",)
    inlines = [AtletasAsignadosInline]
    def get_inlines(self, request, obj=None):
        if obj and obj.tipo == 'atleta':
            return []
        return self.inlines
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        fields = list(fields) 
        
        if obj:
            if obj.tipo == 'entrenador':

                if 'entrenador' in fields:
                    fields.remove('entrenador')
                if 'peso' in fields:
                    fields.remove('peso')
            elif obj.tipo == 'atleta':
                pass
        return fields



@admin.register(Ejercicio)
class EjercicioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "video", "created_at")
    search_fields = ("nombre",)
    ordering = ("nombre",)



@admin.register(Entrenamiento)
class EntrenamientoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "entrenador", "atleta", "created_at")
    list_filter = ("entrenador", "atleta", "created_at")
    search_fields = ("nombre", "entrenador__nombre", "atleta__nombre")
    ordering = ("-created_at",)


@admin.register(DetalleEntrenamiento)
class DetalleEntrenamientoAdmin(admin.ModelAdmin):
    list_display = ("entrenamiento", "ejercicio", "peso_recomendado")
    search_fields = ("entrenamiento__nombre", "ejercicio__nombre")
    ordering = ("entrenamiento", "ejercicio")



@admin.register(SerieEjercicio)
class SerieEjercicioAdmin(admin.ModelAdmin):
    list_display = ("detalle_entrenamiento", "numero_serie", "repeticiones_o_rango", "peso_real", "repeticiones_reales")
    list_filter = ("detalle_entrenamiento",)
    ordering = ("detalle_entrenamiento", "numero_serie")