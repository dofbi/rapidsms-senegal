#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from rapidsms.tests.scripted import TestScript
import apps.smsforum.app as smsforum_app
import apps.logger.app as logger_app
import apps.contacts.app as contacts_app
import apps.reporters.app as reporters_app
import apps.smsforum.app as smsforum_app
 
class TestI18NCommands (TestScript):
    apps = (smsforum_app.App, contacts_app.App, logger_app.App, reporters_app.App, smsforum_app.App )

    def setUp(self):
        TestScript.setUp(self)
        #should setup default village in here
        
    testMsgTooLongEnglish = """
        8005551210 > .create village20
        8005551210 < Community 'village20' was created
        8005551210 > .join village20
        8005551210 < Thank you for joining the village20 community - welcome!
        8005551210 > very long message to blast - very long message to blast - very long message to blast - very long message to blast - very long message to blast - very long message to blast - very long message to blast - very long message to blast - very long message to blast
        8005551210 < Message length (258) is too long. Please limit to: 140.
        8005551210 > À Ä  very long message to blast - very long message to blast - very long message to blast - very long message to blast - very long message to blast - very long message to blast - very long message to blast - very long message to blast - very long message to blast
        8005551210 < Message length (265) is too long. Please limit to 60
        """
           
    testMsgTooLongFrench = u"""
        8005551210 > .creer village20
        8005551210 < La communauté village20 a été créée
        8005551210 > .entrer village20
        8005551210 < Merci d'avoir rejoint la communauté 'village20' - bienvenue!
        8005551210 > tres tres long messages ,tres tres long messages ,tres tres long messages ,tres tres long messages ,tres tres long messages ,tres tres long messages ,tres tres long messages ,tres tres long messages ,tres tres long messages ,
        8005551210 < Désolé, ce message fait plus de 140 caractères. Merci de le reccourcir et de l'envoyer à nouveau.
        8005551210 > À Ä Trop long caracteres  unicode ,À Ä Trop long caracteres  unicodeÀ Ä Trop long caracteres  unicodeÀ Ä Trop long caracteres  unicodeÀ Ä Trop long caracteres  unicode
        8005551210 < Désolé, ce message fait plus de 60 caractères. Merci de le reccourcir et de l'envoyer à nouveau.
        """
    testMsgToLongWolof = u"""
        8005551210 > .create village20
        8005551210 < Community 'village20' was created
        8005551210 > .lang wol
        8005551210 < Làkk wi nga tànn moo kàllaama Wolof
        8005551220 > .duggu village20
        8005551220 < Jerejef ci dugg bi nga dugg ci 'village20 ' dalal ak jamm
        8005551220 > Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, 
        8005551220 < Nu ngi jéggalu, xebaar bii, araf yi ci embu, dañoo bari te warula epp 140 - nu laay ñaan, nga wàññi leen te yonnewaat ko.
        8005551220 > À Ä Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, 
        8005551220 < Nu ngi jéggalu, xebaar bii, araf yi ci embu, dañoo bari te warula epp 60 - nu laay ñaan, nga wàññi leen te yonnewaat ko.
        """
    testMsgToLongPulaar = u"""
        8005551210 > .create village20
        8005551210 < Community 'village20' was created
        8005551210 > .lang pul
        8005551210 < Demngal ngal cubi- daa ko Pulaar.
        8005551220 > .naattugol village20
        8005551220 < A jaaraama nde tawtu - daa e renndo ngo 'village20' - Bisimilla maa!
        8005551220 > Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, 
        8005551220 < Yaafo, oo kabaaru burii 140. Jaaraama, tiidno ndabbindinaa nuldaa kadi.
        8005551220 > À Ä Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, 
        8005551220 < Yaafo, oo kabaaru burii 60. Jaaraama, tiidno ndabbindinaa nuldaa kadi.
        """
    testMsgToLongDjoola = u"""
        8005551210 > .create village20
        8005551210 < Community 'village20' was created
        8005551210 > .lang dyu
        8005551210 < kasankenak kanu fajulumi ku 'Joola'
        8005551220 > .unoken village20
        8005551220 < abaraka manunoken na di fujojaf fati 'village20'
        8005551220 > Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, 
        8005551220 < ubonket, furimaf fubabaak 140. uciik fo tami man fujaw benen. abaraka.
        8005551220 > À Ä Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, 
        8005551220 < ubonket, furimaf fubabaak 60. uciik fo tami man fujaw benen. abaraka.
        """
    testMsgToLongSoninke = u"""
        8005551210 > .create village20
        8005551210 < Community 'village20' was created
        8005551210 > .lang son
        8005551210 < an ga da xanne be suggandi Sooninken ya ni.
        8005551220 > .ro village20
        8005551220 < Maama ti an ga ro 'village20' - Bisimilla!
        8005551220 > Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, 
        8005551220 < Yanpa, xibaare ke nta dangini sigiru 140. Maama, a defondi nan yille a xayini.
        8005551220 >  À Ä Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, 
        8005551220 < Yanpa, xibaare ke nta dangini sigiru 60. Maama, a defondi nan yille a xayini.
        """
    testMsgToLongMandingo = u"""
        8005551210 > .create village20
        8005551210 < Community 'village20' was created
        8005551210 > .lang man
        8005551210 < La langue que vous avez sélectionnée est 'Mandinka'
        8005551220 > .koo village20
        8005551220 < nseewota na dunaa kaabiloo kono - a la mee tentula 'village20'!
        8005551220 > Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, 
        8005551220 < nbe daani la iye i la kumajuloolu sutiyandi 140 
        8005551220 > À Ä Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, Messasse bou goudou lol, 
        8005551220 < nbe daani la iye i la kumajuloolu sutiyandi 60
        """

