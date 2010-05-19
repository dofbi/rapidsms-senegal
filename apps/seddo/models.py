from django.db import models
from datetime import datetime
import re
from rapidsms.message import Message
from django.core.exceptions import ObjectDoesNotExist , MultipleObjectsReturned
class Receiver(models.Model):
    phone_num = models.CharField(max_length =200)
    def __unicode__(self):
        return unicode(self.phone_num)
    
class USSDTransfert (models.Model):
    STATUS =(
    ('P' , 'Pending') ,
    ('F' , 'Fail'),
    ('S' ,'Success')         
    )
    
    """SMS send to the system"""
    to_num = models.CharField(max_length = 200)
    sent_at = models.DateTimeField (auto_now_add =True )
    #The notification statut of message
    #sent by the operator
    statut_not =models.BooleanField (default =False)
    amount     =models.IntegerField()
    @classmethod
    def _get_ussd_format(cls , msg):
       '''Return  the correct ussd fromat'''
       if ORANGE_PAT.match(msg.text):
            return USSD_ORANGE
         
       elif TIGO_PAT.match(msg.text):
            return USSD_TIGO
        
       elif EXPRESSO_PAT.match(msg.text):
            return USSD_EXPRESSO
        
       else : return None
       
    @classmethod
    def from_msg (cls  , msg):
        '''Get USSD object transfert from message '''
        return USSDTransfert.objects.create(to_num =msg.connection.identity)
        
    def __unicode__(self):
       return unicode (self.to_num)
          