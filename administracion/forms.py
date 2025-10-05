from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.validators import RegexValidator
from django.forms import *
from administracion.models import PersonalSalud, Servicio, Procedimiento, Agenda
from clinpro.models import User
from django_password_eye.fields import PasswordEye
from django_password_eye.widgets import PasswordEyeWidget
from django import forms

class LoginPersonalForm(AuthenticationForm):
    email = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo Electrónico', 'required': 'true'})
    )
    password = PasswordEye(
        label='Contraseña',
        widget=PasswordEyeWidget(attrs={'class': 'form-control', 'placeholder': 'Contraseña', 'required': 'true'})
    )

    remember_me = forms.BooleanField(
        label='Recuérdame',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = User
        fields = ['email', 'password', 'remember_me']


class RegistroPersonalForm(UserCreationForm):
    email = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo Electrónico', 'required': 'true'})
    )
    password1 = PasswordEye(
        label='Contraseña',
        widget=PasswordEyeWidget(attrs={'class': 'form-control', 'placeholder': 'Contraseña', 'required': 'true'})
    )
    password2 = PasswordEye(
        label='Confirmar Contraseña',
        widget=PasswordEyeWidget(attrs={'class': 'form-control', 'placeholder': 'Confirmar Contraseña', 'required': 'true'})
    )
    rut = forms.CharField(
        label='RUT',
        max_length=12,
        validators=[RegexValidator(r'^\d{7,8}-[0-9kK]$', message='El RUT debe tener el formato 12345678-9 o 1234567-8')],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RUT (e.g., 12345678-9)', 'required': 'true'})
    )
    nombre = forms.CharField(
        label='Nombre Completo',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre Completo', 'required': 'true'})
    )
    telefono = forms.CharField(
        label='Teléfono',
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', message='El número de teléfono debe tener entre 9 y 15 dígitos y puede incluir el código de país.')],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono (e.g., +56912345678)', 'required': 'true'})
    )
    rol = forms.ChoiceField(
        label='Rol',
        choices=[('PersonalSalud', 'Personal de Salud'), ('Administrador', 'Administrador'), ('Secretaria', 'Secretaria')],
        widget=forms.Select(attrs={'class': 'form-select', 'required': 'true'})
    )

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2', 'rut', 'nombre', 'telefono', 'rol']

class PersonalSaludForm(ModelForm):
    prefijo = forms.CharField(
        label='Prefijo',
        max_length=4,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prefijo (e.g., Dr., Dra., Lic.)', 'required': 'true', 'id': 'prefijo', 'name': 'prefijo'})
    )
    titulo = forms.CharField(
        label='Título',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título (e.g., Médico, Enfermero)', 'required': 'true', 'id': 'titulo', 'name': 'titulo'})
    )
    especialidad = forms.CharField(
        label='Especialidad',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Especialidad (e.g., Cardiología, Pediatría)', 'required': 'true', 'id': 'especialidad', 'name': 'especialidad'})
    )
    universidad = forms.CharField(
        label='Universidad',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Universidad (e.g., Universidad de Chile)', 'required': 'true', 'id': 'universidad', 'name': 'universidad'})
    )
    user = forms.ModelChoiceField(
        label='Usuario',
        queryset=User.objects.filter(personalsalud__isnull=True, rol='PersonalSalud'),
        widget=forms.Select(attrs={'class': 'form-select', 'required': 'true', 'id': 'user', 'name': 'user'})
    )

    class Meta:
        model = PersonalSalud
        fields = ['prefijo', 'titulo', 'especialidad', 'universidad', 'user']


class ServicioForm(forms.Form):
    nombre = forms.CharField(
        label='Nombre del Servicio',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Servicio', 'required': 'true'})
    )
    personal = forms.ModelMultipleChoiceField(
        label='Personal de Salud',
        queryset=PersonalSalud.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'multiple': 'true'})
    )

    class Meta:
        model = Servicio
        fields = ['nombre', 'personal']

    def save(self, commit):
        pass


class ProcedimientoForm(forms.Form):
    procedimiento = forms.CharField(
        label='Nombre del Procedimiento',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Procedimiento', 'required': 'true'})
    )
    precio = forms.IntegerField(
        label='Precio',
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio', 'required': 'true'})
    )
    personal_salud = forms.ModelMultipleChoiceField(
        label='Personal de Salud',
        queryset=PersonalSalud.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'multiple': 'true'})
    )

    class Meta:
        model = Procedimiento
        fields = ['procedimiento', 'precio', 'personal_salud']


class AdministradorForm(forms.Form):
    administrador = forms.ModelChoiceField(
        label='Administrador',
        queryset=User.objects.filter(rol='Administrador', administrador__isnull=True),
        widget=forms.Select(attrs={'class': 'form-select', 'required': 'true'})
    )

    class Meta:
        model = Servicio
        fields = ['administrador']

class SecretariaForm(forms.Form):
    secretaria = forms.ModelChoiceField(
        label='Secretaria',
        queryset=User.objects.filter(rol='Secretaria', secretaria__isnull=True),
        widget=forms.Select(attrs={'class': 'form-select', 'required': 'true',})
    )

    class Meta:
        model = Servicio
        fields = ['recepcion']