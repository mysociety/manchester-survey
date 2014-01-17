# Create your views here.
from django.shortcuts import get_object_or_404,render_to_response
from django.template import RequestContext
from django.conf import settings

from survey.models import Item, User

import uuid

def has_voted(request):
    if ( request.COOKIES.has_key('usercode') ):
        if ( settings.DEBUG and request.GET and request.GET['ignorecookie'] ):
            return False
        return True
    return False

def survey(request):
    if ( has_voted(request) ):
        u = get_object_or_404(User, code=request.COOKIES['usercode'])

        if u:
            return render_to_response('already_completed.html', {}, context_instance=RequestContext(request))

    if ( request.GET.has_key('site') ):
        request.session['site'] = request.GET['site']

    return render_to_response('survey.html', {}, context_instance=RequestContext(request))

def record(request):
    if ( has_voted(request) ):
        u = get_object_or_404(User, code=request.COOKIES['usercode'])
    else:
        u = User(code=uuid.uuid4())
        u.save()

    site = 'unknown'
    if ( request.session.has_key('site') ):
        site = request.session['site']

    for v in request.POST:
        if v == 'csrfmiddlewaretoken':
            continue
        #TODO: this is almost certainly not the best way but enough for proof of concept
        val = request.POST.getlist(v)
        if len(val) > 1:
            val = ','.join(val)
        else:
            val = request.POST[v]

        r = Item(user_id=u.id, key=v, value=val, site=site, batch=1)
        r.save()

    one_year = 60 * 60 * 24 * 365

    response = render_to_response('thanks.html', {}, context_instance=RequestContext(request))
    response.set_cookie('usercode', value=u.code, max_age=one_year)

    return response
