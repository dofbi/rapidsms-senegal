import rapidsms
import json
import urllib2
from django.core.exceptions import ObjectDoesNotExist , MultipleObjectsReturned
from  models import UserToken ,Message
consumer_key    ="Exgy2LpTAuVCW9G61iafQ"
consumer_secret ="ZOH2MHGOfRxBYr0haX8VweAZ3bjs389LcfKE3bWhHw"
class App (rapidsms.app.App):
    def handle (self, message):
        def get_token_secret_from_website (phone):
            '''Si le Token secret , n'est pas encore dans notre base de donnees '''
            url  = "http://twitter.connectionservice.com/?phone=%s"
            url  = url%phone  
            json_data  = urllib2.urlopen (url).read()
            # Data contient le format suivant 
            # data = {
            #        "key": "234wxvfgrss uYHGGJHHH" ,
            #        "secret": "GDHDHesxxbsUTTOKKKKq2344   "
            #        }
            data = json.load (json_data)
        def get_token_secret_from_db (phone):
            '''A partir du second twit nous stockons le token key et secret
            dans notre base de donnees de cette maniere , nous avons plus
            a le demander a connnectionservice'''
            try:
                return UserToken.objects.get (phone =phone)
            except ObjectDoesNotExist :
                # Nous n'avons pas le token key et le
                # token secret dans notre base de donnees 
                # il faut le demander a connection service
                return None
            except MultipleObjectsReturned:
                return None
        # Nous cherhons deja si le token key 
        # et le token secret est en base de donnees
        token  = get_token_secret_from_db(message.connection.identity)
        if token:
            key  =token.key
            secret= token.secret
        else:
            token  = get_token_secret_from_website(message.connection.identity)
            key = token.get ("key" , None)
            secret =token.get ("secret" ,None)
        import tweepy 
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(key, secret)
        api = tweepy.API(auth)
        api.update_status(message.text)
        # Store into data base
        UserToken.objects.get_or_create (token_key =key, token_secret =secret)
        Message.objects.create (message)

    def parse (self, message):
        """Parse and annotate messages in the parse phase."""
        pass
    def cleanup (self, message):
        """Perform any clean up after all handlers have run in the
           cleanup phase."""
        pass

    def outgoing (self, message):
        """Handle outgoing message notifications."""
        pass

    def stop (self):
        """Perform global app cleanup when the application is stopped."""
        pass
