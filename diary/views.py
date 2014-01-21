from django.shortcuts import render_to_response
from django.template import RequestContext

from diary.forms import RegisterForm
from survey.models import User

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            return render_to_response('register_thanks.html', {}, context_instance=RequestContext(request))
        else:
            return render_to_response('register.html', { 'form': form }, context_instance=RequestContext(request))
    else:
        try:
            token = request.GET['t']
            u = User.objects.get(token=token)
        except:
            return render_to_response('invalid_registration.html', {}, context_instance=RequestContext(request))

        form = RegisterForm()
        return render_to_response('register.html', { 'form': form }, context_instance=RequestContext(request))

def participant_info(request):
    return render_to_response('participant_info.html', {}, context_instance=RequestContext(request))
