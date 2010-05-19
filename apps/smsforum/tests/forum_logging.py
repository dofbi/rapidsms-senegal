#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from rapidsms.tests.scripted import TestScript
import apps.smsforum.app as smsforum_app
import apps.logger.app as logger_app
import apps.contacts.app as contacts_app
import apps.reporters.app as reporters_app
from apps.smsforum.views import get_outgoing_message_count_to
from apps.contacts.models import *
from apps.reporters.models import *
from apps.smsforum.models import Village, CommunityAlias
 
class TestLogging (TestScript):
    apps = (logger_app.App, reporters_app.App, contacts_app.App, smsforum_app.App )

    def testOutgoingMessageLog(self):
        """ Tests
        1. regular command and response
        2. receiving a blast message
        3. receiving a system message
        todo - test receiving a 'region' message
        """
        test_outgoing_message_log = """
            8005551210 > .create village
            8005551210 < Community 'village' was created
            8005551210 > .join village
            8005551210 < Thank you for joining the village community - welcome!
            8005551211 > .join village
            8005551211 < Thank you for joining the village community - welcome!
            8005551210 > message to blast
            8005551210 < Your message was sent to these communities: village
            8005551211 < message to blast - 8005551210
            8005551211 > .junk
            8005551211 < Sorry, I do not understand that command. Type '#help' to see a list of available commands            
            """
        self.runScript(test_outgoing_message_log)
        first_contact = contacts_from_identity("8005551210")
        second_contact = contacts_from_identity("8005551211")
        members = [first_contact]
        count = get_outgoing_message_count_to(members)
        self.assertEquals(count,3)
        members = [second_contact]
        count = get_outgoing_message_count_to(members)
        self.assertEquals(count,3)
        members = [first_contact,second_contact]
        count = get_outgoing_message_count_to(members)
        self.assertEquals(count,6)

    def testAliases(self):
        v = Village(name="original")
        v.save()
        v2 = CommunityAlias(community=v.community, alias="alias")
        v2.save()
        test_outgoing_message_log = """
            8005551210 > .join alias
            8005551210 < Thank you for joining the original community - welcome!
        """

def contacts_from_identity(identity):
    """ Gets a 'contact' given a user_identifier
    WARNING: This function assumes the identifier is globally unique
    """
    conn = PersistantConnection.objects.get(identity=identity)
    return Contact.objects.get(reporter=conn.reporter)

