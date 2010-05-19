#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

"""
set the threshold in which the logs will be handled.
in other words, we will only save logs with level > than what we set.
for reference:
CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0
""" 

from django.contrib import admin
from rapidsms.webui.settings import RAPIDSMS_APPS as app_conf
from apps.logtracker.models import LogTrack
from apps.logtracker.init import *

class LogTrackAdmin(admin.ModelAdmin):
    list_display = ('id', 'level', 'channel', 'message', 
                    'filename', 'line_no', 'data_dump')
    list_filter = ['level', 'channel', 'filename']
    
admin.site.register(LogTrack,LogTrackAdmin)
