from django.conf.urls import patterns, url

from diary.views import *

urlpatterns = patterns('',
    url(r'^R/(?P<token>[a-zA-Z0-9]*)/$', 'diary.views.register', name='register'),
    url(r'^D/(?P<token>[a-zA-Z0-9]*)/$', 'diary.views.questions_for_week', name='questions'),
    url(r'^CW/(?P<token>[a-zA-Z0-9]*)/$', 'diary.views.confirm_withdraw', name='confirm_withdraw'),
    url(r'^W/(?P<token>[a-zA-Z0-9]*)/$', 'diary.views.withdraw', name='withdraw'),
    url(r'^record_diary', 'diary.views.record_answers', name='record_answers'),
    url(r'^participant_info', 'diary.views.participant_info', name='participant_info'),
)
