""" 

This exists to provide a utility for email alerts to be sent from runserver
(i.e. where no instance of router is accessible, so no access to email backend)

"""

from django.core.mail import SMTPConnection, EmailMessage
from rapidsms.webui.settings import RAPIDSMS_APPS as conf_app

class EmailAgent(object):
    """ A simple class for handling email sending """
    
    def __init__(self):
        """ Configure the default connection
        Here we take email settings from the email backend
        """
        self.conn = SMTPConnection(username=conf_app['logtracker']['username'],
                                   port=conf_app['logtracker']['smtp_port'],
                                   host=conf_app['logtracker']['smtp_host'],
                                   password=conf_app['logtracker']['password'],
                                   use_tls=True,
                                   fail_silently=False)

    def send_email(self, subject, recipient_addr, msg_payload):
        """ send a basic email message to the group """
        msg = EmailMessage(subject=subject, 
                           body=msg_payload,
                           from_email=conf_app['logtracker']['username'],
                           to=[recipient_addr],
                           connection=self.conn
                           )
        msg.content_subtype = "html"
        msg.send(fail_silently=False)
