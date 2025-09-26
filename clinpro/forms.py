from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import *

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'El email es obligatorio.',
            'max_length': 'El email no puede tener más de 100 caracteres.',
        },
        max_length=100,
    )
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'La contraseña es obligatoria.',
        },
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'La confirmación de la contraseña es obligatoria.',
        },
    )

    class Meta:
        model = User
        fields = ['email', 'password1']


class PacienteForm(forms.ModelForm):
    rut = forms.CharField(
        label='RUT',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12.345.678-9'}),
        error_messages={
            'required': 'El RUT es obligatorio.',
            'max_length': 'El RUT no puede tener más de 12 caracteres.',
        },
        max_length=12,
    )
    nombre = forms.CharField(
        label='Nombre',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'El nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.',
        },
        max_length=100,
    )

    apellido = forms.CharField(
        label='Apellido',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'El apellido es obligatorio.',
            'max_length': 'El apellido no puede tener más de 100 caracteres.',
        },
        max_length=100,
    )

    direccion = forms.CharField(
        label='Dirección',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'La dirección es obligatoria.',
            'max_length': 'La dirección no puede tener más de 100 caracteres.',
        },
        max_length=100,
    )

    telefono = forms.CharField(
        label='Teléfono',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'}),
        error_messages={
            'required': 'El teléfono es obligatorio.',
            'max_length': 'El teléfono no puede tener más de 15 caracteres.',
        },
        max_length=15,
    )

    prevision = forms.CharField(
        label='Previsión',
        widget=forms.Select(attrs={'class': 'form-control'}, choices=[('', 'Seleccione su Previsión'), ('Fonasa', 'Fonasa'), ('Isapre', 'Isapre'), ('Particular', 'Particular') ]),
        error_messages={
            'required': 'La previsión es obligatoria'
        },
    )

    class Meta:
        model = Paciente
        fields = ['rut', 'nombre', 'apellido', 'direccion', 'telefono', 'prevision']



class LoginForm(AuthenticationForm):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'El email es obligatorio.',
            'max_length': 'El email no puede tener más de 100 caracteres.',
            'invalid': 'Ingrese un email válido.',
        },
        max_length=100,
        required=True,
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'La contraseña es obligatoria.',
        },
        required=True,
    )
    remember_me = forms.BooleanField(
        label='Recuérdame',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    class Meta:
        model = User
        fields = ['email', 'password', 'remember_me']



