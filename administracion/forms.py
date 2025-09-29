from datetime import date

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.forms import ModelForm, DateInput, TimeInput, TextInput, NumberInput, Select, CharField, \
    PasswordInput, forms, ValidationError, IntegerField, RadioSelect, ModelChoiceField
from administracion.models import PersonalSalud, Servicio, Procedimiento, Agenda
from clinpro.models import Convenio, User
from django_password_eye.fields import PasswordEye
from django_password_eye.widgets import PasswordEyeWidget




class AgendaForm(ModelForm):
    class Meta:
        model = Agenda
        fields = ['fecha', 'hora', 'profesional']
        widgets = {
            'fecha': DateInput(attrs={'class': 'form-control', 'type': 'date', 'min': '01-01-2025'}, format='%d-%m-%Y'),
            'hora': TimeInput(attrs={'class': 'form-control', 'type': 'time', 'step': '3600', 'min': '08:00', 'max': '20:00'}, format='%H:%M'),
            'profesional': Select(attrs={'class': 'form-control', 'placeholder': 'Seleccione un profesional'}),
        }
        labels = {
            'fecha': 'Fecha',
            'hora': 'Hora',
            'profesional': 'Profesional',
        }

        def clean(self):
            cleaned_data = super().clean()
            fecha = cleaned_data.get('fecha')
            hora = cleaned_data.get('hora')
            profesional = cleaned_data.get('profesional')

            if Agenda.objects.filter(fecha=fecha, hora=hora, profesional=profesional).exists():
                raise ValidationError("La combinación de fecha, hora para este profesional no esta disponible. Por favor, elija otra.")

            elif fecha and fecha < date.today():
                raise ValidationError("La fecha no puede ser en el pasado.")

            elif hora and (hora.hour < 8 or hora.hour > 20):
                raise ValidationError("La hora debe estar entre las 08:00 y las 20:00.")

            elif hora and (hora.hour > 13 and hora.hour < 15):
                raise ValidationError("La hora debe estar fuera del horario de almuerzo (13:00 - 15:00).")

            return cleaned_data

class PersonalSaludForm(ModelForm):
    class Meta:
        model = PersonalSalud
        fields = ['rut', 'nombre', 'especialidad']
        widgets = {
            'rut': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese RUT'}),
            'nombre': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese Nombre'}),
            'especialidad': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese Especialidad'}),
        }

class ServicioForm(ModelForm):
    class Meta:
        model = Servicio
        fields = ['nombre', 'personal']
        widgets = {
            'nombre': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese Nombre del Servicio'}),
            'personal': Select(attrs={'class': 'form-control', 'placeholder': 'Seleccione un profesional'}),
        }

class ProcedimientoForm(ModelForm):
    class Meta:
        model = Procedimiento
        fields = ['procedimiento', 'precio', 'codigo', 'personal_salud']
        widgets = {
            'procedimiento': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese Procedimiento'}),
            'precio': NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese Precio'}),
            'codigo': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese Código'}),
            'personal_salud': Select(attrs={'class': 'form-control', 'placeholder': 'Seleccione un profesional'}),
        }


class ConvenioForm(ModelForm):
    class Meta:
        model = Convenio
        fields = ['nombre', 'descuento']
        widgets = {
            'nombre': TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Convenio'}),
            'descuento': NumberInput(attrs={'class': 'form-control', 'placeholder': 'Descuento en %'}),
        }
        labels = {
            'nombre': 'Convenio',
            'descuento': 'Descuento (%)',
        }

