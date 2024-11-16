from django.db import models
from django.contrib.auth.models import User
from django.db.models import JSONField
from collections import deque
from datetime import datetime, timedelta
from django.shortcuts import redirect
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_image = models.ImageField(upload_to="profile_pics/", null=True, blank=True)
    account_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username


# A user can have multiple recently visited wiki pages
class RecentlyVisitedWikiPages(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recently_visited_wiki_pages"
    )
    url = models.URLField(max_length=255, null=True, blank=True)
    visited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class UserProgress(models.Model):
    wiki_id = models.CharField(max_length=255)  # String field for wiki_id
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="progresses"
    )  # Foreign key to the User model
    progress = models.CharField(max_length=255)  # String field for progress

    def __str__(self):
        return f"{self.user.username} - {self.wiki_id} - {self.progress}"


class Privilege(models.Model):
    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("SUSPENDED", "Suspended"),
    ]

    # one to many relationship with User
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="privileges")
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="ACTIVE")
    penalty_start = models.DateField(null=True, blank=True)

    infractions = models.PositiveIntegerField(default=0)
    total_allowed_infractions = models.PositiveIntegerField(default=3)

    # Override the save method to check if the privilege should be suspended or reactivated
    def save(self, *args, **kwargs):
        if self.status == "ACTIVE":
            # If the number of infractions exceeds the total allowed infractions, suspend the privilege
            if self.infractions >= self.total_allowed_infractions:
                self.status = "SUSPENDED"
                self.penalty_start = datetime.date(datetime.now())
        if self.status == "SUSPENDED":
            if self.penalty_start is not None:
                # If the penalty start date is more than 3 days ago, reactivate the privilege
                if self.penalty_start + timedelta(days=3) < datetime.date(
                    datetime.now()
                ):
                    self.status = "ACTIVE"
                    InfractionEvent.objects.filter(privilege=self).delete()
                    self.infractions = 0
        super().save(*args, **kwargs)

    # Get the timeout length for the privilege
    @property
    def get_timeout_length(self):
        self.save()

        if (
            self.status == "ACTIVE"
            and self.infractions <= self.total_allowed_infractions
        ):
            return None
        if self.penalty_start:
            timeout_length = self.penalty_start + timedelta(days=3)
            return timeout_length
        return None


class UserBadge(models.Model):
    BADGE_LEVELS = [
        ("none", "None"),
        ("normal", "Normal"),
        ("silver", "Silver"),
        ("gold", "Gold"),
    ]

    badge_id = models.CharField(max_length=255)  # Unique identifier for each badge
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="badges"
    )  # Foreign key to the User model
    level = models.CharField(
        max_length=10, choices=BADGE_LEVELS, default="none"
    )  # Overall badge level (None, Normal, Silver, Gold)
    num_things = (
        models.PositiveIntegerField()
    )  # Contribution count for determining level

    def determine_level(self):
        """
        Determines the badge level based on badge_id and contributions.
        The criteria can be customized per badge_id.
        """
        if self.badge_id == "example_badge":
            if self.num_things >= 20:
                self.level = "gold"
            elif self.num_things >= 10:
                self.level = "silver"
            elif self.num_things >= 5:
                self.level = "normal"
            else:
                self.level = "none"
        # Additional badge criteria can be added here for other badge IDs
        self.save()

    def __str__(self):
        return f"{self.user.username} - {self.badge_id} - Level: {self.level} - Contributions: {self.num_things}"


class InfractionEvent(models.Model):
    # one to many relationship with Privilege
    privilege = models.ForeignKey(
        Privilege, on_delete=models.CASCADE, related_name="infraction_events"
    )

    article_title = models.CharField(max_length=200)
    date = models.DateField(auto_now_add=True)
    admin_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="administered_infractions",
    )
    article_history_link = models.URLField(max_length=500)

    def save(self, *args, **kwargs):
        # Increment the infractions count of the associated Privilege
        self.privilege.infractions += 1
        self.privilege.save()
        super().save(*args, **kwargs)


class Report(models.Model):
    revision_id = models.IntegerField()
    article_id = models.IntegerField()
    revision_num = models.IntegerField()
    report_type = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    current_page = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.revision_id} - {self.article_id} - {self.report_type} - {self.current_page}"
