# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..models.account import UserProgress

@csrf_exempt
def save_progress(request):
    if request.method == 'POST':
        wiki_id = request.POST.get('wiki_id')
        progress = request.POST.get('progress')
        user = request.user

        # Handle user authentication and permissions here

        # Save the progress
        # You may need to handle UserProgress creation based on your model
        UserProgress.objects.create(
            wiki_id=wiki_id,
            user=user,
            progress=progress
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
