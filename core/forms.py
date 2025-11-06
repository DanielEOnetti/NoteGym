# core/forms.py

# Importaciones principales del framework Django para la construcción de formularios.
from django import forms
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.forms import inlineformset_factory, modelformset_factory
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.core.mail import EmailMultiAlternatives

# Importación de los modelos y clases requeridas en los formularios definidos.
from .models import PerfilUsuario, Entrenamiento, Ejercicio, SerieEjercicio, DetalleEntrenamiento
from decimal import Decimal, ROUND_HALF_UP

# ========================================================================
# === ¡¡IMPORTS QUE FALTABAN PARA EL LOGIN!! ===
# ========================================================================
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
        fields = ["atleta", "nombre", "notas"]
        widgets = {
            "atleta": forms.Select(attrs={"class": SELECT_CLASSES}),
            "nombre": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "notas": forms.Textarea(attrs={"class": TEXTAREA_CLASSES, "rows": 4}),
        }
        labels = {
            "nombre": "Nombre del Entrenamiento ",
            "atleta": "Atleta ",
            "notas": "📝 Notas del Entrenamiento",
        }

    def __init__(self, *args, **kwargs):
        # 1. Extrae el 'user' que pasamos desde la CreateView
        user = kwargs.pop('user', None) 
        
        super().__init__(*args, **kwargs)

        # 2. Comprueba que el usuario está logueado y tiene perfil
        if user and hasattr(user, 'perfil'):
            
            perfil_entrenador = user.perfil 
            
            # 3. Filtra el queryset de 'atleta'
            self.fields['atleta'].queryset = PerfilUsuario.objects.filter(
                Q(tipo='atleta'), # Condición 1: Debe ser un atleta
                
                # Condición 2 (OR): O es mi atleta O no tiene entrenador
                Q(entrenador=perfil_entrenador) | 
                Q(entrenador__isnull=True)     
            
            ).distinct().order_by('nombre') # .distinct() por si acaso y ordenado

        else:
            # 4. Fallback: si no hay user, solo muestra atletas
            # (Útil si un SuperAdmin entra desde /admin)
            self.fields['atleta'].queryset = PerfilUsuario.objects.filter(
                tipo='atleta'
            ).order_by('nombre')

