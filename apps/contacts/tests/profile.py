#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from rapidsms.tests.scripted import TestScript
import apps.contacts.app as contacts_app
import apps.reporters.app as reporters_app
from reporters.models import Reporter, PersistantConnection
from contacts.models import Contact

class TestContactProfile (TestScript):
    apps = (contacts_app.App, reporters_app.App )

    def testContactCreation(self):
        reg_script = """
            reg_1 > anything goes
        """
        self.runScript(reg_script)
        try:
            conn = PersistantConnection.objects.get(identity="reg_1")
        except PersistantConnection.DoesNotExist:
            self.fail("PersistantConnectio not created properly")
        r = conn.reporter
        if r is None:
            self.fail("Reporter not created properly")
        try:
            r = Reporter.objects.get(pk=r.pk)
        except Reporter.DoesNotExist:
            self.fail("Reporter not saved properly")
        contact = r.get_profile()
        if contact is None:
            self.fail("Contact not created properly")
        try:
            contact = Contact.objects.get(id=contact.pk)
        except Reporter.DoesNotExist:
            self.fail("Contact not saved properly")
