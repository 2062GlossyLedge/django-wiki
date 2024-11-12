from django.urls import re_path
from wiki.core.plugins import registry
from wiki.core.plugins.base import BasePlugin

from . import settings
from . import views


class ProgressPlugin(BasePlugin):
    slug = settings.SLUG
    urlpatterns = {
        "root": [
            re_path(
                r"^$",
                views.UserProgressListView.as_view(),
                name="user_progress",
            ),
        ]
    }

    article_view = views.UserProgressListView().dispatch


registry.register(ProgressPlugin)
