from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView

from .models import Aviso


def index(request):
    avisos = Aviso.objects.all()
    context = {
        'is_in_equipe': request.user.is_in_equipe_group() if request.user.is_authenticated else False,
        'avisos': avisos,
    }
    return render(request, 'index.html', context)


class EmConstrucaoView(LoginRequiredMixin, TemplateView):
    template_name = 'em_construcao.html'
