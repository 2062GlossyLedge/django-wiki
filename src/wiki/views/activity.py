# views/activity.py
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.shortcuts import render
from datetime import timedelta
from wiki.models.article import ArticleRevision
from django.db.models import Count
from django.utils import timezone
from django.http import JsonResponse

class ActivityView(TemplateView):
    template_name = "wiki/activity.html"

    def get_revision_data(self):
        # Group revisions by day and count the number of revisions per day (SQLite-compatible)
        revisions = (
            ArticleRevision.objects
            .extra(select={'day': "strftime('%Y-%m-%d', created)"})
            .values('day')
            .annotate(revision_count=Count('id'))
            .order_by('day')
        )
        return {
            "labels": [rev["day"] for rev in revisions],
            "data": [rev["revision_count"] for rev in revisions],
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["revision_data"] = self.get_revision_data()
        return context
