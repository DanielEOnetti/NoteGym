# core/views.py

import logging
from django import forms
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DeleteView, FormView
from django.db.models import Subquery, OuterRef, DecimalField
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction  # Proporciona herramientas para manejar transacciones atómicas en la base de datos.
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.forms import inlineformset_factory,modelformset_factory
from decimal import Decimal
# Clases base de vistas genéricas proporcionadas por Django.
from django.views.generic import CreateView, UpdateView, DetailView, ListView, TemplateView

# Importación de los modelos utilizados en las vistas.
from .models import PerfilUsuario, Entrenamiento, Ejercicio, SerieEjercicio, DetalleEntrenamiento
# Importación de formularios y formsets definidos en el módulo forms.py.
from .forms import (
    RegistroUsuarioForm, EntrenamientoForm, EjercicioForm,
    SerieRegistroFormSet,  DetalleEntrenamientoForm,DetalleEntrenamientoFormSet, SerieFormSet, SeriePrescripcionInlineFormSet
)
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.db import transaction
import json

def root_redirect(request):
    return redirect('login')
# -------------------------------------------------
# AUTENTICACIÓN DE USUARIOS
# -------------------------------------------------

class RegistroUsuarioView(CreateView):
    """
    Vista basada en clase encargada de gestionar el registro de nuevos usuarios.
    Combina la creación del modelo User de Django con el modelo PerfilUsuario personalizado.
    """
    model = PerfilUsuario
    form_class = RegistroUsuarioForm
    template_name = "core/registro.html"
    success_url = reverse_lazy("dashboard")  # Redirige al panel principal tras un registro exitoso.

    def form_valid(self, form):
        """
        Sobrescribe el método form_valid para manejar la creación simultánea de User y PerfilUsuario.
        """
        user = User.objects.create_user(
            username=form.cleaned_data["email"],
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password1"]
        )
        perfil = form.save(commit=False)
        perfil.user = user
        perfil.tipo = form.cleaned_data.get("tipo")
        perfil.save()
        login(self.request, user)
        return redirect("dashboard")


# -------------------------------------------------
# DASHBOARD PRINCIPAL
# -------------------------------------------------

