"""

This would ideally go in __init__ so that it could be used 
by both runserver and router

For now, we put it here, since putting it in __init__
raises 'database not defined' errors

TODO: fix and move this into __init__

"""

import logging
from rapidsms.webui.settings import RAPIDSMS_APPS as app_conf
from apps.logtracker.handlers import TrackingHandler

# Initialise and register the handler
handler = TrackingHandler()

#the log_threshold is the ini value for what level the error 
# handler should listen for if it's less than the threshold 
# set, the handler will never trigger. 
logging.root.setLevel(int(app_conf['logtracker']['log_threshold']))
logging.root.addHandler(handler)
