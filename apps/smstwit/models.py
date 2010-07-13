from django.db import models
# Create your Django models here, if you need them.
class SMSTwit (models.Model):
    """
    Stoker les messages des utilisateurs qui envoient des 
    sms au systeme  [apptwitter]
    lorsque un sms arrive dans l 'application smstwit 
    on ne fait que ajouter  le sms dans la base de donnees
    avec le numero de l'appelant et le message 
    Le module [twitter_handler] si le message doit etre 
    twitte ou pas 
    """
    phone  = models.CharField(max_length =20 , help_text = "Numero de telephones des gens qui vont utiliser l 'application apptwit")
    txtmsg = models.TextField (max_length = 140)
    def __unicode__(self):
      return  ("%s : %s"%(self.phone , self.txtmsg))


            
