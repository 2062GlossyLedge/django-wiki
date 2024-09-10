from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from ..models.account import UserProgress

@csrf_exempt
@login_required
def save_user_progress(request):
    if request.method == 'POST':
        user = request.user
        wiki_id = request.POST.get('wiki_id')
        progress = request.POST.get('progress')

        progress_record, created = UserProgress.objects.update_or_create(
            user=user,
            wiki_id=wiki_id,
            defaults={'progress': progress}
        )

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'}, status=400)
