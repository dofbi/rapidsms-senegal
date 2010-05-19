#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.tests.harness import MockRouter, MockBackend
from rapidsms.message import Message
from rapidsms.connection import Connection
import time
import backend

class Backend(backend.Backend):
    """
    Dummy backend to test construction of connections

    """
    def __init__ (self, router):
        Receiver.__init__(self)
        self._router = router
        self._running = False
       
    @property
    def running (self):
        return self._running

    def start(self):
        self._running = True
        try:
            self.run()
        finally:
            self._running = False

    def run (self):
        while self.running:
            time.sleep(1)
    
    def stop(self):
        self._running = False
   
    def message(self, identity, text, date=None):
        c = Connection(self, identity)
        return Message(c, text, date)

    def route(self, msg):
        # do nothing
        pass

