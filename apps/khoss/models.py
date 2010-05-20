from django.db import models
# Create your models here
class CreditCode (models.Model):
    '''Store the sms from file '''
    code      = models.CharField (max_length = 260)
    used      = models.BooleanField (default =False)
    def __unicode__(self):
        return  "%s %s"%( self.code , self.used)
                                                
class Caller (models.Model):
    """ Users to brodcast messages """
    identity  =models.IntegerField()
    receive   =models.BooleanField (default =False)
    def __unicode__(self):
        return  "%s"%self.identity


class Transaction(models.Model): 
   """credit transaction"""
   caller  = models.ForeignKey (Caller)
   creditcode =models.ForeignKey (CreditCode)
   def __unicode__(self):
	return  "%s %s " %(self.caller.identity , self.creditcode.code)
	
    
    
    
    
