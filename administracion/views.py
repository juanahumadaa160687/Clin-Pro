import datetime
from io import BytesIO
from django.contrib.auth.models import Group
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from django.urls import reverse_lazy
from clinpro.forms import UserCreationForm, RegistroUserForm
from administracion.forms import LoginPersonalForm, RegistroPersonalForm, ServicioForm, ProcedimientoForm, \
    PersonalSaludForm, AdministradorForm, SecretariaForm
from administracion.models import PersonalSalud, Servicio, Procedimiento, Agenda
from clinpro.models import User, Paciente, Convenio, Pago
import sweetify
from django.contrib.auth import login as auth_login, authenticate
from xhtml2pdf import pisa


def dashboard_admin(request):

    personal_tipo = PersonalSalud.objects.all().values('titulo').annotate(total=Count('titulo'))
    personal_esp = PersonalSalud.objects.all().values('especialidad').annotate(total=Count('especialidad'))
    personal_rend = PersonalSalud.objects.all().values('prefijo', 'user__nombre' ,'titulo', 'procedimiento__personal_salud__procedimiento').annotate(total=Count('procedimiento__personal_salud__procedimiento'))

    convenios_vigentes = Convenio.objects.all().values('nombre', 'descuento')

    total_pacientes_mes = Paciente.objects.filter(reservahora__fecha_reserva__month=datetime.date.today().month).values('user_id').annotate(total=Count('user_id'))
    total_ingresos_mes = Pago.objects.filter(fecha__month=datetime.date.today().month).values('fecha__month', 'monto').aggregate(total=Sum('monto'))['total'] or 0
    total_ingresos_anio = Pago.objects.filter(fecha__year=datetime.date.today().year).values('fecha__year', 'monto').aggregate(total=Sum('monto'))['total'] or 0

    personal_sal = PersonalSalud.objects.values('prefijo', 'user__nombre', 'especialidad', 'titulo', 'universidad', 'user__email', 'user__telefono', 'user__rut')
    secretarias = User.objects.filter(rol='secretaria').values('nombre', 'email', 'telefono', 'rut')
    administradores = User.objects.filter(rol='administrador').values('nombre', 'email', 'telefono', 'rut')



    if request.method == 'POST' and 'servicio' in request.POST:
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

    personal_clin = User.objects.all().values('nombre', 'email', 'telefono', 'rut', 'rol').exclude(rol='Paciente')


    pac_servicios= Servicio.objects.all().values('personal__servicio__nombre', 'personal__reservahora__paciente_id').annotate(total=Count('personal__reservahora__paciente_id'))
    rend_servicios= Servicio.objects.all().values('personal__servicio__nombre', 'personal__reservahora__pago_id__monto').aggregate(total=Sum('personal__reservahora__pago_id__monto'))['total'] or 0
    rend_especialidad = Servicio.objects.all().values('personal__especialidad', 'personal__reservahora__pago_id__monto').aggregate(total=Sum('personal__reservahora__pago_id__monto'))['total'] or 0
    #prof_servicio = Servicio.objects.all().values('personal__servicio__nombre', 'personal__user__nombre', 'personal__titulo', 'personal__especialidad', 'personal__universidad', 'personal__user__email', 'personal__user__telefono', 'personal__user__rut')



    return render(request, 'administracion/dashboard_servicios.html',
                  {
                        'pac_servicios': pac_servicios,
                        'rend_servicios': rend_servicios,
                        'rend_especialidad': rend_especialidad,
                        'personal_clin': personal_clin,
                  })

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'
    success_message = "Se ha enviado un correo electrónico con instrucciones para restablecer su contraseña."
    success_url = reverse_lazy('index')



