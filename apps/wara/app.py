import rapidsms
from rapidsms.parsers.keyworder import *
import models as m
import time
from datetime import datetime 
from time import localtime


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
            
            print "Excpetion"
            print e
            message.respond ("Invalid commande : wara theme [theme]  date [jour h] nom [nom]")
    

    @kw("help")
    def help (message):
        message.respond ("wara theme <theme> date <jour mois>")

    @kw("wara theme (.+) date (\d\d? \d\d?) nom (.+)")
    def add_presentation (self , message , theme , date , nom):
	"""
	Ajouter un nouveau presentateur au seminaire
	"""
        try:
	    jr  , hr  =tuple(date.split())
            an ,mois = localtime ()[0], localtime()[1]
            m.Seminaire.objects.create\
            (theme=theme , 
             phone =message.connection.identity,
             date=datetime (int (an),int (mois),int (jr),int (hr)),
             nom =nom)
            message.respond ("Merci d'avoir proposer un theme  au seminaire ,\
                    tapez [wara themes] pour la liste")
            return True
        except Exception , e:
            print "Exception"
            print e
    

    @kw ("wara themes|warathemes")
    def _get_wara_themes (self , message , *args):
        """
	Lister tous les themes proposes lors du seminaire WARA
        (WEST AFRICAN RESEARCH )
	"""       
        def to_str(el):
            return  "[Presentation: %s ,Date : le %s a %s Heures ,Par :%s ]"%\
                        (el.theme  ,el.date.day ,  el.date.hour ,  el.nom)
        def _get_presentation (old_list , given_el):
             try:
                   
                   item  =old_list [-1]        
                   new_given  = to_str (item) + given_el
                   if len (new_given)>= 140:
                        return given_el
                   else :
                        old_list.pop ()
                        return  new_given 
                        
             except Exception , e:
                print "Into _get_presentation"
                print  e
                return  given_el
    

        seminaires  = m.Seminaire.objects.all ()
        if not seminaires  or len (seminaires)==0:
            message.respond  ("Aucun seminaire pour le  moment")
            return  
        # We got some presentations into data base
        seminaires  = list (seminaires)
        given_el    =  seminaires.pop ()
        given_el    = to_str (given_el)
        while True :
            try:
                output_el  =_get_presentation (seminaires , given_el)
                # Good message size 
                if  output_el  == given_el:
                    message.respond(output_el) 
                    given_el  =to_str (seminaires.pop ())

                    time.sleep (10)
                else :
                     given_el =output_el 
            
            except Exception , e :
                print  e
                break 
                
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
