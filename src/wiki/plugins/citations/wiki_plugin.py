from django.urls import re_path
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from wiki.core.plugins import registry
from wiki.core.plugins.base import BasePlugin
from wiki.plugins.citations import settings
from wiki.plugins.citations import views
from wiki.plugins.citations.mdx.djangowikilinks import WikiPathExtension
from wiki.plugins.citations.mdx.urlize import makeExtension as urlize_makeExtension


class CitationPlugin(BasePlugin):
    slug = "citations"
    urlpatterns = {
        "article": [
            re_path(
                r"^json/query-urlpath/$",
                views.QueryUrlPath.as_view(),
                name="citations_query_urlpath",
            ),
        ]
    }

    sidebar = {
        "headline": _("Citations"),
        "icon_class": "fa-quote-left",
        "template": "wiki/plugins/citations/sidebar.html",
        "form_class": None,
        "get_form_kwargs": (lambda a: {}),
    }

    wikipath_config = [
        ("base_url", reverse_lazy("wiki:get", kwargs={"path": ""})),
        ("default_level", settings.LOOKUP_LEVEL),
    ]

    markdown_extensions = [
        urlize_makeExtension(),
        WikiPathExtension(wikipath_config),
    ]

registry.register(CitationPlugin)
