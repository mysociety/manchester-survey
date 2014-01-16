# Create your views here.
from django.shortcuts import get_object_or_404,render_to_response
from django.template import RequestContext

from survey.models import Item, User

import uuid

def survey(request):
    return render_to_response('survey.html', {}, context_instance=RequestContext(request))

def record(request):
    if ( request.COOKIES.has_key('usercode') ):
        u = get_object_or_404(User, code=request.COOKIES['usercode'])
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

        r = Item(user_id=u.id, key=v, value=val, site='test', batch=1)
        r.save()

    one_year = 60 * 60 * 24 * 365

    response = render_to_response('thanks.html', {}, context_instance=RequestContext(request))
    response.set_cookie('usercode', value=u.code, max_age=one_year)

    return response
