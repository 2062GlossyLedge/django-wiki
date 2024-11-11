from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.utils import timezone
from datetime import timedelta
from wiki.models.article import ArticleRevision
from django.db.models import Count
from django.db.models.functions import TruncDay, ExtractWeekDay

class ActivityView(TemplateView):
    template_name = "wiki/activity.html"

    def get_revision_data(self):
        today = timezone.now()
        start_date = today - timedelta(days=30)

        revisions = (
            ArticleRevision.objects
            .filter(created__gte=start_date)
            .annotate(day=TruncDay('created'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )

        labels = [rev['day'].strftime('%Y-%m-%d') for rev in revisions]
        data = [rev['count'] for rev in revisions]

        return {'labels': labels, 'data': data}

    def get_top_articles_data(self):
        top_articles = (
            ArticleRevision.objects
            .values('title')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )

        labels = [article['title'] for article in top_articles]
        data = [article['count'] for article in top_articles]

        return {'labels': labels, 'data': data}

    def get_top_editors_data(self):
        top_editors = (
            ArticleRevision.objects
            .values('user__username')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )

        labels = [editor['user__username'] for editor in top_editors]
        data = [editor['count'] for editor in top_editors]

        return {'labels': labels, 'data': data}

    def get_edit_distribution_data(self):
        distribution = (
            ArticleRevision.objects
            .annotate(day_of_week=ExtractWeekDay('created'))
            .values('day_of_week')
            .annotate(count=Count('id'))
            .order_by('day_of_week')
        )

        labels = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        data = [0] * 7

        for dist in distribution:
            data[dist['day_of_week'] - 1] = dist['count']

        return {'labels': labels, 'data': data}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['revision_data'] = self.get_revision_data()
        context['top_articles_data'] = self.get_top_articles_data()
        context['top_editors_data'] = self.get_top_editors_data()
        context['edit_distribution_data'] = self.get_edit_distribution_data()
        return context
