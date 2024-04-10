from django.views.generic import TemplateView

from django.shortcuts import redirect, render
# def homepage(request):
#     return render(request, "wiki/homepage.html")

class Homepage(TemplateView):
    template_name = "wiki/homepage.html"