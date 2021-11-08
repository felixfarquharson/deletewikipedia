from django.contrib.auth.models import User
from django.db import models
from django.db.models.functions import Lower


class Article(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.TextField(blank=True, null=True, db_index=True)
    text = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'article'
        indexes = [
            models.Index(Lower('title'), name='lower_title_idx')
        ]

    def __str__(self):
        return self.title

class DeletedSentence(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    sentence_number = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    dt = models.DateTimeField(auto_now_add=True)

class DeletedArticle(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    dt = models.DateTimeField(auto_now_add=True)