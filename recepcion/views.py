from django.shortcuts import render

# Create your views here.
def dashboard_view(request):

    return render(request, 'recepcion/dashboard_recep.html')