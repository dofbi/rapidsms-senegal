#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

"""

Note: reporting outgoing messages on a per-village basis is actually quite tricky.

Say you have 2 users, A and B.
Both are members of the same 2 communities, 1 and 2, but only B is a member of
community 3. User A sends a message, which is blasted to the 2 communities he 
shared with B. User B should only receive the message once. (After all, why 
would we send the same user the same message 2 times?) So while User B has only 
received one message, in theory that message was sent 'across' 2 different 
communities. (Which we can record as set of domain_of_message model with a 
foreign key to the specific message instance). The tricky part is that 
nodegraph abstracts away the calculation of who-is-in-which-community and 
discarding-of-duplicate-messages-to-same-person-in-two-communities. 

To support this feature properly in the future, we would need to extend nodegraph
to return not only members_of_village as a list of members, but also
members_of_villages as a list of tuples of (member, village_membership1, 
village_membership2, etc.)

"""

import re, urllib

from django.utils.translation import ugettext as _
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.exceptions import FieldError

from rapidsms.webui.utils import *
from tagging.models import Tag
from smsforum.models import *
from smsforum.utils import *
from smsforum.forms import *
from smsforum.app import CMD_MESSAGE_MATCHER
from contacts.models import Contact
from logger.models import *
# from contacts.models import *
from contacts.forms import GSMContactForm
from contacts.views import edit_contact
from reporters.models import *
from utilities.export import export

from datetime import datetime, timedelta

@login_required
def visualize(request, template="smsforum/visualize.html"):
    context = {}
    villages = Village.objects.all().order_by('name')
    v_filter, r_filter = get_village_and_region(request, context)
    if v_filter is not None:
        villages = [v_filter]
    elif r_filter is not None:
        villages = r_filter.get_children(klass=Village)
    for village in villages:
        # once this site bears more load, we can replace flatten() with village.subnodes
        # and stop reporting num_messages
        members = village.flatten(klass=Contact)
        village.member_count = len( members )
        village.incoming_message_count = IncomingMessage.objects.filter(domains=village).count()
        last_week = ( datetime.now()-timedelta(weeks=1) )
        village.incoming_message_this_week_count = IncomingMessage.objects.filter(domains=village,received__gte=last_week).count()
        # reporting outgoing messages is actually quite tricky. see top of this file.
        village.outgoing_message_count = get_outgoing_message_count_to(members)
    context['villages'] = Village.objects.all().order_by('name')
    context['regions'] = Region.objects.all().order_by('name')
    context['villages_paginated'] = paginated(request, villages)
    context.update( totals(context) )
    return render_to_response(request, template, context)

@login_required
def manage(request, template="smsforum/manage.html"):
    return render_to_response(request, template)

@login_required
def access(request, template="smsforum/manage_access.html"):
    return render_to_response(request, template)

@login_required
def regions(request, template="smsforum/manage_regions.html"):
    context = {}
    # context['orphan_villages'] = Village.objects.filter(_parents=None)
    
    # there's gotta be a better way to do this
    villes = Village.objects.all().order_by('name')
    orphans = []
    for v in villes:
        if v.get_parent_count()==0: 
            orphans.append(v)
    if len(orphans)>0:
        context['orphan_villages'] = orphans
    
    regions = Region.objects.all().order_by('name')
    for region in regions:
        region.villages = region.get_children(klass=Village)
        region.count = len(region.villages)
    context['regions'] = regions
    return render_to_response(request, template, context)

@login_required
def citizens(request, template="smsforum/manage_citizens.html"):
    context = {'contacts': paginated(request, Contact.objects.all().order_by('common_name')),
               'villages': Village.objects.all().order_by('name'), 
               'regions': Region.objects.all().order_by('name')}
    village, region = get_village_and_region(request, context)
    if village is not None:
        context['contacts'] = paginated(request, village.flatten(klass=Contact))
    elif region is not None:
        context['contacts'] = paginated(request, region.flatten(klass=Contact))
    context['edit_link'] = "/member/edit/"
    return render_to_response(request, template, context)

