from django.shortcuts import render


def dashboard_fichas(request):
    return render(request, 'personal_salud/ficha_medicina.html')