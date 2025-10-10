import datetime
from io import BytesIO

from django.contrib.auth.models import Group
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from django.urls import reverse_lazy

from clinpro.functions import money_format
from clinpro.decorators import allowed_users
from administracion.forms import RegistroPersonalForm, ServicioForm, ProcedimientoForm, \
    PersonalSaludForm
from administracion.models import PersonalSalud, Servicio, Procedimiento
from accounts.models import User
from clinpro.models import ReservaHora
import sweetify
from xhtml2pdf import pisa



@allowed_users(allowed_roles=['Administrador'])
def dashboard_admin(request):

    servicios = Servicio.objects.all().values('nombre').distinct()
    print(servicios)

    servicio_form = ServicioForm()

    if request.method == 'POST' and 'servicio' in request.POST:

        request.session['servicio'] = request.POST.getlist('servicio')[0]
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

        servicio_mes1 = data
        print(servicio_mes1)


        monto_mes = ReservaHora.objects.values('fecha_reserva__month').filter(profesional__servicio__nombre=request.session['servicio']).annotate(monto=Sum('pago__monto')).order_by('fecha_reserva__month')


        personal_servicio = PersonalSalud.objects.filter(servicio__nombre=request.session['servicio']).values('user_id', 'user__rut', 'user__nombre', 'user__email', 'user__telefono', 'titulo', 'prefijo', 'especialidad').distinct()
        print(personal_servicio)

        return render(request, 'administracion/dashboard_admin.html', {'atencion_servicios': atencion_servicios, 'servicio_form': servicio_form, 'servicio_mes': servicio_mes1, 'monto_mes': monto_mes, 'personal_servicio': personal_servicio})
    else:
        return render(request, 'administracion/dashboard_admin.html', {'servicios': servicios, 'servicio_form': servicio_form})

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'accounts/password_reset.html'
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
        first_name = request.POST.getlist('first_name')[0]
        last_name = request.POST.getlist('last_name')[0]
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

        user = User.objects.create_user(rut=rut, first_name=first_name, last_name=last_name, email=email, telefono=telefono, rol=rol, password=password1, username=username)

        user.save()

        if user:
            sweetify.success(request, f"Usuario {first_name} {last_name} Registrado con Éxito.", button='Aceptar')
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

    procedimientos_disponibles = Procedimiento.objects.all().values('id', 'procedimiento', 'precio').annotate(total=Count('personal_salud__user_id'))

    data=[]

    for procedimiento in procedimientos_disponibles:
        precio_formato = money_format(procedimiento['precio'])
        var = {
            'id': procedimiento['id'],
            'procedimiento': procedimiento['procedimiento'],
            'precio': precio_formato,
        }

        data.append(var)

    procedimientos_disponibles=data
    print(procedimientos_disponibles)

    procedimiento_form = ProcedimientoForm()

    if request.method == 'POST' and 'procedimiento' in request.POST:

        procedimiento = request.POST.getlist('procedimiento')[0]
        print(procedimiento)
        precio = request.POST.getlist('precio')[0]
        print(precio)
        personal_salud = request.POST.getlist('personal_salud')
        print(personal_salud)

        nuevo_procedimiento = Procedimiento.objects.create(procedimiento=procedimiento, precio=precio)
        nuevo_procedimiento.personal_salud.set(personal_salud)
        nuevo_procedimiento.save()

        if Procedimiento.objects.filter(procedimiento=procedimiento).exists():
            sweetify.error(request, 'El nombre del procedimiento ya está registrado. Por favor, inténtelo de nuevo.', button='Aceptar')
            return render(request, 'administracion/procedimientos.html', {'procedimiento_form': procedimiento_form, 'procedimientos_disponibles': procedimientos_disponibles})

        sweetify.success(request, f"Procedimiento {procedimiento} Registrado con Éxito.", button='Aceptar')
        return redirect('procedimientos')

    elif request.method == 'POST' and 'agregar' in request.POST:
        procedimiento = request.POST.getlist('agregar')[0]
        personal_salud = request.POST.getlist('personal_salud')

        procedure = Procedimiento.objects.get(pk=procedimiento)
        procedure.personal_salud.set(personal_salud)
        procedure.save()

        sweetify.success(request, 'Procedimiento asociado al profesional con éxito', button='Aceptar')
        return redirect('procedimientos')

    return render(request, 'administracion/procedimientos.html', {'procedimientos_disponibles': procedimientos_disponibles, 'procedimiento_form': procedimiento_form})

@login_required(login_url='login')
@allowed_users(allowed_roles=['Administrador'])
def editar_servicio(request, servicio_id):

    servicios = get_object_or_404(Servicio, id=servicio_id)

    if request.method == 'POST':
        form = ServicioForm(request.POST, instance=servicios)
        if form.is_valid():
            form.save()
            sweetify.success(request, f"Servicio Editado con Éxito.", button='Aceptar')
            return redirect('servicios')
    else:
        form = ServicioForm(instance=servicios)

    return render(request, 'administracion/editar_servicio.html', {'form': form})

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

def editar_procedimiento(request, procedimiento_id):

    procedimiento = get_object_or_404(Procedimiento, pk=procedimiento_id)

    if request.method == 'POST':
        form = ProcedimientoForm(request.POST, instance=procedimiento)
        if form.is_valid():
            form.save()
            sweetify.success(request, f"Procedimiento Editado con Éxito.", button='Aceptar')
            return redirect('procedimientos')
    else:
        form = ProcedimientoForm(instance=procedimiento)

    return render(request, 'administracion/editar_procedimiento.html', {'form': form})

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