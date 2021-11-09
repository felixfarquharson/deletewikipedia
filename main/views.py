import json
import re
import urllib

from django.contrib.auth.models import User
from django.db.models import Count
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import ListView

from deletewikipedia import settings
from main.models import DeletedArticle, DeletedSentence, Article

def _get_context():
    context = {}

    context["top_article_deleters"] = User.objects.annotate(num_articles=Count("deletedarticle")
                                                                ).order_by("num_articles")[:4]
    context["top_sentence_deleters"] = User.objects.annotate(num_sentences=Count("deletedsentence")
                                                                ).order_by("num_sentences")[:4]
    context["recently_deleted_sentences"] = DeletedSentence.objects.order_by("-dt")[:4]
    context["recently_deleted_articles"] = DeletedArticle.objects.order_by("-dt")[:4]
    return context


def home(request):
    context=_get_context()
    return render(request, "home.html", context=context)


def about(request):
    context=_get_context()
    return render(request, "about.html", context=context)


def contact(request):
    context=_get_context()
    return render(request, "contact.html", context=context)


def _get_sentences(article_obj, del_sen_list):
    text = article_obj.text.replace("\n", "UjioO087SS")
    split_text = list(re.split("(\.UjioO087SS|\.\W?)", text))
    print(split_text)
    split_text = [split_text[i-1]+split_text[i] for i in range(1, len(split_text), 2) if split_text[i] == ". "
                  or split_text[i] == ".UjioO087SS"]
    print(split_text)
    text_list = [{"id": i, "text": split_text[i], "deleted":False, "newline":False}
                 for i in range(len(split_text))]
    for i in text_list:
        if "UjioO087SS" in i["text"]:
            i["text"]=i["text"][:-10]
            i["newline"]=True
    for i in del_sen_list:
        text_list[i.sentence_number]["deleted"] = True
    return text_list


class NojsSearch(ListView):
    #paginate_by = 10
    template_name = 'nojs_search.html'

    def get_queryset(self):
        query = self.request.GET.get("q", '')
        if query != "":
            return Article.objects.filter(title__contains=query, deletedarticle__isnull=True)[:30]
        else:
            return Article.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(_get_context())
        return context


def nojs_article(request, article_id):
    context=_get_context()
    article_object = get_object_or_404(Article, id=article_id)
    context["title"] = article_object.title
    context["article_id"] = article_object.id
    context["sentences"] = _get_sentences(article_object, DeletedSentence.objects.filter(article=article_object))
    return render(request, "nojs_article.html", context=context)


def nojs_delete_sentence(request, article_id):
    if request.method != "POST":
        return Http404()

    article_object = get_object_or_404(Article, id=article_id)

    recaptcha_response = request.POST.get('g-recaptcha-response')
    url = 'https://www.google.com/recaptcha/api/siteverify'
    values = {
        'secret': settings.RECAPTCHA_PRIVATE_KEY,
        'response': recaptcha_response
    }
    data = urllib.parse.urlencode(values).encode()
    req = urllib.request.Request(url, data=data)
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode())

    if result['success']:
        deleted_sentences = DeletedSentence.objects.filter(article=article_object)
        text_list = _get_sentences(article_object, deleted_sentences)
        keys=[]
        for i in request.POST.keys():
            try:
                keys+=[int(i)]
            except:
                pass
        print(keys)
        if keys:
            top_id = max(keys)
            if top_id>len(text_list):
                messages.error(request, "out of range")
            else:
                for sen_id in keys:
                    if request.POST[str(sen_id)]:
                        if DeletedSentence.objects.filter(article=article_object, sentence_number=sen_id).exists():
                            messages.error(request, "already deleted " + str(sen_id))
                        else:
                            DeletedSentence(article=article_object, sentence_number=sen_id).save()
                            messages.info(request, "deleted " + str(sen_id))
        else:
            messages.error(request, "nothing selected to delete")
    else:
        messages.error(request, 'Invalid reCAPTCHA. Please try again.')

    return redirect("nojs_article", article_object.id)


def nojs_delete_article(request, article_id):
    article_object = get_object_or_404(Article, id=article_id)
    if DeletedArticle.objects.filter(article=article_object).exists():
        messages.error(request, "alredy deleted")
    else:
        DeletedArticle(article=article_object).save()
        messages.info(request, "article deleted")
    return redirect("home")


def article(request):
    return render(request, "home.html", context=context)


def api_changes_since(request, article, time):
    return render(request, "home.html", context=context)


def api_article(request, article):
    return render(request, "home.html", context=context)


def api_delete_sentence(request, article, sentence_number):
    return render(request, "home.html", context=context)


def api_delete_article(request, article):
    return render(request, "home.html", context=context)

