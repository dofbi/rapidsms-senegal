from django.contrib.auth.decorators import login_required
from rapidsms.webui.utils import render_to_response
from rapidsms.webui.utils import paginated
from smsforum.models import Village
from contacts.models import Contact
from tostan.reports import ContactReport
from tostan.reports import MembershipReport
from tostan.reports import IncomingMessageReport
from tostan.reports import OutgoingMessageReport

@login_required
def export(request, template="tostan/export.html"):
    context = {}
    context['villages'] = Village.objects.all()
    return render_to_response(request, template, context)

def export_contacts(request, village_pk=None):
    c = ContactReport()
    if village_pk is not None:
        v = Village.objects.get(pk=village_pk)
        c.queryset = v.flatten(klass=Contact)
        c.header_rows["Title"] +=\
                 " from %(village)s"%{"village":v.name}
    if not request.user.has_perm('contacts.can_view'):
        c.fields = ['node_ptr', 'messages.sent', 'messages.received', 
                    'first_seen', 'locale']
    return c.get_csv_response(request)

def export_membership(request, village_pk=None):
    c = MembershipReport()
    if village_pk is not None:
        v = Village.objects.get(pk=village_pk)
        c.queryset = c.queryset.filter(village=v)
        c.header_rows["Title"] +=\
                 " from %(village)s"%{"village":v.name}
    if not request.user.has_perm('contacts.can_view'):
        c.fields = ['id','date','action']
    return c.get_csv_response(request)

def export_incoming_messages(request, village_pk=None):
    c = IncomingMessageReport()
    if village_pk is not None:
        v = Village.objects.get(pk=village_pk)
        c.queryset = c.queryset.filter(domains=v)
        c.header_rows["Title"] +=\
                 " from %(village)s"%{"village":v.name} 
    if not request.user.has_perm('contacts.can_view'):
        c.fields = ['id','text','date']
    return c.get_csv_response(request)

def export_outgoing_messages(request, village_pk=None):
    c = OutgoingMessageReport()
    if village_pk is not None:
        v = Village.objects.get(pk=village_pk)
        c.header_rows["Title"] +=\
                 " from %(village)s"%{"village":v.name}
        c.queryset = c.queryset.filter(domains=v)
    if not request.user.has_perm('contacts.can_view'):
        c.fields = ['id','text','date']
    return c.get_csv_response(request)
