from django.shortcuts import render
from .models import Aviso

def index(request):
    avisos = Aviso.objects.all()
    context = {
        'is_in_equipe': request.user.is_in_equipe_group() if request.user.is_authenticated else False,
        'avisos': avisos,
    }
    return render(request, 'index.html', context)