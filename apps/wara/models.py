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
    date = models.DateTimeField (auto_now_add =True)
    def __unicode__(self):
        return ("presentation_num :%s\
		 theme :%s\
		 date_presentation :%s"\
                  %(self.presentateur_phone, \
                    self.theme,\
                    self.date_presentation)
        )


