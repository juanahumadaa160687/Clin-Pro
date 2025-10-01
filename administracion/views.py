import datetime

from django.contrib.auth.models import Group
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Sum
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

from administracion.forms import LoginPersonalForm, RegistroPersonalForm, ServicioForm, ProcedimientoForm
from administracion.models import PersonalSalud, Servicio, Procedimiento, Agenda
from clinpro.models import User, Paciente, Convenio, Pago
import sweetify
from django.contrib.auth import login as auth_login, authenticate


def login_personal(request):

    if request.method == 'POST':
        login_form = LoginPersonalForm(request, data=request.POST)
        if login_form.is_valid():

            email = login_form.cleaned_data.get('email')
            password = login_form.cleaned_data.get('password')
            remember_me = login_form.cleaned_data.get('remember_me')

            user = authenticate(username=email, password=password)

            if user is not None:
                auth_login(request, user)

                if request.user.rol == 'administrador':
                    return render(request, 'administracion/dashboard_admin.html')
                elif request.user.rol == 'personal_salud':
                    return render(request, 'personal_salud/dashboard_personal_salud.html')
                elif request.user.rol == 'secretaria':
                    return render(request, 'recepcion/dashboard_recep.html')

                if not remember_me:
                    request.session.set_expiry(0)  # La sesión expira al cerrar el navegador

            else:
                sweetify.error(request, 'Credenciales inválidas. Por favor, inténtelo de nuevo.', button='Aceptar')
        else:
            sweetify.error(request, 'Formulario inválido. Por favor, inténtelo de nuevo.', button='Aceptar')
    else:
        login_form = LoginPersonalForm()

    return render(request, 'login_personal.html', {'login_form': login_form})


