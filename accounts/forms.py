from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm
from django import forms
from django.core.validators import RegexValidator
from .models import *
from django_password_eye.fields import PasswordEye
from django_password_eye.widgets import PasswordEyeWidget

class ResetPasswordForm(PasswordResetForm):
    email = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo Electrónico', 'required': 'true', 'autofocus': 'true','id': 'email', 'name': 'email'})
    )

    class Meta:
        model = User
        fields = ['email']

class ChangePasswordForm(PasswordChangeForm):
    old_password = PasswordEye(
        label='Contraseña Actual',
        widget=PasswordEyeWidget(attrs={'class': 'form-control', 'placeholder': 'Contraseña Actual', 'required': 'true'}, independent=True)
    )
    new_password1 = PasswordEye(
        label='Nueva Contraseña',
        widget=PasswordEyeWidget(attrs={'class': 'form-control', 'placeholder': 'Nueva Contraseña', 'required': 'true'}, independent=True)
    )
    new_password2 = PasswordEye(
        label='Confirmar Nueva Contraseña',
        widget=PasswordEyeWidget(attrs={'class': 'form-control', 'placeholder': 'Confirmar Nueva Contraseña', 'required': 'true'}, independent=True)
    )

    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']

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
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo Electrónico', 'required': 'true', 'autofocus': 'true',})
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
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rut sin puntos con guión', 'required': 'true', 'autofocus': 'true',})
    )
    first_name = forms.CharField(
        label='Nombre',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre', 'required': 'true', 'autofocus': 'true', 'id': 'first_name', 'name': 'first_name'})
    )
    last_name = forms.CharField(
        label='Apellido',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido', 'required': 'true', 'id': 'last_name', 'name': 'last_name', 'autofocus': 'true',})
    )
    telefono = forms.CharField(
        label='Teléfono',
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', message='El número de teléfono debe tener entre 9 y 15 dígitos y puede incluir el código de país.')],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono (e.g., +56912345678)', 'required': 'true', 'autofocus': 'true',})
    )

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2', 'rut', 'first_name', 'last_name', 'telefono']