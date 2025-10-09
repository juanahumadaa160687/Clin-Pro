from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.validators import RegexValidator
from django.forms import *
from administracion.models import PersonalSalud, Servicio, Procedimiento, Agenda
from clinpro.models import User
from django_password_eye.fields import PasswordEye
from django_password_eye.widgets import PasswordEyeWidget
from django import forms

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
        choices=[('Personal Salud', 'Personal de Salud'), ('Administrador', 'Administrador'), ('Secretaria', 'Secretaria')],
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
        queryset=User.objects.filter(personalsalud__isnull=True, rol='Personal Salud'),
        widget=forms.Select(attrs={'class': 'form-select', 'required': 'true', 'id': 'user', 'name': 'user'})
    )

    class Meta:
        model = PersonalSalud
        fields = ['prefijo', 'titulo', 'especialidad', 'universidad', 'user']


class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['nombre', 'personal']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Servicio', 'required': 'true'}),
            'personal': forms.SelectMultiple(attrs={'class': 'form-select', 'multiple': 'true', 'use_required_attribute': 'true'}),
        }
        labels = {
            'nombre': 'Nombre del Servicio',
            'personal': 'Personal de Servicio',
        }



class ProcedimientoForm(forms.ModelForm):
    class Meta:
        model = Procedimiento
        fields = ['procedimiento', 'precio', 'personal_salud']
        widgets = {
            'procedimiento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Procedimiento', 'required': 'true'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio en CLP', 'required': 'true', 'min': 0, 'step': 0.01}),
            'personal_salud': forms.SelectMultiple(attrs={'class': 'form-select', 'multiple': 'true', 'use_required_attribute': 'true'}),
        }
        labels = {
            'procedimiento': 'Nombre del Procedimiento',
            'precio': 'Precio (CLP)',
            'personal_salud': 'Personal de Salud que realiza el Procedimiento',
        }
