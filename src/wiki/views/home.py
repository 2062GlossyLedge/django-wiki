from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from wiki.models.account import UserProfile


from django.shortcuts import redirect, render
from openai import OpenAI


class Homepage(TemplateView):
    template_name = "wiki/homepage.html"

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["profile_picture"] = UserProfile.objects.get(
    #         user=self.request.user
    #     ).profile_image.url
    #     return context
