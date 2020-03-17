import gevent
from gevent.queue import Queue
from enum import Enum
from gevent import Greenlet

class States(Enum):
    Idle = 0
    Stopped = 1
    Running = 2
    Failed = 3

class Work(Enum):
    Event = 0
    Misc = 1


class Actor(gevent.Greenlet):

    def __init__(self):
        self.inbox = Queue()
        Greenlet.__init__(self)

    def receive(self, message):
        raise NotImplemented("Be sure to implement this.")

    def _run(self):
        """
        Upon calling run, begin to receive items from actor's inbox.
        """
        self.running = True

        while self.running:
            message = self.inbox.get()
            self.receive(message)

    def stop(self):
        self.state = States.Stopped
        self.running = False
        Greenlet.kill(self)
 
    def get_state(self):
        return self.state

    def get_name(self):
        return self.name

