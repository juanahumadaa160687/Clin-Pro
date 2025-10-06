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
from pyhanko.generated.w3c import Object

from clinpro.decorators import allowed_users
from clinpro.forms import UserCreationForm, RegistroUserForm
from administracion.forms import LoginPersonalForm, RegistroPersonalForm, ServicioForm, ProcedimientoForm, \
    PersonalSaludForm
from administracion.models import PersonalSalud, Servicio, Procedimiento, Agenda
from clinpro.models import User, Convenio, Pago, ReservaHora
import sweetify
from django.contrib.auth import login as auth_login, authenticate
from xhtml2pdf import pisa
from django.contrib import messages

@login_required(login_url='login')
@allowed_users(allowed_roles=['Administrador'])
def dashboard_admin(request):

    servicios = Servicio.objects.all().values('nombre').distinct()
    print(servicios)

    servicio_form = ServicioForm()

    if request.method == 'POST' and 'servicio' in request.POST:

        request.session['servicio'] = request.POST['servicio']
        print(request.session['servicio'])

        services = Servicio.objects.filter(nombre=request.session['servicio']).values('nombre')
        print(services)


        atencion_servicios = Servicio.objects.values('nombre').filter(personal__agenda__fecha__year=datetime.date.today().year).annotate(total=Count('personal__agenda__id'))
        print(atencion_servicios)

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
        print(servicio_mes)


        monto_mes = ReservaHora.objects.values('fecha_reserva__month').filter(profesional__servicio__nombre=request.session['servicio']).annotate(monto=Sum('pago__monto')).order_by('fecha_reserva__month')
        print(monto_mes)

        personal_servicio = Servicio.objects.values('personal__user_id', 'personal__user__rut', 'personal__user__nombre', 'personal__user__email', 'personal__user__telefono').filter(personal__servicio__nombre=services)

        return render(request, 'administracion/dashboard_admin.html', {'atencion_servicios': atencion_servicios, 'servicio_form': servicio_form, 'servicio_mes': servicio_mes, 'monto_mes': monto_mes, 'personal_servicio': personal_servicio})
    else:
        return render(request, 'administracion/dashboard_admin.html', {'servicios': servicios, 'servicio_form': servicio_form})

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'
    success_message = "Se ha enviado un correo electrónico con instrucciones para restablecer su contraseña."
    success_url = reverse_lazy('index')


@login_required(login_url='login')
@allowed_users(allowed_roles=['Administrador'])
def dashboard_personal(request):

    registro_personal = RegistroPersonalForm()
    per_salud_form = PersonalSaludForm()

    if request.method == 'POST' and 'registro' in request.POST:

        registro_personal = RegistroPersonalForm()

        rut = request.POST.getlist('rut')[0]
        nombre = request.POST.getlist('nombre')[0]
        email = request.POST.getlist('email')[0]
        telefono = request.POST.getlist('telefono')[0]
        rol = request.POST.getlist('rol')[0]
        password1 = request.POST.getlist('password1')[0]
        password2 = request.POST.getlist('password2')[0]
        username = email.split('@')[0]

        if User.objects.filter(rut=rut).exists():
            sweetify.error(request, 'El RUT ya está registrado. Por favor, inténtelo de nuevo.', button='Aceptar')
            return render(request, 'administracion/personal_dashboard.html', {'form': registro_personal, 'per_salud_form': per_salud_form})
        if User.objects.filter(email=email).exists():
            sweetify.error(request, 'El correo electrónico ya está registrado. Por favor, inténtelo de nuevo.', button='Aceptar')
            return render(request, 'administracion/personal_dashboard.html', {'form': registro_personal, 'per_salud_form': per_salud_form,})
        if password1 != password2:
            sweetify.error(request, 'Las contraseñas no coinciden. Por favor, inténtelo de nuevo.', button='Aceptar')
            return render(request, 'administracion/personal_dashboard.html', {'form': registro_personal, 'per_salud_form': per_salud_form,})
        if len(password1) < 8:
            sweetify.error(request, 'La contraseña debe tener al menos 8 caracteres. Por favor, inténtelo de nuevo.', button='Aceptar')
            return render(request, 'administracion/personal_dashboard.html', {'form': registro_personal, 'per_salud_form': per_salud_form,})

        user = User.objects.create_user(rut=rut, nombre=nombre, email=email, telefono=telefono, rol=rol, password=password1, username=username)

        user.save()

        if user:
            sweetify.success(request, f"Usuario {nombre} Registrado con Éxito.", button='Aceptar')
            group = Group.objects.get(name=rol)
            user.groups.add(group)
            return render(request, 'administracion/personal_dashboard.html', {'form': registro_personal, 'per_salud_form': per_salud_form,})
        else:

            sweetify.error(request, 'Error al registrar usuario. Por favor, inténtelo de nuevo.', button='Aceptar')


        return render(request, 'administracion/personal_dashboard.html', {'form': registro_personal, 'per_salud_form': per_salud_form,})



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
            return render(request, 'administracion/personal_dashboard.html', {'per_salud_form': per_salud_form, 'form': registro_personal})
        else:

            sweetify.error(request, 'Error al registrar personal de salud. Por favor, inténtelo de nuevo.', button='Aceptar')
            return render(request, 'administracion/personal_dashboard.html', {'per_salud_form': per_salud_form, 'form': registro_personal})


    else:
        registro_personal = RegistroPersonalForm()
        per_salud_form = PersonalSaludForm()

        return render(request, 'administracion/personal_dashboard.html', {'form': registro_personal, 'per_salud_form': per_salud_form})

