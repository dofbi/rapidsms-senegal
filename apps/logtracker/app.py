#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf8

"""

Here we have an empty app, just so that rapidsms route
doesn't raise any alarming complaing about missing 'App'

"""
from apps.logtracker.init import *

import rapidsms

class App(rapidsms.app.App):
    pass

