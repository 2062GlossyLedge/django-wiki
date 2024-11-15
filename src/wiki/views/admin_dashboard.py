from django.views.generic import TemplateView
from django.utils.decorators import method_decorator

from django.shortcuts import redirect, render
from datetime import timedelta
from wiki.models.account import Report, DiscussionReport, DiscussionBoard
from django.shortcuts import get_object_or_404
from .. import models
from wiki.models.article import Article


class AdminDashboard(TemplateView):
    template_name = "wiki/accounts/adminDashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report_data = Report.objects.all().order_by("date")
        discussion_report_data = DiscussionReport.objects.all().order_by("date")
        reports = []
        discussion_reports = []
        for report in report_data:
            revision = get_object_or_404(
                models.ArticleRevision, article=report.article_id, id=report.revision_id
            )
            article = get_object_or_404(models.Article, id=report.article_id)
            reports.append(
                {
                    "date": report.date,
                    "user": revision.user,
                    "wiki": report.current_page,
                    "content": revision.content,
                    "reason": report.report_type,
                    "revision_number": report.revision_num,
                    "revision_id": report.revision_id,
                    "article_id": report.article_id,
                }
            )

        for report in discussion_report_data:
            post = get_object_or_404(
                DiscussionBoard, post_id=report.post_id
            )
            discussion_reports.append(
                {
                    "date": report.date,
                    "user": post.user,
                    "wiki": report.current_page,
                    "content": post.content,
                    "reason": report.report_type,
                    "post_id": report.post_id,
                    "article_id": report.article_id
                }
            )
            # access all articles that have potential spoilers
        articles = Article.objects.filter(has_potential_spoilers=True)

        context = {"reports": reports, "articles": articles, "discussion": discussion_reports}
        return context
