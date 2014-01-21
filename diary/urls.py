from django.conf.urls import patterns, url

from diary.views import *

urlpatterns = patterns('',
    url(r'^register', 'diary.views.register', name='register'),
    url(r'^questions', 'diary.views.questions_for_week', name='questions'),
    url(r'^participant_info', 'diary.views.participant_info', name='participant_info'),
)
