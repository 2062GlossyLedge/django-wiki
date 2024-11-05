from django.views.generic import TemplateView
from django.shortcuts import render
from wiki.models.account import UserBadge 
from django.contrib.auth.mixins import LoginRequiredMixin

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

        # Update the badges queryset in the context
        context["badges"] = self.get_queryset()

        return context