def get_village_and_region(request, context):
    if request.method != "POST":
        return (None, None)
    if 'village' in request.POST and len(request.POST["village"])>0:
        village = Village.objects.get(id=request.POST["village"])
        context['village_filter'] = village
        if 'region' in request.POST and len(request.POST["region"])>0:
            # region, if specified, should match village
            region = Region.objects.get(id=request.POST["region"])
            village_region = village.get_parents(klass=Region)
            if region not in village_region:
                context['error'] = "Village does not match selected region.\n" + \
                                   "Filtering by village '%s'" % village.name
            else:
                context['region_filter'] = region
        return (village, None)
    elif 'region' in request.POST and len(request.POST["region"])>0:
        region = Region.objects.get(id=request.POST["region"])
        context['region_filter'] = region
        return (None, region)
    return (None, None)
    
@login_required
def messages(request, template="smsforum/manage_messages.html"):
    if request.method == 'POST':    
        # now iterate through all the messages you learned about
        for id in request.POST.getlist('message'):
            m = IncomingMessage.objects.get(id=int(id))
            
            # get submitted translation + category
            trans_txt = request.POST['trans_'+str(id)]
            category_txt = request.POST['category_'+str(id)]
            
            # update categories and translation
            # m.tags = category_txt.strip()
            m.update_tag (category_txt)
            m.update_translation(trans_txt)
    if 'next' in request.GET:
        return HttpResponseRedirect(request.GET['next'])
    messages = IncomingMessage.objects.select_related().order_by('-received')
    context = {'villages': Village.objects.all().order_by('name'), 
               'regions': Region.objects.all().order_by('name')}
    (village, region) = get_village_and_region(request, context)
    if village is not None:
        messages = messages.filter(domains=village)
    elif region is not None:
        villages = region.get_children(klass=Village)
        messages = messages.filter(domains__in=villages)
    context = add_categories(context)
    # although we can support arbitrary UIs, the current drop-down ui
    # for tags only shows one tag 'selected' at any given time.
    annotated_messages = []
    for m in messages:
        matcher=CMD_MESSAGE_MATCHER.match(m.text)
        if matcher is None: 
            #if len(m.tags)>0:
            #    m.selected = m.tags[0].name.strip()
            if m.basictags.count()>0:
                m.selected  = m.basictags.all()[0].txt
            if m.annotations.count() > 0:
                m.note = m.annotations.all()[0].text
            annotated_messages.append(m)
    context['messages'] = paginated(request, annotated_messages)
    return render_to_response(request, template, context)

def add_categories(context):
    try:
        root = Tag.objects.get(name='category_root')
        context['categories'] = root.flatten_preorder(klass=Tag)
        for cat in context['categories']:
            cat.name = cat.name.strip().strip('"')
    except Tag.DoesNotExist:
        # fail cleanly in case categories are not yet defined in DB
        pass
    return context
    
def get_outgoing_message_count_to(members):
    """ Return all outgoing messages sent to any of the identities
    associated with a group of contacts
    """
    conns = PersistantConnection.objects.filter(reporter__in=[m.reporter for m in members])
    identities = conns.values_list('identity', flat=True)
    outgoing_message_count = OutgoingMessage.objects.filter(identity__in=identities).count()
    return outgoing_message_count

def format_messages_in_context(request, context, raw_messages):
    messages = []
    for msg in raw_messages:
        msg = annotate_msg(msg)
        messages.append(msg)
    if len(messages)>0:
        context['messages'] = paginated(request, messages, per_page=10, prefix="blast")
    return context

def annotate_msg(msg):
    if hasattr(msg,'messageannotation_set'):
        notes = msg.messageannotation_set.filter(message=msg)
        if len(notes) > 0: 
            msg.note = notes[0].text
    if len(msg.tags)>0:
        msg.selected = msg.tags[0].name.strip()
    if msg.annotations.count() > 0:
        msg.note = msg.annotations.all()[0].text
    return msg

def format_messages_in_context_sorted(request, context, messages):
    cmd_messages = []
    blast_messages = []
    for msg in messages:
        msg = annotate_msg(msg)
        # are we a command?
        m=CMD_MESSAGE_MATCHER.match(msg.text)
        if m is None: blast_messages.append(msg)
        else: cmd_messages.append(msg)
    if len(cmd_messages)>0:
        context['cmd_messages'] = paginated(request, cmd_messages, per_page=5, prefix="cmd")
    if len(blast_messages)>0:
        context['blast_messages'] = paginated(request, blast_messages, per_page=10, prefix="blast")
    return context

