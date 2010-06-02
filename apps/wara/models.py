from django.db import models
from time import localtime
from datetime import datetime
# Create your Django models here, if you need them.

class Seminaire(models.Model):
    """
    Model to Store all communication
    """
    phone = models.CharField (max_length =160)
    theme = models.CharField (max_length =160)
    date = models.DateTimeField ()
    def __unicode__(self):
        return (" %s:%s:%s "%(self.phone  , self.theme , self.date))


