import datetime
from django.db import models
from userprofile.models import BaseProfile
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

# we register IncomingMessage for tagging here
# because Tostan wants to be able to tag IncomingMessages
from logger.models import IncomingMessage
import tagging.managers as tagging
tagging.register(IncomingMessage)

GENDER_CHOICES = ( ('F', _('Female')), ('M', _('Male')),)

class TostanProfile(BaseProfile):
    firstname = models.CharField(max_length=255, blank=True)
    middlename = models.CharField(max_length=255, blank=True)
    surname = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    birthdate = models.DateField(default=datetime.date.today(), blank=True)    
    about = models.TextField(blank=True)

