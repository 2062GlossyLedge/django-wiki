from django.urls import re_path
from wiki.core.plugins import registry
from wiki.core.plugins.base import BasePlugin

from . import settings
from . import views


# class NotifyPlugin(BasePlugin):
#     slug = settings.SLUG
#     urlpatterns = {
#         "root": [
#             re_path(
#                 r"^$",
#                 views.UserProgress.as_view(),
#                 name="user_progress",
#             ),
#         ]
#     }

#     article_view = views.UserProgress().dispatch

#     settings_form = "wiki.plugins.userprogress.forms.SubscriptionForm"


# registry.register(NotifyPlugin)
