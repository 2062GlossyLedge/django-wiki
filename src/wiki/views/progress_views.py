from django.http import JsonResponse
from django.views import View
from ..models.account import UserProgress
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models import URLPath

class SaveUserProgressView(View):
    def post(self, request, *args, **kwargs):
        # Extract wiki_id and progress from the POST request
        wiki_id = request.POST.get('wiki_id')
        progress = request.POST.get('progress')
        curr_page = request.POST.get('curr_page')

        # Ensure the user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User is not authenticated"}, status=403)

        # Get or create the UserProgress object
        user_progress, created = UserProgress.objects.update_or_create(
            user=request.user,
            wiki_id=wiki_id,
            defaults={'progress': progress}
        )
        reformatedPage = curr_page.strip().strip('/')
        splitIntoSlugs = reformatedPage.split('/')
        numSlugs = len(splitIntoSlugs)
        
        filter_args = {
            'slug': splitIntoSlugs[-1],
            'level': numSlugs,
        }
        for i in range(2, numSlugs + 1):  
            filter_args[f'parent{"__parent" * (i - 2)}__slug'] = splitIntoSlugs[-i]
        curPageUrlPath = URLPath.objects.get(**filter_args)
        curPageUrlPath.article.clear_cache()
        
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

class UserProgressView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        wiki_id = request.GET.get('wiki_id', None)
        if wiki_id:
            try:
                progress = UserProgress.objects.get(user=request.user, wiki_id=wiki_id)
                return JsonResponse({'progress': progress.progress, 'wiki': progress.wiki_id}, status=200)
            except UserProgress.DoesNotExist:
                # Return a specific response when no progress is found
                return JsonResponse({'progress': None, 'wiki': wiki_id}, status=200)
        return JsonResponse({'error': 'wiki_id not provided'}, status=400)

class ResetCacheView(View):
    def post(self, request, *args, **kwargs):
        # Extract wiki_id and progress from the POST request
        wiki_id = request.POST.get('wiki_id')

        # Directly get page
        
        reformatedId = wiki_id.strip().strip('/')
        splitIntoSlugs = reformatedId.split('/')
        numSlugs = len(splitIntoSlugs)
        
        filter_args = {
            'slug': splitIntoSlugs[1],
            'parent__slug': splitIntoSlugs[0],
            'level': numSlugs
        }
        
        baseWikiPath = URLPath.objects.get(**filter_args)
        for descendent in baseWikiPath.article.descendant_objects():
                        descendent.article.clear_cache()
        
        # Respond with appropriate success message
        message = "Cache for " + wiki_id + " cleared."

        return JsonResponse({
            "message": message,
            "user": request.user.username,
            "wiki_id": wiki_id,
        }, status=200)