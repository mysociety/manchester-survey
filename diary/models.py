from django.db import models

# Create your models here.
class Week(models.Model):
    week = models.IntegerField()

class Question(models.Model):
    for_week = models.ForeignKey(Week)
    question = models.TextField(null=False)
    optional = models.BooleanField(default=True)

class User(models.Model):
    usercode = models.TextField(unique=True, null=False, db_index=True)
    email = models.TextField(unique=True, null=False)
    startdate = models.DateTimeField()
    withdrawn = models.BooleanField(default=False)

class Entries(models.Model):
    user = models.ForeignKey(User)
    question = models.ForeignKey(Question)
    week = models.ForeignKey(Week)
    answer = models.TextField()
