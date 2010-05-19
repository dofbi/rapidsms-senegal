#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django import template
register = template.Library()


import datetime
from django.utils.timesince import timesince
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.template.defaultfilters import date as filter_date, time as filter_time

@register.filter()
def human_readable_action(action):
    """Given a MessageLog Action, returns a human-readable interpretation of events"""
    if action == 'C':
        return "Join"
    elif action == 'D':
        return "Leave"
    return "Unknown"

@register.filter
def get_range( value ):
  """
    Filter - returns a list containing range made from given value
    Usage (in template):

    <ul>{% for i in 3|get_range %}
      <li>{{ i }}. Do something</li>
    {% endfor %}</ul>

    Results with the HTML:
    <ul>
      <li>0. Do something</li>
      <li>1. Do something</li>
      <li>2. Do something</li>
    </ul>

    Instead of 3 one may use the variable set in the views
  """
  return range( value )
