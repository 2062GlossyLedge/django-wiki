from django.views.generic import TemplateView

from django.shortcuts import redirect, render
from openai import OpenAI


class Homepage(TemplateView):
    template_name = "wiki/homepage.html"
   


  


