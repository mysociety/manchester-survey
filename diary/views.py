import random
from datetime import date
from collections import defaultdict

from django.contrib.auth.decorators import permission_required
from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext, loader, Context, Template
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from django.contrib import sites

from manchester_survey.utils import SurveyDate, int_to_base32, UnicodeWriter
from diary.forms import RegisterForm
from diary.models import Entries, Week
from survey.models import User, UserManager

def get_user_from_session(request):
    u = User.objects.get(id=request.session['u'])
    return u

def add_user_to_session(request, user):
    request.session['u'] = user.id

def register(request, id, token):
    if request.method == 'POST':
        u = get_user_from_session(request)
        if u.startdate:
            return render_to_response('already_registered.html', {}, context_instance=RequestContext(request))

        form = RegisterForm(request.POST)
        if form.is_valid():
            u.name = form.cleaned_data['name']
            sd = SurveyDate(date=SurveyDate.now())
            u.startdate = sd.get_start_date(sd.now())
            u.save()
            is_diary_day = sd.is_diary_day()
            send_start_email(u, is_diary_day)
            return render_to_response('register_thanks.html', { 'is_diary_day': is_diary_day }, context_instance=RequestContext(request))
        else:
            return render_to_response('register.html', { 'form': form, 'id': id, 'token': token }, context_instance=RequestContext(request))
    else:
        try:
            u = UserManager.get_user_from_token(id, token)
            if not u:
                return render_to_response('invalid_registration.html', {}, context_instance=RequestContext(request))
            add_user_to_session(request, u)
        except:
            return render_to_response('invalid_registration.html', {}, context_instance=RequestContext(request))

        if u.startdate:
            return render_to_response('already_registered.html', {}, context_instance=RequestContext(request))

        form = RegisterForm()
        return render_to_response('register.html', { 'form': form, 'id': id, 'token': token }, context_instance=RequestContext(request))

def questions_for_week(request, id, token):
    week_num = week_override = 0
    sd = SurveyDate(date=SurveyDate.now())
    if settings.DEBUG and request.GET and request.GET['week']:
        week_num = week_override = request.GET['week']
    else:
        if not sd.is_diary_day():
            return render_to_response('diary_closed.html', {},  context_instance=RequestContext(request))

    try:
        u = UserManager.get_user_from_token(id, token)
        add_user_to_session(request, u)
    except:
        return render_to_response('invalid_week.html', {}, context_instance=RequestContext(request))

    if not week_override:
        week_num = sd.get_week_from_startdate(SurveyDate.now(), u.startdate)

    try:
        week = Week.objects.get(week=week_num)
        template = week.template
    except:
        return render_to_response('invalid_week.html', { 'week': week_num }, context_instance=RequestContext(request))

    try:
        entry = Entries.objects.filter(week=week).filter(user_id=u.id)
        if not week_override and entry.count() > 0:
            return render_to_response('invalid_week.html', { 'already_answered': 1 }, context_instance=RequestContext(request))
    except:
        pass

    return render_to_response(template, { 'week': week }, context_instance=RequestContext(request))

def record_answers(request):
    week_num = request.POST['week']
    week = Week.objects.get(week=week_num)

    u = get_user_from_session(request)

    for v in request.POST:
        if v == 'csrfmiddlewaretoken' or v == 'week':
            continue
        val = request.POST.getlist(v)
        if len(val) > 1:
            val = ','.join(val)
        else:
            val = request.POST[v]

        r = Entries(user_id=u.id, week_id=week.id, question=v, answer=val)
        r.save()

    r = Entries(user_id=u.id, week_id=week.id, question='recorded', answer=SurveyDate.now())
    r.save();

    return render_to_response('question_thanks.html', { 'week': week }, context_instance=RequestContext(request))

def confirm_withdraw(request, id, token):
    try:
        u = UserManager.get_user_from_token(id, token)
    except:
        return render_to_response('invalid_week.html', {}, context_instance=RequestContext(request))

    u.withdraw = True
    u.save()
    return render_to_response('confirm_withdrawl.html', { 'id': id, 'token': token }, context_instance=RequestContext(request))

def withdraw(request, id, token):
    try:
        u = UserManager.get_user_from_token(id, token)
    except:
        return render_to_response('invalid_week.html', {}, context_instance=RequestContext(request))

    u.withdrawn = True
    u.save()
    return render_to_response('withdrawn.html', {}, context_instance=RequestContext(request))



def participant_info(request):
    return render_to_response('participant_info.html', {}, context_instance=RequestContext(request))

def send_start_email(user, is_diary_day):
    subject = 'mySociety Diary: your first entry'
    host = sites.models.Site.objects.get_current()

    template_file = 'email/initial_diary_email.txt'
    if not is_diary_day:
        template_file = 'email/late_diary_email.txt'
        subject = 'mySociety Diary: thank you for registering'
    template = loader.get_template(template_file)

    if user.email == '':
        return
    context = {
            'id': int_to_base32(user.id),
            'token': user.generate_token(random.randint(0,32767)),
            'host': host,
            'contact_email': settings.CONTACT_EMAIL
            }
    content = template.render(Context(context))
    send_mail(subject, content, settings.FROM_EMAIL, [user.email])

"""
we only export the multiple choice fields as the text answers are exported
seperately
"""
@permission_required('survey.can_export')
def export(request, week):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="survey_week%s.csv"' % week

    writer = UnicodeWriter(response)

    checkboxes = [
        'media', 'attention', 'help', 'impact', 'activity'
    ]

    fields_a = [ 'id', 'recorded', 'paper', 'online', 'local', 'tv', 'radion', 'search', 'social', 'blog', 'video', 'internation', 'national', 'local', 'community', 'sport', 'business', 'science', 'entertainment', 'health', 'neighbour', 'improve', 'solve' ]
    fields_b = [ 'id', 'recorded', 'paper', 'online', 'local', 'tv', 'radion', 'search', 'social', 'blog', 'video', 'internation', 'national', 'local', 'community', 'sport', 'business', 'science', 'entertainment', 'health', 'big', 'moderate', 'small', 'none' ]
    fields_d = [ 'id', 'recorded', 'paper', 'online', 'local', 'tv', 'radion', 'search', 'social', 'blog', 'video', 'internation', 'national', 'local', 'community', 'sport', 'business', 'science', 'entertainment', 'health', 'petition', 'protest', 'boycott', 'contact', 'politician', 'voluntary', 'social' ]

    fields_for_weeks = {
        '1': fields_a,
        '2': fields_b,
        '3': fields_a,
        '4': fields_d,
        '5': fields_a,
        '6': fields_b,
        '7': fields_a,
        '8': fields_d,
        '9': fields_a,
        '10': fields_b,
        '11': fields_a,
        '12': fields_d,
    }

    writer.writerow(fields_for_weeks[week])

    users = User.objects.filter(startdate__isnull=False)
    for user in users:
        entries = Entries.objects.filter(user_id=user.id)
        values = defaultdict(str)
        for entry in entries:
            if entry.question in checkboxes:
                answers = entry.answer.split(',')
                for answer in answers:
                    values[answer] = 1
            else:
                values[entry.question] = entry.answer

        values['id'] = user.id

        all_values = [ values[field] for field in fields_for_weeks[week] ]
        writer.writerow(all_values)

    return response
