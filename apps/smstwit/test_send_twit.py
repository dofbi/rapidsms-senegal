"""
Ce module permet de tester l'autentification d'un utilisateur 
Le principe est le suivant nous utilisons [oauth] pour se 
pour permettre l'authentification d'un nouveau utilisateur 
afin de permettre notre application de twitter 

Une fois cette etape franchie , nous pouvons alors 
obtenir un couple  [token_key , token_secret] pour pour 
chaque utilisteur.

Enfin nous pouvons alors utiliser le module [twitterpy]
pour twitter 

Nous aurons pas forcment besion  de cette partie 
puisque nous allons demander le  [(token_key , token_secret)]
a [connectionservice] .

Mais c'est important de comprendre le principe :)
"""

from oauthtwitter import *
import oauth 
consumer_key    ="Exgy2LpTAuVCW9G61iafQ"
consumer_secret ="ZOH2MHGOfRxBYr0haX8VweAZ3bjs389LcfKE3bWhHw"
def run_test ():
    twitter =OAuthApi(consumer_key , consumer_secret)
    req_token = twitter.getRequestToken ()
    sin_url = twitter.getAuthorizationURL (req_token)
    print (">>>Copie this url and login to allow The application\
      post some messages for you :)\
      \n :URL :%s" %sin_url)

    raw_input (">>>Type any caractere to continue testing :")
    token = oauth.OAuthToken.from_string (req_token.to_string())
    twitter = OAuthApi(consumer_key , consumer_secret , token)
    access_token =twitter.getAccessToken ()
    print "access_token  :%s"%(access_token)
    print "methods"
    print dir (access_token)
    print  "key : %s"%access_token.key
    print  "secret :%s"%access_token.secret
    # A ce niveau nous avons un (token_key) et (token_secret)
    # nous allons maintenant utiliser [tweepy] qui utilise 
    # un token_key et un token_secret pour twitter 
    import tweepy 
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token.key, access_token.secret)
    api = tweepy.API(auth)
    api.update_status("Hello Iam Alioune Dia I love Python and Oauth , I posted the same message!")
    print "Finished posting message"

if __name__ =='__main__':
    run_test ()

