# Create your views here.
from django.http import Http404
from django.shortcuts import get_object_or_404,render_to_response
from django.template import RequestContext
from django.conf import settings

from survey.models import Item, User, Sites
from survey.forms import SurveyForm

def has_voted(request):
    if ( request.COOKIES.has_key('surveydone') ):
        if ( settings.DEBUG and request.GET and request.GET['ignorecookie'] ):
            return False
        return True
    return False

def about(request):
    return render_to_response('about.html', {}, context_instance=RequestContext(request))

def management(request):
    return render_to_response('management.html', {}, context_instance=RequestContext(request))

def contact(request):
    return render_to_response('contact.html', {}, context_instance=RequestContext(request))


def survey(request, site, source):
    if ( has_voted(request) ):
        return render_to_response('already_completed.html', {}, context_instance=RequestContext(request))

    vars = {}
    vars['site_code'] = site
    try:
        vars['site_name'] = Sites.sites[site]
    except:
        raise Http404

    vars['source'] = source

    return render_to_response('survey.html', vars, context_instance=RequestContext(request))

def record(request):
    if ( has_voted(request) ):
        return render_to_response('already_completed.html', {}, context_instance=RequestContext(request))
    else:
        u = User()
        u.save()


    f = SurveyForm(request.POST)
    if f.is_valid():
        for v in f.cleaned_data:
            if v == 'email':
                continue
            val = f.cleaned_data[v]

            r = Item(user_id=u.id, key=v, value=val, batch=1)
            r.save()

        if f.cleaned_data.has_key('email'):
            u.email = f.cleaned_data['email']
            u.save()
    else:
        return render_to_response('survey.html', { 'form': f }, context_instance=RequestContext(request))


    """
    We don't use django's session handling as we want to save the cookie for a long
    time and we also use the built in session things for actual session data
    """
    one_year = 60 * 60 * 24 * 365

    response = render_to_response('thanks.html', {}, context_instance=RequestContext(request))
    response.set_cookie('surveydone', 1, max_age=one_year)

    return response
