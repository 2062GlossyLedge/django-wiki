from django.views.generic import TemplateView
from django.utils.decorators import method_decorator

from django.shortcuts import redirect, render
from wiki.models.account import Privilege, InfractionEvent
from wiki.models import Article
from datetime import timedelta


class Privileges(TemplateView):
    template_name = "wiki/accounts/privilegeDashboard.html"
    context_object_name = "privileges"
    model = Privilege

    def get_queryset(self):
        return Privilege.objects.filter(user=self.request.user).prefetch_related(
            "infraction_events"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        privilege_types = [
            "Commenting",
            "Editing",
            "Spoiler flagging",
            "Wiki creation",
        ]

        for priv_type in privilege_types:
            priv = Privilege.objects.get_or_create(
                user=self.request.user,
                name=priv_type,
                defaults={"status": "ACTIVE"},
            )

        context["privileges"] = self.get_queryset()

        # access all articles that have potential spoilers
        articles = Article.objects.filter(has_potential_spoilers=True)
        context["articles"] = articles

        return context
