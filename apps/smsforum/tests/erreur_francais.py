#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

"""

At some point, we should run all these tests in all the languages we support.
We really need to write some sort of automated tool to do that.

"""

from rapidsms.tests.scripted import TestScript
import apps.smsforum.app as smsforum_app
import apps.logger.app as logger_app
import apps.contacts.app as contacts_app
import apps.reporters.app as reporters_app
import apps.smsforum.app as smsforum_app
from apps.smsforum.models import Village
 
class TestErreurFrancai (TestScript):
    apps = (smsforum_app.App, contacts_app.App, logger_app.App, reporters_app.App, smsforum_app.App )

    #citizens-fail_no-village
    testRemove = u"""
        8005551220 > 123 creer village1
        8005551220 < La communauté village1 a été créée
        8005551220 > 123 enlever
        8005551220 < Merci de renvoyer avec le nom d'une communauté, e.g.: '.enlever village'
        8005551220 > 123 enlever xx
        8005551220 < Je ne peux pas trouver le communauté 'xx'
        """

    testErrorCodesFrancais = u"""
        8005551229 > .entrer
        8005551229 < Sorry, I don't know that place. Did you mean one of: community name ?
        8005551231 > .quitter village
        8005551231 < Could not find a community named 'village'
        8005551229 > .join village
        8005551229 < Sorry, I don't know that place. Did you mean one of: community name ?
        8005551229 > .lang
        8005551229 < You may set your language to any of: English, Français, Joola, Pulaar, Wolof
        8005551229 > .create
        8005551229 < Please send a village name, e.g. #create 'community name'
        8005551229 > .member village
        8005551229 < You are not a member of any community
        8005551231 > .leave
        8005551231 < You are not a member of any communities
        8005551229 > .create village
        8005551229 < Community 'village' was created
        8005551229 > .join village
        8005551229 < Thank you for joining the village community - welcome!
        8005551229 > .member village
        8005551229 < You are not a member of any community
        8005551229 > msg_to_blast_longer_than_160_msg_to_blast_longer_than_160_msg_to_blast_longer_than_160_msg_to_blast_longer_than_160_msg_to_blast_longer_than_160_msg_to_blast_longer_than_160
        8005551229 < Message length (173) is too long. Latin script max: 140. Unicode max: 60
        8005551229 > .entrer xxx
        """
    
    testDirectedMessagingErrors = u"""
        8005551229 > .creer village
        8005551229 < La communauté village a été créée
        8005551231 > .entrer village
        8005551231 < Merci d'avoir rejoint la communauté 'village' - bienvenue!
        8005551229 > 123 village 123 bonjour
        8005551229 < Votre message a été envoyé à: village
        8005551231 < bonjour - 8005551229
        8005551229 > 123 unknown 123 bonjour
        8005551229 < Je ne peux pas envoyer cette message. Je ne peux pas trouvé 'unknown'
        8005551229 > .create villagedup1
        8005551229 < La communauté villagedup1 a été créée
        8005551229 > .create villagedup2
        8005551229 < La communauté villagedup2 a été créée
        8005551229 > 123 villagedup 123 bonjour
        8005551229 < Je ne peux pas trouver ce recipient. Est-ce que vous voulez dire villagedup1?
        """
        
    testCreateNoArg = u"""
        8005551229 > 123 creer
        8005551229 < SVP envoyer un nom pour le communauté, e.g. 123 entrer 'nom de communauté'
        """

    testCreateDup = u"""
        8005551229 > .creer village2
        8005551229 < La communauté village2 a été créée
        8005551229 > .creer village2
        8005551229 < La communauté village2 existe déjà
        """

    testVillageNameTooLong = u"""
        8005551229 > 123 creer villagenametoolongvillagenametoolongvillagenametoolongvillagenametoolongvillagenametoolong
        8005551229 < Désolé, ce nom fait plus de 40 caractères. Merci de le reccourcir et de l'envoyer à nouveau.
        """
                
    testMemberLong = u"""
        8005551229 > 123 creer village1
        8005551229 < La communauté village1 a été créée
        8005551220 > .entrer village1
        8005551220 < Merci d'avoir rejoint la communauté 'village1' - bienvenue!
        8005551229 > 123 creer village2
        8005551229 < La communauté village2 a été créée
        8005551220 > .entrer village2
        8005551220 < Merci d'avoir rejoint la communauté 'village2' - bienvenue!
        8005551229 > 123 creer village3
        8005551229 < La communauté village3 a été créée
        8005551220 > .entrer village3
        8005551220 < Merci d'avoir rejoint la communauté 'village3' - bienvenue!
        8005551229 > 123 creer village4
        8005551229 < La communauté village4 a été créée
        8005551220 > .entrer village4
        8005551220 < Merci d'avoir rejoint la communauté 'village4' - bienvenue!
        8005551229 > 123 creer village5
        8005551229 < La communauté village5 a été créée
        8005551220 > .entrer village5
        8005551220 < Merci d'avoir rejoint la communauté 'village5' - bienvenue!
        8005551229 > 123 creer village6
        8005551229 < La communauté village6 a été créée
        8005551220 > .entrer village6
        8005551220 < Merci d'avoir rejoint la communauté 'village6' - bienvenue!
        8005551229 > 123 creer village7
        8005551229 < La communauté village7 a été créée
        8005551220 > .entrer village7
        8005551220 < Merci d'avoir rejoint la communauté 'village7' - bienvenue!
        8005551229 > 123 creer village8
        8005551229 < La communauté village8 a été créée
        8005551220 > .entrer village8
        8005551220 < Merci d'avoir rejoint la communauté 'village8' - bienvenue!
        8005551220 > 123 member
        8005551220 < Vous etes membre des communautés suivants: village1, village2, village3, village4, village5, village6, village7, village8 et de plus
        """
    
    testErrorCodesFrancais = u"""
        8005551216 > 123 nom nomtroplonguenomtroplonguenomtroplonguenomtroplonguenomtroplonguenomtroplonguenomtroplongue
        8005551216 < Désolé, ce nom fait plus de 30 caractères. Merci de le reccourcir et de l'envoyer à nouveau.
        """

