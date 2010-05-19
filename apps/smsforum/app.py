#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

""""
DEPENDENCIES: 
logger, contacts
"""
from pygsm import gsmcodecs
import logging
import re, os
import rapidsms
from rapidsms.parsers.bestmatch import BestMatch, MultiMatch
import gettext
import traceback
from apps.smsforum.models import Village, villages_for_contact, MembershipLog
from apps.contacts.models import Contact

MAX_LATIN_SMS_LEN = 160 
MAX_LATIN_BLAST_LEN = MAX_LATIN_SMS_LEN - 20 # reserve 20 chars for us
MAX_UCS2_SMS_LEN = 70 
MAX_UCS2_BLAST_LEN = MAX_UCS2_SMS_LEN - 10 # reserve 10 chars for info
MAX_VILLAGE_NAME_LEN = 40
MAX_CONTACT_NAME_LEN = 30

CMD_MARKER=ur'(?:[\.\*\#]|(?:123))'
DM_MESSAGE_MATCHER = re.compile(ur'^\s*'+CMD_MARKER+'(.+?)'+ \
                                    CMD_MARKER+'\s*(.+)?', re.IGNORECASE)
CMD_MESSAGE_MATCHER = re.compile(ur'^\s*'+CMD_MARKER+'\s*(\S+)?(.+)?',re.IGNORECASE)


         
#
# Module level translation calls so we don't have to prefix everything 
# so we don't have to prefix _t() with 'self'!!
#

# Mutable globals hack 'cause Python module globals are WHACK
_G = { 
    'SUPPORTED_LANGS': {
        # 'deb':u'Debug',
        'pul':['Pulaar','Pular'],
        'wol':['Wolof'],
        'dyu':['Joola','Dyula','Dioula','Diola'],
        'snk':['Sooninke','Soninke','Soninké','Sooninké'],
        'mnk':['Mandinka','Mandingo'],
        'fr':[u'Français',u'Francais'],
        'en':['English'],
        },
    'TRANSLATORS':dict(),
    'DEFAULT_LANG':'fr',
    'ADMIN_CMD_PWD': None
    }

#####################
# Helpful Decorator #
#####################

def passwordProtectedCmd(f):
    """
    Password protect command calls.

    NOTE: only works within this module as
    depends on global config

    """
    def pwd_protected_f(*args, **kwargs):
        if _G['ADMIN_CMD_PWD'] != None:
            cmd_string = kwargs.pop('arg').strip()
            msg = args[1] # args[0] is the app object
            pwd,sp,rest = cmd_string.partition(' ')
            if pwd.strip() != _G['ADMIN_CMD_PWD']:
                msg.sender.send_response_to(
                    _st(msg.sender, 'admin-cmd-fail_pwd-incorrect')
                    )
                return True
            
            kwargs['arg'] = rest.strip()
        return f(*args, **kwargs)
    return pwd_protected_f

########
# i18n #
########
def _init_translators():
    path = os.path.join(os.path.dirname(__file__),"locale")
    for lang,name in _G['SUPPORTED_LANGS'].items():
        trans = gettext.translation('django',path,[lang,_G['DEFAULT_LANG']])
        _G['TRANSLATORS'].update( {lang:trans} )

def _t(locale, text):
    """translate text with default language"""
    translator=_G['TRANSLATORS'][_G['DEFAULT_LANG']]
    if locale in _G['TRANSLATORS']:
        translator=_G['TRANSLATORS'][locale]
    return translator.ugettext(text)

def _st(sender,text):
    """translate a message for the given sender"""
    # TODO: handle fall back from say eng_US to eng
    # AND mappings from old-stylie two letter ('en') to 
    # new hotness 3-letter codes 'eng'
    return _t(sender.locale, text)


#
# App class
#

