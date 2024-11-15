from django.views.generic import TemplateView
from django.utils.decorators import method_decorator

from django.shortcuts import redirect, render
from openai import OpenAI
from wiki.models.account import UserProfile, Privilege, RecentlyVisitedWikiPages


class Homepage(TemplateView):
    template_name = "wiki/homepage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # show the max 5 most recently visited wiki pages to authenticated users
        if self.request.user.is_authenticated:

            UserProfile.objects.get_or_create(user=self.request.user)

            # get all urls of the user
            urls = (
                RecentlyVisitedWikiPages.objects.filter(user=self.request.user)
                .order_by("-visited_at")
                .values_list("url", flat=True)
            )

            if urls is None:
                urls = []
                context["urls_dict"] = urls

            else:
                # Remove empty paths and duplicate urls masked by having different number of slashes in url
                urls = [url.replace("//", "/") for url in urls if url != "/"]
                context["urls"] = urls

                urls_dict = {url: url.replace("/", " ") for url in urls}
                context["urls_dict"] = urls_dict

        return context


class HelpPage(TemplateView):
    template_name = "wiki/help.html"