[smstwit] est une application qui permter de twitter
les sms recus sur le modem .smstwit utilise le moteur 
sms [rapidsms].
Pour voir le fonctionnement vous pouver executer 
le fichier [test.py]

-Dependances: 
------------
    *[smstwit] utilise [http://code.google.com/p/oauth-python-twitter/]
    pour l'autentification chez twitter .La premiere difference entre 
    l'authentification basique et oauth est que l'on ne connait 
    pas l'utilisateur jusqu'a ce que l'on fasse la demande hez twitter .

    * [http://code.google.com/p/oauth-python-twitter/]  
      utilise l'api [http://code.google.com/p/python-twitter/]
    * [smstwit] utilise egalement le module [tweepy] pour poster 
      le twits .l'API peut etre telecharge ici
    http://github.com/joshthecoder/tweepy
    
    * [smstwit] utilise egalement le module [oauth] vous
    pouvez telecharger ici [http://oauth.googlecode.com/svn/code/python/oauth/]

-Testes:
-------
Pour tester juste le moteur qui twit indenpendamment de [smstwit]
vous pouvez executer le [test_send_twit.py]
   *Le teste vous genere  un URL pour que l'utilisateur puisse
    s'inscrire  a votre site , ensuite 
   *le teste va twitter un "Hello , Iam Alioune Dia and I love Python"
 
   *Il faut remplacer dans le fihier [test_send_twit.py] par votre [consumer_key]
   *et votre consumer_secret 



 

