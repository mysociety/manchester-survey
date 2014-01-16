from django.db import models

# Create your models here.

class Secret(models.Model):
    secret = models.TextField(null=False)

class User(models.Model):
    code = models.TextField(unique=True, null=False, db_index=True)
    email = models.TextField(unique=True, db_index=True)

class Item(models.Model):
    user = models.ForeignKey(User)
    whenstored = models.DateTimeField(auto_now_add=True)
    batch = models.TextField(db_index=True, null=False)
    site = models.TextField(db_index=True, null=False)
    key = models.TextField(db_index=True, null=False)
    value = models.TextField(db_index=True, null=False)