# would declare this as a class but we don't need the extra database table
def SetCode(tag, str):
    code = Code.objects.get(slug=str)
    tag.code = code
    return tag

@login_required
def village_history(request, pk, template="smsforum/history.html"):
    context = {}
    village = Village.objects.get(id=pk)
    history = MembershipLog.objects.filter(village=village).select_related('contact')
    context['village'] = village
    context['history'] = paginated(request, history)
    return render_to_response(request, template, context)

@login_required
def members(request, pk, template="smsforum/members.html"):
    context = {}
    village = Village.objects.get(id=pk)
    members = village.flatten(klass=Contact)
    total_incoming_messages = 0
    total_incoming_messages_this_week = 0
    for member in members:
        member = add_message_info(member, village)
        total_incoming_messages = total_incoming_messages + member.message_count
        total_incoming_messages_this_week = total_incoming_messages_this_week + member.message_count_this_week
    context['village'] = village
    context['members'] = paginated(request, members)
    context['member_count'] = len(members)
    context['incoming_message_count'] = total_incoming_messages
    context['incoming_message_count_this_week'] = total_incoming_messages_this_week
    messages = IncomingMessage.objects.filter(domains=village).order_by('-received')
    format_messages_in_context(request, context, messages)
    return render_to_response(request, template, context)

def add_message_info(member, village):
    connections = PersistantConnection.objects.filter(reporter=member.reporter)
    if len(connections) > 0:
        # we can always click on the user to see a list of all their connections
        member.phone_number = connections[0].identity
        last_week = ( datetime.now()-timedelta(weeks=1) )
        member.message_count = IncomingMessage.objects.filter(identity=member.phone_number).count()
        member.message_count_this_week = IncomingMessage.objects.filter(identity=member.phone_number,received__gte=last_week).count()
        member.received_message_count = OutgoingMessage.objects.filter(identity=member.phone_number).count()
    log = MembershipLog.objects.filter(contact=member,village=village).order_by('-id')
    if (log):
        member.date_joined = log[0].date

@login_required
def member(request, pk, template="smsforum/member.html"):
    context = {}
    contact = Contact.objects.get(id=pk)
    if request.method == "POST":
        if request.POST["message_body"]:
            pass
            """
            be = self.router.get_backend(pconn.backend.slug)
            return be.message(pconn.identity, form["text"]).send()
            
            xformmanager = XFormManager()
            xformmanager.remove_schema(form_id)
            logging.debug("Schema %s deleted ", form_id)
            #self.message_user(request, _('The %(name)s "%(obj)s" was deleted successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj_display)})                    
            return HttpResponseRedirect("../register")
            """
    try:
        connections = PersistantConnection.objects.get(reporter=contact.reporter)
        contact.phone_number = connections.identity
        messages = IncomingMessage.objects.filter(identity=contact.phone_number).order_by('-received')
        contact.message_count = len(messages)
        last_week = ( datetime.now()-timedelta(weeks=1) )
        last_month = ( datetime.now()-timedelta(days=30) )
        contact.message_count_this_week = IncomingMessage.objects.filter(identity=contact.phone_number,received__gte=last_week).order_by('-received').count()
        contact.message_count_this_month = IncomingMessage.objects.filter(identity=contact.phone_number,received__gte=last_month).order_by('-received').count()
        contact.received_message_count = OutgoingMessage.objects.filter(identity=contact.phone_number).count()
        # note: this defaults to the first date the member joined any community in the system
        log = MembershipLog.objects.filter(contact=contact).order_by('-id')
        if (log):
            contact.date_joined = log[0].date
        format_messages_in_context(request, context, messages)
    except PersistantConnection.DoesNotExist:
        #this is a contact without a phone number
        pass
    # if you decide to add 'date_joined', remember you need to do it for all villages
    # this person is member of
    context['member'] = contact
    return render_to_response(request, template, context)

