from django.http import JsonResponse
from django.views import View
from ..models.account import UserProgress
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models.account import Report, InfractionEvent

from ..models import URLPath
from .. import models
from datetime import datetime

class SubmitReportView(View):
    def post(self, request, *args, **kwargs):
        revision_id = request.POST.get('revision_id')
        revision_num = request.POST.get('revision_number')
        revision_type = request.POST.get('report_type')
        curr_page = request.POST.get('curr_page')[:-9]
        article_id = request.POST.get('article_id')
        date = datetime.now().replace(microsecond=0)
        
        if not Report.objects.filter(revision_id = revision_id, article_id = article_id).exists():
            report = Report.objects.create(
                revision_id = revision_id,
                revision_num = revision_num,
                article_id=article_id,
                report_type=revision_type,
                current_page=curr_page,
                date=date
            )

        return JsonResponse({
            "message": "Success"
        }, status=200)
    
class ApproveReportView(View):
    def post(self, request, *args, **kwargs):
        user = request.POST.get('user')
        wiki = request.POST.get('article')
        approval = request.POST.get('approval')

        if approval == 'Infraction':
            pass
            # infraction = InfractionEvent.objects.create(
            #     privilege = "Editing",
            #     article_title = wiki,
            #     admin_user = user,
            #     article_history_link = wiki + "/_history/"
            # )

        report = Report.objects.get(
            revision_id = request.POST.get('revision_id'),
            article_id=request.POST.get('article_id'),
        )
        report.delete()
        return JsonResponse({
            "message": "Success"
        }, status=200)