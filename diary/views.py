from datetime import date

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.mail import send_mail
from django.utils import timezone

from manchester_survey.utils import SurveyDate
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
            sd = SurveyDate()
            u.startdate = sd.get_start_date(sd.now())
            u.save()
            send_start_email(u)
            return render_to_response('register_thanks.html', {}, context_instance=RequestContext(request))
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
    sd = SurveyDate(date=SurveyDate.now())
    if not sd.is_diary_day():
        return render_to_response('diary_closed.html', {},  context_instance=RequestContext(request))

    try:
        u = UserManager.get_user_from_token(id, token)
        add_user_to_session(request, u)
    except:
        return render_to_response('invalid_week.html', {}, context_instance=RequestContext(request))

    week_num = sd.get_week_from_startdate(timezone.now(), u.startdate)
    try:
        week = Week.objects.get(week=week_num)
        template = week.template
    except:
        return render_to_response('invalid_week.html', { 'week': week_num }, context_instance=RequestContext(request))

    try:
        entry = Entries.objects.filter(week=week).filter(user_id=u.id)
        if entry.count() > 0:
            return render_to_response('invalid_week.html', {}, context_instance=RequestContext(request))
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

    return render_to_response('question_thanks.html', {}, context_instance=RequestContext(request))

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

def send_start_email(user):
    #TODO: template this
    send_mail('Initial Diary Entry', 'This is link for the diary for the first week', 'from@example.com',
    [user.email])
