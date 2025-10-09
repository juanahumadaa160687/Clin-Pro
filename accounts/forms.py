from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.core.validators import RegexValidator
from .models import *
from django_password_eye.fields import PasswordEye
from django_password_eye.widgets import PasswordEyeWidget


class LoginUserForm(AuthenticationForm):
    email = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo Electrónico', 'required': 'true'})
    )
    password1 = PasswordEye(
        label='Contraseña',
        widget=PasswordEyeWidget(attrs={'class': 'form-control', 'placeholder': 'Contraseña', 'required': 'true'})
    )

    class Meta:
        model = User
        fields = ['email', 'password1']



class RegistroUserForm(UserCreationForm):
    email = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo Electrónico', 'required': 'true'})
    )
    password1 = PasswordEye(
        label='Contraseña',
        widget=PasswordEyeWidget(attrs={'class': 'form-control', 'placeholder': 'Contraseña', 'required': 'true', }, independent=True)
    )
    password2 = PasswordEye(
        label='Confirmar Contraseña',
        widget=PasswordEyeWidget(attrs={'class': 'form-control', 'placeholder': 'Confirmar Contraseña', 'required': 'true'}, independent=True)
    )
    rut = forms.CharField(
        label='RUT',
        max_length=12,
        validators=[RegexValidator(r'^\d{7,8}-[0-9kK]$', message='El RUT debe tener el formato 12345678-9 o 1234567-8')],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rut sin puntos con guión', 'required': 'true'})
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

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2', 'rut', 'nombre', 'telefono']