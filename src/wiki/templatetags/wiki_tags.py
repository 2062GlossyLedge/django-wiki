import json
import re
from urllib.parse import quote as urlquote

from django import template
from django.apps import apps
from django.conf import settings as django_settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model
from django.forms import BaseForm
from django.template.defaultfilters import striptags
from django.utils.safestring import mark_safe
from wiki import models
from wiki.conf import settings
from wiki.core.plugins import registry as plugin_registry

register = template.Library()


# Cache for looking up objects for articles... article_for_object is
# called more than once per page in multiple template blocks.
_cache = {}


@register.simple_tag(takes_context=True)
def article_for_object(context, obj):
    if not isinstance(obj, Model):
        raise TypeError(
            "A Wiki article can only be associated to a Django Model "
            "instance, not %s" % type(obj)
        )

    content_type = ContentType.objects.get_for_model(obj)

    # TODO: This is disabled for now, as it should only fire once per request
    # Maybe store cache in the request object?
    if True or obj not in _cache:
        try:
            article = models.ArticleForObject.objects.get(
                content_type=content_type, object_id=obj.pk
            ).article
        except models.ArticleForObject.DoesNotExist:
            article = None
        _cache[obj] = article
    return _cache[obj]


@register.inclusion_tag("wiki/includes/render.html", takes_context=True)
def wiki_render(context, article, preview_content=None):
    user_progress = context.get('user_progress')  # Access user_progress from the context
    if preview_content:
        content = article.render(preview_content=preview_content)
    elif article.current_revision:
        content = article.get_cached_content(user=context.get("user"), local_progress=user_progress)
    else:
        content = None

    context.update(
        {
            "article": article,
            "content": content,
            "preview": preview_content is not None,
            "user_progress": user_progress, 
            "plugins": plugin_registry.get_plugins(),
            "STATIC_URL": django_settings.STATIC_URL,
            "CACHE_TIMEOUT": settings.CACHE_TIMEOUT,
        }
    )
    return context


@register.inclusion_tag("wiki/includes/form.html", takes_context=True)
def wiki_form(context, form_obj):
    if not isinstance(form_obj, BaseForm):
        raise TypeError(
            "Error including form, it's not a form, it's a %s" % type(form_obj)
        )
    context.update({"form": form_obj})
    return context


@register.inclusion_tag("wiki/includes/messages.html", takes_context=True)
def wiki_messages(context):
    messages = context.get("messages", [])
    for message in messages:
        message.css_class = settings.MESSAGE_TAG_CSS_CLASS[message.level]
    context.update({"messages": messages})
    return context


# XXX html strong tag is hardcoded
@register.filter
def get_content_snippet(content, keyword, max_words=30):
    """
    Takes some text. Removes html tags and newlines from it.
    If keyword in this text - returns a short text snippet
    with keyword wrapped into strong tag and max_words // 2 before and after it.
    If no keyword - return text[:max_words].
    """

    def clean_text(content):
        """
        Removes tags, newlines and spaces from content.
        Return array of words.
        """

        # remove html tags
        content = striptags(content)
        # remove whitespace
        words = content.split()

        return words

    max_words = int(max_words)

    match_position = content.lower().find(keyword.lower())

    if match_position != -1:
        try:
            match_start = content.rindex(" ", 0, match_position) + 1
        except ValueError:
            match_start = 0
        try:
            match_end = content.index(" ", match_position + len(keyword))
        except ValueError:
            match_end = len(content)
        all_before = clean_text(content[:match_start])
        match = content[match_start:match_end]
        all_after = clean_text(content[match_end:])
        before_words = all_before[-max_words // 2 :]
        after_words = all_after[: max_words - len(before_words)]
        before = " ".join(before_words)
        after = " ".join(after_words)
        html = (f"{before} {striptags(match)} {after}").strip()
        kw_p = re.compile(r"(\S*%s\S*)" % re.escape(keyword), re.IGNORECASE)
        html = kw_p.sub(r"<strong>\1</strong>", html)

        return mark_safe(html)

    return " ".join(clean_text(content)[:max_words])


@register.filter
def can_read(obj, user):
    """
    Takes article or related to article model.
    Check if user can read article.
    """
    return obj.can_read(user)


@register.filter
def can_write(obj, user):
    """
    Takes article or related to article model.
    Check if user can write article.
    """
    return obj.can_write(user)


@register.filter
def can_delete(obj, user):
    """
    Takes article or related to article model.
    Check if user can delete article.
    """
    return obj.can_delete(user)


@register.filter
def can_moderate(obj, user):
    """
    Takes article or related to article model.
    Check if user can moderate article.
    """
    return obj.can_moderate(user)


@register.filter
def is_locked(model):
    """
    Check if article is locked.
    """
    return model.current_revision and model.current_revision.locked




@register.simple_tag(takes_context=True)
def login_url(context):
    request = context["request"]
    qs = request.META.get("QUERY_STRING", "")
    if qs:
        qs = urlquote("?" + qs)
    else:
        qs = ""
    return settings.LOGIN_URL + "?next=" + request.path + qs


@register.filter
def plugin_enabled(plugin_name):
    """
    Example: {% if 'wiki.plugins.notifications'|plugin_enabled %}

    :param: plugin_name: String specifying the full name of the plugin, e.g.
                         'wiki.plugins.attachments'
    """
    return apps.is_installed(plugin_name)


@register.filter
def wiki_settings(name):
    return getattr(settings, name, "")


@register.filter
def starts_with(value, arg):
    return value.startswith(arg)

@register.filter(name='progress_process')
def progress_process(value):
    try:
        # Parse the JSON string
        progress_dict = json.loads(value)

        # Extract book and chapter
        book = progress_dict.get('book', '')
        chapter = progress_dict.get('chapter', '')

        # Process book (assuming it might contain a path-like structure)
        book_parts = chapter.split('/')

        book_processed = book_parts[-2].replace('book', 'Book ').replace('season', 'Season ') + ' ' + book_parts[-1].replace('episode', 'Episode ').replace('chapter', 'Chapter ') if len(book_parts) > 1 else book

        # Combine processed book and chapter
        return f"{book_processed}".strip()
    except json.JSONDecodeError:
        # If JSON parsing fails, fall back to the original string processing
        if isinstance(value, str):
            splt = value.split('/')
            return splt[-2] + ' ' + splt[-1] if len(splt) > 1 else value
        return value
    except Exception as e:
        # Handle any other unexpected errors
        return f"Error processing progress: {str(e)}"

@register.filter(name='media_process')
def before_colon(value):
    if isinstance(value, str):
        splt = value.split('/')
        return splt[1].replace('-', ' ') + ' ' + splt[2]
    return value

from wiki.models.account import UserProfile

@register.filter
def profile_picture(request):
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            profile_picture = (
                user_profile.profile_image.url
                if user_profile.profile_image
                else "/path/to/default/profile_image.jpg"
            )
        except UserProfile.DoesNotExist:
            profile_picture = "/path/to/default/profile_image.jpg"
    else:
        profile_picture = None

    return {"profile_picture": profile_picture}