@login_required(login_url='login')
@allowed_users(allowed_roles=['Administrador'])
def editar_usuario(request, user_id):

    personal_salud = PersonalSalud.objects.values('prefijo', 'user_id', 'titulo', 'especialidad', 'universidad', 'user')

    id_user = User.objects.values('id').get(pk=user_id)
    print(id_user)

    if user_id is None:
        return redirect('personal_dashboard')

    if request.method == 'POST' and 'editar_user' in request.POST:
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        rut = request.POST.get('rut')
        rol = request.POST.get('rol')

        usuario = User.objects.get(pk=id_user)

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


    elif request.method == 'POST' and 'personal_salud' in request.POST:

        prefijo = request.POST.get('prefijo')
        titulo = request.POST.get('titulo')
        especialidad = request.POST.get('especialidad')
        universidad = request.POST.get('universidad')
        user = request.POST.get('user')

        personal_salud = PersonalSalud.objects.get(pk=id_user)

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

    return render(request, 'administracion/editar_usuario.html', {'usuarios': personal_salud})

@login_required(login_url='login')
@allowed_users(allowed_roles=['Administrador'])
def eliminar_usuario(request, user_id):

    if user_id is None:
        return redirect('personal_dashboard')

    usuario = User.objects.get(pk=user_id)
    usuario.delete()
    sweetify.success(request, f"Usuario Eliminado con Éxito.", button='Aceptar')
    return redirect('personal_dashboard')

@login_required(login_url='login')
@allowed_users(allowed_roles=['Administrador'])
def servicios_view(request):

    servicios_disponibles = Servicio.objects.values('id', 'nombre').annotate(total=Count('personal__user_id')).order_by('nombre').annotate(total1=Count('personal__especialidad'))
    print(servicios_disponibles)

    form = ServicioForm()

    if request.method == 'POST' and 'servicio' in request.POST:

        nombre = request.POST.getlist('nombre')[0]
        personal = request.POST.getlist('personal')

        if Servicio.objects.filter(nombre=nombre).exists():
            sweetify.error(request, 'El nombre del servicio ya está registrado. Por favor, inténtelo de nuevo.', button='Aceptar')
            return render(request, 'administracion/servicios.html', {'form': form, 'servicios_disponibles': servicios_disponibles})

        servicio = Servicio.objects.create(nombre=nombre)
        servicio.personal.set(personal)
        servicio.save()
        sweetify.success(request, f"Servicio {nombre} Registrado con Éxito.", button='Aceptar')
        return redirect('servicios')

    elif request.method == 'POST' and 'agregar' in request.POST:

        servicio = request.POST.getlist('agregar')[0]
        personal = request.POST.getlist('personal')[0]
        print(personal)
        print(servicio)
        service = Servicio.objects.get(pk=servicio)
        service.personal.add(personal)
        service.save()

        sweetify.success(request, f"Personal de Salud Agregado con Éxito al Servicio {service}.", button='Aceptar')
        return redirect('servicios')

    return render(request, 'administracion/servicios.html', {'form': form, 'servicios_disponibles': servicios_disponibles})

