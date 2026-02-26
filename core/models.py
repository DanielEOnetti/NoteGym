# core/models.py
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal  
from django.utils import timezone

class PerfilUsuario(models.Model):
    """
    Modelo que extiende el modelo base de usuario de Django, permitiendo almacenar
    información adicional específica según el rol del usuario (entrenador o atleta).
    Este diseño permite un manejo más flexible y escalable de los distintos tipos de usuarios.
    """

    # Definición de las opciones disponibles para el campo 'tipo', que determina el rol del usuario.
    TIPO_USUARIO = [
        ('entrenador', 'Entrenador'),
        ('atleta', 'Atleta'),
    ]

    # Relación uno a uno con el modelo User proporcionado por Django.
    # Esta relación permite ampliar los datos del usuario sin modificar el modelo original.
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil'  # Permite acceder al perfil mediante user.perfil
    )

    # Tipo de usuario (entrenador o atleta), restringido a las opciones definidas en TIPO_USUARIO.
    tipo = models.CharField(max_length=20, choices=TIPO_USUARIO)

    # Nombre completo del usuario.
    nombre = models.CharField(max_length=100)

    # Dirección de correo electrónico, establecida como campo único para evitar duplicaciones.
    email = models.EmailField(unique=True)

    # Peso corporal del usuario (solo relevante para los atletas).
    # Se permiten valores nulos y campos en blanco para mantener la flexibilidad en el registro.
    # Esta sección del modelo servirá para mejoras futuras
    peso = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Peso en kilogramos (solo atletas)"
    )

    # Relación recursiva que asocia un atleta con su entrenador.
    # En caso de eliminación del entrenador, el campo se establece en NULL.
    entrenador = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='atletas', 
        help_text="Entrenador asignado (solo para atletas)"
    )

    # Representación legible del objeto, útil en el panel de administración y consultas.
    def __str__(self):
        return f"{self.nombre} ({self.tipo})"

    class Meta:
        # Etiquetas legibles para la administración de Django.
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"
        # Define el orden por defecto en las consultas: orden alfabético por nombre.
        ordering = ["nombre"]

    
    
    def get_marcas_personales(self):
        """
        Calcula y devuelve una lista estructurada de los récords personales (PRs)
        para ESTE perfil de atleta.
        """
        
        # 1. Validación: Asegurarse de que el perfil es de un atleta.
        if self.tipo != 'atleta':
            return []  # Los entrenadores no tienen PRs personales

        # 2. Filtrar series válidas
        series_validas = SerieEjercicio.objects.filter(
            detalle_entrenamiento__entrenamiento__atleta=self,
            peso_real__isnull=False,
            repeticiones_reales__isnull=False,
            peso_real__gt=0,
            repeticiones_reales__gt=0
        ).select_related(
            'detalle_entrenamiento__ejercicio',
            'detalle_entrenamiento__entrenamiento'
        )
        
        # 3. Agrupar series por ejercicio y REPETICIONES
        marcas_por_ejercicio = {}
        
        for serie in series_validas:
            ejercicio = serie.detalle_entrenamiento.ejercicio
            peso = Decimal(str(serie.peso_real))
            reps = serie.repeticiones_reales
            fecha = serie.detalle_entrenamiento.entrenamiento.created_at

            if ejercicio.id not in marcas_por_ejercicio:
                marcas_por_ejercicio[ejercicio.id] = {
                    'ejercicio': ejercicio,
                    'records_por_reps': {}
                }

            records = marcas_por_ejercicio[ejercicio.id]['records_por_reps']
            
            # Guardar el PESO MÁXIMO para cada número de repeticiones
            if reps not in records or peso > records[reps]['peso']:
                records[reps] = {
                    'peso': peso,
                    'repeticiones': reps,
                    'fecha': fecha
                }
            elif peso == records[reps]['peso'] and fecha > records[reps]['fecha']:
                records[reps]['fecha'] = fecha
        
        # 4. Procesar récords por ejercicio
        marcas_finales = []
        
        for ejercicio_id, data in marcas_por_ejercicio.items():
            # Esta es la lista de todos los PRs (ej: max 1 rep, max 2 reps, etc.)
            records_lista = list(data['records_por_reps'].values())
            
            if not records_lista:
                continue
            
            # Esto se calcula sobre la lista COMPLETA, antes de filtrar
            record_max_peso = None
            record_max_reps = None
            record_max_peso_1rm = None
            
            for record in records_lista:
                if record_max_peso is None or record['peso'] > record_max_peso['peso']:
                    record_max_peso = record.copy()
                if record_max_reps is None or record['repeticiones'] > record_max_reps['repeticiones']:
                    record_max_reps = record.copy()
                if record['repeticiones'] == 1:
                    if record_max_peso_1rm is None or record['peso'] > record_max_peso_1rm['peso']:
                        record_max_peso_1rm = record.copy()
            
            marcas_no_dominadas = []
            for record_a in records_lista:
                es_dominado = False
                for record_b in records_lista:
                    # No comparar un récord consigo mismo
                    if record_a == record_b:
                        continue
                    
                    # ¿'record_b' domina a 'record_a'?
                    # (Si B tiene MÁS reps con un peso IGUAL O SUPERIOR)
                    if (record_b['peso'] >= record_a['peso'] and 
                        record_b['repeticiones'] > record_a['repeticiones']):
                        
                        es_dominado = True
                        break # 'record_a' es dominado, no necesitamos seguir
                
                # Si, tras comprobar contra todos, no fue dominado, lo añadimos
                if not es_dominado:
                    marcas_no_dominadas.append(record_a)

            # Ordenar la lista filtrada por repeticiones (ascendente: 1, 2, 3, ...)
            marcas_no_dominadas.sort(key=lambda x: x['repeticiones'])

            marcas_finales.append({
                'ejercicio': data['ejercicio'],
                'records_por_reps': marcas_no_dominadas,  
                'record_max_peso': record_max_peso,
                'record_max_reps': record_max_reps,
                'record_max_peso_1rm': record_max_peso_1rm,
            })

        # 5. Ordenar ejercicios alfabéticamente
        marcas_finales.sort(key=lambda x: x['ejercicio'].nombre)
        
        # 6. Devolver el resultado final
        return marcas_finales
    

