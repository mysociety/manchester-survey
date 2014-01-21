from django.conf.urls import patterns, url

from diary.views import *

urlpatterns = patterns('',
    url(r'^register', 'diary.views.register', name='register'),
    url(r'^participant_info', 'diary.views.participant_info', name='participant_info'),
)
