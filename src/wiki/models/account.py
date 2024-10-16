from django.db import models
from django.contrib.auth.models import User
from django.db.models import JSONField
from collections import deque
from datetime import datetime, timedelta
from django.shortcuts import redirect


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_image = models.ImageField(upload_to="profile_pics/", null=True, blank=True)

    urls = JSONField(default=list, null=True, blank=True)  # Store URLs as JSON

    # show the 4 most recently visited wiki pages
    def save_url(self, url):

        if self.urls is None:
            self.urls = []

        if url in self.urls:
            self.urls.remove(url)

        if url not in self.urls:
            self.urls.insert(0, url)
        self.urls = self.urls[:5]
        self.save()

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
