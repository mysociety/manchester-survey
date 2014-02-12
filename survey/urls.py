from django.conf.urls import patterns, url, include

from survey.views import *

urlpatterns = patterns('',
    url(r'^about', 'survey.views.about', name='about'),
    url(r'^management', 'survey.views.management', name='management'),
    url(r'^contact', 'survey.views.contact', name='contact'),
    url(r'^S/(?P<site>[a-z]{,4})/(?P<source>[a-z])/$', 'survey.views.survey', name='survey'),
    url(r'^record$', 'survey.views.record', name='record'),
    url(r'^export$', 'survey.views.export', name='export'),
)
