from django.utils.decorators import method_decorator
from django.views.generic import View
from wiki import models
from wiki.core.utils import object_to_json_response
from wiki.decorators import get_article


class QueryUrlPath(View):
    @method_decorator(get_article(can_read=True))
    def dispatch(self, request, article, *args, **kwargs):
        max_num = kwargs.pop("max_num", 100)
        query = request.GET.get("query", None)
        wiki = request.GET.get("wiki", None)
        subwiki = request.GET.get("subwiki", None)

        matches = []
        if query:
            matches = (
                models.URLPath.objects.can_read(request.user)
                .active()
                .filter(
                    article__current_revision__title__contains=query,
                    article__current_revision__deleted=False,
                )
            )
            
            if subwiki:
                subwiki = subwiki.strip('/').split('/')
                fandom, medium, submedium = subwiki
                matches = matches.filter(level__icontains=4)
                matches = matches.filter(parent__slug__icontains=submedium)
                matches = matches.filter(parent__parent__slug__icontains=medium)
                matches = matches.filter(parent__parent__parent__slug__icontains=fandom)
            elif wiki:
                 # Split the wiki path into parts and strip empty strings
                wiki = wiki.strip('/').split('/')
                fandom, medium = wiki
                matches = matches.filter(level__icontains=3)
                matches = matches.filter(parent__parent__slug__icontains=fandom)
                matches = matches.filter(parent__slug__icontains=medium)
                
            matches = matches.select_related_common()
            matches = [
                "{title:s} : wiki:{url:s}".format(
                    title=m.article.current_revision.title,
                    url="/" + m.path.strip("/"),
                )
                for m in matches[:max_num]
            ]

        return object_to_json_response(matches)
