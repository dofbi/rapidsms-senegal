import rapidsms
from app_cedo.models import Receiver , USSDTransfert
import re
from rapidsms.parsers.keyworder import * 
class App (rapidsms.app.App):
    """ Desciption:
	Application pour Faire un tranfert de credit
	vers un numero donnee .
	Au sein de l'entrepise un agent demande au
	systeme de transfert de l'entrerise de
	lui envoyer un montant donnne

	>join <PHONE>
	< bienvenu sur le systeme de transfert
	> demande <MONTANT>
	< Veuiller utiliser ce montant <MONTANT>

	 Note : For orange SENEGAL:
	 Pour ORANGE SENEGAL le message de notification pour un
	 transfert reussi est <210>
    """
    kw = Keyworder ()
    def parse (self, msg):
        pass
    
    def handle (self, msg):
          '''Method to handle messages'''
          try:
              func , captures = self.kw.match (msg.text)
              func(self , msg ,*captures)
              return True
          except Exception , error:
              self.help (msg)
              
    @kw.blank ()
    def help (self , msg ):
        '''help  message '''
        msg.respond ("""
        join  <call> ,
        demande <montant>
        """)
    
    def _get (model , **kw):
        '''Get models with given keywod arguments'''
        try:
           model.objects.get (**kw)
           return True 
        
        except : return False
        
    def _get_or_create (model , **kw):
         '''Get objects or create it'''
         obj  , created  =None , False
         try:
           obj , created =  model.objects.get_or_create (**kw)
         except  :
            pass  
         return obj , created
     
    def _identify_caller (self ,msg, task = None):
        '''Verifie if caller is registered else send messages to register '''
        obj  = _get(Receiver , *{ "phone_num" : msg.connection.identity })
        if obj : return True 
        else : 
             res_msg   ="Indetifiez vous avant  %s"%task
             msg.respond (res_msg)
        
    @kw ("(demande)\s+(\d[3-4])")
    def send_cedo (self ,msg,amount):
        """
        Sending cedo
        caller : The destination of transfert
        amount : The montant of transfert
        """     
        caller =self._identify_caller (task  ="de demander du credit ")
        ussd_trans = USSDTransfert.from_msg(msg)
        ussd_trans.amount = amount
        ussd_form  = USSDTransfert._get_ussd_format(msg)
        ussd_message = usss_form %{ "destination": ussd_trans.amount,
                    "amount": ussd_trans.amount ,
                    "PIN": PIN }
        try:
            msg.connection.backend.__runussd(ussd_message)
        except :
            raise ("Cannot send message , check balance , please")
            
         
    @kw("210")
    def _get_notification (self , msg):
        """
        The ORANGE Operarator send us a nofification message
        so we are going to find a cedo that match
        """
        try:
            phone =re.sub("\D" , msg.text)
            if re.match ('^((\+?|71|77|76)\d{7})$' ,phone):
                    return re.match ('^((\+?|71|77|76)\d{7})$' ,phone).group(0)
        except : pass
        if not phone_num :
            return    
        USSDTransfert.objects.filter\
             (**{"to_num": phone_num , "statut_not": "P" })\
             .order_by("date").update(statut_not ="S")
        

    @kw ("(join)")
    def register_mem (self, msg):
        '''Register a new member  '''
        Receiver.objects.create (**{ "phone_num" : msg.connection.identity})
        msg.respond  ( "Vous etes enregistré")
        
    def outgoing (self, message):
        pass
    
    def stop (self):
        pass
    
    
