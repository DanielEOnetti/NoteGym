from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Entrenamiento, PerfilUsuario 

# Escucha el evento 'post_save' (después de guardar) del modelo Entrenamiento
@receiver(post_save, sender=Entrenamiento)
def asignar_entrenador_a_atleta(sender, instance, created, **kwargs):
    """
    Cuando se crea un nuevo Entrenamiento, esta función se activa.
    Comprueba si el atleta de ese entrenamiento ya tiene un entrenador asignado.
    Si no lo tiene, le asigna el entrenador que creó el entrenamiento.
    """
    
    # 'created' es True solo la primera vez que se guarda (creación)
    if created:
        atleta = instance.atleta
        entrenador = instance.entrenador 

        # Verificación de seguridad:
        # 1. ¿Existe un atleta en el entrenamiento?
        # 2. ¿Existe un entrenador en el entrenamiento?
        # 3. ¿El atleta NO tiene ya un entrenador asignado?
        if atleta and entrenador and atleta.entrenador is None:
            
            # ¡La asignación automática!
            atleta.entrenador = entrenador
            atleta.save()
            
            # (Opcional) Puedes dejar esto para verificar en tu consola que funciona
            print(f"Signal: Atleta {atleta.nombre} asignado a Entrenador {entrenador.nombre}")