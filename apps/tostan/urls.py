#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
import apps.tostan.views as views

urlpatterns = patterns('',
    url(r'^$',         login_required(direct_to_template), 
                       {'template':"tostan/dashboard.html"}, name="dashboard"),
    url(r'^help$',     login_required(direct_to_template), 
                       {'template':"tostan/smscommands.html"}, name="help"),
    url(r'^export$',   views.export, name="export"),
    url(r'^404$',      login_required(direct_to_template), 
                       {'template':"tostan/404.html"}, name="404"),
    url(r'^export/users$',          views.export_contacts, name="export_contacts"),
    url(r'^export/registrations$',  views.export_membership, name="export_registration"),
    url(r'^export/messages/in$',    views.export_incoming_messages, name="export_incoming_messages"),
    url(r'^export/messages/out$',   views.export_outgoing_messages, name="export_outgoing_messages"),
    url(r'^export/users/(?P<village_pk>\d+)$',          views.export_contacts, name="export_contacts"),
    url(r'^export/registrations/(?P<village_pk>\d+)$',  views.export_membership, name="export_registration"),
    url(r'^export/messages/in/(?P<village_pk>\d+)$',    views.export_incoming_messages, name="export_incoming_messages"),
    url(r'^export/messages/out/(?P<village_pk>\d+)$',   views.export_outgoing_messages, name="export_outgoing_messages"),
)
