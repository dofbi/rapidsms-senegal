import rapidsms
from rapidsms.parsers.keyworder import *
import models as m
import time
from datetime import datetime 
from time import localtime
# Les reponses aux enregistrements du seminaire
OK=           "Merci d'avoir porposer un theme : Taper [wara themes] pour voir la liste des themes"
HELP =        "wara theme [theme] data [date]"
THEME_FAIL=   "Impossible de vous envoyer la liste ,Essayez plus tard"
MSG_HEAD=     "Le systeme va vous envoyer un SMS toutes les %s"


class App (rapidsms.app.App):
    kw = Keyworder ()
    INTERVAL=10

    def start (self):
        """Configure your app in the start phase."""
        pass
   
    def parse (self, message):
        """Parse and annotate messages in the parse phase."""
        pass
   
    def handle (self, message):
        """Add your main application logic in the handle phase."""
        # pass
        try:
           function , captures = self.kw.match (self, message.text)
           function (self,message ,*captures)
        except Exception , e:
            print "Exception when handling message"
            print e
    

    @kw("help")
    def help (message):
        message.respond (HELP)

    @kw("wara theme (.+) date (\d\d? \d\d?)")
    def add_presentation (self , message , theme , date):
	"""
	Ajouter un nouveau presentateur au seminaire
	"""
        try:
	    jr  , hr  =tuple(date.split())
            an ,mois = localtime ()[0], localtime()[1]
            m.Seminaire.objects.create (
                theme=theme ,
                phone =message.connection.identity,
                date=datetime (int (an),\
                               int (mois),\
                               int (jr),\
                               int (hr)))
            message.respond (OK)
            return True
        except Exception , e:
            print "Exception"
            print e
            message.respond (SAVE_FAIL)
    

    @kw ("wara themes|warathemes")
    def _get_wara_themes (self , message , *args):
        """
	Lister tous les themes proposes lors du seminaire WARA
        (WEST AFRICAN RESEARCH )
	"""
        try:
	   seminaires  = m.Seminaire.objects.all()
	   if not  len(seminaires):
		message.respond ("""
		Aucun seminaire enregistre pour le moment :
		Tapez: wara theme [Votre theme] date [date]   
		""")
                return  True

           message.respond (MSG_HEAD%str(self.INTERVAL))
           for s in seminaires :
                    blast = "Presentation sur : %s le %d a %d  heures"\
                            %( s.theme ,\
                               s.date.day,\
                               s.date.hour)
                    try:
                        message.respond (blast)
                        time.sleep (self.INTERVAL)
                    except Exception ,e:
                        print "Message trop long , peu etre"
                        print e


        except Exception ,e :
            print "Exception"
            print e
            message.respond (THEME_FAIL)
    
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
