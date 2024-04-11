from django.views.generic import TemplateView

from django.shortcuts import redirect, render

class Homepage(TemplateView):
    template_name = "wiki/homepage.html"