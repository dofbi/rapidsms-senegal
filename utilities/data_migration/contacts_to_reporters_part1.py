#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

11/29/09 The following script is used to migrate data 
from the old contacts models into the new reporters model

"""
from django.db import connection

def run():
    print "starting contacts to reporters part 1"
    create_backends()
    create_reporters()
    remove_channels()
    cleanup()
    print "done"                 
            
def create_backends():
    from apps.contacts.models import Contact, CommunicationChannel, ChannelConnection
    from apps.reporters.models import Reporter, PersistantBackend, PersistantConnection
    # create various connection objects
    channels = CommunicationChannel.objects.all()
    for channel in channels:
        backend,created = PersistantBackend.objects.get_or_create(slug=channel.backend_slug, 
                                    title=channel.title)  
    # check
    channel_count = channels.count()
    backend_count = PersistantBackend.objects.all().count()
    if channel_count != backend_count:
        raise Exception("channel count does not match backend count! %s %s" \
                        % (channel_count, backend_count))

def create_reporters():
    from apps.contacts.models import Contact, CommunicationChannel, ChannelConnection
    from apps.reporters.models import Reporter, PersistantBackend, PersistantConnection

    # add reporter_id, allowing null values for now
    cursor = connection.cursor()
    cursor.execute("ALTER TABLE `contacts_contact` ADD COLUMN `reporter_id` INT(11) DEFAULT NULL AFTER `node_ptr_id`;")
    cursor.execute("ALTER TABLE `contacts_contact` ADD CONSTRAINT `reporter_id_refs_id_32f59ca5` FOREIGN KEY (`reporter_id`) REFERENCES `reporters_reporter` (`id`);")
    cursor.execute("ALTER TABLE `contacts_contact` ADD CONSTRAINT UNIQUE `reporter_id_unique` (`reporter_id`);")

    all_contacts = Contact.objects.all()
    for contact in all_contacts:
        print "processing contact %s" % contact.get_signature()
        
        # NEW reporter models
        rep = Reporter()
        rep.alias = contact.unique_id
        rep.first_name = contact.given_name
        rep.last_name = contact.family_name
        rep.language = contact._locale
        rep.save()
        
        contact.reporter = rep
        contact.save()
        
        # check
        conns = contact.channel_connections.all()
        conns_count = conns.count()
        if conns_count==0:
            print "%s has no connections" % (contact.get_signature())
        elif conns_count>1:
            print "%s has more than one connections" % (contact.get_signature())

        # create various connection objects
        for conn in conns:
            new_conn = PersistantConnection()
            new_conn.identity = conn.user_identifier
            new_conn.backend = PersistantBackend.objects.get(slug=conn.communication_channel.backend_slug)
            new_conn.reporter = rep
            new_conn.save()
            conn.delete()
                   
    # check
    unassociated_contacts = Contact.objects.filter(reporter=None)
    if len(unassociated_contacts)>0:
        print "PROBLEMS WITH GENERATING REPORTERS!"
        print "UNASSOCIATED: "
        for con in unassociated_contacts:
            print " contact id: %s\n" % con.id 

    # check
    contact_count = all_contacts.count()
    reporter_count = Reporter.objects.all().count()
    if contact_count != reporter_count:
        raise Exception("Mismatch between contact and reporter count! %s %s" \
                        % (contact_count, reporter_count))

def remove_channels():
    from apps.contacts.models import Contact, CommunicationChannel, ChannelConnection
    from apps.reporters.models import Reporter, PersistantBackend, PersistantConnection
    # drop old connection objects
    channels = CommunicationChannel.objects.all()
    for channel in channels:
        channel.delete()

"""
Fields that stay in contact: 
        first_seen = models.DateTimeField(auto_now_add=True)
        common_name = models.CharField(max_length=255,blank=True)
        location = models.ForeignKey(Location, null=True, blank=True)
        gender = models.CharField(max_length=1,choices=GENDER_CHOICES,blank=True) 
        age_months = models.IntegerField(null=True,blank=True)
        _permissions = models.PositiveSmallIntegerField(default=__PERM_RECEIVE | __PERM_SEND)
        _quota_send_max = models.PositiveSmallIntegerField(default=0)
        _quota_send_period = models.PositiveSmallIntegerField(default=0) # period in minutes
        _quota_send_period_begin = models.DateTimeField(null=True,blank=True)
        _quota_send_seen = models.PositiveSmallIntegerField(default=0) # num messages seen in current period
        _quota_receive_max = models.PositiveSmallIntegerField(default=0)
        _quota_receive_period = models.PositiveSmallIntegerField(default=0) # period in minutes
        _quota_receive_period_begin = models.DateTimeField(null=True,blank=True)
        _quota_receive_seen = models.PositiveSmallIntegerField(default=0) # num messages seen in current period

"""
            
def cleanup():
    cursor = connection.cursor()
    cursor.execute("ALTER TABLE `contacts_contact` MODIFY COLUMN `reporter_id` INT(11) NOT NULL AFTER `node_ptr_id`;")

    # manually trim old db tables
    cursor.execute("ALTER TABLE `contacts_contact` DROP COLUMN `given_name`;")
    cursor.execute("ALTER TABLE `contacts_contact` DROP COLUMN `family_name`;")
    cursor.execute("ALTER TABLE `contacts_contact` DROP COLUMN `unique_id`;")
    cursor.execute("ALTER TABLE `contacts_contact` DROP COLUMN `location_id`;")
    cursor.execute("ALTER TABLE `contacts_contact` DROP COLUMN `_locale`;")
    
    cursor.execute("DROP TABLE `smsforum_community`;")
    cursor.execute("RENAME TABLE `smsforum_village` TO `smsforum_community`;")
    cursor.execute("ALTER TABLE `smsforum_community` ADD COLUMN `notes` longtext AFTER `location_id`;")
    cursor.execute("DROP TABLE `smsforum_villagealias`;")
    cursor.execute("DROP TABLE `smsforum_membershiplog`;")

