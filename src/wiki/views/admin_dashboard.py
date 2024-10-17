from django.views.generic import TemplateView
from django.utils.decorators import method_decorator

from django.shortcuts import redirect, render
from wiki.models.account import Privileges
from datetime import timedelta
from wiki.models.article import Report
from django.shortcuts import get_object_or_404
from .. import models


class AdminDashboard(TemplateView):
    template_name = "wiki/accounts/adminDashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report_data = Report.objects.all().order_by('date')
        reports = []
        for report in report_data:
            revision = get_object_or_404(
                models.ArticleRevision, article=report.article_id, id=report.revision_id
            )
            reports.append({
                "date": report.date,
                "user": revision.user,
                "wiki": report.current_page,
                "content": revision.content,
                "reason": report.report_type,
                "revision_number": report.revision_num
            })

        context = {
            "reports": reports,
        }
        return context