class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Vista principal del sistema (Dashboard), accesible únicamente para usuarios autenticados.
    Muestra información personalizada según el tipo de usuario (entrenador o atleta).
    """
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user

        try:
            perfil = PerfilUsuario.objects.get(user=usuario)
        except PerfilUsuario.DoesNotExist:
            perfil = None

        context["usuario"] = usuario
        context["perfil"] = perfil
        context["tipo_usuario"] = perfil.tipo if perfil else None

        # Personaliza el contexto en función del tipo de perfil.
        if perfil:
            if perfil.tipo == "entrenador":
                context["entrenamientos_creados"] = Entrenamiento.objects.filter(entrenador=perfil)
                context["total_atletas"] = PerfilUsuario.objects.filter(entrenador=perfil).count()
            elif perfil.tipo == "atleta":
                context["mis_rutinas"] = Entrenamiento.objects.filter(atleta=perfil)

        return context


# -------------------------------------------------
# GESTIÓN DE ENTRENAMIENTOS (CREACIÓN Y EDICIÓN)
# -------------------------------------------------

class EntrenamientoCreateView(LoginRequiredMixin, CreateView):
    """
    Vista que permite al entrenador crear un nuevo entrenamiento.
    Utiliza un formset para asociar múltiples ejercicios a una misma rutina.
    """
    model = Entrenamiento
    form_class = EntrenamientoForm
    template_name = "core/entrenamientos/crear.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["detalle_formset"] = DetalleEntrenamientoFormSet(
                self.request.POST, prefix='detalles'
            )
        else:
            context["detalle_formset"] = DetalleEntrenamientoFormSet(prefix='detalles')
        return context

    def form_valid(self, form):
        """
        Guarda el entrenamiento y los detalles asociados en una transacción atómica
        para mantener la consistencia de la base de datos.
        """
        form.instance.entrenador = self.request.user.perfil
        context = self.get_context_data()
        detalle_formset = context["detalle_formset"]

        if detalle_formset.is_valid():
            with transaction.atomic():
                self.object = form.save()
                detalle_formset.instance = self.object
                detalle_formset.save()
            return redirect('configurar_series', pk=self.object.pk)
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('configurar_series', kwargs={'pk': self.object.pk})


class EntrenamientoUpdateView(LoginRequiredMixin, UpdateView):
    model = Entrenamiento
    form_class = EntrenamientoForm
    template_name = "core/entrenamientos/editar.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entrenamiento = self.object

        if self.request.POST:
            context["detalle_formset"] = DetalleEntrenamientoFormSet(
                self.request.POST,
                instance=entrenamiento,
                prefix='detalles'
            )
        else:
            # (Correcto) Aseguramos el orden al cargar
            queryset_detalles = entrenamiento.detalles.order_by('orden')
            context["detalle_formset"] = DetalleEntrenamientoFormSet(
                instance=entrenamiento,
                prefix='detalles',
                queryset=queryset_detalles 
            )
        
        # (Correcto) Aseguramos el orden para la visualización
        context['detalles'] = entrenamiento.detalles.order_by('orden').prefetch_related('series')
        return context

    # ==========================================================
    # ===       ¡FORM_VALID 100% CORREGIDO Y FUSIONADO!      ===
    # ==========================================================
    def form_valid(self, form):
        context = self.get_context_data()
        detalle_formset = context["detalle_formset"]

        if detalle_formset.is_valid():
            with transaction.atomic():
                # 1. Guardar entrenamiento
                self.object = form.save()
                
                # 2. Obtener el 'orden' máximo actual
                max_orden_result = self.object.detalles.aggregate(Max('orden'))
                current_max_orden = max_orden_result['orden__max'] or 0

                # 3. Preparar el formset (pero no guardar aún)
                detalle_formset.instance = self.object
                
                # 4. Construir el mapa Y guardar objetos (¡FUSIÓN DE LÓGICA!)
                detalle_map = {} # El mapa que tu _procesar_series necesita
                
                # Iteramos sobre los FORMULARIOS (tu método original)
                for i, form_in_formset in enumerate(detalle_formset.forms):
                    
                    # 4A. Manejar borrados (Usando 'deleted_forms' - ¡LA FORMA CORRECTA!)
                    if form_in_formset in detalle_formset.deleted_forms:
                        # Si el objeto ya existe en la BBDD, bórralo
                        if form_in_formset.instance.pk:
                            form_in_formset.instance.delete()
                        # Si no, simplemente no lo procesamos
                        continue
                    
                    # 4B. Saltar formularios inválidos (si los hubiera)
                    if not form_in_formset.is_valid():
                        # (Opcional: podrías querer 'raise' un error aquí)
                        continue 
                        
                    # 4C. Procesar formularios válidos
                    detalle = form_in_formset.instance
                    
                    # ¡AQUÍ ESTÁ LA LÓGICA DEL 'ORDEN'!
                    # Si es un objeto nuevo (sin pk), le asignamos un 'orden'
                    if not detalle.pk:
                        current_max_orden += 1
                        detalle.orden = current_max_orden
                    
                    # Guardamos el objeto (sea nuevo o modificado)
                    detalle.save() # Ahora SÍ tiene un .pk
                    
                    # ¡USAMOS TU LÓGICA DE MAPA!
                    # Añadimos la instancia guardada (con .pk) al mapa
                    detalle_map[str(i)] = detalle
                        
                # 5. Procesar series (Tu lógica original, que ahora recibe el mapa correcto)
                self._procesar_series(self.request.POST, detalle_map)

            messages.success(self.request, "✅ Entrenamiento actualizado correctamente")
            return redirect(self.get_success_url())
        
        else:
            # Si el formset NO es válido
            messages.error(self.request, "⚠️ Por favor, corrige los errores en el formulario.")
            # Pasamos el formset con errores al contexto
            context = self.get_context_data() # Recargamos el contexto
            context['detalle_formset'] = detalle_formset # Sobrescribimos con el formset inválido
            return self.render_to_response(context)

    # (Tu método _procesar_series se mantiene 100% igual)
    def _procesar_series(self, post_data, detalle_map):
        # ... (TU CÓDIGO ORIGINAL VA AQUÍ) ...
        # 1️⃣ Actualizar o eliminar series existentes
        series_existentes = SerieEjercicio.objects.filter(
            detalle_entrenamiento__entrenamiento=self.object
        )

        for serie in series_existentes:
            serie_id = serie.id
            delete_key = f"serie_{serie_id}_delete"
            reps_key = f"serie_{serie_id}_repeticiones"

            if post_data.get(delete_key) == "1":
                serie.delete()
                continue

            if reps_key in post_data:
                serie.repeticiones_o_rango = post_data[reps_key]
            
            serie.save()

        # 2️⃣ Crear nuevas series usando el 'detalle_map'
        new_series_data = {} 

        for key, value in post_data.items():
            if not key.startswith("new_serie_form_"):
                continue
            
            try:
                parts = key.split("_")
                form_index = parts[3] 
                counter = parts[4]    
                data_type = parts[5]  

                serie_key = (form_index, counter)
                
                if serie_key not in new_series_data:
                    new_series_data[serie_key] = {}
                
                new_series_data[serie_key][data_type] = value
                
            except (IndexError, ValueError):
                continue
        
        series_para_crear = []
        for (form_index, counter), data in new_series_data.items():
            
            detalle = detalle_map.get(form_index)
            
            if not detalle:
                continue 
                
            reps = data.get("repeticiones", "")
            numero = data.get("numero", 1) # El JS lo envía
            
            series_para_crear.append(
                SerieEjercicio(
                    detalle_entrenamiento=detalle,
                    repeticiones_o_rango=reps,
                    numero_serie=int(numero)
                )
            )

        # Usar bulk_create para eficiencia
        if series_para_crear:
            SerieEjercicio.objects.bulk_create(series_para_crear)

    # (Tu método get_success_url se mantiene 100% igual)
    def get_success_url(self):
        return reverse("dashboard")


class EntrenamientoDetailView(LoginRequiredMixin, DetailView):
    """
    Vista de detalle de un entrenamiento. Muestra la lista de ejercicios y series asociadas,
    enriquecida con el último peso levantado por el atleta para cada ejercicio.
    """
    model = Entrenamiento
    template_name = "core/entrenamientos/ver_detalle.html"
    context_object_name = "entrenamiento"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entrenamiento = self.get_object()
        
        # Obtenemos al atleta de este entrenamiento
        atleta = entrenamiento.atleta

        # ------------------------------------------------------------------
        # Subquery para el último peso (Esto se mantiene igual)
        # ------------------------------------------------------------------
        ultimo_peso_subquery = SerieEjercicio.objects.filter(
            detalle_entrenamiento__ejercicio=OuterRef('ejercicio__pk'),
            entrenamiento__atleta=atleta,
            peso_real__isnull=False
        ).order_by(
            '-updated_at'
        ).values(
            'peso_real'
        )[:1]

        # ------------------------------------------------------------------
        # Consulta Principal (¡AQUÍ ESTÁ LA ACTUALIZACIÓN!)
        # ------------------------------------------------------------------
        # Añadimos .order_by('orden') para respetar el nuevo campo
        detalles = entrenamiento.detalles.order_by('orden').select_related('ejercicio').annotate(
            ultimo_peso_utilizado=Subquery(
                ultimo_peso_subquery, 
                output_field=DecimalField() # Especificamos el tipo de dato
            )
        ).prefetch_related('series') # Hacemos prefetch de las series del plan actual

        context["detalles"] = detalles
        return context


# -------------------------------------------------
# CONFIGURACIÓN DE SERIES (PRESCRIPCIÓN)
# -------------------------------------------------

class ConfigurarSeriesView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    form_class = forms.Form # Formulario 'dummy'
    # ✅ CORREGIDO: Template name apunta a la página completa
    template_name = "core/includes/serie_ejercicio_form.html" 

    def test_func(self):
        """Asegura que solo el entrenador dueño pueda configurar series."""
        # ✅ MOVIDO: La obtención del entrenamiento se hace ahora en setup()
        # self.entrenamiento = get_object_or_404(Entrenamiento, pk=self.kwargs['pk'])
        try:
            # ✅ RESTAURADO: Usa la relación 'perfil' que funcionó
            return self.request.user.perfil == self.entrenamiento.entrenador
        except AttributeError:
             print(f"Error en test_func: El usuario {self.request.user} no tiene 'perfil' o el entrenamiento no tiene 'entrenador'.")
             return False
        except PerfilUsuario.DoesNotExist:
             print(f"Error en test_func: No existe PerfilUsuario para {self.request.user}.")
             return False


    def setup(self, request, *args, **kwargs):
        """
        ✅ NUEVO: Obtiene el objeto Entrenamiento una vez al inicio 
        y lo guarda en self.entrenamiento.
        Se ejecuta antes que test_func, get_context_data y post.
        """
        super().setup(request, *args, **kwargs)
        self.entrenamiento = get_object_or_404(Entrenamiento, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        """Prepara la lista de (detalle, formset) para el template."""
        context = super().get_context_data(**kwargs)
        # ✅ USA self.entrenamiento obtenido en setup()
        detalles = self.entrenamiento.detalles.all().select_related('ejercicio')
        
        detalles_with_formsets = []
        
        for detalle in detalles:
            prefix = f'series-{detalle.pk}' 
            if self.request.POST:
                serie_formset = SeriePrescripcionInlineFormSet(
                    self.request.POST, 
                    instance=detalle, 
                    prefix=prefix
                )
            else:
                serie_formset = SeriePrescripcionInlineFormSet(
                    instance=detalle, 
                    prefix=prefix
                )
            detalles_with_formsets.append((detalle, serie_formset))
            
        context['entrenamiento'] = self.entrenamiento
        context['detalles_with_formsets'] = detalles_with_formsets
        return context

    def post(self, request, *args, **kwargs):
        """Valida y guarda todos los formsets."""
        print("\n--- ¡Método POST alcanzado! ---") # Mantenemos el print
        # ✅ USA self.entrenamiento obtenido en setup()
        detalles = self.entrenamiento.detalles.all()
        formsets = []
        is_valid = True 

        for detalle in detalles:
            prefix = f'series-{detalle.pk}'
            serie_formset = SeriePrescripcionInlineFormSet(
                self.request.POST, 
                instance=detalle, 
                prefix=prefix
            )
            formsets.append(serie_formset)
            if not serie_formset.is_valid():
                is_valid = False 
                print(f"Errores en formset para Detalle {detalle.pk} (Prefijo: {prefix}):")
                print(serie_formset.errors) 
                print(serie_formset.non_form_errors())

        print("\n--- request.POST ---")
        print(request.POST)
        print("--------------------\n")

        if is_valid:
            try:
                with transaction.atomic():
                    for formset in formsets:
                        # 1. Obtener instancias SIN guardar en DB todavía
                        instances = formset.save(commit=False) 
                        
                        # 2. Iterar y asignar numero_serie ANTES de guardar
                        for i, instance in enumerate(instances):
                            # Comprobación más robusta para None o vacío
                            if instance.numero_serie is None or str(instance.numero_serie).strip() == '': 
                                instance.numero_serie = i + 1 # Asignar número basado en el índice
                            
                            # Importante: Asegurar que la FK al detalle está asignada
                            # (inlineformset_factory debería hacerlo, pero es una doble comprobación)
                            if not instance.detalle_entrenamiento_id and formset.instance:
                                instance.detalle_entrenamiento = formset.instance

                            # Solo guardar si tiene la FK (evita errores si el detalle no existe)
                            if instance.detalle_entrenamiento_id:
                                instance.save() 
                        
                        # 3. Manejar borrados (el formset lo hace automáticamente al guardar)
                        #    Si commit=False no los maneja, puedes hacerlo manualmente:
                        for obj in formset.deleted_objects:
                             obj.delete()

                messages.success(request, "✅ Series configuradas correctamente.")
                return redirect(self.get_success_url()) 
            except Exception as e:
                 print(f"Error durante la transacción de guardado: {e}") 
                 messages.error(request, f"⚠️ Ocurrió un error al guardar: {e}")
        else:
            messages.error(request, "⚠️ Por favor, corrige los errores en las series.")
            
        context = self.get_context_data() 
        return self.render_to_response(context)
    success_url = reverse_lazy("dashboard")

# -------------------------------------------------
# GESTIÓN DE EJERCICIOS
# -------------------------------------------------

class EjercicioCreateView(LoginRequiredMixin, CreateView):
    """
    Vista que permite al usuario crear nuevos ejercicios en el sistema.
    """
    model = Ejercicio
    form_class = EjercicioForm
    template_name = "core/ejercicios/crear.html"
    success_url = reverse_lazy("dashboard")


# -------------------------------------------------
# VISTAS DESTINADAS AL ATLETA
# -------------------------------------------------

class MisRutinasListView(LoginRequiredMixin, ListView):
    """
    Vista que muestra al atleta todas las rutinas asignadas por su entrenador.
    """
    model = Entrenamiento
    template_name = "core/atleta/mis_rutinas.html"
    context_object_name = "rutinas"

    def get_queryset(self):
        return Entrenamiento.objects.filter(atleta=self.request.user.perfil)


logger = logging.getLogger(__name__)


class RutinaEditarRegistroView(LoginRequiredMixin, UpdateView):
    """
    Vista exclusiva para ATLETAS: 
    Permite registrar el peso real y las repeticiones realizadas 
    en las Series de un Entrenamiento.
    """
    model = Entrenamiento
    template_name = "core/atleta/detalle_rutina.html"
    fields = []
    
    # --- Lógica de Permisos (Se mantiene igual) ---
    def dispatch(self, request, *args, **kwargs):
        entrenamiento = self.get_object()
        perfil = request.user.perfil
        
        if perfil.tipo != 'atleta' or entrenamiento.atleta != perfil:
            messages.error(request, "Acceso denegado. Solo el atleta asignado puede registrar este entrenamiento.")
            return redirect('dashboard')
            
        return super().dispatch(request, *args, **kwargs)

    # --- Gestión del Formset (¡AQUÍ ESTÁ LA ACTUALIZACIÓN 1!) ---
    def get_formset(self):
        """Inicializa o procesa el Formset de Series para registro."""
        entrenamiento = self.get_object()
        
        # CAMBIO: Ordenamos por el 'orden' del detalle, y luego por 'numero_serie'
        queryset_series = SerieEjercicio.objects.filter(
            detalle_entrenamiento__entrenamiento=entrenamiento
        ).order_by('detalle_entrenamiento__orden', 'numero_serie')

        if self.request.method == 'POST':
            return SerieRegistroFormSet(
                self.request.POST, 
                queryset=queryset_series, 
                prefix='series'
            )
        else:
            return SerieRegistroFormSet(
                queryset=queryset_series, 
                prefix='series'
            )

    # --- Datos de Contexto (¡AQUÍ ESTÁ LA ACTUALIZACIÓN 2!) ---
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entrenamiento = self.get_object()
        
        context['modo_usuario'] = 'atleta'
        context['entrenamiento'] = entrenamiento
        
        # CAMBIO: Añadimos .order_by('orden') para respetar el nuevo campo
        context['detalles'] = entrenamiento.detalles.order_by('orden').prefetch_related('series') 
        context['series_formset'] = self.get_formset()
        
        return context

    # --- POST (Se mantiene igual) ---
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        series_formset = self.get_formset()

        if series_formset.is_valid():
            with transaction.atomic():
                series_formset.save()
            
            messages.success(request, "✅ Tu registro de entrenamiento ha sido guardado con éxito.")
            return redirect(self.get_success_url())
        
        else:
            messages.error(request, "⚠️ Por favor, corrige los errores en el formulario.")
            context = self.get_context_data()
            context['series_formset'] = series_formset
            return self.render_to_response(context)
    
    # --- get_success_url (Se mantiene igual) ---
    def get_success_url(self):
        """Define a dónde redirigir tras un POST exitoso."""
        return reverse_lazy('detalle_rutina', kwargs={'pk': self.object.pk})

# -------------------------------------------------
# CONSULTAS Y VISUALIZACIÓN DE PROGRESOS
# -------------------------------------------------

class MarcasPersonalesListView(LoginRequiredMixin, TemplateView):
    """
    Vista que muestra las marcas personales registradas por el atleta.
    """
    template_name = "core/atleta/marcas_personales.html"


class ProgresionEjercicioDetailView(LoginRequiredMixin, DetailView):
    """
    Vista detallada de la progresión de un ejercicio específico a lo largo del tiempo.
    """
    model = Ejercicio
    template_name = "core/atleta/progresion_ejercicio.html"


class AtletaProgresionMaxView(LoginRequiredMixin, DetailView):
    """
    Vista que muestra la evolución del levantamiento máximo del atleta en un ejercicio concreto.
    """
    model = Ejercicio
    template_name = "core/atleta/progresion_max.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ejercicio = self.get_object()
        context["series"] = SerieEjercicio.objects.filter(
            detalle_entrenamiento__ejercicio=ejercicio
        ).order_by("-peso_real")[:5]
        return context


# -------------------------------------------------
# FUNCIONES AUXILIARES
# -------------------------------------------------

def custom_logout_view(request):
    """
    Cierra la sesión del usuario actual y redirige a la página de inicio de sesión.
    """
    logout(request)
    return redirect("login")




class MarcasPersonalesListView(LoginRequiredMixin, TemplateView):
    """
    Vista que MUESTRA los récords personales (PR) del atleta.
    La lógica de cálculo ha sido movida al modelo PerfilUsuario.
    """
    template_name = 'core/atleta/marcas_personales.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Obtener el perfil del atleta logueado
        perfil = self.request.user.perfil
        
        # 2. Llamar al método del modelo que hace todo el trabajo
        context['marcas'] = perfil.get_marcas_personales()
        
        # (Opcional) Si aún quieres las variables de debug, puedes añadirlas,
        # aunque ya no son tan necesarias para depurar la lógica de PRs.
        # context['debug_perfil_id'] = perfil.id
        
        return context


class EntrenamientoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Entrenamiento
    template_name = 'core/entrenamientos/entrenamiento_confirm_delete.html' 
    success_url = reverse_lazy('dashboard') 

    def test_func(self):
        entrenamiento = self.get_object()
        try:
            # ✅ CAMBIO: Usamos 'perfil' (el related_name) en lugar de 'perfilusuario'
            perfil_actual = self.request.user.perfil 
            
            if perfil_actual.tipo != 'entrenador':
                 return False
                 
            # Comparamos el PerfilUsuario del user logueado con el PerfilUsuario 
            # guardado en entrenamiento.entrenador (que ya sabemos que es un PerfilUsuario)
            return perfil_actual == entrenamiento.entrenador 
            
        except AttributeError:
             # Este except ahora captura si el User no tiene un Perfil asociado
             print(f"Error: El usuario {self.request.user} no tiene un PerfilUsuario asociado.")
             return False
        except PerfilUsuario.DoesNotExist: 
             # Opcional: Captura específica si la relación es OneToOne y no existe
             print(f"Error: No existe PerfilUsuario para el usuario {self.request.user}.")
             return False


    def delete(self, request, *args, **kwargs):
        messages.success(self.request, f"✅ Entrenamiento '{self.get_object().nombre}' eliminado correctamente.")
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entrenamiento'] = self.get_object() 
        return context
    




class ListaAtletasView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    
    model = PerfilUsuario
    template_name = 'core/entrenador/lista_atletas.html'
    context_object_name = 'atletas'

    def test_func(self):
        # --- ESTA PARTE (PROBABLEMENTE YA LA CORREGISTE) ---
        if hasattr(self.request.user, 'perfil'):
            return self.request.user.perfil.tipo == 'entrenador'
        return False

    def handle_no_permission(self):
        return redirect('dashboard')

    def get_queryset(self):
        entrenador_actual = self.request.user.perfil
        
        queryset = super().get_queryset().filter(
            
            # === ¡EL ERROR ESTÁ AQUÍ! ===
            # Asegúrate de que ponga "tipo" y no "tipo_usuario"
            tipo='atleta', 
            
            entrenador=entrenador_actual
        )
        return queryset


class AtletaRecordDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Vista de Detalle que permite a un entrenador ver los récords
    de un atleta específico.
    Usa el template 'atleta_record.html'.
    """
    model = PerfilUsuario
    template_name = 'core/entrenador/atleta_record.html'
    context_object_name = 'atleta' # El atleta estará disponible como 'atleta' en el template
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # self.get_object() es el PerfilUsuario del atleta (obtenido por la PK de la URL)
        atleta = self.get_object()
        
        # Usamos el MISMO método de lógica, pero en el objeto del atleta
        context['marcas'] = atleta.get_marcas_personales()
        return context

    def test_func(self):
        """
        Función de seguridad crucial:
        Asegura que el usuario logueado no solo sea entrenador,
        sino que sea EL entrenador del atleta que intenta ver.
        """
        if not hasattr(self.request.user, 'perfil'):
            return False

        perfil_entrenador = self.request.user.perfil
        
        # 1. ¿El usuario es un entrenador?
        if perfil_entrenador.tipo != 'entrenador':
            return False
            
        # 2. ¿El atleta que intenta ver (self.get_object()) 
        #    es realmente un atleta DE ESTE entrenador?
        atleta_a_ver = self.get_object()
        
        return atleta_a_ver.entrenador == perfil_entrenador

    def handle_no_permission(self):
        # Si falla el test_func, lo sacamos de aquí.
        return redirect('dashboard') # O a la lista de atletas
    

