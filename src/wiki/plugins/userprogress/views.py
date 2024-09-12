from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from ...models.account import UserProgress

class UserProgressListView(LoginRequiredMixin, ListView):
    model = UserProgress
    template_name = 'wiki/plugins/userprogress/settings.html'
    context_object_name = 'progress_list'

    def get_queryset(self):
        return UserProgress.objects.filter(user=self.request.user)
