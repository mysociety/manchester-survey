# Create your views here.
from collections import defaultdict
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404,render_to_response
from django.template import RequestContext
from django.conf import settings
from django.db import IntegrityError, transaction

from survey.models import Item, User, UserManager, Sites
from survey.forms import SurveyForm, Survey2Form
from manchester_survey.utils import UnicodeWriter, SurveyDate

def has_voted(request, survey_num=1):
    cookie_name = 'surveydone'
    if ( survey_num == 2 ):
        cookie_name = 'surveydone2'

    if ( request.COOKIES.has_key(cookie_name) ):
        if ( settings.DEBUG and request.GET and request.GET['ignorecookie'] ):
            return False
        return True
    return False

def get_user_from_session(request):
    u = User.objects.get(id=request.session['u'])
    return u

def add_user_to_session(request, user):
    request.session['u'] = user.id

def about(request):
    return render_to_response('about.html', {}, context_instance=RequestContext(request))

def management(request):
    return render_to_response('management.html', {}, context_instance=RequestContext(request))

def contact(request):
    return render_to_response('contact.html', {}, context_instance=RequestContext(request))

def closed(request):
    return render_to_response('closed.html', {}, context_instance=RequestContext(request))

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
    if ( has_voted(request, 1) ):
        return render_to_response('already_completed.html', {}, context_instance=RequestContext(request))

    f = SurveyForm(request.POST)
    if f.is_valid():
        u = None
        if f.cleaned_data.has_key('email'):
            u = User()
            u.email = f.cleaned_data['email']
            try:
                """ depressingly this is here to stop the tests expoloding """
                with transaction.atomic():
                    u.save()
            except IntegrityError:
                u.email = None
                u.save()
        else:
            u = User()
            u.save()

        for v in f.cleaned_data:
            if v == 'email':
                continue
            val = f.cleaned_data[v]

            r = Item(user_id=u.id, key=v, value=val, batch=1)
            r.save()

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

def survey2(request, id, token):
    if ( has_voted(request, 2) ):
        return render_to_response('already_completed.html', {}, context_instance=RequestContext(request))

    try:
        u = UserManager.get_user_from_token(id, token)
        add_user_to_session(request, u)
    except:
        return render_to_response('invalid_link.html', {}, context_instance=RequestContext(request))

    return render_to_response('survey2.html', {}, context_instance=RequestContext(request))

def record2(request):
    if ( has_voted(request, 2) ):
        return render_to_response('already_completed.html', {}, context_instance=RequestContext(request))

    u=get_user_from_session(request)

    f = Survey2Form(request.POST)
    if f.is_valid():
        for v in f.cleaned_data:
            val = f.cleaned_data[v]

            r = Item(user_id=u.id, key=v, value=val, batch=2)
            r.save()

        r = Item(user_id=u.id, key='recorded', value=SurveyDate.now(), batch=2)
        r.save();

    else:
        return render_to_response('survey.html', { 'form': f }, context_instance=RequestContext(request))

    """
    We don't use django's session handling as we want to save the cookie for a long
    time and we also use the built in session things for actual session data
    """
    one_year = 60 * 60 * 24 * 365

    response = render_to_response('thanks.html', {}, context_instance=RequestContext(request))
    response.set_cookie('surveydone2', 1, max_age=one_year)

    return response

