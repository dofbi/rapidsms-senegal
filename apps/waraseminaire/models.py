from django.db import models
from time import localtime
from datetime import datetime 
# Create your Django models here, if you need them.

class Seminaire(models.Model):
    """
    Model to Store all communication
    """
    presentateur_phone = models.CharField (max_length =160)
    theme              = models.CharField (max_length =160)
    date_presentation  = models.DateTimeField (auto_now_add =True)

    def __unicode__(self):
        return  ("presentation_num  :%s\
                  theme             :%s\
                  date_presentation :%s"\
                  %(self.presentateur_phone, \
                    self.theme,\
                    self.date_presentation)
                )

    @staticmethod    
    def hour2datetime (hour):
        """
        datetime from hour
        """
        local_time  =localtime ()
        return datetime (local_time[0] , local_time [1], local_time[2] ,int (hour))
    @staticmethod
    def is_available_hour (hour):
        """
        Is it an hour already registered by a presentateur
        """
        sem_list  =Seminaire.objects.all ()
        for  sem in sem_list :
            if sem.date_presentation.day ==localtime ()[3]:
                    if sem.date_presentation.hour == int (hour):
                        return False
        return True


