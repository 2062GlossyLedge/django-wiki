from django.http import JsonResponse
from django.views import View
from ..models.account import UserProgress
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

class SaveUserProgressView(View):
    def post(self, request, *args, **kwargs):
        # Extract wiki_id and progress from the POST request
        wiki_id = request.POST.get('wiki_id')
        progress = request.POST.get('progress')
        print("HELP HELP HELP HELP")
        # Ensure the user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User is not authenticated"}, status=403)

        # Get or create the UserProgress object
        user_progress, created = UserProgress.objects.update_or_create(
            user=request.user,
            wiki_id=wiki_id,
            defaults={'progress': progress}
        )

        # Respond with appropriate success message
        if created:
            message = "Progress successfully created."
        else:
            message = "Progress successfully updated."

        return JsonResponse({
            "message": message,
            "user": request.user.username,
            "wiki_id": wiki_id,
            "progress": user_progress.progress
        }, status=200)