@permission_required('survey.can_export')
def export(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="survey.csv"'

    writer = UnicodeWriter(response)

    """
    these are field where the values are stored as a comma seperated list and we want
    to export on column per value with a 1 for selected and a 0 for not. hence we combine
    the list in the field of selected values with the list in all_fields
    """
    checkboxes = ['15', '16', '17', '28']

    """
    because most of the fields are optional and we need to produce a consistent list for each
    row we need to have a list of all fields for output
    """
    all_fields = [
        'id', 'recorded', 'permission', '1', '2', '3', '4', '5', '6', '7', '8government', '8council', '9', '10petition', '10march', '10refused', '10bought',
        '9', '10', '11community', '11country', '11', '12community', '12country', '12', '13community', '13country', '13', '14',
        '15browsed', '15registered', '15joined', '15attended', '15promote', '15other', "15 don't know", '15how',
        '16browsed', '16registered', '16joined', '16attended', '16promote', '16other', "16 don't know", '16how',
        'party_information', 'party_joined', 'party_attended', 'party_voluntary', 'union_information', 'union_joined',
        'union_attended', 'union_voluntary', 'local_information', 'local_joined', 'local_attended', 'local_voluntary',
        'ngo_information', 'ngo_joined', 'ngo_attended', 'ngo_voluntary', 'religious_information', 'religious_joined',
        'religious_attended', 'religious_voluntary', 'hobby_information', 'hobby_joined', 'hobby_attended', 'hobby_voluntary',
        'health_information', 'health_joined', 'health_attended', 'health_voluntary', 'other_information', 'other_joined',
        'other_attended', 'other_voluntary', '17none', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27',
        'blog', 'purchase', 'logged on', 'commented', 'multimedia', 'emailed', 'blog comment', '28 none',
        '29', 'email', 'site', 'source',
    ]

    writer.writerow(all_fields)

    users = User.objects.all()
    for user in users:
        items = Item.objects.filter(user_id=user.id)
        values = defaultdict(str)
        for item in items:
            if item.key in checkboxes:
                answers = item.value.split(',')
                for answer in answers:
                    values[answer] = 1
            else:
                values[item.key] = item.value

        values['id'] = user.id
        values['email'] = 0
        if user.email:
            values['email'] = 1


        all_values = [ values[field] for field in all_fields ]
        writer.writerow(all_values)

    return response


@permission_required('survey.can_export')
def export2(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="survey.csv"'

    writer = UnicodeWriter(response)

    """
    these are field where the values are stored as a comma seperated list and we want
    to export on column per value with a 1 for selected and a 0 for not. hence we combine
    the list in the field of selected values with the list in all_fields
    """
    checkboxes = ['1', '2', '15', '16', '17', '22']

    """
    because most of the fields are optional and we need to produce a consistent list for each
    row we need to have a list of all fields for output
    """
    all_fields = [
        'id', 'recorded', '1writetothem', '1fixmystreet', '1whatdotheyknow', '1theyworkforyou', '1dontknow',
        '2browsing', '2street', '2transport', '2foi', '2message', '2alerts', '2representative', '2topic', '2authority',
        '2problem_others', '2info_others', '2other_uses', '2dontknow', '2response', '2resolve', '3', '4', '5', '6', '7', '8government',
        '8council', '8', '9', '10petition', '10march', '10refused', '10bought', '10',
        '11community', '11country', '11', '12community', '12country', '12', '13community', '13country', '13', '14',
        '15browsed', '15registered', '15joined', '15attended', '15promote', '15other', "15 don't know", '15how',
        '16browsed', '16registered', '16joined', '16attended', '16promote', '16other', "16 don't know", '16how',
        'party_information', 'party_joined', 'party_attended', 'party_voluntary', 'union_information', 'union_joined',
        'union_attended', 'union_voluntary', 'local_information', 'local_joined', 'local_attended', 'local_voluntary',
        'ngo_information', 'ngo_joined', 'ngo_attended', 'ngo_voluntary', 'religious_information', 'religious_joined',
        'religious_attended', 'religious_voluntary', 'hobby_information', 'hobby_joined', 'hobby_attended', 'hobby_voluntary',
        'health_information', 'health_joined', 'health_attended', 'health_voluntary', 'other_information', 'other_joined',
        'other_attended', 'other_voluntary', '17none', '18', '19', '20', '21',
        'blog', 'purchase', 'logged on', 'commented', 'multimedia', 'emailed', 'blog comment', '22 none',
        '23', '24', '25', '26'
    ]

    writer.writerow(all_fields)

    users = User.objects.all()
    for user in users:
        items = Item.objects.filter(user_id=user.id,batch=2)
        values = defaultdict(str)
        for item in items:
            if item.key in checkboxes:
                answers = item.value.split(',')
                for answer in answers:
                    values[answer] = 1
            else:
                values[item.key] = item.value

        if values['recorded']:
            values['id'] = user.id

            all_values = [ values[field] for field in all_fields ]
            writer.writerow(all_values)

    return response
