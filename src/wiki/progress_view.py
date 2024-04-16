from django.shortcuts import render
from wiki.models import Article

def select_progress_popup(request, article_id):
    try:
        parent_article = Article.objects.get(id=article_id)
        chapters = parent_article.children.all()
    except Article.DoesNotExist:
        chapters = []

    return render(request, 'select_subarticle_popup.html', {'sub_articles': chapters})