@login_required(login_url='login')
@allowed_users(allowed_roles=['Administrador'])
def procedimientos_view(request):

    procedimientos_disponibles = Procedimiento.objects.all().values('id', 'procedimiento', 'precio')
    print(procedimientos_disponibles)
    procedimiento_form = ProcedimientoForm()

    if request.method == 'POST' and 'procedimiento' in request.POST:

        procedimiento = request.POST.getlist('procedimiento')[0]
        precio = request.POST.getlist('precio')[0]
        personal_salud = request.POST.getlist('personal_salud')

        if Procedimiento.objects.filter(procedimiento=procedimiento).exists():
            sweetify.error(request, 'El nombre del procedimiento ya está registrado. Por favor, inténtelo de nuevo.', button='Aceptar')
            return render(request, 'administracion/servicios.html', {'procedimiento_form': procedimiento_form, 'procedimientos_disponibles': procedimientos_disponibles})

        procedimiento = Procedimiento.objects.create(procedimiento=procedimiento, precio=precio)
        procedimiento.personal_salud.set(personal_salud)
        procedimiento.save()
        sweetify.success(request, f"Procedimiento {procedimiento} Registrado con Éxito.", button='Aceptar')
        return redirect('servicios')

    return render(request, 'administracion/procedimientos.html', {'procedimientos_disponibles': procedimientos_disponibles, 'procedimiento_form': procedimiento_form})

@login_required(login_url='login')
@allowed_users(allowed_roles=['Administrador'])
def editar_servicio(request, servicio_id):
    if servicio_id is None:
        return redirect('servicios')

    if request.method == 'POST' and 'servicio' in request.POST:
        nombre = request.POST.get('nombre')
        personal = request.POST.getlist('personal')

        servicio = Servicio.objects.get(pk=servicio_id)

        if nombre:
            servicio.nombre = nombre
        else:
            servicio.nombre = servicio.nombre

        if personal:
            servicio.personal.set(personal)
        else:
            servicio.personal = servicio.personal

        servicio.save()
        sweetify.success(request, f"Servicio Editado con Éxito.", button='Aceptar')
        return redirect('servicios')

    return render(request, 'administracion/editar_servicio.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['Administrador'])
def eliminar_servicio(request, servicio_id):

    if servicio_id is None:
        return redirect('servicios')

    servicio = Servicio.objects.get(pk=servicio_id)
    servicio.delete()
    sweetify.success(request, f"Servicio Eliminado con Éxito.", button='Aceptar')
    return redirect('servicios')

@login_required(login_url='login')
@allowed_users(allowed_roles=['Administrador'])
def eliminar_procedimiento(request, procedimiento_id):

    if procedimiento_id is None:
        return redirect('servicios')

    procedimiento = Procedimiento.objects.get(pk=procedimiento_id)
    procedimiento.delete()
    sweetify.success(request, f"Procedimiento Eliminado con Éxito.", button='Aceptar')
    return redirect('servicios')

@login_required(login_url='login')
@allowed_users(allowed_roles=['Administrador'])
def generar_pdf_view(request):

    servicios = Servicio.objects.values('nombre').annotate(total=Count('personal__id')).order_by('nombre')
    print(servicios)

    procedimientos = Procedimiento.objects.values('procedimiento').annotate(total=Count('personal_salud__id')).order_by('procedimiento')
    print(procedimientos)

    profesionales = PersonalSalud.objects.values('user__rut', 'prefijo', 'user__nombre', 'titulo', 'especialidad', 'universidad', 'user__email')
    print(profesionales)

    template_path = 'administracion/informe_template.html'

    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
             'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    # Obtener mes del reporte
    mes_actual =  datetime.date.today().month - 1 # Restar 1 porque los meses en Python van de 0 a 11

    month = meses[mes_actual]

    context = {
        'month' : month,
        'year' : datetime.date.today().year,
        'servicios': servicios,
        'fecha': datetime.date.today().strftime('%d/%m/%Y'),
        'procedimientos': procedimientos,
        'title': 'Informe de Servicios y Procedimientos',
        'profesionales': profesionales,
    }

    template = get_template(template_path)
    html = template.render(context)

    response = BytesIO()

    pdf = pisa.CreatePDF(html, dest=response)

    if not pdf.err:
        return HttpResponse(response.getvalue(), content_type='application/pdf')
    return HttpResponse('Error generating PDF <pre>' + html + '</pre>')