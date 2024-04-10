from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProgressConfig(AppConfig):
    name = "wiki.plugins.progress"
    verbose_name = _("Wiki Progress")
    label = "wiki_progress"
