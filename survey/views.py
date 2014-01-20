# Create your views here.
from django.shortcuts import get_object_or_404,render_to_response
from django.template import RequestContext
from django.conf import settings

from survey.models import Item, User, Sites

import uuid

def has_voted(request):
    if ( request.COOKIES.has_key('usercode') ):
        if ( settings.DEBUG and request.GET and request.GET['ignorecookie'] ):
            return False
        return True
    return False

def get_user_from_cookie(request):
    u = User.objects.get(code=request.COOKIES['usercode'])
    return u

def management(request):
    return render_to_response('management.html', {}, context_instance=RequestContext(request))

def contact(request):
    return render_to_response('contact.html', {}, context_instance=RequestContext(request))


def survey(request):
    if ( has_voted(request) ):
        u = get_user_from_cookie(request)

        if u:
            return render_to_response('already_completed.html', {}, context_instance=RequestContext(request))

    vars = {}
    if ( request.GET.has_key('site') ):
        site = request.GET['site']
        vars['site_code'] = site
        vars['site_name'] = Sites.sites[site]

    if ( request.GET.has_key('source') ):
        source = request.GET['source']
        vars['source'] = source

    return render_to_response('survey.html', vars, context_instance=RequestContext(request))

def record(request):
    if ( has_voted(request) ):
        u = get_user_from_cookie(request)
    else:
        u = User(code=uuid.uuid4())
        u.save()

    for v in request.POST:
        if v == 'csrfmiddlewaretoken':
            continue
        #TODO: this is almost certainly not the best way but enough for proof of concept
        val = request.POST.getlist(v)
        if len(val) > 1:
            val = ','.join(val)
        else:
            val = request.POST[v]

        r = Item(user_id=u.id, key=v, value=val, batch=1)
        r.save()

    """
    We don't use django's session handling as we want to save the cookie for a long
    time and we also use the built in session things for actual session data
    """
    one_year = 60 * 60 * 24 * 365

    response = render_to_response('thanks.html', {}, context_instance=RequestContext(request))
    response.set_cookie('usercode', value=u.code, max_age=one_year)

    return response
