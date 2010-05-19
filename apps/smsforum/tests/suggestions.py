#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from rapidsms.tests.scripted import TestScript
import apps.smsforum.app as smsforum_app
import apps.logger.app as logger_app
import apps.contacts.app as contacts_app
import apps.reporters.app as reporters_app
import apps.smsforum.app as smsforum_app
from apps.smsforum.models import Village
 
class TestSuggestions (TestScript):
    apps = (smsforum_app.App, contacts_app.App, logger_app.App, reporters_app.App, smsforum_app.App )

    def setUp(self):
        TestScript.setUp(self)
        ville = Village(name='nonexistant1')
        ville.save()
        ville = Village(name='nonexistant2')
        ville.save()
        
    testEnglishSuggestions = """
        8005551210 > 123 lang en
        8005551210 < You language has been set to: English
        8005551210 > 123 o join test
        8005551210 < Command not understood. Did you mean one of: unoken or upur?
        8005551210 > 123 join nonexistant
        8005551210 < Sorry, I don't know that place. Did you mean one of: nonexistant2, nonexistant1 ?
        """
           
    testFrenchSuggestions = u"""
        8005551210 > 123 o entrer village20
        8005551210 < Désolé, je ne peux pas comprendre cet ordre. Est-ce que vous voulez dire: unoken ou upur?
        8005551210 > 123 entrer to
        8005551210 < Désolé, je ne reconnais pas cet endroit. Est-ce que vous pensez de l'un de ceci? nonexistant1, nonexistant2
        """
    testWolofSuggestions = u"""
        8005551210 > .lang wol
        8005551210 < Làkk wi nga tànn moo kàllaama Wolof
        8005551210 > 123 o duggu test
        8005551210 < Maa ngi jéggalu ci ñàkka xam li nga begga santaane. Besal '# ndimbal wolof' ngir am mbooleem santaane yi mena nekk
        8005551210 > 123 duggu to
        8005551210 < Nu ngi jéggalu ci ñàkka xam bérab bi nga soxla. Ñu lay ñaan, nga bind # dugg, teg ci nonexistant1, nonexistant2.
        """
        
    testPulaarSuggestions = u"""
        8005551210 > .lang pul
        8005551210 < Demngal ngal cubi- daa ko Pulaar.
        8005551210 > 123 o naattugol test
        8005551210 < Yaafo mi faamaani ngol laawol. Mbii-daa unoken walla upur?
        8005551210 > 123 naattugol to
        8005551210 < Yaafo mi heptinaani nokku o. Hoo ko nonexistant1, nonexistant2?
        """
        
    testJoolaSuggestions = u"""
        8005551210 > .lang dyu
        8005551210 < kasankenak kanu fajulumi ku 'Joola'
        8005551210 > 123 o unoken test
        8005551210 < ubonket, imanjut wanuciike. uciik '#karamben' manurambeni
        8005551210 > 123 unoken to
        8005551210 < ubonket,imanjut esukey uyu. uciik #noken karess kati esukey. nan, nonexistant1, nonexistant2
        """
        
    testSoninkeSuggestions = u"""
        8005551210 > .lang son
        8005551210 < an ga da xanne be suggandi Sooninken ya ni.
        8005551210 > 123 o ro test
        8005551210 < Ma a faamu. A lefi manne koono unoken ma upur?
        8005551210 > 123 ro to
        8005551210 < Yanpa noqu tana faayi. Selli nonexistant1, nonexistant2
        """
        
    testMandinkoSuggestions = u"""
        8005551210 > .lang man
        8005551210 < La langue que vous avez sélectionnée est 'Mandinka'
        8005551210 > 123 o koo test
        8005551210 < i si yanfuma nte niy kumanaa fahamula. Foo unoken fo upur?
        8005551210 > 123 koo to
        8005551210 < i si yanfuma man nindulaalon, ye mune miira nonexistant1, nonexistant2.
        """

