from django.conf.urls import patterns, url

from diary.views import *

urlpatterns = patterns('',
    url(r'^register', 'diary.views.register', name='register'),
)
