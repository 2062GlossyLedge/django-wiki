from django.views.generic import TemplateView

from django.shortcuts import redirect, render
from openai import OpenAI
from wiki.views.mixins import ArticleMixin
from wiki.views.chatbot import Chatbot
from wiki.decorators import get_article
from django.utils.decorators import method_decorator


class Homepage(TemplateView):
    template_name = "wiki/homepage.html"


class AgnosticChatbot(TemplateView):
    template_name = "wiki/includes/agnosticChatbot.html"
    chatbot = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chatbot = Chatbot()

    def dispatch(self, request, *args, **kwargs):

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kwargs["selected_tab"] = "view"
        kwargs["button_state"] = self.request.session.get("button_state", "on")
        kwargs["spoiler_free_button_state"] = self.request.session.get(
            "spoiler_free_button_state", "on"
        )

        kwargs["chat_history"] = self.chatbot.get_chat_history(
            self.request.session.get("urlPath")
        )

        return kwargs

    def post(self, request, *args, **kwargs):
        # breakpoint()
        context = self.get_context_data(**kwargs)
        session = self.request.session.get("urlPath", "") + str(request.user)
        selected_chapter_url = None

        if "selected-chapter-url" in request.POST:
            # selected book url not needed since location picker for book doesn't affect ch picker
            # selected_book_url = request.POST.get("selected-book-url")
            selected_chapter_url = request.POST.get("selected-chapter-url")
            urlPath = selected_chapter_url.split("wiki:")[1]
            self.request.session["chapter_selected"] = True
            self.request.session["urlPath"] = urlPath

        # prompt chatbot
        elif "prompt" in request.POST:

            user_message = request.POST.get("prompt", "")

            # When location is set, handle without llm knowledge. Use custom url
            if request.session.get(
                "spoiler_free_button_state", "on"
            ) == "on" and self.request.session.get("chapter_selected", False):
                print("yo")
                self.chatbot.handle_message_given_location(
                    user_message,
                    self.request.session.get("urlPath", ""),
                    session,
                )
            # When location isn't set or choose don't filter by location, prompt with llm knowledge and without a url

            # check if spoiler free button is toggled, if so, use the chatbot without LLM knowledge
            elif request.session.get("spoiler_free_button_state", "off") == "off":
                self.chatbot.handle_message_given_no_location(
                    user_message,
                    self.request.session.get("urlPath", ""),
                    session,
                )

        # toggle chatbot view
        elif "chatbot-view-button" in request.POST:
            current_state = self.request.session.get("button_state", "off")
            new_state = "on" if current_state == "off" else "off"
            self.request.session["button_state"] = new_state  # Update the session state
            context["button_state"] = new_state

        elif "spoiler-free-button" in request.POST:
            current_state = self.request.session.get("spoiler_free_button_state", "off")
            new_state = "on" if current_state == "off" else "off"
            # only allow personality to be default if spoiler free is on
            if new_state == "on":
                self.request.session["personality"] = "default"
            self.request.session["spoiler_free_button_state"] = new_state
            context["spoiler_free_button_state"] = new_state

        elif "dropdown-button" in request.POST:
            current_state = self.request.session.get("dropdown_button_state", "off")
            new_state = "on" if current_state == "off" else "off"
            self.request.session["dropdown_button_state"] = new_state
            context["dropdown_button_state"] = new_state

        elif "user-selected-personality" in request.POST:
            user_selected_personality = request.POST.get(
                "user-selected-personality", "default"
            )
            self.request.session["personality"] = user_selected_personality

        elif "default-personality" in request.POST:
            self.request.session["personality"] = "default"

        elif "delete-chat-history" in request.POST:
            self.chatbot.delete_chat_history(session)

        # elif "chatbot-chooses-personality" in request.POST:
        #     context["personality"] = "chatbot-chooses"
        context["personality"] = self.request.session.get("personality", "default")
        context["dropdown_button_state"] = self.request.session.get(
            "dropdown_button_state", "off"
        )
        context["button_state"] = self.request.session.get("button_state", "on")
        context["spoiler_free_button_state"] = self.request.session.get(
            "spoiler_free_button_state", "on"
        )

        # update chat history
        context["chat_history"] = self.chatbot.get_chat_history(session)
        return self.render_to_response(context)
