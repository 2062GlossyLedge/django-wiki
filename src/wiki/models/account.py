from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_image = models.ImageField(upload_to="profile_pics/", null=True, blank=True)

    def __str__(self):
        return self.user.username


class UserProgress(models.Model):
    wiki_id = models.CharField(max_length=255)  # String field for wiki_id
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="progresses")  # Foreign key to the User model
    progress = models.CharField(max_length=255)  # String field for progress

    def __str__(self):
        return f"{self.user.username} - {self.wiki_id} - {self.progress}"