def dashboard_admin(request):

    personal_tipo = PersonalSalud.objects.all().values('titulo').annotate(total=Count('titulo'))
    personal_esp = PersonalSalud.objects.all().values('especialidad').annotate(total=Count('especialidad'))
    personal_rend = PersonalSalud.objects.all().values('sufijo', 'user__nombre' ,'titulo', 'procedimiento__personal_salud__procedimiento').annotate(total=Count('procedimiento__personal_salud__procedimiento'))

    convenios_vigentes = Convenio.objects.all().values('nombre', 'descuento')

    total_pacientes_mes = Paciente.objects.filter(reservahora__fecha_reserva__month=datetime.date.today().month).values('user_id').annotate(total=Count('user_id'))
    total_ingresos_mes = Pago.objects.filter(fecha__month=datetime.date.today().month).values('fecha__month', 'monto').aggregate(total=Sum('monto'))['total'] or 0
    total_ingresos_anio = Pago.objects.filter(fecha__year=datetime.date.today().year).values('fecha__year', 'monto').aggregate(total=Sum('monto'))['total'] or 0

    personal_sal = PersonalSalud.objects.values('sufijo', 'user__nombre', 'especialidad', 'titulo', 'universidad', 'user__email', 'user__telefono', 'user__rut')
    secretarias = User.objects.filter(rol='secretaria').values('nombre', 'email', 'telefono', 'rut')
    administradores = User.objects.filter(rol='administrador').values('nombre', 'email', 'telefono', 'rut')

    if request.method == 'POST' and 'registro' in request.POST:
        registro_personal = RegistroPersonalForm(request.POST)

        if registro_personal.is_valid():
            user =registro_personal.save(commit=False)

            user.email = registro_personal.cleaned_data.get('email')
            user.set_password(registro_personal.cleaned_data.get('password1'))
            user.nombre = registro_personal.cleaned_data.get('nombre')
            user.telefono = registro_personal.cleaned_data.get('telefono')
            user.rut = registro_personal.cleaned_data.get('rut')
            user.rol = registro_personal.cleaned_data.get('rol')

            user.save()

            group = Group.objects.get_or_create(name=user.rol)[0]
            user.groups.add(group)

            sweetify.success(request, f"Functionary Registrado con Éxito.", button='Aceptar')
            return render(request, 'login_personal.html')
        else:
            sweetify.error(request, 'Error al registrar funcionario. Por favor, inténtelo de nuevo.', button='Aceptar')
            return render(request, 'login_personal.html', {'registro_personal': registro_personal})

    elif request.method == 'POST' and 'servicio' in request.POST:
        servicio_form = ServicioForm(request.POST)

        if servicio_form.is_valid():
            servicio = servicio_form.save(commit=False)

            servicio.nombre = servicio_form.cleaned_data.get('servicio')
            servicio.personal = servicio_form.cleaned_data.get('personal_salud')

            servicio.save()
            sweetify.success(request, f"Servicio Registrado con Éxito.", button='Aceptar')
            return render(request, 'administracion/dashboard_admin.html')
        else:
            sweetify.error(request, 'Error al registrar servicio. Por favor, inténtelo de nuevo.', button='Aceptar')
            return render(request, 'login_personal.html', {'servicio_form': servicio_form})

    elif request.method == 'POST' and 'procedimiento' in request.POST:
        procedimiento_form = ProcedimientoForm(request.POST)

        if procedimiento_form.is_valid():
            procedimiento = procedimiento_form.save(commit=False)

            procedimiento.procedimiento = procedimiento_form.cleaned_data.get('procedimiento')
            procedimiento.precio = procedimiento_form.cleaned_data.get('precio')
            procedimiento.personal_salud = procedimiento_form.cleaned_data.get('personal_salud')

            procedimiento.save()
            sweetify.success(request, f"Procedimiento Registrado con Éxito.", button='Aceptar')
            return render(request, 'administracion/dashboard_admin.html')
        else:
            sweetify.error(request, 'Error al registrar procedimiento. Por favor, inténtelo de nuevo.', button='Aceptar')
            return render(request, 'login_personal.html', {'procedimiento_form': procedimiento_form})


    else:
        registro_personal = RegistroPersonalForm()
        servicio_form = ServicioForm()
        return render(request, 'administracion/dashboard_admin.html',
                      {
                            'registro_personal': registro_personal,
                            'servicio_form': servicio_form,
                            'personal_tipo': personal_tipo,
                            'personal_esp': personal_esp,
                            'personal_rend': personal_rend,
                            'convenios_vigentes': convenios_vigentes,
                            'total_pacientes_mes': total_pacientes_mes,
                            'total_ingresos_mes': total_ingresos_mes,
                            'total_ingresos_anio': total_ingresos_anio,
                            'personal_sal': personal_sal,
                            'secretarias': secretarias,
                            'administradores': administradores,
                      })


def dashboard_servicios(request):

    per_servicios= Servicio.objects.all().values('personal__servicio__nombre', 'personal__user__nombre', 'personal__titulo').annotate(total=Count('personal__user__nombre'))
    pac_servicios= Servicio.objects.all().values('personal__servicio__nombre', 'personal__reservahora__paciente_id').annotate(total=Count('personal__reservahora__paciente_id'))
    rend_servicios= Servicio.objects.all().values('personal__servicio__nombre', 'personal__reservahora__pago_id__monto').aggregate(total=Sum('personal__reservahora__pago_id__monto'))['total'] or 0
    rend_especialidad = Servicio.objects.all().values('personal__especialidad', 'personal__reservahora__pago_id__monto').aggregate(total=Sum('personal__reservahora__pago_id__monto'))['total'] or 0

    return render(request, 'administracion/dashboard_servicios.html',
                  {
                        'per_servicios': per_servicios,
                        'pac_servicios': pac_servicios,
                        'rend_servicios': rend_servicios,
                        'rend_especialidad': rend_especialidad,
                  })

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'
    success_message = "Se ha enviado un correo electrónico con instrucciones para restablecer su contraseña."
    success_url = reverse_lazy('index')



