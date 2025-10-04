from django.shortcuts import render

# Create your views here.
def dashboard_view(request):

    return render(request, 'recepcion/dashboard_recepcion.html')

def reservas_view(request):

    return render(request, 'recepcion/reservas_recepcion.html')

def calendar_view(request):

    return render(request, 'recepcion/calendar_recepcion.html')

def pagos_view(request):

    return render(request, 'recepcion/pagos_recepcion.html')