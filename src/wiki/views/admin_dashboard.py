from django.views.generic import TemplateView
from django.utils.decorators import method_decorator

from django.shortcuts import redirect, render
from wiki.models.account import Privileges
from datetime import timedelta


class AdminDashboard(TemplateView):
    template_name = "wiki/accounts/adminDashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Dummy data for privileges
        reports = [
            {
                "date": "10-01-2024",
                "user": "User1",
                "wiki": "One Piece TV",
                "content": "Luffy goes gear 10 on episode 1102",
                "reason": "Inaccurate data"
            },
            {
                "date": "10-02-2024",
                "user": "User2",
                "wiki": "First Law Book",
                "content": "Logen has nine fingers",
                "reason": "Spoiler"
            },
        ]
        context = {
            "reports": reports
        }
        return context

