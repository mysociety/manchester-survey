from django.conf.urls import patterns, url, include

from survey.views import *

urlpatterns = patterns('',
    url(r'^management', 'survey.views.management', name='management'),
    url(r'^$', 'survey.views.survey', name='survey'),
    url(r'^record$', 'survey.views.record', name='record'),
)
