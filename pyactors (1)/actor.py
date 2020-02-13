# https://medium.com/@ianjuma/the-actor-model-in-python-with-gevent-b8375d0986fa

import gevent
from gevent.queue import Queue
from gevent import Greenlet

class Actor(gevent.Greenlet):

    def __init__(self, name):
        self.inbox = Queue()
        # self.system = NotImplemented()
        # self.system = NotImplementedError()
        self.name = name
        Greenlet.__init__(self)

    def receive(self, message):
        """
        Define in your subclass.
        """
        username  = message.get('username')
        self.date = message.get('date')
        print("Received message:")
        print(message)
        # raise NotImplemented()

    # def send(self, message, address):
        # TODO

    def _run(self):
        print("Running")
        self.running = True

        while self.running:
            try:
                message = self.inbox.get()
                self.receive(message)
            except Exception:
                self.system.notify("I'm dead", self.name)
                # how to propageate to self.system.notify()
