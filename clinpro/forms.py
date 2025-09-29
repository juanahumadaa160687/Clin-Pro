from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.core.validators import RegexValidator

from .models import *
from django_password_eye.fields import PasswordEye
from django_password_eye.widgets import PasswordEyeWidget


class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'El email es obligatorio.',
            'max_length': 'El email no puede tener más de 100 caracteres.',
        },
        max_length=100,
    )
    password1 = PasswordEye(
        widget=PasswordEyeWidget(
            independent=True,
            attrs={'placeholder': '********',
                   'autocomplete': 'off',
                   'data-toggle': 'password',
                   'class': 'form-control password-field'}),
        label='Contraseña',
        validators=[
            RegexValidator(
                regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
                message="Password debe tener al menos 8 caracteres y contener al menos una letra mayúscula, "
                        "una letra minúscula, un dígito y un carácter especial."
            )]
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': 'La confirmación de la contraseña es obligatoria.',
        },
    )
    rol = forms.CharField(
        label='Rol',
        widget=forms.HiddenInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'type': 'text', 'name': 'rol', 'id': 'rol', 'value': 'Paciente'}),
    )

    class Meta:
        model = User
        fields = ['email', 'password1', 'rol']


class LoginPacienteForm(AuthenticationForm):
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
    password = PasswordEye(
        widget=PasswordEyeWidget(
            independent=True,
            attrs={
                   'autocomplete': 'off',
                   'data-toggle': 'password',
                     'class': 'form-control password-field'}),
    )
    remember_me = forms.BooleanField(
        label='Recuérdame',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'type': 'checkbox'}),
    )

    class Meta:
        model = User
        fields = ['email', 'password', 'remember_me']



class PacienteModelForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['rut', 'nombre', 'direccion', 'telefono', 'prevision']
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control', 'type': 'text', 'id': 'rut', 'name': 'rut', 'pattern': r'\d{1,2}\.\d{3}\.\d{3}-[\dkK]', 'title': 'Formato RUT: 12.345.678-9'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'type': 'text', 'id': 'nombre', 'name': 'nombre'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'type': 'text', 'id': 'direccion', 'name': 'direccion'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'type': 'tel', 'pattern': '+[5-6]{2} [0-9]{1} [6]{1} [0-9]{2} [0-9]{2} [0-9]{3}', 'id': 'telefono', 'name': 'telefono'}),
            'prevision': forms.Select(attrs={'class': 'form-select', 'id':'prevision', 'name': 'nombre'}, choices=[('', 'Seleccione su Previsión'), ('Fonasa', 'Fonasa'), ('Isapre', 'Isapre'), ('Particular', 'Particular') ]),
        }

        labels = {
            'rut': 'RUT',
            'nombre': 'Nombre Completo',
            'direccion': 'Dirección',
            'telefono': 'Teléfono',
            'prevision': 'Previsión',
        }

