from django.views.generic import TemplateView

from django.shortcuts import redirect, render
from openai import OpenAI
from wiki.views.mixins import ArticleMixin
from wiki.views.article import ArticleRevision


class Chatbot(TemplateView):
    template_name = "wiki/view.html"
    # get url

    # get prompt

    # @method_decorator(get_article(can_read=True))
    # def dispatch(self, request, article, *args, **kwargs):
    #     return super().dispatch(request, article, *args, **kwargs)

    # def get_context_data(self, **kwargs):
    #     kwargs["selected_tab"] = "view"
    #     kwargs["response"] = "Hi"
    #     kwargs["URL"] = ArticleMixin.get_context_data(self, **kwargs)["urlpath"]
    #     return ArticleMixin.get_context_data(self, **kwargs)

    # def get(self, request, *args, **kwargs):
    #     response = "Hi, I'm your friendly chatbot"
    #     context = self.get_context_data(**kwargs)
    #     context["response"] = response
    #     return self.render_to_response(context)

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     print(context)  # Print the context to the console for debugging
    #     return context


#     # pass in url of current wiki page and query. Return chabot response
# get current wiki contents and prompt. Return chatbot response


#     def getResponse(request):
#         response= "Hi, I'm your friendly chatbot"
#         context = {'response': response}
#         return render(request, template_name, context)    # pass response to template
# def responseContext(self):
#     # get prompt
#     if request.method == "POST":
#         prompt = request.POST.get("prompt")