def dashboard_personal(request):

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
        return render(request, 'administracion/personal_dashboard.html', {'registro_personal': registro_personal})

    elif request.method == 'POST' and 'personal_salud' in request.POST:

        per_salud_form = PersonalSaludForm(request.POST)

        if per_salud_form.is_valid():
            personal_salud = per_salud_form.save(commit=False)

            personal_salud.prefijo = per_salud_form.cleaned_data.get('prefijo')
            personal_salud.titulo = per_salud_form.cleaned_data.get('titulo')
            personal_salud.especialidad = per_salud_form.cleaned_data.get('especialidad')
            personal_salud.universidad = per_salud_form.cleaned_data.get('universidad')
            personal_salud.user = per_salud_form.cleaned_data.get('user')

            personal_salud.save()
            sweetify.success(request, f"Personal de Salud Registrado con Éxito.", button='Aceptar')
            return render(request, 'administracion/personal_dashboard.html')
        else:
            sweetify.error(request, 'Error al registrar personal de salud. Por favor, inténtelo de nuevo.', button='Aceptar')
            return render(request, 'administracion/personal_dashboard.html', {'per_salud_form': per_salud_form})

    elif request.method == 'POST' and 'administrador' in request.POST:
        admin_form = AdministradorForm(request.POST)
        if admin_form.is_valid():
            administrador = admin_form.cleaned_data.get('administrador')

            administrador.save()

            sweetify.success(request, f"Administrador Asignado con Éxito.", button='Aceptar')
            return render(request, 'administracion/personal_dashboard.html')
        else:
            sweetify.error(request, 'Error al asignar administrador. Por favor, inténtelo de nuevo.', button='Aceptar')
            return render(request, 'administracion/personal_dashboard.html', {'admin_form': admin_form})

    elif request.method == 'POST' and 'secretaria' in request.POST:
        secre_form = RegistroUserForm(request.POST)
        if secre_form.is_valid():
            secretaria = secre_form.cleaned_data.get('secretaria')

            secretaria.save()

            sweetify.success(request, f"Secretaria Registrada con Éxito.", button='Aceptar')
            return render(request, 'administracion/personal_dashboard.html')
        else:
            sweetify.error(request, 'Error al registrar secretaria. Por favor, inténtelo de nuevo.', button='Aceptar')
            return render(request, 'administracion/personal_dashboard.html', {'secre_form': secre_form})

    else:
        registro_personal = RegistroPersonalForm()
        per_salud_form = PersonalSaludForm()
        admin_form = AdministradorForm()
        secre_form = SecretariaForm()

        return render(request, 'administracion/personal_dashboard.html', {'form': registro_personal, 'per_salud_form': per_salud_form, 'admin_form': admin_form, 'secre_form': secre_form,})

def editar_usuario(request, user_id):

    if user_id is None:
        return redirect('personal_dashboard')

    if request.method == 'POST' and 'usuario' in request.POST:
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        rut = request.POST.get('rut')
        rol = request.POST.get('rol')

        usuario = User.objects.get(pk=user_id)

        if nombre:
            usuario.nombre = nombre
        else:
            usuario.nombre = usuario.nombre

        if email:
            usuario.email = email
        else:
            usuario.email = usuario.email

        if telefono:
            usuario.telefono = telefono
        else:
            usuario.telefono = usuario.telefono

        if rut:
            usuario.rut = rut
        else:
            usuario.rut = usuario.rut

        if rol:
            usuario.rol = rol
        else:
            usuario.rol = usuario.rol

        usuario.save()
        sweetify.success(request, f"Usuario Editado con Éxito.", button='Aceptar')
        return redirect('personal_dashboard')

    return render(request, 'administracion/editar_usuario.html')

def editar_personal_salud(request, personal_id):

    if personal_id is None:
        return redirect('personal_dashboard')

    if request.method == 'POST' and 'personal_salud' in request.POST:
        prefijo = request.POST.get('prefijo')
        titulo = request.POST.get('titulo')
        especialidad = request.POST.get('especialidad')
        universidad = request.POST.get('universidad')
        user = request.POST.get('user')

        personal_salud = PersonalSalud.objects.get(pk=personal_id)

        if prefijo:
            personal_salud.prefijo = prefijo
        else:
            personal_salud.prefijo = personal_salud.prefijo

        if titulo:
            personal_salud.titulo = titulo
        else:
            personal_salud.titulo = personal_salud.titulo

        if especialidad:
            personal_salud.especialidad = especialidad
        else:
            personal_salud.especialidad = personal_salud.especialidad

        if universidad:
            personal_salud.universidad = universidad
        else:
            personal_salud.universidad = personal_salud.universidad

        if user:
            personal_salud.user = User(pk=user)
        else:
            personal_salud.user = personal_salud.user

        personal_salud.save()
        sweetify.success(request, f"Personal de Salud Editado con Éxito.", button='Aceptar')
        return redirect('personal_dashboard')

    return render(request, 'administracion/editar_personal_salud.html')

def eliminar_usuario(request, user_id):

    if user_id is None:
        return redirect('personal_dashboard')

    usuario = User.objects.get(pk=user_id)
    usuario.delete()
    sweetify.success(request, f"Usuario Eliminado con Éxito.", button='Aceptar')
    return redirect('personal_dashboard')


def informe_admin(request):

    if request.method == 'POST':
        month = request.POST.get('month')
        if month:
            return redirect('generar_pdf')
        else:
            sweetify.error(request, 'Error al generar informe. Por favor, inténtelo de nuevo.', button='Aceptar')
            return render(request, 'administracion/informes_admin.html')

    return render(request, 'administracion/informes_admin.html')


def generar_pdf_view(request):

    template_path = 'administracion/informe_template.html'

    context = {}

    template = get_template(template_path)
    html = template.render(context)

    response = BytesIO()
    pdf = pisa.CreatePDF(html, dest=response)
    if not pdf.err:
        return HttpResponse(response.getvalue(), content_type='application/pdf')
    return HttpResponse('Error generating PDF <pre>' + html + '</pre>')