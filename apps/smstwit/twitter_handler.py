"""
twitter_handler.py 
Ce module permet  de recuperer un nomero de la table 
[SMSTwitter] , cette table est alimmente par RAPIDSMS 
.Lorsque un  message  arrive dans le modem .l'application 
(rapidtwitter) insere le sms  avec son  numero dans la Table
SMSTwitter.

le module twitter_handler  va parcourir  cette 
table et pour chaque numero va interoger via http 
l'application [(http://twitter.connexionservice.com/]
.L'URL passe est  [http://twitter.connexionservice.com/?phone =[Numero]]
Si l'autorisation passe on recupere le login et le mot de passe 
via le site  [http://twitter.connexionservice.com].

La reponse attendue est donc un format json :
  {
	"user_name" :"dialune" ,
        "password" :""
  }

twitter handler utilise l'api  [python-twitter] comme un client twitter
.Telechargeable sur le site  :[http://code.google.com/p/python-twitter/]

"""
DEFAULT_USER = "dialune"
DEFAULT_PASSWORD = ""


# from models import SMSTwitter
import twitter
class TwitterHandler:
       def __init__(self, user = DEFAULT_USER, password =DEFAULT_PASSWORD):
	  """
	  Initailisation d'une instance de twitter handler avec un login
	  et un mot de passe .Le login et le mot de passe est fourni 
	  par le  site [(http://twitter.connexionservice.com/] moyennant
	  un numero de telephone 
	  """
	  self.user  = user 
	  self.password = password
	  self.api = twitter.Api(username=self.user, password=self.password)
       def post_message (self, msg ="Alioune Test API twitter pour genova "):
	  """Poster un nouveau message"""
	  status = self.api.PostUpdate(msg)

if __name__=="__main__":
	twitter_ins  =   TwitterHandler()
	#Poster un nouveau message en utilisant  l'utilisateur 
	#Par defaut Alioune Dia  [dialune] et le mot de  passe []
	print "Posting message teste"
	twitter_ins.post_message  ()