# ========================================================================
# Formulario de Detalle de Entrenamiento (para el Formset)
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
class SeriePrescripcionForm(forms.ModelForm):
    class Meta:
        model = SerieEjercicio
        fields = ["numero_serie", "repeticiones_o_rango"] 
        widgets = {
            "numero_serie": forms.HiddenInput(), 
            "repeticiones_o_rango": forms.TextInput(attrs={
                "placeholder": "Ej: 10 o 8-12",
                "class": INPUT_CLASSES 
            }),
        }
        labels = {
            "repeticiones_o_rango": "Repeticiones / Rango *", 
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['numero_serie'].required = False

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
    class Meta:
        model = SerieEjercicio
        fields = [
            "detalle_entrenamiento",
            "numero_serie",
            "peso_real",
            "repeticiones_reales",
        ]

        # --- Clases de Tailwind para los Inputs ---
        # Definidas una vez para reutilizarlas y mantener consistencia
        input_classes = (
            "w-full text-center text-sm rounded-md border-0 "
            "bg-transparent "                  # <-- Fondo transparente por defecto
            "px-2 py-1.5 "                     # <-- Padding interno
            "text-gray-900 font-medium "       # <-- Color de texto
            "transition-all duration-150 "     # <-- Transición suave
            "focus:outline-none "
            "focus:bg-white "                  # <-- Al seleccionar: fondo blanco
            "focus:ring-2 "                    # <-- Al seleccionar: anillo
            "focus:ring-green-500 "            # <-- Tu color 'green-500'
            "placeholder-gray-400"             # <-- Color del placeholder
        )

        widgets = {
            "detalle_entrenamiento": forms.HiddenInput(),
            "numero_serie": forms.HiddenInput(),
            
            "peso_real": forms.NumberInput(attrs={
                # Coincide con tu validación de 0.25
                "step": "0.25", 
                "placeholder": "Peso (kg)",
                "class": input_classes  # Aplicamos las clases
            }),
            
            "repeticiones_reales": forms.NumberInput(attrs={
                "placeholder": "Reps",
                "class": input_classes  # Aplicamos las clases
            }),
        }
        
        # Estos labels son útiles para accesibilidad, aunque no se vean
        labels = {
            "peso_real": "Peso",
            "repeticiones_reales": "Reps",
        }

    # --- Validación Personalizada ---
    # (Tu código de validación, que es excelente, sin cambios funcionales)
    def clean_peso_real(self):
        peso = self.cleaned_data.get('peso_real')
        
        # Permite valores nulos (si el campo no es obligatorio)
        if peso is None:
            return peso

        # Asegura que sea un Decimal para la validación
        if not isinstance(peso, Decimal):
            try:
                peso = Decimal(str(peso))
            except Exception:
                raise ValidationError("El peso debe ser un número válido.")
        
        # Redondeo estándar
        peso = peso.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        INCREMENTO_MINIMO = Decimal('0.25')
        residuo = peso % INCREMENTO_MINIMO

        # Comprueba si el residuo no es cero
        if not residuo.is_zero():
             raise ValidationError(
                f"El peso debe ser un múltiplo de {INCREMENTO_MINIMO} (ej. 17.0, 17.25, 17.5, 17.75). "
                "Verifica tus incrementos de peso."
             )
        
        # Devuelve un entero si el peso es un número entero (ej. 17.0 -> 17)
        if peso == peso.to_integral_value():
            return peso.to_integral_value()
            
        return peso

# ========================================================================
# Creación de FormSets para gestión masiva de series
# ========================================================================
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

# ========================================================================
# Formulario de Login Inteligente (Username o Email)
# ========================================================================
class EmailOrUsernameLoginForm(AuthenticationForm):
    """
    Formulario de autenticación que permite a los usuarios iniciar sesión
    usando su Username (email), su Email O su Nombre de Perfil.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # El label ya es correcto por el placeholder del template
        self.fields['username'].label = "Usuario o Email" 

    def clean(self):
        # El campo 'username' del formulario contiene lo que el usuario escribió
        username_or_email_or_nombre = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username_or_email_or_nombre is not None and password:
            User = get_user_model()
            # Inicializamos el caché de usuario como None
            self.user_cache = None

            # ------------------------------------------------------------
            # INTENTO 1: Autenticar por USERNAME
            # (En tu app, el username ES el email)
            # ------------------------------------------------------------
            self.user_cache = authenticate(
                self.request, 
                username=username_or_email_or_nombre, 
                password=password
            )
            
            # ------------------------------------------------------------
            # INTENTO 2: Autenticar por EMAIL (Fallback)
            # ------------------------------------------------------------
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

            # ------------------------------------------------------------
            # ¡NUEVO! INTENTO 3: Autenticar por NOMBRE DE PERFIL
            # ------------------------------------------------------------
            if self.user_cache is None:
                try:
                    # Buscamos el *perfil* por el campo 'nombre'
                    perfil = PerfilUsuario.objects.get(nombre__iexact=username_or_email_or_nombre)
                    
                    # ¡Encontrado! Autenticamos usando el 'username' del usuario de ese perfil
                    self.user_cache = authenticate(
                        self.request,
                        username=perfil.user.username, 
                        password=password
                    )
                except PerfilUsuario.DoesNotExist:
                    pass # No era un nombre, se acabaron los intentos
                except PerfilUsuario.MultipleObjectsReturned:
                    # Si dos usuarios se llaman "Juan Pérez", no podemos adivinar.
                    # El login fallará, lo cual es el comportamiento de seguridad correcto.
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
            'id': 'id_email', # Asegura que el <label> funcione
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
    Formulario personalizado para inyectar el ID de plantilla de Brevo
    en el correo de recuperación de contraseña.
    """
    
    # 📌 REEMPLAZA ESTE NÚMERO CON TU ID DE PLANTILLA DE BREVO
    BREVO_TEMPLATE_ID = 2 

    def send_mail(self, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None):
        
        # 1. Crear el objeto EmailMultiAlternatives base
        msg = EmailMultiAlternatives(
            self.subject, 
            self.message, 
            from_email, 
            [to_email]
        )
        
        # 2. **AQUÍ ESTÁ LA CLAVE:** Inyectar el ID de Brevo a través de Anymail
        # 'esp_extra' permite pasar parámetros específicos del proveedor (Brevo/Sendinblue)
        msg.esp_extra = {
            'templateId': self.BREVO_TEMPLATE_ID,
            # También puedes pasar variables de personalización si las necesitas
            # 'params': {'enlace_recuperacion': context['protocol'] + '://' + context['domain'] + context['url']}
        }

        # 3. Envía el mensaje. Anymail detectará 'templateId' y lo usará.
        msg.send()