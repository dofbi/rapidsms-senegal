import rapidsms
from rapidsms.parsers.keyworder import *
import  models as   m


# Les reponses aux enregistrements du seminaire
pre_success   ="Merci de proposer la presatation (%s) a (%d) au seminaire"
pre_fail      ="Desole mais votre sujet de presentation nest pas pris en comtpte"
pre_date_fail ="Cette heure est deja prise par un autre presentateur"
# Les reponses aux renseignement des themes du seminaires
ren_succes    ="Voici la liste des heures de presentions %s"
ren_fail      ="Desole mais la liste des themes n'est pas disponible"

class App (rapidsms.app.App):
    kw  = Keyworder ()
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

           function , captures  = self.kw.match (self, message.text)
           function (self,message ,*captures)

        except Exception , e:
            print "Exception  when handling message"
            print e 
        
    @kw("wara theme (.+) heure (\d+)")
    def add_presentation (self  , message , theme , hour):
        """
        Ajouter un nouveau presentateur au seminaire 
        """
        try:
            # Test si cette heure de presentation n'est pas prise
            # par un autre seminariste
            if not   m.Seminaire.is_available_hour (int (hour)):
                message.respond  (pre_date_fail)
                return True

            # L'heure propose n'est pas prise par un autre seminariste
            # donc on est  bon
            local_date = m.Seminaire.hour2datetime (hour)
            m.Seminaire.objects.create (
                theme=theme ,
                presentateur_phone =message.connection.identity,
                date_presentation=local_date)
            
            res_success = pre_success% (theme,int (hour))
            message.respond (res_success)
            return True
            

        except Exception , e:
            print "Exception"
            print e
            message.respond (pre_fail)




    @kw ("wara themes|warathemes")
    def all_themes (self  , message , *args):
        """
        Lister tous les themes proposes lors du semianire   WARA
        """
        MAX =140
        try:
           sem_list  =m.Seminaire.objects.all()
           string = "%s" %";".join( ["T:%s,H:%s" %(str(s.theme) , str(s.date_presentation.hour))\
                for  s in sem_list ])
           res_success =ren_succes%string
           if len(res_success)<140:
                message.respond(res_success)
           else:
              # Si le message est superieur  a 140 caracteres  
              # on envoi plusieurs messages


              n = len (res_success)/MAX 
              message_list  = []
              for index in range (0 , n):
                    message_list.append (res_success[(index)*MAX:(index+1)*MAX])
            
              # Envoi des messages 
              for msg in message_list:
                    message.respond (msg)
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
