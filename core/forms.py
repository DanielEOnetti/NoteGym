# core/forms.py
from django import forms
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.forms import inlineformset_factory, modelformset_factory
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.template import loader
from .models import PerfilUsuario, Entrenamiento, Ejercicio, SerieEjercicio, DetalleEntrenamiento, Mesociclo
from decimal import Decimal, ROUND_HALF_UP
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, get_user_model


# ========================================================================
# Formulario de Registro de Usuario
# ========================================================================
class RegistroUsuarioForm(forms.ModelForm):
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Repetir contraseña", widget=forms.PasswordInput)

    class Meta:
        model = PerfilUsuario
        fields = ["nombre", "email", "tipo"]

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return p2


# ========================================================================
# Formulario de Entrenamiento
# ========================================================================
INPUT_CLASSES = "appearance-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
SELECT_CLASSES = INPUT_CLASSES
TEXTAREA_CLASSES = INPUT_CLASSES + " h-24"


class EntrenamientoForm(forms.ModelForm):
    class Meta:
        model = Entrenamiento
        fields = ["atleta", "mesociclo", "nombre", "semana", "dia_orden", "notas"] # Añadimos campos de organización
        widgets = {
            "atleta": forms.Select(attrs={"class": SELECT_CLASSES}),
            "mesociclo": forms.Select(attrs={"class": SELECT_CLASSES}),
            "nombre": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "semana": forms.NumberInput(attrs={"class": INPUT_CLASSES, "min": "1"}),
            "dia_orden": forms.NumberInput(attrs={"class": INPUT_CLASSES, "min": "1"}),
            "notas": forms.Textarea(attrs={"class": TEXTAREA_CLASSES, "rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and hasattr(user, 'perfil'):
            perfil = user.perfil
            # Solo mostrar mesociclos que pertenecen a este entrenador
            self.fields['mesociclo'].queryset = Mesociclo.objects.filter(entrenador=perfil)
            # Solo mostrar atletas vinculados
            self.fields['atleta'].queryset = PerfilUsuario.objects.filter(
                Q(tipo='atleta'),
                Q(entrenador=perfil) | Q(entrenador__isnull=True)
            ).distinct()

# ========================================================================
# Formulario de Detalle de Entrenamiento
# ========================================================================
class DetalleEntrenamientoForm(forms.ModelForm):
    class Meta:
        model = DetalleEntrenamiento
        fields = ["ejercicio", "notas"] 
        widgets = {
            "ejercicio": forms.Select(attrs={"class": SELECT_CLASSES}),
            "notas": forms.TextInput(attrs={ 
                "class": INPUT_CLASSES, 
                "placeholder": "Indicaciones, series, reps, RIR..."
            }),
        }
        labels = {"notas": "Notas / Series"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ejercicio'].empty_label = "Selecciona un ejercicio"

# ========================================================================
# Definición del FormSet
# ========================================================================
DetalleEntrenamientoFormSet = inlineformset_factory(
    Entrenamiento,
    DetalleEntrenamiento,
    form=DetalleEntrenamientoForm,
    extra=0,
    can_delete=True
)

# ========================================================================
# Formulario de Ejercicio
# ========================================================================
class EjercicioForm(forms.ModelForm):
    class Meta:
        model = Ejercicio
        fields = ["nombre", "video"]
        widgets = {
            "video": forms.URLInput(attrs={"placeholder": "https://..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        input_classes = "appearance-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
        self.fields['nombre'].widget.attrs.update({
            'class': input_classes,
            'placeholder': 'Ej: Press de Banca'
        })
        self.fields['video'].widget.attrs.update({
            'class': input_classes,
        })

# ========================================================================
# Formularios de Series
# ========================================================================

# ------------------------------------------------------------------------
# 1. SeriePrescripcionForm
# ------------------------------------------------------------------------
# core/forms.py

class SeriePrescripcionForm(forms.ModelForm):
    class Meta:
        model = SerieEjercicio
        fields = ["numero_serie", "repeticiones_o_rango", "rpe_prescrito"] # <-- Añadido
        widgets = {
            "numero_serie": forms.HiddenInput(), 
            "repeticiones_o_rango": forms.TextInput(attrs={
                "placeholder": "Ej: 10 o 8-12",
                "class": INPUT_CLASSES 
            }),
            "rpe_prescrito": forms.NumberInput(attrs={ # <-- Nuevo widget
                "placeholder": "RPE",
                "class": INPUT_CLASSES,
                "step": "0.5",
                "min": "1",
                "max": "10"
            }),
        }
        labels = {
            "repeticiones_o_rango": "Repeticiones / Rango *",
            "rpe_prescrito": "RPE Objetivo",
        }

# ========================================================================
# Inline FormSet para Prescripción de Series
# ========================================================================
SeriePrescripcionInlineFormSet = inlineformset_factory(
    DetalleEntrenamiento,
    SerieEjercicio,
    form=SeriePrescripcionForm,
    extra=1,
    can_delete=True,
)

# ------------------------------------------------------------------------
# 2. SerieRegistroForm
# ------------------------------------------------------------------------
class SerieRegistroForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        """
        1. Pone los valores de la sesión anterior (peso/reps/rPE) en el placeholder.
        2. Vacía el valor 'initial' del campo para que aparezca vacío.
        """
        super().__init__(*args, **kwargs)
        
        if not self.is_bound and self.instance and self.instance.pk:
            
            # --- Lógica para 'peso_real' ---
            if self.instance.peso_real is not None:
                peso_val = self.instance.peso_real
                formatted_peso_str = str(peso_val.to_integral_value()) if peso_val == peso_val.to_integral_value() else str(peso_val)
                self.fields['peso_real'].widget.attrs['placeholder'] = f"{formatted_peso_str} kg"
                self.initial['peso_real'] = None

            # --- Lógica para 'repeticiones_reales' ---
            if self.instance.repeticiones_reales is not None:
                reps_val = self.instance.repeticiones_reales
                self.fields['repeticiones_reales'].widget.attrs['placeholder'] = f"{reps_val}"
                self.initial['repeticiones_reales'] = None

            # --- NUEVO: Lógica para 'rpe_real' ---
            if self.instance.rpe_real is not None:
                rpe_val = self.instance.rpe_real
                # Formatear para quitar el .0 si es entero (ej: 8.0 -> 8)
                formatted_rpe = str(rpe_val.to_integral_value()) if rpe_val == rpe_val.to_integral_value() else str(rpe_val)
                self.fields['rpe_real'].widget.attrs['placeholder'] = f"RPE {formatted_rpe}"
                self.initial['rpe_real'] = None

    class Meta:
        model = SerieEjercicio
        fields = [
            "detalle_entrenamiento",
            "numero_serie",
            "peso_real",
            "repeticiones_reales",
            "rpe_real", 
        ]

        input_classes = (
            "w-full text-center text-sm rounded-md border-0 "
            "bg-transparent "
            "px-2 py-1.5 "
            "text-gray-900 font-medium "
            "transition-all duration-150 "
            "focus:outline-none "
            "focus:bg-white "
            "focus:ring-2 "
            "focus:ring-green-500 "
            "placeholder-gray-400"
        )

        widgets = {
            "detalle_entrenamiento": forms.HiddenInput(),
            "numero_serie": forms.HiddenInput(),
            "peso_real": forms.NumberInput(attrs={"step": "0.25", "placeholder": "Peso", "class": input_classes}),
            "repeticiones_reales": forms.NumberInput(attrs={"placeholder": "Reps", "class": input_classes}),
            "rpe_real": forms.NumberInput(attrs={
                "step": "0.5", 
                "placeholder": "RPE", 
                "class": input_classes,
                "min": "1",
                "max": "10"
            }),
        }
        
        labels = {
            "peso_real": "Peso",
            "repeticiones_reales": "Reps",
            "rpe_real": "RPE",
        }

    def clean_peso_real(self):
        peso = self.cleaned_data.get('peso_real')
        if peso is None:
            return peso

        if not isinstance(peso, Decimal):
            try:
                peso = Decimal(str(peso))
            except Exception:
                raise ValidationError("El peso debe ser un número válido.")
        
        peso = peso.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        INCREMENTO_MINIMO = Decimal('0.25')
        residuo = peso % INCREMENTO_MINIMO

        if not residuo.is_zero():
             raise ValidationError(
                 f"El peso debe ser un múltiplo de {INCREMENTO_MINIMO} (ej. 17.0, 17.25, 17.5, 17.75)."
             )
        return peso.to_integral_value() if peso == peso.to_integral_value() else peso

    def clean(self):
        cleaned_data = super().clean()
        
        if not self.instance or not self.instance.pk:
            return cleaned_data

        # Restaurar valores originales si se envían vacíos (para no perder datos al editar)
        if cleaned_data.get('peso_real') is None and self.instance.peso_real is not None:
            cleaned_data['peso_real'] = self.instance.peso_real

        if cleaned_data.get('repeticiones_reales') is None and self.instance.repeticiones_reales is not None:
            cleaned_data['repeticiones_reales'] = self.instance.repeticiones_reales

        # --- NUEVO: Restaurar 'rpe_real' si se envía vacío ---
        if cleaned_data.get('rpe_real') is None and self.instance.rpe_real is not None:
            cleaned_data['rpe_real'] = self.instance.rpe_real

        return cleaned_data


# Creación de FormSets 

SerieFormSet = modelformset_factory(
    SerieEjercicio,
    form=SeriePrescripcionForm,
    extra=0,
    can_delete=True
)

SerieRegistroFormSet = modelformset_factory(
    SerieEjercicio,
    form=SerieRegistroForm,
    extra=0,
    can_delete=False
)


# Formulario de Login Inteligente 

class EmailOrUsernameLoginForm(AuthenticationForm):
    """
    Formulario de autenticación que permite a los usuarios iniciar sesión
    usando su Username (email), su Email O su Nombre de Perfil.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Usuario o Email" 

    def clean(self):
        # El campo 'username' del formulario contiene lo que el usuario escribió
        username_or_email_or_nombre = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username_or_email_or_nombre is not None and password:
            User = get_user_model()
            # Inicializamos el caché de usuario como None
            self.user_cache = None


            # INTENTO 1: Autenticar por USERNAME
            # (El username es el email)
            self.user_cache = authenticate(
                self.request, 
                username=username_or_email_or_nombre, 
                password=password
            )
            

            # INTENTO 2: Autenticar por EMAIL (Fallback)
            if self.user_cache is None:
                try:
                    # Buscamos al usuario por su email
                    user_by_email = User.objects.get(email__iexact=username_or_email_or_nombre)
                    # Si lo encontramos, autenticamos usando su username real
                    self.user_cache = authenticate(
                        self.request, 
                        username=user_by_email.username, 
                        password=password
                    )
                except User.DoesNotExist:
                    pass # No era un email, pasamos al siguiente intento

            # ¡NUEVO! INTENTO 3: Autenticar por NOMBRE DE PERFIL

            if self.user_cache is None:
                try:
                    # Buscamos el *perfil* por el campo 'nombre'
                    perfil = PerfilUsuario.objects.get(nombre__iexact=username_or_email_or_nombre)
                    
                    # Autenticamos usando el 'username' del usuario de ese perfil
                    self.user_cache = authenticate(
                        self.request,
                        username=perfil.user.username, 
                        password=password
                    )
                except PerfilUsuario.DoesNotExist:
                    pass 
                except PerfilUsuario.MultipleObjectsReturned:
                    pass

            # ------------------------------------------------------------
            # Comprobaciones finales de Django
            # ------------------------------------------------------------
            if self.user_cache is None:
                # Si los 3 intentos fallaron, lanzamos el error
                raise self.get_invalid_login_error()
            else:
                # Si alguno funcionó, confirmamos el login
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data
    


class MyPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="Correo electrónico",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm',
            'placeholder': 'Correo electrónico',
            'id': 'id_email', 
            'autocomplete': 'email'
        })
    )

class MySetPasswordForm(SetPasswordForm):
    
    # Sobreescribimos el campo new_password1
    new_password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm',
            'placeholder': 'Nueva contraseña',
            'id': 'id_new_password1',
            'autocomplete': 'new-password'
        })
    )
    
    # Sobreescribimos el campo new_password2
    new_password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm',
            'placeholder': 'Confirmar nueva contraseña',
            'id': 'id_new_password2',
            'autocomplete': 'new-password'
        })
    )

class CustomPasswordResetForm(PasswordResetForm):
    """
    Formulario personalizado que corrige el Error 500.
    
    1. Renderiza el texto base (para evitar el error).
    2. Construye la URL de recuperación manualmente.
    3. Inyecta el ID de Brevo y los datos (contexto) a Anymail.
    """
    
    # ID de plantilla de Brevo
    BREVO_TEMPLATE_ID = 2 

    
    email = forms.EmailField(
        label="Correo electrónico",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm',
            'placeholder': 'Correo electrónico',
            'id': 'id_email',
            'autocomplete': 'email'
        })
    )

    def send_mail(self, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None):
        
        # 1. Renderiza el asunto 
        subject = loader.render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines()) # Limpia saltos de línea

        # 2. Renderiza el cuerpo de texto 
        body = loader.render_to_string(email_template_name, context)

        # 3. Construimos la URL de recuperación manualmente
        try:
            url_path = reverse('password_reset_confirm', kwargs={'uidb64': context['uid'], 'token': context['token']})
        except Exception:
            url_path = f"/reset/{context['uid']}/{context['token']}/"

        context['recovery_url'] = f"{context['protocol']}://{context['domain']}{url_path}"

        # 4. Crea el email
        msg = EmailMultiAlternatives(
            subject,    
            body,       
            from_email, 
            [to_email]
        )
        
        # 5. INSTRUCCIONES PARA ANYMAIL (BREVO)
        
        # 5a. Asigna el ID de la plantilla de Brevo.
        msg.template_id = self.BREVO_TEMPLATE_ID
        
        # 5b. ¡AQUÍ ESTÁ LA SOLUCIÓN 1!
        # Obtenemos el objeto User
        user = context.get('user') 

        # Hacemos la consulta del nombre más segura
        try:
             # Accedemos al perfil relacionado y cogemos el campo 'nombre'
             nombre_usuario = user.perfil.nombre
             # Si el nombre está en la BD pero es una cadena vacía ""
             if not nombre_usuario:
                 nombre_usuario = 'usuario' # Usamos el default
        except Exception:
             # Si user.perfil no existe o falla cualquier cosa, usamos el default
             nombre_usuario = 'usuario'

        # Creamos el diccionario de datos limpio
        brevo_data = {
            "recovery_url": context.get('recovery_url'),
            "uid": context.get('uid'),
            "token": context.get('token'),
            "domain": context.get('domain'),
            "site_name": context.get('site_name'),
            
            # Usamos la variable segura que acabamos de crear
            "first_name": nombre_usuario, 
            
            # Usamos el email del objeto User, que es el correcto para el login
            "email": getattr(user, 'email', ''), 
        }
        
        # 5c. Pasa el diccionario LIMPIO (solo strings) a Brevo
        msg.merge_global_data = brevo_data

        # 6. Envía el mensaje.
        try:
            msg.send()
        except Exception as e:
            # Imprime el error real en la consola del servidor para depuración
            print(f"ERROR AL ENVIAR CORREO CON ANYMAIL/BREVO: {e}")
            raise e
        

class MesocicloForm(forms.ModelForm):
    class Meta:
        model = Mesociclo
        fields = ["nombre", "atleta", "objetivo", "fecha_inicio", "semanas_objetivo", "notas"]
        widgets = {
            "fecha_inicio": forms.DateInput(attrs={"type": "date", "class": INPUT_CLASSES}),
            "nombre": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "objetivo": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "notas": forms.Textarea(attrs={"class": TEXTAREA_CLASSES, "rows": 3}),
            "semanas_objetivo": forms.NumberInput(attrs={"class": INPUT_CLASSES}),
            "atleta": forms.Select(attrs={"class": SELECT_CLASSES}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and hasattr(user, 'perfil'):
            # CORRECCIÓN: Usamos Q para permitir atletas propios O libres (igual que en EntrenamientoForm)
            self.fields['atleta'].queryset = PerfilUsuario.objects.filter(
                Q(tipo='atleta'), 
                Q(entrenador=user.perfil) | Q(entrenador__isnull=True)
            ).distinct().order_by('nombre')
        else:
            # Fallback por si acaso
            self.fields['atleta'].queryset = PerfilUsuario.objects.filter(tipo='atleta').order_by('nombre')