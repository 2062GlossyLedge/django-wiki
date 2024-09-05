from django.views.generic import TemplateView

from django.shortcuts import redirect, render
from openai import OpenAI


class Chatbot(TemplateView):
    template_name = "wiki/view.html"
   
   
    def get(self, request, *args, **kwargs):
        response = "Hi, I'm your friendly chatbot"
        context = self.get_context_data(**kwargs)
        context['response'] = response
        return self.render_to_response(context)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(context)  # Print the context to the console for debugging
        return context
