# views/activity.py
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.shortcuts import render
from datetime import timedelta

class ActivityView(TemplateView):
    template_name = "wiki/activity.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Example: Fetch activity data for the graph

        # Aggregate data for the graph (customize as needed)
        activity_data = {
            "labels": ["Jan", "Feb", "Mar"],  # Placeholder for actual months/dates
            "data": [10, 15, 7]  # Placeholder for activity counts
        }

        context["activity_data"] = activity_data
        return context
