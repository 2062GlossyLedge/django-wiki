# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..models.account import UserProgress

@csrf_exempt
def save_progress(request):
    if request.method == 'POST':
        wiki_id = request.POST.get('wiki_id')
        progress = request.POST.get('progress')

        # Ensure the user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User is not authenticated"}, status=403)

        # Get or create the UserProgress object
        user_progress, created = UserProgress.objects.update_or_create(
            user=request.user,
            wiki_id=wiki_id,
            user=user,
            progress=progress
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
