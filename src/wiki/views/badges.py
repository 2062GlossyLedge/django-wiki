from django.views.generic import TemplateView
from django.shortcuts import render
from wiki.models.account import UserBadge 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from wiki.models.account import UserBadge
from ..models.account import UserProgress
from ..models.account import UserProfile
from ..models.article import ArticleRevision
from ..models.article import Article
from django.utils import timezone
from django.db.models import Q
import re

class Badges(LoginRequiredMixin, TemplateView):
    template_name = "wiki/accounts/badgeDashboard.html"
    context_object_name = "badges"
    model = UserBadge

    def get_queryset(self):
        # Get badges associated with the logged-in user
        return UserBadge.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Define badge types
        badge_types = [
            "Reader",
            "Contributor",
            "Editor",
            "Reviewer",
            "Moderator",
            "Explorer",
            "Survivor",
            "Gourmand",
            "Painter",
            "Guardian",
            "Commenter",
            "Reporter"
        ]

        # Initialize each badge type if not already created for the user
        for badge_type in badge_types:
            UserBadge.objects.get_or_create(
                user=self.request.user,
                badge_id=badge_type,
                defaults={"level": "none", "num_things": 0},
            )
        self.update_badges(self.request.user)
        
        # Update the badges queryset in the context
        context["badges"] = self.get_queryset()

        return context
    
    def update_badges(self, user):
        readerBadge = UserBadge.objects.filter(user=user, badge_id="Reader").first()
        progressCount = UserProgress.objects.filter(user=user).count()
        readerBadge.num_things = progressCount
        if readerBadge.num_things >= 20:
            readerBadge.level = "gold"
        elif readerBadge.num_things >= 5:
            readerBadge.level = "silver"
        elif readerBadge.num_things >= 1:
            readerBadge.level = "normal"
        readerBadge.save()
        
        contributorBadge = UserBadge.objects.filter(user=user, badge_id="Contributor").first()
        articlesCreatedCount = Article.objects.filter(owner=user).count()
        contributorBadge.num_things = articlesCreatedCount
        if contributorBadge.num_things >= 100:
            contributorBadge.level = "gold"
        elif contributorBadge.num_things >= 10:
            contributorBadge.level = "silver"
        elif contributorBadge.num_things >= 5:
            contributorBadge.level = "normal"
        contributorBadge.save()

        editorBadge = UserBadge.objects.filter(user=user, badge_id="Editor").first()
        editCount = ArticleRevision.objects.filter(user=user).count()
        editorBadge.num_things = editCount
        if editorBadge.num_things >= 10:
            editorBadge.level = "gold"
        elif editorBadge.num_things >= 100:
            editorBadge.level = "silver"
        elif editorBadge.num_things >= 1000:
            editorBadge.level = "normal"
        editorBadge.save()
        
        reviewerBadge = UserBadge.objects.filter(user=user, badge_id="Reviewer").first()
        if reviewerBadge.num_things >= 20:
            reviewerBadge.level = "gold"
        elif reviewerBadge.num_things >= 5:
            reviewerBadge.level = "silver"
        elif reviewerBadge.num_things >= 1:
            reviewerBadge.level = "normal"
        reviewerBadge.save()
        
        moderatorBadge = UserBadge.objects.filter(user=user, badge_id="Moderator").first()
        if moderatorBadge.num_things >= 50:
            moderatorBadge.level = "gold"
        elif moderatorBadge.num_things >= 10:
            moderatorBadge.level = "silver"
        elif moderatorBadge.num_things >= 1:
            moderatorBadge.level = "normal"
        moderatorBadge.save()
        
        explorerBadge = UserBadge.objects.filter(user=user, badge_id="Explorer").first()
        wikisCreatedCount = Article.objects.filter(
            owner=user,
            urlpath__slug__in=["book", "tv"]  # Check if 'slug' is either "book" or "tv"
        ).count()
        explorerBadge.num_things = wikisCreatedCount
        if explorerBadge.num_things >= 10:
            explorerBadge.level = "gold"
        elif explorerBadge.num_things >= 5:
            explorerBadge.level = "silver"
        elif explorerBadge.num_things >= 1:
            explorerBadge.level = "normal"
        explorerBadge.save()
        
        survivorBadge = UserBadge.objects.filter(user=user, badge_id="Survivor").first()
        user_profile = UserProfile.objects.get(user=user)
        daysAccountActive = (timezone.now() - user_profile.account_created).days
        survivorBadge.num_things = daysAccountActive
        if survivorBadge.num_things >= 1000:
            survivorBadge.level = "gold"
        elif survivorBadge.num_things >= 365:
            survivorBadge.level = "silver"
        elif survivorBadge.num_things >= 30:
            survivorBadge.level = "normal"
        survivorBadge.save()
        
        gourmandBadge = UserBadge.objects.filter(user=user, badge_id="Gourmand").first()
        furthestBook = UserProgress.objects.filter(user=user).count()
        user_progress_objects = UserProgress.objects.filter(user=user)
        furthestBook = 0
        for progress in user_progress_objects:
            match = re.search(r'Book (\d+)|Season (\d+)', progress.progress)
            if match:
                bookNumber = int(match.group(1) or match.group(2))
                furthestBook = max(furthestBook, bookNumber)
        gourmandBadge.num_things = furthestBook
        if gourmandBadge.num_things >= 20:
            gourmandBadge.level = "gold"
        elif gourmandBadge.num_things >= 5:
            gourmandBadge.level = "silver"
        elif gourmandBadge.num_things >= 1:
            gourmandBadge.level = "normal"
        gourmandBadge.save()
        
        painterBadge = UserBadge.objects.filter(user=user, badge_id="Painter").first()
        if painterBadge.num_things >= 100:
            painterBadge.level = "gold"
        elif painterBadge.num_things >= 20:
            painterBadge.level = "silver"
        elif painterBadge.num_things >= 5:
            painterBadge.level = "normal"
        painterBadge.save()
        
        guardianBadge = UserBadge.objects.filter(user=user, badge_id="Guardian").first()
        if guardianBadge.num_things >= 20:
            guardianBadge.level = "gold"
        elif guardianBadge.num_things >= 5:
            guardianBadge.level = "silver"
        elif guardianBadge.num_things >= 1:
            guardianBadge.level = "normal"
        guardianBadge.save()
        
        # Put commenter here once comment boards are implemented
        
        reporterBadge = UserBadge.objects.filter(user=user, badge_id="Reporter").first()
        if reporterBadge.num_things >= 20:
            reporterBadge.level = "gold"
        elif reporterBadge.num_things >= 5:
            reporterBadge.level = "silver"
        elif reporterBadge.num_things >= 1:
            reporterBadge.level = "normal"
        reporterBadge.save()
        
    
class IncrementBadgeProgressView(View):
    def post(self, request, *args, **kwargs):
        badge_id = request.POST.get('badge_id')
        increment = int(request.POST.get('increment', 1))  

        badge = UserBadge.objects.filter(user=request.user, badge_id=badge_id).first()
        if not badge:
            return JsonResponse({"error": f"Badge with ID '{badge_id}' not found for the user"}, status=404)

        badge.num_things += increment
        
        badge.save()

        return JsonResponse({
            "message": f"Badge '{badge_id}' updated successfully.",
            "badge_id": badge.badge_id,
            "new_num_things": badge.num_things,
            "new_level": badge.level
        }, status=200)