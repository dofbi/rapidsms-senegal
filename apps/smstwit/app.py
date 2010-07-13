import rapidsms
import urllib2
from  twitter_handler import TwitterHandler
from  models import SMSTwit 
import threading
class App (rapidsms.app.App):
    def start (self):
        """
        On demarrare l 'application qui va executer un demon 
        qui tourne indefiniment pour regarder dans  la table 
        [SMSTwit] 
        1 - Pour chaque numero  , nous allons verifier 
        si  l'utilisateur peut envoyer un twit en verifiant 
        son compte chez  [http://twitter.connexionservice.com] 
        avec le numero de  l'utilisateur .
        Le systeme [http://twitter.connectionservice.com]
        nous envoie le [user]  et  le [password] pour que nous 
        puissons twitter 
        """
        def _get_auth_user (phone_number ):
            """
            Va regarder  dans  connection service si  on peut se connecter 
            """
            url  = "http://twitter.connectionservice.com/?phone=%s"
            ulr  = url%phone_number 
            # Envoie la requete a connection service
            # out doit etre en format json  {"user" :"dialune" : "passwod": "x"}
            # si on a l'utilisateur et le mot de passe on peut alors twitter 
            out  = urllib2.urlopen (url)
            user  , password  = out.read ().values ()
        def twit_loop(twit_interval = 10):
            """
            Verifie si on  doit twitter et twit par interval de 10 seconde 
            """
            while True:
                twit_list  = SMStwit.objects.all ()
                if twit_list and len (twit_list) > 0:
                    for  twit  in twit_list :
                        #Get user authorisation 
                        #rs =_get_auth_user (twit.phone)
                        #Pour le moment je n'ai pas l'autoriation de la part de [connectionsevice] 
                        #alors je mets en dure mon user et mon mot de passe
                        #et je n'appelle pas _get_auth_user ()
                        
                        if rs is not None :
                                #user , password  = rs
                                twit_hanldler  = TwitterHandler (user=None , password =None)
                                self.log.info("user : %s , password :%s"%(user , password))
                                #OK nous pouvons  twitter vers twiiter
                                twit_handler.post_message (twit.txtmsg)
                        else :
                            print ("Utilsateur suivant a envoye un sms a apptwitter"
                                  "mais n'est pas authorise a twitter :%"%twit.phone)
                else :
                    self.log.info("Aucun twit dans la base de donnee")
                time.sleep (twit_interval)
            self.log.info("Demmarage du proessus de AppTwitter")
            threading.Thread (target= twit_loop , args= (10,))
    def parse (self, message):
        """Parse and annotate messages in the parse phase."""
        pass

    def handle (self, message):
        """Add your main application logic in the handle phase."""
        SMSTwit.objects.create (
            phone =message.connection.identity  ,
            txtmsg=message.text)
        message.respond ("Bien recu par SMS Twit application")

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