@method_decorator(csrf_protect, name='dispatch') # Asegura la protección CSRF
class ActualizarOrdenEjerciciosView(LoginRequiredMixin, View):
    """
    Vista AJAX que recibe el nuevo orden de los ejercicios (DetalleEntrenamiento)
    y actualiza sus campos 'orden' en la base de datos.
    """

    def post(self, request, *args, **kwargs):
        # 1. Validar que el usuario sea un entrenador
        if not request.user.perfil or request.user.perfil.tipo != 'entrenador':
            return HttpResponseForbidden("Acceso denegado. No eres entrenador.")

        # 2. Cargar los datos enviados por AJAX
        try:
            data = json.loads(request.body)
            detalle_ids = data.get('orden') # Esperamos una lista de IDs [3, 1, 2]
            if not isinstance(detalle_ids, list):
                return HttpResponseBadRequest("Datos inválidos.")
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Formato JSON inválido.")
        
        try:
            # 3. Seguridad y Verificación de Datos
            
            # Obtenemos todos los detalles de una vez
            detalles = list(DetalleEntrenamiento.objects.filter(pk__in=detalle_ids))
            
            if not detalles:
                return HttpResponseBadRequest("No se encontraron ejercicios.")
            
            # Obtenemos el 'entrenamiento' del primer ejercicio
            entrenamiento_base = detalles[0].entrenamiento
            
            # --- ¡CHEQUEO DE SEGURIDAD CLAVE! ---
            # Asumimos que la propiedad del Entrenamiento viene dada por
            # el 'entrenador' del 'atleta' asignado.
            if entrenamiento_base.atleta.entrenador != request.user.perfil:
                return HttpResponseForbidden("No tienes permiso para editar este entrenamiento.")

            # Chequeo de integridad: ¿pertenecen todos los IDs al mismo entrenamiento?
            if any(d.entrenamiento_id != entrenamiento_base.id for d in detalles):
                return HttpResponseBadRequest("Los ejercicios pertenecen a entrenamientos diferentes.")

            # 4. Actualizar la base de datos (¡Transacción Atómica!)
            with transaction.atomic():
                # Creamos un mapa de {id: instancia} para eficiencia
                detalle_map = {d.id: d for d in detalles}
                
                # Recorremos la lista de IDs que envió el frontend
                for (index, detalle_id) in enumerate(detalle_ids):
                    # El nuevo orden es el índice + 1 (ej. 1, 2, 3...)
                    nuevo_orden = index + 1
                    
                    detalle = detalle_map.get(int(detalle_id))
                    
                    if detalle and detalle.orden != nuevo_orden:
                        detalle.orden = nuevo_orden
                        detalle.save(update_fields=['orden']) # Eficiente: solo actualiza 'orden'

            # 5. Enviar respuesta de éxito
            return JsonResponse({"status": "ok", "message": "¡Orden actualizado!"})
        
        except DetalleEntrenamiento.DoesNotExist:
            return HttpResponseBadRequest("Un ejercicio no existe.")
        except Exception as e:
            # Captura de error genérico
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
        





class EjercicioListView(LoginRequiredMixin, ListView):
    model = Ejercicio
    template_name = 'core/ejercicios/lista.html'  # La ruta a tu nuevo template
    context_object_name = 'ejercicios'     # El nombre que usaremos en el template
    paginate_by = 15                       # Buena práctica para listas largas


class EjercicioDeleteView(LoginRequiredMixin, DeleteView):
    model = Ejercicio
    
    # URL a la que redirigir después de borrar con éxito
    success_url = reverse_lazy('ejercicio_lista')