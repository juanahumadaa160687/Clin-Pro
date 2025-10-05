import datetime
from calendar import month
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
from clinpro.models import User, Paciente, Convenio, Pago, ReservaHora
import sweetify
from django.contrib.auth import login as auth_login, authenticate
from xhtml2pdf import pisa
from django.contrib import messages


def dashboard_admin(request):

    servicios = Servicio.objects.all().values('nombre').distinct()

    servicio_form = ServicioForm()

    if request.method == 'POST' and 'servicio' in request.POST:

        request.session['servicio'] = request.POST['servicio']

        services = Servicio.objects.filter(nombre=request.session['servicio']).values('nombre')


        atencion_servicios = Servicio.objects.filter(personal__agenda__fecha__year=datetime.date.today().year).values('nombre').annotate(total=Count('personal__agenda__id'))


        servicio_mes = Servicio.objects.values('personal__agenda__fecha__month').filter(nombre=request.session['servicio']).annotate(total=Count('personal__servicio__nombre')).order_by('personal__agenda__fecha__month')
        print(servicio_mes)

        data = []

        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];

        for smes in servicio_mes:
            if smes['personal__agenda__fecha__month'] is None:
                pass
            else:
                month_name = meses[smes['personal__agenda__fecha__month'] -1]
                data.append({'month': month_name, 'total': smes['total']})

        servicio_mes = data


        monto_mes = ReservaHora.objects.values('fecha_reserva__month').filter(profesional__servicio__nombre=request.session['servicio']).annotate(monto=Sum('pago__monto')).order_by('fecha_reserva__month')

        personal_servicio = Servicio.objects.filter(personal__servicio__nombre=request.session['servicio']).values('personal__user_id', 'personal__user__rut', 'personal__prefijo', 'personal__user__nombre', 'personal__titulo', 'personal__user__email', 'personal__user__rol').distinct()
        print(personal_servicio)

        return render(request, 'administracion/dashboard_admin.html', {'atencion_servicios': atencion_servicios, 'servicio_form': servicio_form, 'servicio_mes': servicio_mes, 'monto_mes': monto_mes, 'personal_servicio': personal_servicio})
    else:
        return render(request, 'administracion/dashboard_admin.html', {'servicios': servicios, 'servicio_form': servicio_form})

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'
    success_message = "Se ha enviado un correo electrónico con instrucciones para restablecer su contraseña."
    success_url = reverse_lazy('index')



def dashboard_personal(request):

    registro_personal = RegistroPersonalForm()
    per_salud_form = PersonalSaludForm()
    admin_form = AdministradorForm()
    secre_form = SecretariaForm()

    if request.method == 'POST' and 'registro' in request.POST:

        registro_personal = RegistroPersonalForm()

        if registro_personal.is_valid():

            user = registro_personal.save(commit=False)
            user.email = registro_personal.cleaned_data.get('email')
            user.nombre = registro_personal.cleaned_data.get('nombre')
            user.telefono = registro_personal.cleaned_data.get('telefono')
            user.rut = registro_personal.cleaned_data.get('rut')
            user.rol = registro_personal.cleaned_data.get('rol')
            user.set_password(registro_personal.cleaned_data.get('password1'))
            user.save()
            messages.success(request, f"Usuario {user.nombre} Registrado con Éxito.")
            sweetify.success(request, f"Usuario {user.nombre} Registrado con Éxito.", button='Aceptar')
            return render(request, 'administracion/personal_dashboard.html', {'form': registro_personal, 'per_salud_form': per_salud_form, 'admin_form': admin_form, 'secre_form': secre_form})
        else:
            messages.error(request, 'Error al registrar usuario. Por favor, inténtelo de nuevo.')
            sweetify.error(request, 'Error al registrar usuario. Por favor, inténtelo de nuevo.', button='Aceptar')

        return render(request, 'administracion/personal_dashboard.html', {'form': registro_personal, 'per_salud_form': per_salud_form, 'admin_form': admin_form, 'secre_form': secre_form})



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
            return render(request, 'administracion/personal_dashboard.html', {'per_salud_form': per_salud_form, 'form': registro_personal, 'admin_form': admin_form, 'secre_form': secre_form,
                                                                              'success': 'Personal de Salud Registrado con Éxito.'})
        else:
            sweetify.error(request, 'Error al registrar personal de salud. Por favor, inténtelo de nuevo.', button='Aceptar')
            return render(request, 'administracion/personal_dashboard.html', {'per_salud_form': per_salud_form, 'form': registro_personal, 'admin_form': admin_form, 'secre_form': secre_form})

    elif request.method == 'POST' and 'administrador' in request.POST:
        admin_form = AdministradorForm(request.POST)
        if admin_form.is_valid():
            administrador = admin_form.cleaned_data.get('administrador')

            administrador.save()

            sweetify.success(request, f"Administrador Asignado con Éxito.", button='Aceptar')
            return render(request, 'administracion/personal_dashboard.html', {'admin_form': admin_form, 'form': registro_personal, 'per_salud_form': per_salud_form, 'secre_form': secre_form})
        else:
            sweetify.error(request, 'Error al asignar administrador. Por favor, inténtelo de nuevo.', button='Aceptar')
            return render(request, 'administracion/personal_dashboard.html', {'admin_form': admin_form, 'form': registro_personal, 'per_salud_form': per_salud_form, 'secre_form': secre_form})

    elif request.method == 'POST' and 'secretaria' in request.POST:
        secre_form = RegistroUserForm(request.POST)
        if secre_form.is_valid():
            secretaria = secre_form.cleaned_data.get('secretaria')

            secretaria.save()

            sweetify.success(request, f"Secretaria Registrada con Éxito.", button='Aceptar')
            return render(request, 'administracion/personal_dashboard.html', {'secre_form': secre_form, 'form': registro_personal, 'per_salud_form': per_salud_form, 'admin_form': admin_form})
        else:
            sweetify.error(request, 'Error al registrar secretaria. Por favor, inténtelo de nuevo.', button='Aceptar')
            return render(request, 'administracion/personal_dashboard.html', {'secre_form': secre_form, 'form': registro_personal, 'per_salud_form': per_salud_form, 'admin_form': admin_form})

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



def generar_pdf_view(request):

    servicios = Servicio.objects.values('nombre').filter(personal__agenda__fecha__month=datetime.date.today().month).annotate(total=Count('personal__reservahora__id'))
    print(servicios)

    template_path = 'administracion/informe_template.html'

    context = {
        'month' : datetime.date.today().month,
        'year' : datetime.date.today().year,
        'servicios': servicios,
    }

    template = get_template(template_path)
    html = template.render(context)

    response = BytesIO()
    pdf = pisa.CreatePDF(html, dest=response)
    if not pdf.err:
        return HttpResponse(response.getvalue(), content_type='application/pdf')
    return HttpResponse('Error generating PDF <pre>' + html + '</pre>')