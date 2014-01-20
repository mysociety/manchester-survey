from django.db import models
from survey.models import User

# Create your models here.
class Week(models.Model):
    week = models.IntegerField()

class Question(models.Model):
    for_week = models.ForeignKey(Week)
    question = models.TextField(null=False)
    optional = models.BooleanField(default=True)

class Entries(models.Model):
    user = models.ForeignKey(User)
    question = models.ForeignKey(Question)
    week = models.ForeignKey(Week)
    answer = models.TextField()
