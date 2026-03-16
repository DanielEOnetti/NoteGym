from django.db import transaction
from .models import Entrenamiento, DetalleEntrenamiento, SerieEjercicio

def replicar_planificacion_semanal(entrenamiento_origen, semanas_destino):
    """
    Toma un entrenamiento existente (ej: Semana 1, Día A) y crea copias idénticas
    para las semanas indicadas, pero SIN los datos de ejecución (pesos reales/RPE real).
    
    Args:
        entrenamiento_origen (Entrenamiento): El objeto base a copiar.
        semanas_destino (list[int]): Lista de números de semana (ej: [2, 3, 4]).
    """
    
    # Validaciones básicas
    if not entrenamiento_origen.mesociclo:
        raise ValueError("Este entrenamiento no pertenece a un mesociclo.")
    
    nuevos_entrenamientos = []

    with transaction.atomic():
        for num_semana in semanas_destino:
            
            # 1. Verificar si ya existe ese día en esa semana para evitar duplicados
            ya_existe = Entrenamiento.objects.filter(
                mesociclo=entrenamiento_origen.mesociclo,
                semana=num_semana,
                dia_orden=entrenamiento_origen.dia_orden
            ).exists()
            
            if ya_existe:
                continue # Saltamos si ya existe para no machacar datos por error

            # 2. Copiar el objeto Entrenamiento (Cabecera)
            nuevo_entreno = Entrenamiento.objects.create(
                entrenador=entrenamiento_origen.entrenador,
                atleta=entrenamiento_origen.atleta,
                mesociclo=entrenamiento_origen.mesociclo,
                nombre=entrenamiento_origen.nombre, # Ej: "Torso A"
                notas=entrenamiento_origen.notas,   # Copiamos notas generales
                dia_orden=entrenamiento_origen.dia_orden, # Mismo "Día A"
                semana=num_semana # Cambiamos solo la semana
            )
            
            # 3. Copiar Detalles (Ejercicios)
            detalles_origen = entrenamiento_origen.detalles.all().order_by('orden')
            
            for detalle in detalles_origen:
                nuevo_detalle = DetalleEntrenamiento.objects.create(
                    entrenamiento=nuevo_entreno,
                    ejercicio=detalle.ejercicio,
                    orden=detalle.orden,
                    peso_recomendado=detalle.peso_recomendado, # Opcional: Copiar o dejar None
                    notas=detalle.notas
                )
                
                # 4. Copiar Series (Aquí está la clave del RPE)
                series_origen = detalle.series.all().order_by('numero_serie')
                
                # ¡ATENCIÓN A LA INDENTACIÓN AQUÍ! Debe ir dentro del "for detalle"
                for serie in series_origen:
                    SerieEjercicio.objects.create(
                        detalle_entrenamiento=nuevo_detalle,
                        numero_serie=serie.numero_serie,
                        
                        # --- LO QUE SE COPIA (La prescripción del entrenador) ---
                        repeticiones_o_rango=serie.repeticiones_o_rango,
                        rpe_prescrito=serie.rpe_prescrito, 
                        
                        # --- LO QUE AHORA SE MANTIENE COMO REFERENCIA ---
                        peso_real=serie.peso_real,                    # Mantiene el peso de la semana anterior
                        repeticiones_reales=serie.repeticiones_reales, # Mantiene las repeticiones logradas
                        
                        # --- LO QUE SE LIMPIA (El feedback de la nueva sesión) ---
                        rpe_real=None                                 # Se vacía el esfuerzo percibido para que lo rellene
                    )
            
            # Esto debe ir fuera del "for detalle", para añadir el entreno una sola vez
            nuevos_entrenamientos.append(nuevo_entreno)
            
    return nuevos_entrenamientos