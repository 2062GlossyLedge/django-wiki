from django import forms
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.translation import gettext_lazy as _
from mptt.admin import MPTTModelAdmin

from . import editors
from . import models

from wiki.models.account import (
    UserProfile,
    UserProgress,
    Privilege,
    UserBadge,
    InfractionEvent,
    RecentlyVisitedWikiPages,
    Report,
    DiscussionBoard,
    DiscussionReport,
)


class ArticleObjectAdmin(GenericTabularInline):
    model = models.ArticleForObject
    extra = 1
    max_num = 1
    raw_id_fields = ("article",)


class ArticleRevisionForm(forms.ModelForm):
    class Meta:
        model = models.ArticleRevision
        exclude = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO: This pattern is too weird
        editor = editors.getEditor()
        self.fields["content"].widget = editor.get_admin_widget(self.instance)


class ArticleRevisionAdmin(admin.ModelAdmin):
    form = ArticleRevisionForm
    list_display = ("title", "created", "modified", "user", "ip_address")

    class Media:
        js = editors.getEditorClass().AdminMedia.js
        css = editors.getEditorClass().AdminMedia.css


class ArticleRevisionInline(admin.TabularInline):
    model = models.ArticleRevision
    form = ArticleRevisionForm
    fk_name = "article"
    extra = 1
    fields = (
        "content",
        "title",
        "deleted",
        "locked",
    )

    class Media:
        js = editors.getEditorClass().AdminMedia.js
        css = editors.getEditorClass().AdminMedia.css


class ArticleForm(forms.ModelForm):
    class Meta:
        model = models.Article
        exclude = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            revisions = models.ArticleRevision.objects.select_related("article").filter(
                article=self.instance
            )
            self.fields["current_revision"].queryset = revisions
        else:
            self.fields["current_revision"].queryset = (
                models.ArticleRevision.objects.none()
            )
            self.fields["current_revision"].widget = forms.HiddenInput()


class ArticleAdmin(admin.ModelAdmin):
    inlines = [ArticleRevisionInline]
    form = ArticleForm
    search_fields = ("current_revision__title", "current_revision__content")


class URLPathAdmin(MPTTModelAdmin):
    inlines = [ArticleObjectAdmin]
    list_filter = (
        "site",
        "articles__article__current_revision__deleted",
        "articles__article__created",
        "articles__article__modified",
    )
    list_display = ("__str__", "article", "get_created")
    raw_id_fields = ("article",)

    def get_created(self, instance):
        return instance.article.created

    get_created.short_description = _("created")

    def save_model(self, request, obj, form, change):
        """
        Ensure that there is a generic relation from the article to the URLPath
        """
        obj.save()
        obj.article.add_object_relation(obj)


admin.site.register(models.URLPath, URLPathAdmin)
admin.site.register(models.Article, ArticleAdmin)
admin.site.register(models.ArticleRevision, ArticleRevisionAdmin)
admin.site.register(UserProfile)
admin.site.register(UserProgress)
admin.site.register(Report)
admin.site.register(DiscussionBoard)
admin.site.register(DiscussionReport)


@admin.register(InfractionEvent)
class InfractionEventAdmin(admin.ModelAdmin):
    list_display = ("privilege", "article_title", "date", "admin_user")
    list_filter = ("date", "admin_user")
    search_fields = ("article_title", "privilege__user__username")


admin.site.register(Privilege)
admin.site.register(UserBadge)
admin.site.register(RecentlyVisitedWikiPages)
