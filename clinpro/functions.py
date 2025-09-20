
def getCargo(request):
    cargo = request.GET.get('cargo')
    print(cargo)

    return cargo