@login_required
def community(request, pk, template="smsforum/community.html"):
    context = {}
    village = get_object_or_404(Community, id=pk)
    if request.method == "POST":
        f = VillageForm(request.POST, instance=village)
        if not f.is_valid():
            context['error'] = f.errors
        else:
            village = f.save()
            if village.location is None:
                village.location = Location.objects.get_or_create(name=village.name, code=village.name)[0]
            village.location.latitude = f.cleaned_data['latitude']
            village.location.longitude = f.cleaned_data['longitude']
            village.location.save()
            village.save()
    context['form'] = VillageForm(instance=village)
    context['title'] = _("EDIT VILLAGE")
    context['village'] = village
    # this is so we can reuse the 'totals' partial template 
    # from the 'messages' page
    context['villages'] = paginated(request, [village])
    members = village.flatten(klass=Contact)
    for member in members:
        member = add_message_info(member, village)
    context['members'] = paginated(request, members)
    messages = IncomingMessage.objects.filter(domains=village).order_by('-received')
    format_messages_in_context(request, context, messages)
    add_categories(context)
    return render_to_response(request, template, context)

@login_required
def region(request, pk=None, template="smsforum/community.html", add=False):
    context = {}
    region = (None if pk is None else get_object_or_404(Region, id=pk))
    if request.method == "POST":
        form = RegionForm(request.POST, instance=region)
        context['form'] = form
        if not form.is_valid():
            context['error'] = form.errors
        else:
            # TODO - move this logic to forms.py
            region,created =Region.objects.get_or_create( name=form.cleaned_data['name'] )
            context['status'] = _("Region '%(region_name)s' successfully editted" % \
                                  {'region_name':region.name} )
            if add:
                # this looks rather hackish
                if created:
                    context['status'] = _("Region '%(region_name)s' successfully created" % \
                                          {'region_name':region.name} )
                else:
                    context['status'] = _("Region already exists!")
            if 'communities' in form.cleaned_data and len(form.cleaned_data['communities'])>0:
                region.add_children(*form.cleaned_data['communities'])
            else:
                region.remove_all_children()
            region.save()
    else:
        context['form'] = RegionForm(instance=region)
    if region:
        context['delete_link'] = reverse('delete_region', args=[region.pk])
    context['title'] = (_("Add Region") if pk is None else _("EDIT REGION"))
    context['village'] = region
    context['previous_link'] = reverse('regions')
    return render_to_response(request, template, context)

@login_required
def add_region(request, template="smsforum/add.html"):
    return region(request, template=template, add=True)

@login_required
def delete_region(request, pk, template="smsforum/confirm_delete.html"):
    context = {}
    community = get_object_or_404(Region, id=pk)    
    if request.method == "POST":
        if request.POST["confirm_delete"]:
            community.delete()
            return HttpResponseRedirect(reverse('regions'))
    context['village'] = community
    return render_to_response(request, template, context)

@login_required
def delete_village(request, pk, template="smsforum/confirm_delete.html"):
    context = {}
    village = get_object_or_404(Village, id=pk)    
    if request.method == "POST":
        if request.POST["confirm_delete"]: # The user has already confirmed the deletion.
            #workaround for django bug. 
            #marginally useful, since we don't really want to delete the logs ever.
            logs = MembershipLog.objects.filter(village=village)
            for log in logs:
                log.village = None
                log.save()
            village.delete()
            return HttpResponseRedirect(reverse('regions'))
    context['village'] = village
    return render_to_response(request, template, context)

@login_required
def add_village(request, template="smsforum/add.html"):
    context = {}
    if request.method == 'POST':
        form = VillageForm(request.POST)
        if form.is_valid():
            v,created =Village.objects.get_or_create( name=form.cleaned_data['name'] )
            if created:
                context['status'] = _("Village '%(village_name)s' successfully created" % {'village_name':v.name} )
            else:
                context['status'] = _("Village already exists!")
        else:
                context['status'] = _("Form invalid")
    context['form'] = VillageForm()
    context['title'] = _("Add Village")
    context['previous_link'] = reverse("regions")
    return render_to_response(request, template, context)    

def totals(context):
    context['village_count'] = Village.objects.all().count()
    context['member_count'] = Contact.objects.all().count()
    context['incoming_message_count'] = IncomingMessage.objects.all().count()
    last_week = ( datetime.now()-timedelta(weeks=1) )
    context['incoming_message_count_this_week'] = IncomingMessage.objects.filter(received__gte=last_week).count()
    context['outgoing_message_count'] = OutgoingMessage.objects.all().count()
    return context

