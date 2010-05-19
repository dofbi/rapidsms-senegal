#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import django
from django.db import models
from apps.nodegraph.models import NodeSet

MAX_LATIN_SMS_LEN = 160 

class MessageBase(models.Model):
    text = models.CharField(max_length=MAX_LATIN_SMS_LEN)
    # TODO save connection title rather than wacky object string?
    identity = models.CharField(max_length=150)
    backend = models.CharField(max_length=150)
    # this isn't modular
    # but it's optional and saves some ridiculous querying for smsforum frontpage
    # TODO save domain to wacky object string rather than connection title?
    # (to reduce app dependencies)
    domains = models.ManyToManyField(NodeSet, null=True)
    
    def __unicode__(self):
        return u'%s (%s) %s' % (self.identity, self.backend, self.text)
    
    class Meta:
        abstract = True
        # define permissions for web users
        permissions = (
            ("can_view", "Can view"),
        )

class IncomingMessage(MessageBase):
    received = models.DateTimeField(auto_now_add=True)
    
    # Helper methods to allow this object to be treated similar
    # to the outgoing message, e.g. if they are in the same list
    # in a template
    @property
    def date(self):
        '''Same as received''' 
        return self.received
    
    def is_incoming(self):
        return True
    
    def __unicode__(self):
        return u"%s %s" % (MessageBase.__unicode__(self), self.received)

    def update_translation(self, text):
        """ creates a dependency on MessageAnnotation 
        this code is messy; clean up later
        """
        note = None
        #notes = MessageAnnotation.objects.filter(message=m)
        notes = self.annotations.all()
        if len(notes) > 0: 
            note = notes[0]
        if note is None:
            if len(text) > 0:
                note = MessageAnnotation(message=self)
                note.text = text
                note.save()
        else:
            if len(text) == 0: 
                note.delete()
            else:
                note.text = text
                note.save()
    def update_tag (self , txt):
        """
        Allow to update an message's category 
        It store the category text of the message
        into the BasicTag table
        """
        from tagging.models import BasicTag
        if self.basictags.count ()>0:
                tag = self.basictags.all()[0]
                tag.txt = txt
                tag.save()
        else:
            tag = BasicTag (message =self)
            tag.txt =txt
            tag.save ()
           
class OutgoingMessage(MessageBase):
    sent = models.DateTimeField(auto_now_add=True)
    
    @property
    def date(self):
        '''Same as sent''' 
        return self.sent
    
    def is_incoming(self):
        return False
    
    def __unicode__(self):
        return u"%s %s" % (MessageBase.__unicode__(self), self.sent)

class CodeSet(models.Model):
    """
    An arbitrary set of codes with which messages can be tagged.
    e.g. category, state, flagged
    """
    name = models.CharField(max_length = 64, unique=True) 
    
    def __unicode__(self):
        return unicode(self.name)

class Code(models.Model):
    """
    This model holds codes which can be mapped to individual messages
    e.g. good/bad/ignore, open/inprogress/closed, flagged/not_flagged
    """
    set = models.ForeignKey(CodeSet, null=False)
    name = models.CharField(max_length = 64, unique=True) # e.g. sante, les droits humain, etc.
    slug = models.CharField(max_length = 8, unique=True) # e.g. san, dro, etc.
    
    def __unicode__(self):
        return u"%(name)s" % { 'name':self.name }

class MessageTag(models.Model):
    """
    A dynamic way of associating messages with codes without requiring that
    all messages be coded
    """
    message = models.ForeignKey(IncomingMessage)
    code = models.ForeignKey(Code)

    def __unicode__(self):
        return u"%(message)s: %(tag)s" % { 'message':self.message, 'tag':self.code }

class MessageAnnotation(models.Model):
    """
    A dynamic way of associating messages with free-form annotations
    without requiring that all messages be annotated
    """
    message = models.ForeignKey(IncomingMessage, related_name="annotations")
    text = models.CharField(max_length=255,blank=True)

    def __unicode__(self):
        return u"%(message)s: %(annotation)s" % { 'message':self.message, 'annotation':self.text }

