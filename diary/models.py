from django.db import models
from survey.models import User

# Create your models here.
class Week(models.Model):
    week = models.IntegerField()
    template = models.TextField(null=True)


class Entries(models.Model):
    user = models.ForeignKey(User)
    week = models.ForeignKey(Week)
    question = models.TextField()
    answer = models.TextField()
