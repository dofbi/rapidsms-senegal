#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.conf.urls.defaults import *
import contacts.views as views

urlpatterns = patterns('',
    url(r'^contacts/$', views.index, name='contacts'),
    url(r'^contacts/csv/$', views.csv, name='export_contacts'),
    url(r'^contact/add/$', views.add_contact),
    url(r'^contact/edit/(?P<pk>\d+)$', views.edit_contact),
    url(r'^contact/delete/(?P<pk>\d+)$', views.delete_contact),
)

