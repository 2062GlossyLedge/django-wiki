from django.http import JsonResponse
from django.views import View
from ..models.account import UserProgress
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models.article import Report

from ..models import URLPath
from .. import models
from datetime import datetime

class SubmitReportView(View):
    def post(self, request, *args, **kwargs):
        revision_id = request.POST.get('revision_id')
        revision_num = request.POST.get('revision_number')
        revision_type = request.POST.get('revision_type')
        curr_page = request.POST.get('curr_page')[:-9]
        article_id = request.POST.get('article_id')
        date = datetime.now().replace(microsecond=0)

        # Create a new report instance and save it
        report = Report.objects.create(
            revision_id=revision_id,
            revision_num = revision_num,
            article=article_id,
            report_type=revision_type,
            current_page=curr_page,
            date=date
        )

        return JsonResponse({
            "message": "Success"
        }, status=200)