def export_village_history(request, pk, format='csv'):
    village = Village.objects.get(id=pk)
    history = MembershipLog.objects.filter(village=village)
    if request.user.has_perm('contacts.can_view'):
        return export(history, ['id','date','contact','action'])
    return export(history, ['id','date','action'])

def export_village_membership(request, pk, format='csv'):
    village = Village.objects.get(id=pk)
    members = village.flatten(klass=Contact)
    if request.user.has_perm('contacts.can_view'):
        return export(members, ['first_seen', 'given_name', 'family_name', 
                                'common_name', 'reporter.alias', 'gender', 
                                'age_months', '_locale'])
    return export(members, ['first_seen', 'gender', 
                            'age_months', '_locale'])

@login_required
def add_member(request, village_id=0, member_id=0, template="contacts/phone_number.html"):
    """ adding a member to a village involves either
    1. creating a new contact and adding that new contact to the village, or
    2. finding an existing contact and adding that contact to this village
    this view deals with both cases, by requiring the web user to specify
    a phone number first, and using the phone number to search for existing matches
    
    """
    context = {}
    context['title'] = _("Add Member")
    if request.method == 'POST':
        if 'phone_number_query' in request.POST:
            # we received a post of the contact's phone number
            phone_number_query = request.POST['phone_number_query'].strip()
            if phone_number_query:
                # try to find a matching contact
                try:
                    cxn = PersistantConnection.objects.get(identity=phone_number_query)
                except PersistantConnection.DoesNotExist:
                    # if nothing matches, create new contact
                    form = GSMContactForm()
                    form.initial = {'phone_number':phone_number_query}
                    template="contacts/add.html"
                    context['form'] = form
                    return render_to_response(request, template, context)
                else:
                    # if contact matches, redirect to that contact's edit page
                    return HttpResponseRedirect("/village/%s/member/add/%s" % \
                                                (village_id, cxn.reporter.profile.id) )
                    # when we move to django 1.1, use the following intead:
                    # redirect(add_member, village_id, cxn.contact.id)
            else:
                context['error'] = "Please enter a phone number for member."
        else:
            # we received a post from the add/edit_member form. save()
            action = ""
            if member_id != 0:
                contact = get_object_or_404( Contact, pk=member_id )
                form = GSMContactForm(request.POST, instance=contact)
                action = "edited"
            else:
                form = GSMContactForm(request.POST)
                action = "created"
            if form.is_valid():
                c = form.save()
                context['status'] = _("Member '%(member_name)s' successfully %(action)s" % \
                                      {'member_name':c.signature, 'action':action} )
                if village_id != 0:
                    village = Village.objects.get(id=village_id)
                    village.add_children( c )
                    context['status']  = context['status'] + _(" and added to village: %s") % village.name
            else:
                context['error'] = form.errors
    if member_id != 0:
        contact = get_object_or_404(Contact, pk=member_id)
        form = GSMContactForm(instance=contact)
        context['form'] = form
        context['title'] = _("Add Member %s to village %s") % (contact.signature,village_id)
        template = "contacts/add.html"
    return render_to_response(request, template, context)

@login_required
def edit_member(request, pk, template="contacts/edit.html"):
    context = {}
    context['previous_link'] = reverse('citizens')
    return edit_contact(request, pk, template="contacts/edit.html", 
                        context=context)

