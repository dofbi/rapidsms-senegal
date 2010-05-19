#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.conf.urls.defaults import *
from contacts.views import edit_contact
import smsforum.views as views

urlpatterns = patterns('',
    url(r'^visualize$',                               views.visualize),
    url(r'^regions$',                                 views.regions, name='regions'),
    url(r'^region/(?P<pk>\d+)$',                      views.region, {'template':"smsforum/community.html"}, name='region', ),
    url(r'^citizens$',                                views.citizens, name='citizens'),
    url(r'^messages$',                                views.messages),
    url(r'^messaging$',                               views.messaging, name="messaging"),
    url(r'^manage$',                                  views.manage, {'template':"smsforum/manage.html"}),
    url(r'^access$',                                  views.access, {'template':"smsforum/manage_access.html"}),
    url(r'^villages$',                                views.index),
    url(r'^village/(?P<pk>\d+)$',                     views.community, {'template':"smsforum/village.html"}, name='community', ),
    url(r'^village/add$',                             views.add_village),
    url(r'^region/add$',                              views.add_region, name='add_region'),
    url(r'^village/delete/(?P<pk>\d+)$',              views.delete_village),
    url(r'^region/delete/(?P<pk>\d+)$',               views.delete_region, name='delete_region'),
    url(r'^village/(?P<pk>\d+)/history$',             views.village_history),
    url(r'^village/(?P<pk>\d+)/history/csv$',         views.export_village_history, name='export_village_history'),
    url(r'^village/(?P<pk>\d+)/membership/csv$',      views.export_village_membership, name='export_village_membership'),
    url(r"^add_alias/(?P<pk>\d+)$",                   views.add_alias_to_community ,name  ="add_alias_to_community"),
    url(r'^member/(?P<pk>\d+)$',                      views.member),
    url(r'^village/(?P<village_id>\d+)/member/add$',  views.add_member),
    url(r'^village/(?P<village_id>\d+)/member/add/(?P<member_id>\d+)$',  views.add_member),
    url(r'^member/edit/(?P<pk>\d+)$',                 views.edit_member),
    url(r'^i18n/',                                    include('django.conf.urls.i18n')),
    #url(r'^community/add$',                          views.add_community),
)

