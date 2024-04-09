from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CitationsConfig(AppConfig):
    name = "wiki.plugins.citations"
    verbose_name = _("Wiki citations")
    label = "wiki_citations"
