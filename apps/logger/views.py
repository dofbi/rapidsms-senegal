from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from rapidsms.webui.utils import render_to_response
from rapidsms.webui.utils import paginated
from utilities.export import export
from models import *

@login_required
def index(req, template_name="logger/index.html"):
    incoming = IncomingMessage.objects.order_by('received')
    outgoing = OutgoingMessage.objects.order_by('sent')
    all = []
    [ all.append(msg) for msg in incoming ]
    [ all.append(msg) for msg in outgoing]
    # sort by date, descending
    all.sort(lambda x, y: cmp(y.date, x.date))
    context = {}
    context['messages'] = paginated(req, all, per_page=50)
    return render_to_response(req, template_name, context )

@login_required
def csv_in(request, format='csv'):
    context = {}
    # HACK: creates a dependency on contacts
    # TODO - add a check for contacts app activated and fix
    if request.user.has_perm('contacts.can_view'):
    #if request.user.is_authenticated():
        return export(IncomingMessage.objects.all())
    return export(IncomingMessage.objects.all(), ['id','text','backend','domains','received'])
    
@login_required
def csv_out(request, format='csv'):
    context = {}
    # HACK: creates a dependency on contacts
    # TODO - add a check for contacts app activated and fix
    if request.user.has_perm('contacts.can_view'):
    #if request.user.is_authenticated():
        return export(OutgoingMessage.objects.all())    
    return export(OutgoingMessage.objects.all(), ['id','text','backend','domains','sent'])
