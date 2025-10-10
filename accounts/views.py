import base64
import io
import os

import pyotp
import qrcode
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth.models import Group
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordResetConfirmView, \
    PasswordChangeDoneView
from django.shortcuts import render, redirect, get_object_or_404
from clinpro.decorators import allowed_users
from clinpro.functions import confirmacionregistro
from clinpro.models import ReservaHora
from .forms import LoginUserForm, RegistroUserForm, ChangePasswordForm, ResetPasswordForm
import sweetify
from .models import User



def signup(request):
    if request.method == 'POST':
        form = RegistroUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.rut = form.cleaned_data.get('rut')
            user.email = form.cleaned_data.get('email')
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.telefono = form.cleaned_data.get('telefono')
            user.set_password(form.cleaned_data.get('password1'))
            user.username = user.email.split('@')[0]  # Asignar username basado en el email
            user.rol = 'Paciente'  # Asignar rol por defecto

            user.save()

            grupo_paciente, created = Group.objects.get_or_create(name='Paciente')
            user.groups.add(grupo_paciente)

            remitente = os.getenv('EMAIL_HOST_USER')
            destinatario = user.email
            nombre = f'{user.first_name} {user.last_name}'

            confirmacionregistro(remitente, destinatario, nombre)

            sweetify.success(request, 'Registro exitoso. Ahora puedes iniciar sesión.', button='Aceptar', timer=3000, persistent='Ok', icon='success')
            return redirect('login')
        else:
            sweetify.error(request, 'Error en el registro. Por favor, verifica los datos ingresados.', button='Aceptar', timer=3000, persistent='Ok', icon='error')
    else:
        form = RegistroUserForm()

    return render(request, 'accounts/signup.html', {'form': form})


def login(request):
    if request.method == 'POST':

        email = request.POST.get('email')
        password = request.POST.get('password1')
        print(email, password)

        user = authenticate(request, email=email, password=password)

        usuario = User.objects.get(email=email)
        print(usuario)

        if user is not None:

            if usuario.rol == 'Paciente':
                auth_login(request, user)
                return redirect('reserva_hora')

            elif usuario.mfa_secret:
                print(usuario.id)
                auth_login(request, user)
                return render(request, 'accounts/verificar_otp.html', {'user_id': usuario.id})

            else:
                auth_login(request, user)
                return redirect('activate_mfa')
        else:
            sweetify.error(request, 'Credenciales inválidas. Por favor, intenta nuevamente.', button='Aceptar', timer=3000, persistent='Ok', icon='error')
            return redirect('login')
    else:
        form = LoginUserForm()
        return render(request, 'accounts/login.html', {'form': form})


def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)

    return redirect('index')


def verify_2fa_otp(user, otp):
    totp = pyotp.TOTP(user.mfa_secret)
    print(totp)
    if totp.verify(otp):
        user.mfa_verified = True
        user.save()
        return True
    return False

def activate_mfa(request):

    user = request.user
    print(user)
    print(user.rut)
    print(f'User MFA Secret before check: {user.mfa_secret}')

    if not user.mfa_secret:
        user.mfa_secret = pyotp.random_base32()
        user.save()
        print(f'User MFA Secret after generation: {user.mfa_secret}')

    otp_uri = pyotp.totp.TOTP(user.mfa_secret).provisioning_uri(name=user.email, issuer_name="ClinPro")
    print(otp_uri)
    qr = qrcode.make(otp_uri)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")

    buffer.seek(0)
    qr_code = base64.b64encode(buffer.getvalue()).decode("utf-8")

    qr_code_data_uri = f"data:image/png;base64,{qr_code}"

    return render(request, 'accounts/enable2FA.html', {'qr_code': qr_code_data_uri})

