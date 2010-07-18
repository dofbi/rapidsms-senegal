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

    #Add  attribute  name   to the  model
    #to match Nokia web UI
    nom  = models.CharField (max_length  = 160   ,  null =True ,  blank =True)
    def __unicode__(self):
     
         return    "phone  :%s  , theme :%s  , date : %s , nom  : %s"%\
             (self.phone  , self.theme , self.date  , self.nom)

     


