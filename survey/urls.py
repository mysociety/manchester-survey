from django.conf.urls import patterns, url, include

from survey.views import *

urlpatterns = patterns('',
    url(r'^about', 'survey.views.about', name='about'),
    url(r'^management', 'survey.views.management', name='management'),
    url(r'^contact', 'survey.views.contact', name='contact'),
    url(r'^survey2/(?P<id>[0-9A-Za-z]+)-(?P<token>.+)/$', 'survey.views.survey2', name='survey2'),
    url(r'^[Ss]/.*$', 'survey.views.closed', name='survey'),
    url(r'^record$', 'survey.views.record', name='record'),
    url(r'^record2$', 'survey.views.record2', name='record2'),
    url(r'^export$', 'survey.views.export', name='export'),
)
