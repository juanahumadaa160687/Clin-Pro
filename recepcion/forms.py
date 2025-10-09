from django import forms
from django.core.validators import RegexValidator
from django_password_eye.fields import PasswordEye
from django_password_eye.widgets import PasswordEyeWidget

class PacienteNoRegistradoForm(forms.Form):
    nombre = forms.CharField(
        label='Nombre Completo',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre completo'})
    )
    rut = forms.CharField(
        label='RUT',
        max_length=12,
        validators=[RegexValidator(r'^\d{7,8}-[0-9kK]$', message='El RUT debe tener el formato 12345678-9 o 1234567-8')],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el RUT'})
    )
    telefono = forms.CharField(
        label='Teléfono',
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', message='Ingrese un número de teléfono válido')],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el teléfono'})
    )
    email = forms.EmailField(
        label='Correo Electrónico',
        max_length=100,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el correo electrónico','required': False, 'value': 'No Presenta'})
    )

    class Meta:
        fields = ['nombre', 'rut', 'telefono', 'email']