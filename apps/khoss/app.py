import rapidsms
from models import Transaction , CreditCode , Caller
from datetime import datetime 
import threading
from rapidsms.message import Message
from rapidsms.parsers.keyworder import * 
class App (rapidsms.app.App):
    """
    Transfert le credit 
    Transaction :table contenant la transaction
    CreditCode  :table contenant le  code du credit 
    User        :Table contenant la liste des utilisateurs 
    """
    ADMIN_IDEN = "778303030"
    kw = Keyworder ()
    def start (self):
        pass
    def parse (self, message):
        pass
    def handle (self, message):
         try:
              func , captures = self.kw.match (message.text)
              func(self, message, *captures)
              # Message is handled with succes
              return True
         except Exception , error:
                self.help_caller (message)
             
    
    @kw.blank()        
    def help_caller (self , msg):
        msg.respond ("start khoss_credit <montant>")
    
    @kw ("(start khoss (\d+))")
    def start(self, msg , amount ):
        """
        Starting running transaction
        """
	# Is he the admin
	if msg.connection.identity != App.ADMIN_IDEN:
		msg.respond ("You are not admin")
		return None
        self.log ("Starting running transaction at %s "%(datetime.now ()))
        if  msg.khoss :
                return True
        # Broadcast message
        broadcaster_khoss(amount)
        # The notification loop , all credit that send 
        msg.khoss =True 
        
        
    def broadcaster_khoss (self, message ,amount):
        """Send cedit montant to all users into database"""
        khoss_thread = Thread (target = khoss_loop  , args =(message, amount))
        khoss_thread.start ()
             
    def khoss_loop (self ,message, amount):
        """
        Starting run transaction loop
        We are going to send credit to all user into the database
        """
        self.transaction_start =True
        while True :
           credit_list = CreditCode.objects.filter (used =False , amount =amount)
           caller_list = Caller.objects.all (receive =False)
           if len (caller_list)> len (credit_list):
               caller_list  = caller_list[0: len (credit_list)]
           
           
           elif len (credit_list)>len(caller_list):
               credit_list  = credit_list[0: len (caller_list)]
           

           else :
		pass
           
           for credit , caller in zip (credit_list , caller_list) :
               try:    

		       # Send credit to each caller
		       Transaction.objects.create\
		           (credit =credit ,caller =caller)
		       self.log ("Sending credit : %s , to : %s " \
		                  %(credit.code , caller.identity))
		       message.connection.backend.message(\
				identity  = caller.identity ,
				text = "Please use this credit %s "%credit.code).send ()
		       credit.used =True
		       credit.save ()
		 	
	 	       caller.receive =True 
		       caller.save ()
                 except Exception , e:
			print "Exception"
			print e
  
  	   
 	    return True

    def cleanup (self, message):
        pass
    def outgoing (self, message):
        pass
    def stop (self):
        pass
