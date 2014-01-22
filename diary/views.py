from datetime import date

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.mail import send_mail
from django.utils import timezone

from diary.forms import RegisterForm
from diary.models import Entries, Week
from survey.models import User

def register(request):
    if request.method == 'POST':
        u = User.objects.get(code=request.session['u'])
        if u.startdate:
            return render_to_response('already_registered.html', {}, context_instance=RequestContext(request))

        form = RegisterForm(request.POST)
        if form.is_valid():
            u.name = form.cleaned_data['name']
            u.startdate = timezone.now()
            u.save()
            send_start_email(u)
            return render_to_response('register_thanks.html', {}, context_instance=RequestContext(request))
        else:
            return render_to_response('register.html', { 'form': form }, context_instance=RequestContext(request))
    else:
        try:
            token = request.GET['t']
            u = User.objects.get(token=token)
            request.session['u'] = u.code
        except:
            return render_to_response('invalid_registration.html', {}, context_instance=RequestContext(request))

        if u.startdate:
            return render_to_response('already_registered.html', {}, context_instance=RequestContext(request))

        form = RegisterForm()
        return render_to_response('register.html', { 'form': form }, context_instance=RequestContext(request))

def questions_for_week(request):
    token = request.GET['t']
    u = User.objects.get(token=token)
    request.session['u'] = u.code

    week = u.get_current_week()
    try:
        week = Week.objects.get(week=week)
        template = week.template
    except:
        return render_to_response('invalid_week.html', {}, context_instance=RequestContext(request))

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

    code = request.session['u']
    u = User.objects.get(code=code)

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



def participant_info(request):
    return render_to_response('participant_info.html', {}, context_instance=RequestContext(request))

def send_start_email(user):
    #TODO: template this
    send_mail('Initial Diary Entry', 'This is link for the diary for the first week', 'from@example.com',
    [user.email])
