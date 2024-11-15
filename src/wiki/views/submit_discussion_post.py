from django.http import JsonResponse
from django.views import View
from django.contrib.auth.models import User
from ..models.account import DiscussionBoard

class SubmitDiscussionPost(View):
    def post(self, request, *args, **kwargs):
        article_id = request.POST.get('article_id')
        content = request.POST.get('content')
        userObj = User.objects.get_or_create(username=request.user)
        post = DiscussionBoard.objects.get_or_create(
            user = userObj[0],
            article_id=article_id,
            content = content
        )

        return JsonResponse({
            "message": "Success"
        }, status=200)
    