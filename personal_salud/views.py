import sweetify
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
import requests
from django import forms

from accounts.models import User
from recepcion.models import NoRegistrado


@login_required(login_url='/accounts/login/')
def dashboard_fichas(request):

    if request.method == 'POST' and 'search' in request.POST:

        rut_pac = request.POST.getlist('search')[0]
        print(f'Rut: {rut_pac}')

        api_url = f'https://clinpro-api-1.onrender.com/api/v1/ficha/{rut_pac}'
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            ficha_data = response.json()
            print(ficha_data)

            return render(request, 'personal_salud/ficha_medicina.html', {'ficha': ficha_data})

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from API: {e}")
            sweetify.error(request, 'Error al buscar ficha, intente nuevamente.', button='Aceptar', timer=3000)
            return render(request, 'personal_salud/ficha_medicina.html')


    return render(request, 'personal_salud/ficha_medicina.html')