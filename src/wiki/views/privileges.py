from django.views.generic import TemplateView
from django.utils.decorators import method_decorator

from django.shortcuts import redirect, render
from wiki.models.account import Privileges
from datetime import timedelta


class Privileges(TemplateView):
    template_name = "wiki/accounts/privilegeDashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Dummy data for incidents
        incident_events = [
            {
                "date": "2024-09-01",
                "admin": "Admin1",
                "article_title": "Gravity Falls tv season 1 episode 1",
                "article_history_link": "/gravity-falls/tv/season1/episode1/",
            },
            {
                "date": "2024-09-02",
                "admin": "Admin2",
                "article_title": "Dune book 1 chapter 1",
                "article_history_link": "/dune/book/book1/chapter1/",
            },
            {
                "date": "2024-09-03",
                "admin": "Admin2",
                "article_title": "Dune book 1 chapter 2",
                "article_history_link": "/dune/book/book1/chapter2/",
            },
        ]

        # Dummy data for privileges
        privileges = [
            {
                "name": "Edit Articles",
                "status": "Bad",
                "penalty_length": 3,
                "numOfIncidents": 0,
                "totalIncidents": 3,
                "incidentEvents": incident_events,
            },
            {
                "name": "Commenting",
                "status": "Good",
                "numOfIncidents": 10,
                "totalIncidents": 10,
                "incidentEvents": [],
            },
        ]

        # Pass dummy data to the template
        context = {
            "privileges": privileges,
        }

        return context