class App(rapidsms.app.App):
    def __init__(self, router):
        rapidsms.app.App.__init__(self, router)
        
        # NB: this cannot be called globally
        # because of depencies between GNUTranslations (a -used here) 
        # and DJangoTranslations (b -used in views)
        # i.e. initializing b then a is ok, but a then b fails
        _init_translators()

        # command target. ToDo--get names from gettext...
        # needs to be here so that 'self' has meaning.
        # could also do the hasattr thing when calling instead
        self.cmd_targets = [ 
            # NOTE: make sure all commands are unicode strings!
            # Pulaar
            ([u'naalde', u'naatde', u'tawtude',u'naattugol'], {'lang':'pul','func':self.join}),
            (u'yettoode', {'lang':'pul','func':self.register_name}),
            ([u'yaltude',u'iwde'], {'lang':'pul','func':self.leave}),
            ([u'dallal',u'ballal'], {'lang':'pul','func':self.help}),
            (u'penngugol', {'lang':'pul','func':self.create_village}),
            # Wolof
            ([u'boole', u'yokk', u'duggu'], {'lang':'wol','func':self.join}),
            ([u'genn', u'génn'], {'lang':'wol','func':self.leave}),
            ([u'sant', u'tur'], {'lang':'wol','func':self.register_name}),
            (u'ndimbal', {'lang':'wol','func':self.help}),
            # Dyuola    
            ([u'unoken', u'ounoken'], {'lang':'dyu','func':self.join}),
            ([u'karees', u'karees'], {'lang':'dyu','func':self.register_name}),
            ([u'upur', u'oupour'], {'lang':'dyu','func':self.leave}),
            (u'rambenom', {'lang':'dyu','func':self.help}),
            # Soninke
            (u'ro', {'lang':'snk','func':self.join}),
            (u'toxo', {'lang':'snk','func':self.register_name}),
            (u'bagu', {'lang':'snk','func':self.leave}),
            (u'deema', {'lang':'snk','func':self.help}),
            (u'taga', {'lang':'snk','func':self.create_village}),
            # Mandinka
            (u'koo', {'lang':'mnk','func':self.join}),
            (u'ntoo', {'lang':'mnk','func':self.register_name}),
            (u'nbetaamala', {'lang':'mnk','func':self.leave}),
            (u"n'deemaa", {'lang':'mnk','func':self.help}),
            # French
            (u'entrer', {'lang':'fr','func':self.join}),
            (u'nom', {'lang':'fr','func':self.register_name}),
            (u'quitter', {'lang':'fr','func':self.leave}),
            (u'aide', {'lang':'fr','func':self.help}),
            ([u'créer', u'creer'], {'lang':'fr','func':self.create_village}),
            (u'enlever', {'lang':'fr','func':self.destroy_community}),
            (u'langue', {'lang':'fr','func':self.lang}),
            # English
            (u'join', {'lang':'en','func':self.join}),
            (u'name', {'lang':'en','func':self.register_name}),
            (u'leave', {'lang':'en','func':self.leave}),
            (u'help', {'lang':'en','func':self.help}),
            (u'create', {'lang':'en','func':self.create_village}),
            (u'member', {'lang':'en','func':self.member}),
            (u'citizens', {'lang':'en','func':self.community_members}),
            (u'remove', {'lang':'en','func':self.destroy_community}),
            ]
        
        self.cmd_matcher=BestMatch(self.cmd_targets)
        #villes=[(v.name, v) for v in Village.objects.all()]
        #self.village_matcher=BestMatch(villes, ignore_prefixes=['keur'])
        # swap dict so that we send in (name,code) tuples rather than (code,name
        self.lang_matcher=BestMatch([
                (names,code) for code,names in _G['SUPPORTED_LANGS'].items()
                ])
        
    def __get_village_matcher(self):
        """
        HACK to force reload of names before each match
        
        """
        villes = []
        for v in Village.objects.all():
            names = [v.name] + [a.alias for a in v.aliases.all()]
            villes.append( (names,v) )
        return BestMatch(villes, ignore_prefixes=['keur'])
        
    def configure(self, **kwargs):
        try:
            _G['DEFAULT_LANG'] = kwargs.pop('default_lang')
        except:
            pass

        try:
            _G['ADMIN_CMD_PWD'] = kwargs.pop('admin_cmd_pwd')
        except:
            pass

    def start(self):
        self.__loadFixtures()
    
    #####################
    # Message Lifecycle #
    #####################
    def handle(self, msg):
        self.__log_incoming_message(msg, villages_for_contact(msg.sender))
        self.debug("In handle smsforums: %s" % msg.text)
        
        # check permissions
        if msg.sender.perm_ignore:
            self.debug('Ignoring sender: %s' % msg.sender.signature)
            return False

        if not msg.sender.can_send:
            self.debug('Sender: %s does no have receive perms' % msg.sender.signature)
            self.__reply(msg,'inbound-message_rejected')
        
        # Ok, we're all good, start processing
        msg.sender.sent_message_accepted(msg)
        
        #
        # Now we figure out if it's a direct message, a command, or a blast
        #
        # ok, this is a little weird, but stay with me.
        # commands start with '.' '*' or '#'--the cmd markers. e.g. '.join <something>'
        # addresses are of form cmd_marker address cmd_mark--e.g. '.jeff. hello'
        #
        address=None
        rest=None

        # check for direct message first
        m=DM_MESSAGE_MATCHER.match(msg.text)
        if m is not None:
            address=m.group(1).strip()
            rest=m.group(2)
            if rest is not None:
                rest=rest.strip()
            return self.blast_direct(msg,address,rest)
        
        # are we a command?
        m=CMD_MESSAGE_MATCHER.match(msg.text)
        if m is None:
            # we are a blast
            return self.blast(msg)

        # we must be a command
        cmd,rest=m.groups()
        if cmd is None:
            #user tried to send some sort of command (a message with .,#, or *, but nothing after)
            self.__reply(msg,"command-not-understood")
            return True
        else:
            cmd=cmd.strip()

        if rest is not None:
            rest=rest.strip()

        # Now match the possible command to ones we know
        cmd_match=self.cmd_matcher.match(cmd,with_data=True)

        if len(cmd_match)==0:
            # no command match
            self.__reply(msg,"command-not-understood")
            return True

        if len(cmd_match)>1:
            # too many matches!
            self.__reply(msg, 'command-not-understood %(sug_1)s %(sug_rest)s', \
                              { 'sug_1':', '.join([t[0] for t in cmd_match[:-1]]),
                                'sug_rest':cmd_match[-1:][0][0]})
            return True
        #
        # Ok! We got a real command
        #
        cmd,data=cmd_match[0]
        #arg=msg_text[msg_match.end():]

        # set the senders default language, if not sent
        if msg.sender.locale is None:
            msg.sender.locale=data['lang']
            msg.sender.save()
        return data['func'](msg,arg=rest)

    def outgoing(self, msg):
        # TODO
        # create a ForumMessage class
        # log messages with associated domain
        # report on dashboard
        pass
        

    ####################
    # Command Handlers #
    ####################
    def help(self, msg,arg=None):
        if arg is not None and len(arg)>0:
            # see if it is a language and send help 
            # for that lang
            langs=self.lang_matcher.match(arg,with_data=True)
            if len(langs)==1:
                self.__reply(msg, "help-with-commands_%s" % langs[0][1])
                return True
            else:
                # send the list of available langs by passing
                # to the 'lang' command handler
                return self.help(msg)
            
        self.__reply(msg, "help-with-commands")
        return True

    @passwordProtectedCmd
    def create_village(self, msg, arg=None):
        self.debug("SMSFORUM:CREATEVILLAGE")        
        if arg is None or len(arg)<1:
            self.__reply(msg, "create-village-fail_no-village-name")
            return True
        else:
            village = arg

        if len(Village.objects.filter(name=village)) != 0:
            self.__reply(msg, "create-village-fail_village-already-exists %(village)s", {'village':village})
            return True
        try:
            # TODO: add administrator authentication
            if len(village) > MAX_VILLAGE_NAME_LEN:
                self.__reply(msg, "create-village-fail_name-too-long %(village)s %(max_char)d", \
                             {'village':village, 'max_char':MAX_VILLAGE_NAME_LEN} )
                return True
            ville = Village(name=village)
            ville.save()
            # self.village_matcher.add_target((village,ville))
            self.__reply(msg, "create-village-success %(village)s", {'village':village} )
        except:
            self.debug( traceback.format_exc() )
            traceback.print_exc()
            self.__reply(msg, "internal-error")

        return True
             
    def member(self,msg,arg=None):
        try:
            villages=villages_for_contact(msg.sender)
            if len(villages)==0:
                self.__reply(msg, "member-fail_not-member-of-village")
            else:
                village_names = ', '.join([v.name for v in villages])
                txt = "member-success %(village_names)s"
                if len(villages)>5: 
                    villages = villages[0:5]
                    txt = "member-success_long-list %(village_names)s"
                self.__reply(msg, txt, {"village_names":village_names})
        except:
            traceback.print_exc()
            self.debug( traceback.format_exc() )
            rsp= _st(msg.sender,"internal-error")
            self.debug(rsp)
            self.__reply(msg,rsp)
        return True

    @passwordProtectedCmd
    def community_members(self,msg,arg=None):
        if arg is None or len(arg)==0:
            self.__reply(msg, "citizens-fail_no-village")
            return True

        villes=self.__get_village_matcher().match(arg,with_data=True)
        if len(villes)==0:
            self.__reply(msg, "village-not-known %(unknown)s", {'unknown':arg})
            return True

        for name,ville in villes:
            members=[c.get_signature(max_len=10) for c in \
                         ville.flatten(klass=Contact)]
            if len(members)>20: 
                members = members[0:20]
                txt = 'citizens-success_long-list %(village)s %(citizens)s'
            else:
                txt = 'citizens-success %(village)s %(citizens)s'
                
            self.__reply(msg, txt, {'village':name, 'citizens':','.join(members)})
        return True

    @passwordProtectedCmd
    def destroy_community(self,msg,arg=None):
        if arg is None or len(arg)==0:
            self.__reply(msg, "remove-fail_no-village")
            return True

        try:
            # EXACT MATCH ONLY!
            ville=Village.objects.get(name=arg)
            # the following really shouldn't be necessary
            # but under MySQL InnoDB, this seems to be required
            logs = MembershipLog.objects.filter(village=ville)
            for log in logs:
                log.village = None
                log.save()
            ville.delete()
            # self.village_matcher.remove_target(arg)
            self.__reply(msg, "remove-success %(village)s", {'village': arg})
            return True
        except Exception, e:
            rsp= _st(msg.sender,"village-not-known %(unknown)s") % {'unknown':arg} 
            self.debug(rsp)
            self.__reply(msg,rsp)
        return True

            
    def register_name(self,msg,arg=None):
        if arg is None or len(arg)==0:
            self.__reply(msg,"name-acknowledge %(name)s",
                         {'name':msg.sender.common_name})
            return True

        name=arg
        try:
            if len(name) > MAX_CONTACT_NAME_LEN:
                self.__reply(msg, "name-register-fail_name-too-long %(name)s %(max_char)d", \
                             {'name':name, 'max_char':MAX_CONTACT_NAME_LEN} )
                return True
            msg.sender.common_name = name.strip()
            msg.sender.save()
            rsp=_st(msg.sender, "name-register-success %(name)s") % {'name':msg.sender.common_name}
            self.__reply(msg,rsp)
        except:
            traceback.print_exc()
            self.debug( traceback.format_exc() )
            rsp= _st(msg.sender, "internal-error")
            self.debug(rsp)
            self.__reply(msg,rsp)

        return True

    def join(self,msg,arg=None):
        if arg is None or len(arg)==0:
            return self.__suggest_villages(msg)
        else:
            village=arg

        try:
            matched_villes=self.__get_village_matcher().match(village,with_data=True)
            # send helpful message if 0 or more than 1 found
            num_villes=len(matched_villes)
            # unzip data from names if can
            if num_villes>0:
                village_names,villages=zip(*matched_villes)

            if num_villes==0 or num_villes>1:
                if num_villes==0:
                    return self.__suggest_villages(msg)
                else:
                    # use all hit targets
                    rsp=_st(msg.sender, "village-not-found %(suggested)s") % \
                        {"suggested": ', '.join(village_names)}
                    self.__reply(msg,rsp)
                    return True
            
            # ok, here we got just one
            assert(len(villages)==1)
            villages[0].add_children(msg.sender)
            rsp=_st(msg.sender, "join-success %(village)s") % {"village": village_names[0]}
            self.debug(rsp)
            self.__reply(msg,rsp)
        except:
            traceback.print_exc()
            self.debug( traceback.format_exc() )
            rsp=_st(msg.sender, "internal-error")
            self.debu        self.debug('REPSONSE Tmsg.sender, "blast-fail_not-member-of-any-village")
            self.debug(rsp)
            self.__reply(msg,rsp)
            return True

        recips=[v.name for v in villes]
        ok,blast_text,enc=self.__prep_blast_message(msg,msg.text,recips)
        if not ok:
            # message was too long, prep already
            # sent a reply to the sender, so we just 
            # return out
            return True

        # respond to sender first because the delay between now 
        # and the last recint can be long
        #
        # TODO: send a follow-up is message sending fails!
        rsp= _st(msg.sender, "blast-acknowledge %(text)s %(recipients)s") % \
            {'recipients':', '.join(recips),'text':msg.text.strip()} 
        self.debug('REPSONSE TO BLASTER: %s' % rsp)
        self.__reply(msg,rsp)

        return se      ('gsm',MAX_LATIN_BLAST_LEN) if gsm_enc \
                    else ('ucs2',MAX_UCS2_BLAST_LEN))
            
        if len(out_text)>max_len:
            if encoding == 'ucs2':
                rsp= _st(msg.sender, "blast-fail_message-too-long_ucs2 %(msg_len)d %(max_unicode)d") % \
                    {
                    'msg_len': len(out_text),
                    'max_unicode': MAX_UCS2_BLAST_LEN
                    }
            else:
                rsp= _st(msg.sender, "blast-fail_message-too-long %(msg_len)d %(max_latin)d") % \
                    {
                    'msg_len': len(out_text),
                    'max_latin': MAX_LATIN_BLAST_LEN,
                    } 
            self.__reply(msg,rsp)
            return (False, None, encoding)

        # ok, we're long enough, lets make the blast text
        # we replace '%(sender)s' with '%(sender)s' so that
        # localized strings can put the sender where they want
        # we then do another subsitution after we pick the send signature
        blast_tmpl=_st(msg.sender, "blast-message_outgoing %(text)s %(recipients)s %(sender)s") % \
            { 'text':out_text, 'recipients':', '.join(recipients), 'sender': '%(sender)s'}

        #add signature
        tmpl_len=len(blast_tmpl)-10  # -10 accounts from sig placeholder ('%(sender)s')
        max_sig=max_len-tmpl_len
        sig=msg.sender.get_signature(max_len=max_sig,for_message=msg)
        blast_text = blast_tmpl % {'sender': sig}
        return (True, blast_text, encoding)

    def __blast_to_villages(self, villes, sender, text):
        """Takes actual village objects"""
        if villes is None or len(villes)==0:
            return True

        recipients=set()
        for ville in villes:
            recipients.update(ville.flatten(klass=Contact))
            
        # now iterate every member of the group we are broadcasting
        # to, and queue up the same message to each of them
        for recipient in recipients:
            if recipient != sender:
                self.__blast_to_contact(recipient,text)
        vnames = ', '.join([v.name for v in villes])
        self.debug("success! %(villes)s recvd msg: %(txt)s" % { 'villes':vnames,'txt':text})
        return True

    def __blast_to_contact(self, contact, text):
        """Returns True is message sent"""
        if contact.can_receive:
            self.debug('Blast msg: %s to: %s' % (text,contact.signature))
            # TODO: move to lib/pygsm/gsm.py
            # currently just log messages that are too long
            # since these are not handled properly in modem
            self._check_message_length(text)
            contact.send_to(text)
            return True
        else:
            return False

    def leave(self,msg,arg=None):
        self.debug("SMSFORUM:LEAVE: %s" % arg)
        try:
            villages=[]
            if arg is not None and len(arg)>0:
                village_tupes = self.__get_village_matcher().match(arg, with_data=True)
                if len(village_tupes)>0:
                    villages = zip(*village_tupes)[1] # the objects
            else:
                villages = villages_for_contact(msg.sender)
            if len(villages)>0:
                names = list()
                for ville in villages:
                    ville.remove_children(msg.sender)
                    names.append(ville.name)
                self.__reply(msg, "leave-success %(villages)s",
                             { "villages": ','.join(names)})
            else:
                if arg is not None and len(arg)>0:
                    self.__reply(msg, "leave-fail_village-not-found %(village)s", {'village':arg})
                else:
                    self.__reply(msg, "leave-fail_not-member-of-village")
        except:
            # something went wrong - at the
            # moment, we don't care what
            traceback.print_exc()
            self.debug( traceback.format_exc() )
            self.__reply(msg, "internal-error")

        return True

    def lang(self,msg,arg=None):
        name=arg
        self.debug("SMSFORUM:LANG:Current locale: %s" % msg.sender.locale)
        
        def _return_all_langs():
            # return available langs
            langs_sorted=[l[0] for l in _G['SUPPORTED_LANGS'].values()]
            langs_sorted.sort()
            rsp=_st(msg.sender, "language-set-fail_code-not-understood %(langs)s") % \
                { 'langs':', '.join(langs_sorted)}
            self.__reply(msg,rsp)
            return True

        if name is None or len(name)==0:
            return _return_all_langs()
        
        # see if we have that language
        langs=self.lang_matcher.match(name.strip(),with_data=True)
        if len(langs)==1:
            name,code=langs[0]
            msg.sender.locale=code
            msg.sender.save()
            rsp = _st(msg.sender, 'language-set-success %(lang)s') % { 'lang': name }
            self.__reply(msg,rsp)
            return True       
        else:
            # invalid lang code, send them a list
            return _return_all_langs()

            
    #
    # Private helpers
    # 
    def __reply(self,msg,reply_text,format_values=None):
        """
        Formats string for response for message's sender 
        the message's associated sender.

        """
        reply_text=_st(msg.sender,reply_text) 
        if format_values is not None:
            try:
                reply_text = reply_text % format_values
            except TypeError:
                err="Not all format values: %r were used in the string: %s" %\
                    (format_values, reply_text)
                self.error(err)
        # TODO: move to lib/pygsm/gsm.py
        # currently just log messages that are too long
        # since these are not handled properly in modem
        self._check_message_length(reply_text)
        msg.sender.send_response_to(reply_text)
    
    def __suggest_villages(self,msg):
        """helper to send informative messages"""
        # pick some names from the DB
        village_names = [v.name for v in Village.objects.all()[:3]]
        if len(village_names) == 0:
            village_names = _st(msg.sender,"village_name")
        else: 
            village_names=', '.join(village_names)
        self.__reply(msg,"village-not-found %(suggested)s", {"suggested": village_names})
        return True

    def __loadFixtures(self):
        pass

    def __log_incoming_message(self,msg,domains):
        #msg.persistent_msg should never be none if app.logger is used
        #this is to ensure smsforum does not fail even if logger fails...
        if hasattr(msg,'persistent_msg'):
            for domain in domains:
                msg.persistent_msg.domains.add(domain)
        else:
            logging.error('persistent_msg not create for msg: %s from %s' % \
                          (msg.text, msg.sender.signature) )

    def _check_message_length(self, text):
        """
        This function DOES NOT belong here - a temporary measure until 
        rapidsms has a good api for backends to speak to router
        
        checks message length < 160 if gsm, else <70 if ucs-2/utf16
        """

        gsm_enc=True
        try:
            text.encode('gsm')
        except:
            gsm_enc=False
        finally:
            encoding,max_len=(\
                ('gsm',MAX_LATIN_SMS_LEN) if gsm_enc \
                    else ('ucs2',MAX_UCS2_SMS_LEN))
        
        if len(text)>max_len:
            err= ("ERROR: %(encoding)s MESSAGE OF LENGTH '%(msg_len)d' IS TOO LONG. Max is %(max)d.") % \
                         {
                'encoding': encoding,
                'msg_len': len(text),
                'max': MAX_LATIN_SMS_LEN if encoding=='gsm' else MAX_UCS2_SMS_LEN
                } 
            self.error(err)
            return False
        return True

    def update_village_lang (self , msg ):
        # Tring to fine the user 's lang
        lang = lang_from_message (msg)
        if lang is None:
                # msg.respond ("lang-not-yet-configured")
                self.__reply (msg, _st (msg , "lang-not-yet-found "))
        else:
                # get the django lang  from the given lang
                django_lang = utility.get_lang (lang)
                if not django_lang:
                        self.__reply (msg, _st(msg , "django-lang-error"))
                else:
                    indentity  = msg.connection.identity 
                    contact = Contacts.objects.filter (
                            identity = identity ).count ())             
                    if contact  ==0:
                            self.__reply (_st(msg.respond ("contact-not-found")
                    else:
                           contact.lang= lang
                           contact.save ()
                           self.__reply (_st(msg.respond ("contact-lang-updated")))
                            