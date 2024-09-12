from django.db import models
from django.contrib.auth.models import User
from django.db.models import JSONField
from collections import deque


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

    # attempt at using a queue to avoid duplicates
    # def save_url(self, url):

    #     if self.urls is None:
    #         self.urls = []

    # # Create a deque with max length of 4
    # url_queue = deque(self.urls)

    # # If the URL already exists, remove it from the queue
    # if url in url_queue:
    #     url_queue.remove(url)

    # # Insert the new URL at the end
    # url_queue.append(url)

    # # Check if the queue size is bigger than 5
    # if len(url_queue) > 5:
    #     # Remove the oldest URL from the queue
    #     url_queue.popleft()

    # print(url_queue)

    # # Convert the deque back to a list and save
    # self.urls = list(url_queue).reverse()
    # self.save()

    def __str__(self):
        return self.user.username


class UserProgress(models.Model):
    wiki_id = models.CharField(max_length=255)  # String field for wiki_id
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="progresses")  # Foreign key to the User model
    progress = models.CharField(max_length=255)  # String field for progress

    def __str__(self):
        return f"{self.user.username} - {self.wiki_id} - {self.progress}"

