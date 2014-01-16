from django.conf.urls import patterns, url, include

from survey.views import *

urlpatterns = patterns('',
    url(r'^$', 'survey.views.survey', name='survey'),
)
