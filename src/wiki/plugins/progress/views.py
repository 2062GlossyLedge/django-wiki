from django.shortcuts import render
from wiki.models import Article

def page_selection_popup(request):
    # Fetch all wiki pages
    wiki_pages = Article.objects.all()

    return render(request, 'popup.html', {'wiki_pages': wiki_pages})
