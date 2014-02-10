# Create your views here.
from collections import defaultdict
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404,render_to_response
from django.template import RequestContext
from django.conf import settings

from survey.models import Item, User, Sites
from survey.forms import SurveyForm
from manchester_survey.utils import UnicodeWriter, SurveyDate

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

        r = Item(user_id=u.id, key='recorded', value=SurveyDate.now(), batch=1)
        r.save();
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

@permission_required('survey.can_export')
def export(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="survey.csv"'

    writer = UnicodeWriter(response)

    all_fields = [
        'id', 'recorded', 'permission', '1', 'a1other', '1', '2', '3', '4', '5', '6',
        '7government', '7council', '7', '8', '9petition', '9march', '9refused', '9bought',
        '9', '10community', '10country', '10', '11community', '11country', '11',
        '12community', '12country', '12', '13', '14', '14how', '15', '15how', '16party',
        '16union', '16local', '16ngo', '16religious', '16hobby', '16health', '16other',
        '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28',
        'twitter_name', 'email', 'site', 'source',
    ]

    writer.writerow(all_fields)

    users = User.objects.all()
    for user in users:
        items = Item.objects.filter(user_id=user.id)
        values = defaultdict(str)
        for item in items:
            values[item.key] = item.value

        values['id'] = user.id
        if user.email:
            values['email'] = user.email

        all_values = [ values[field] for field in all_fields ]
        writer.writerow(all_values)

    return response