@login_required
def index(request, template="smsforum/index.html"):
    context = {}
    if request.method == 'POST':    
        # now iterate through all the messages you learned about
        for i in request.POST.getlist('message'):
            id = int(i)
            m = IncomingMessage.objects.select_related().get(id=id)
            # GATHER EXISTING TAGS
            tags = MessageTag.objects.select_related().filter(message=m)
            flag = None
            code = None
            for tag in tags:
                if tag.code.set.name == "FLAGGED_CODE":
                    flag = tag 
                elif tag.code.set.name == "TOSTAN_CODE":
                    code = tag
            note = None
            notes = MessageAnnotation.objects.filter(message=m)
            if len(notes) > 0: note = notes[0]
            
            # CHECK FOR SUBMITTED VALUES
            if 'flagged_'+ str(id) in request.POST: flag_bool = True
            else: flag_bool = False
            note_txt = request.POST['text_'+str(id)]
            code_txt = request.POST['code_'+str(id)]
            
            # MAP SUBMITTED VALUES TO NEW DB STATE
            if flag is None:
                if flag_bool == True:
                    flag = MessageTag(message=m)
                    SetFlag(flag)
                    flag.save()
            else:
                if flag_bool == False: flag.delete()
                else:
                    SetFlag(flag)
                    flag.save()
                    
            if code is None:
                if len(code_txt) > 0:
                    code = MessageTag(message=m)
                    code = SetCode(code,code_txt)
                    code.save()
            else:
                if len(code_txt) == 0: code.delete()
                else:
                    SetCode(code,code_txt)
                    code.save() 
                                   
            if note is None:
                if len(note_txt) > 0:
                    note = MessageAnnotation(message=m)
                    note.text = note_txt
                    note.save()
            else:
                if len(note_txt) == 0: note.delete()
                else:
                    note.text = note_txt
                    note.save()                
    villages = Village.objects.all().order_by('name')
    for village in villages:
        # once this site bears more load, we can replace flatten() with village.subnodes
        # and stop reporting num_messages
        members = village.flatten()
        village.member_count = len( members )
        last_week = ( datetime.now()-timedelta(weeks=1) )
        village.message_count = IncomingMessage.objects.filter(domains=village,received__gte=last_week).count()
    context['villages'] = paginated(request, villages)
    messages = IncomingMessage.objects.select_related().order_by('-received')
    context.update( format_messages_in_context(request, context, messages) )
    context.update( totals(context) )
    return render_to_response(request, template, context)

# TODO: move this somewhere Tostan-Specifig
# would declare this as a class but we don't need the extra database table
def SetFlag(flag):
    code = Code.objects.get(slug="True")
    flag.code = code

def IsFlag(tag):
    return tag.code.set.name == "FLAGGED_CODE"

@login_required
def messaging(request, template="smsforum/messaging.html"):
    context = {'contacts': paginated(request, Contact.objects.all().order_by('common_name')),
               'villages': Village.objects.all().order_by('name'), 
               'regions': Region.objects.all().order_by('name')}
    village, region = get_village_and_region(request, context)
    context['edit_link'] = "/member/edit/"
    return render_to_response(request, template, context)

@login_required
def memberships(request, template="smsforum/manage_memberships.html"):
    context = {}
    def cookie_recips(status):
        flat = urllib.unquote(request.COOKIES.get("recip-%s" % status, ""))
        return map(str, re.split(r'\s+', flat)) if flat != "" else []
    checked  = cookie_recips("checked")

    def __reporter(rep):
        rep.is_checked = rep.pk in checked
        return rep
    
    reset_cookie = False
    if request.method == 'POST':
        if not request.POST['community'] or len(request.POST['community'])==0:
            context['error'] = "Please select a community"
        elif request.COOKIES["recip-checked"] == 'None':
            context['error'] = "Please select at least one contact"            
        else:
            members = [Reporter.objects.get(pk=id).profile.get() for id in checked]
            community = Community.objects.get(pk=int(request.POST['community']))
            community.add_children(*members)
            context['status'] = _("%(num)s contact successfully added to %(community)s") % \
                {'num':len(members),'community':community.name}
            reset_cookie = True
    context["query"] = request.GET.get("query", ""),
    reporters = Reporter.objects.filter(profile__node_ptr___parents=None)
    context["reporters"] = paginated(request, reporters, wrapper=__reporter)
    context["num_reporters"] = len(reporters)
    context["communities"] = paginated(request, Village.objects.all())  
    context["debug"] = request.COOKIES['recip-checked']
    response = render_to_response(request, template, context)
    if reset_cookie:
        response.set_cookie("recip-checked", None, expires="01-01-1985")
    return response
def add_alias_to_community(request,pk):
      village =Village.objects.get (id=pk)
      template ="smsforum/community_alias.html"
      context={"village":village}
      if  request.method=="POST":
              # create an new community alias
              c=CommunityAlias(
              alias =request.POST["alias"], 
              community =village
              ) 
              # save the community
              c.save ()
              context["status"]="\
              L'alias pour cette caumunaute a ete  bien cree"
              return  render_to_response (request,template,context)
      return  render_to_response (request,template,context)