def verify_mfa(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        print(user_id)
        otp = request.POST.get('otp_code')
        print(otp)

        if not user_id:
            sweetify.error(request, 'ID de usuario no existe. Por favor, inténtelo de nuevo.', button='Aceptar')
            return render(request, 'accounts/login.html')

        user = User.objects.get(pk=user_id)
        print(user)

        if verify_2fa_otp(user, otp):
            if request.user.is_authenticated:
                sweetify.success(request, 'Usuario verificado correctamente.')

                if request.user.rol == 'Administrador':
                    return redirect('dashboard')
                elif request.user.rol == 'Personal Salud':
                    return redirect('dashboard_fichas')
                elif request.user.rol == 'Secretaria':
                    return redirect('dashboard_recepcion')
            else:
                sweetify.error(request, 'Por favor, inicie sesión nuevamente.', button='Aceptar')
                return redirect('index')

    return render(request, 'accounts/enable2FA.html', {'user_id': request.user.id if request.user.is_authenticated else None})


def deactivate_mfa(request):
    user = request.user
    if user.mfa_enabled:
        user.mfa_enabled = False
        user.save()
        sweetify.success(request, 'Autenticación de dos factores deshabilitada correctamente.', button='Aceptar')
        return redirect('index')
    else:
        sweetify.error(request, 'La autenticación de dos factores ya está deshabilitada.', button='Aceptar')
        return redirect('index')


@login_required(login_url='login')
@allowed_users(allowed_roles=['Paciente'])
def profile(request, id):

    if ReservaHora.objects.filter(user_id=id).exists():
        reservas = ReservaHora.objects.filter(user_id=id).values('id', 'fecha_reserva', 'hora_reserva', 'is_confirmada', 'profesional__user__nombre', 'profesional__prefijo','pago__orden_compra', 'profesional__servicio__nombre').order_by('-fecha_reserva', '-hora_reserva')
        print(reservas)
        return render(request, 'accounts/profile.html', {'reservas': reservas, })

    else:
        sweetify.info(request, 'No tienes horas reservadas aún', button='Aceptar', timer=3000, persistent='Ok', icon='info')
        return render(request, 'accounts/profile.html', )

#######################################################################################################################

@login_required(login_url='login')
@allowed_users(allowed_roles=['Paciente'])
def edit_profile(request, id):
    user = get_object_or_404(User, id=id)

    if request.method == 'POST':
        form = RegistroUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            sweetify.success(request, 'Usuario actualizado correctamente.')
            return redirect('profile', id=user.id)
        else:
            sweetify.error(request, 'Error al actualizar el perfil. Por favor, verifica los datos ingresados.', button='Aceptar', timer=3000, persistent='Ok', icon='error')
            return redirect('edit_profile', id=user.id)
    else:
        form = RegistroUserForm()
        return render(request, 'accounts/edit_profile.html', {'form': form})

#######################################################################################################################

@login_required(login_url='login')
@allowed_users(allowed_roles=['Paciente'])
def delete_profile(request, id):
    user = get_object_or_404(User, id=id)

    if request.method == 'POST':
        user.delete()
        sweetify.success(request, 'Usuario eliminado correctamente.')

    return redirect('index')

class PasswordsChangeView(PasswordChangeView):

    form_class = ChangePasswordForm
    template_name = 'accounts/change_password.html'
    success_url = '/accounts/login/'

    def form_valid(self, form):
        sweetify.success(self.request, 'Contraseña cambiada exitosamente. Por favor, inicia sesión nuevamente.', button='Aceptar', timer=3000, persistent='Ok', icon='success')
        return super().form_valid(form)

class PasswordsResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    form_class = ResetPasswordForm
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = '/accounts/login/'
    from_email = os.getenv('EMAIL_HOST_USER')

    def form_valid(self, form):
        sweetify.success(self.request, 'Se ha enviado un correo para restablecer tu contraseña.', button='Aceptar', timer=3000, persistent='Ok', icon='success')
        return super().form_valid(form)


class PasswordsResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = '/accounts/login/'
    form_class = ChangePasswordForm

    def form_valid(self, form):
        sweetify.success(self.request, 'Contraseña restablecida exitosamente. Por favor, inicia sesión nuevamente.', button='Aceptar', timer=3000, persistent='Ok', icon='success')
        return super().form_valid(form)

class PasswordsChangeDoneView(PasswordChangeDoneView):
    template_name = 'accounts/password_change_done.html'

    def get(self, request, *args, **kwargs):
        sweetify.success(self.request, 'Contraseña cambiada exitosamente.', button='Aceptar', timer=3000, persistent='Ok', icon='success')
        return super().get(request, *args, **kwargs)

