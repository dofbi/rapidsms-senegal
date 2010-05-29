import rapidsms
from rapidsms.parsers.keyworder import *
import models as m
# Les reponses aux enregistrements du seminaire
pre_success   ="Merci d'avoir porposer un theme : Taper wara themes pour voir la list"
pre_date_fail ="Date de presentation deja prise essayez une autre"
# Les reponses aux renseignement des themes du seminaires
ren_fail      ="Erreur lors de l'accees a la liste des themes"
class App (rapidsms.app.App):
    kw = Keyworder ()
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
    @kw("wara theme (.+) date (d\d? \d\d? \d{4})")
    def add_presentation (self , message , date):
	"""
	Ajouter un nouveau presentateur au seminaire
	"""
        try:
	    day  , month  , year  =tuple( date.split())
            m.Seminaire.objects.create (
                theme=theme ,
                phone =message.connection.identity,
                date=datetime (year , month  , day))
            message.respond (res_success)
            return True
        except Exception , e:
            print "Exception"
            print e
            message.respond (pre_fail)
    @kw ("wara themes|warathemes")
    def all_themes (self , message , *args):
        """
	Lister tous les themes proposes lors du semianire WARA
	"""
        MAX =140
        try:
	   waiting_message =False
	   messsage_to_send =""   
	   seminaires  = m.Seminaire.objects.all()
	   if not  len(seminaires):
		message.respond ("""
		Aucun seminaire enregistre pour le moment :
		Tapez wara theme 
		<Rapidsms Application> data  <02 01 2004>""")
           msg_to_send =""               
           for seminaire in  seminaires:
                      # Test if the current message add to the next message is not > MAX
                      if (msg_to_send + "[%s ,%s]"%\
                            (seminaire.theme , seminaire.date))>MAX:
                               message.respond (msg_to_send)
                               # Reset message to empty
                               msg_to_send =""
                      # We can add another message
                      else : msg_to_send += "[%s ,%s]"%\
                               (semaire.theme, seminaire.date)
        except Exception ,e :
            print "Exception"
            print e
            message.respond (ren_fail)
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