class Mesociclo(models.Model):
    """
    Agrupa varios entrenamientos en un bloque temporal (ej: 4 semanas).
    Permite organizar la periodización a largo plazo.
    """
    nombre = models.CharField(max_length=150, help_text="Ej: Bloque Hipertrofia - Enero")
    objetivo = models.CharField(max_length=200, blank=True, help_text="Objetivo principal (ej: Ganar Fuerza)")
    
    # Relaciones
    entrenador = models.ForeignKey(
        PerfilUsuario, 
        on_delete=models.CASCADE, 
        limit_choices_to={'tipo': 'entrenador'},
        related_name='mesociclos_creados'
    )
    atleta = models.ForeignKey(
        PerfilUsuario, 
        on_delete=models.CASCADE, 
        limit_choices_to={'tipo': 'atleta'},
        related_name='mesociclos'
    )
    
    # Configuración del bloque
    fecha_inicio = models.DateField(default=timezone.now, verbose_name="Fecha de Inicio")
    semanas_objetivo = models.PositiveIntegerField(
        default=4, 
        help_text="Duración planeada en semanas"
    )
    
    activo = models.BooleanField(default=True, help_text="Si está activo, aparece en el dashboard")
    notas = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.atleta.nombre})"

    class Meta:
        verbose_name = "Mesociclo"
        verbose_name_plural = "Mesociclos"
        ordering = ["-created_at"]

# ----------------------------------------------------------------------
# EJERCICIOS
# ----------------------------------------------------------------------
class Ejercicio(models.Model):
    """
    Modelo que define un ejercicio físico, que puede ser asignado a rutinas
    de entrenamiento. Permite almacenar información descriptiva y audiovisual.
    """

    # Nombre identificativo del ejercicio.
    nombre = models.CharField(max_length=150)

    # Enlace opcional a un video demostrativo (por ejemplo, en YouTube).
    video = models.URLField(blank=True, null=True)

    # Fecha de creación del registro (solo la primera vez).
    created_at = models.DateTimeField(auto_now_add=True)

    # Fecha de carga del registro. En este caso, actúa igual que created_at.
    # Si se desea registrar modificaciones, debería utilizarse auto_now=True.
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Ejercicio"
        verbose_name_plural = "Ejercicios"
        ordering = ["nombre"]


