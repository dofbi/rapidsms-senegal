from django.db import models
# Create your Django models here, if you need them.
class UserToken (models.Model):
    """
    Model pour stocker le [token_key] 
    et le [token_secret] pour chaque utilisateur 
    Lorsque on se connecte a connectionservice pour
    la premiere fois ,nous recuperons le [token_key]
    et le [token_secret] , et nous le stokons dans
    la base de donnees ,de cette maniere nous 
    pour cette numero de telephone nous accedons
    a connection service juste une fois :)
    Pour la seconde et les autres fois nous 
    y accedons aux cles a partir d'ici .plus 
    besion d'acceder a la base de donnees.
    """
    token_key=     models.CharField(max_length =200 ,
                        help_text = "Numero de telephones des\
                        gens qui vont utiliser l 'application apptwit")
    token_secret = models.CharField (max_length = 200)
    phone        = models.CharField (max_length =200)
    def __unicode__(self):
      return  "%s : %s"%\
        (self.token_secret , self.token_key , phone)

class Message (models.Model):
    '''Stcoke les sms qui sont twittes '''
    message =models.TextField ()
    def __unicode__(self):
        return message