# ----------------------------------------------------------------------
# ENTRENAMIENTO
# ----------------------------------------------------------------------
class Entrenamiento(models.Model):
    """
    Modelo que representa una rutina o plan de entrenamiento asignado a un atleta
    por parte de un entrenador. Incluye relaciones con los perfiles de usuario
    y con los ejercicios a través de una tabla intermedia.
    """

    # Relación con el entrenador que creó la rutina.
    entrenador = models.ForeignKey(
        PerfilUsuario,
        on_delete=models.CASCADE,
        limit_choices_to={'tipo': 'entrenador'},  # Restringe la selección a usuarios con rol de entrenador.
        related_name='entrenamientos_creados'
    )

    # Relación con el atleta al que se le asigna la rutina.
    atleta = models.ForeignKey(
        PerfilUsuario,
        on_delete=models.CASCADE,
        limit_choices_to={'tipo': 'atleta'},  # Restringe la selección a usuarios con rol de atleta.
        related_name='entrenamientos'
    )

    mesociclo = models.ForeignKey(
        Mesociclo, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='entrenamientos',
        help_text="Bloque al que pertenece este entreno"
    )

    nombre = models.CharField(max_length=150, help_text="Nombre de la sesión (ej: Torso A)")
    notas = models.TextField(blank=True, help_text="Notas o comentarios del entrenamiento")

    # NUEVO: Orden temporal dentro del programa
    semana = models.PositiveIntegerField(
        default=1, 
        help_text="Número de semana dentro del mesociclo"
    )
    dia_orden = models.PositiveIntegerField(
        default=1, 
        help_text="Orden de la sesión en la semana (1, 2, 3...)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"S{self.semana} - {self.nombre} ({self.atleta.nombre})"

    class Meta:
        verbose_name = "Entrenamiento"
        verbose_name_plural = "Entrenamientos"
        ordering = ["-created_at"]

    # Nombre identificativo de la rutina.
    nombre = models.CharField(max_length=150, help_text="Nombre del entrenamiento")

    # Notas o comentarios generales sobre la rutina, registrados por el entrenador.
    notas = models.TextField(blank=True, help_text="Notas o comentarios del entrenamiento")

    # Relación muchos a muchos con el modelo Ejercicio, gestionada mediante una tabla intermedia.
    ejercicios = models.ManyToManyField(
        Ejercicio,
        through='DetalleEntrenamiento',
        related_name='entrenamientos'
    )

    # Campos de registro temporal para creación y actualización.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} - {self.atleta.nombre}"

    class Meta:
        verbose_name = "Entrenamiento"
        verbose_name_plural = "Entrenamientos"
        ordering = ["-created_at"]  # Orden descendente por fecha de creación.


# ----------------------------------------------------------------------
# DETALLE DE ENTRENAMIENTO (Tabla intermedia entre Entrenamiento y Ejercicio)
# ----------------------------------------------------------------------
class DetalleEntrenamiento(models.Model):
    """
    Modelo intermedio que define la relación entre un entrenamiento y los ejercicios
    que lo componen. Permite añadir información adicional como peso recomendado,
    notas específicas y material audiovisual del atleta.
    """

    # Referencia al entrenamiento al que pertenece el ejercicio.
    entrenamiento = models.ForeignKey(
        Entrenamiento,
        on_delete=models.CASCADE,
        related_name='detalles'
    )

    # Referencia al ejercicio incluido en el entrenamiento.
    ejercicio = models.ForeignKey(
        Ejercicio,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    

    orden = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
        db_index=True, 
        help_text="Posición del ejercicio en la rutina (1, 2, 3...)"
    )
    

    # Peso sugerido por el entrenador para este ejercicio en esta rutina.
    peso_recomendado = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Peso recomendado por el entrenador (kg)"
    )

    # Notas específicas sobre la ejecución del ejercicio.
    notas = models.TextField(blank=True, help_text="Notas específicas sobre el ejercicio")

    # Campo opcional para que el atleta suba un video con la ejecución.
    # Esto serviría para en un futuruo que el atleta pueda madndar videos de sus ejercicios
    video_atleta = models.FileField(
        upload_to="videos_atletas/",
        blank=True,
        null=True,
        help_text="Video subido por el atleta ejecutando el ejercicio"
    )

    # Campos de control temporal.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.orden}. {self.ejercicio.nombre} - {self.entrenamiento.nombre}"

    class Meta:
        verbose_name = "Detalle de Entrenamiento"
        verbose_name_plural = "Detalles de Entrenamientos"
        ordering = ["entrenamiento", "orden"]

# ----------------------------------------------------------------------
# SERIES DE EJERCICIOS 
# ----------------------------------------------------------------------
class SerieEjercicio(models.Model):
    """
    Modelo que registra los datos específicos de cada serie dentro de un ejercicio.
    Permite almacenar tanto la prescripción (indicaciones del entrenador) como la
    ejecución real (datos del atleta).
    """

    # Relación con el detalle de entrenamiento correspondiente.
    detalle_entrenamiento = models.ForeignKey(
        DetalleEntrenamiento,
        on_delete=models.CASCADE,
        related_name='series'
    )
    entrenamiento = models.ForeignKey(
        Entrenamiento,
        on_delete=models.CASCADE,
        related_name='series',
        null=True,
        blank=True
    )
    
    numero_serie = models.PositiveIntegerField(help_text="Número de la serie")
    repeticiones_o_rango = models.CharField(max_length=20, help_text="Ej: '10' o '8-12'")

    # NUEVO: RPE Prescrito (Instrucción del Entrenador)
    rpe_prescrito = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        null=True, 
        blank=True, 
        help_text="RPE Objetivo (ej: 8, 9)"
    )

    peso_real = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name="Peso levantado (kg)"
    )
    repeticiones_reales = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        verbose_name="Repeticiones realizadas"
    )

    # NUEVO: RPE Real (Feedback del Atleta)
    rpe_real = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        null=True, 
        blank=True,
        verbose_name="RPE Real"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Serie {self.numero_serie} - {self.detalle_entrenamiento.ejercicio.nombre}"

    class Meta:
        verbose_name = "Serie de Ejercicio"
        verbose_name_plural = "Series de Ejercicios"
        ordering = ["detalle_entrenamiento", "numero_serie"]
