import gevent
from gevent.queue import Queue
from enum import Enum
from gevent import Greenlet
import json
import sseclient
import pprint

from .actors import Actor, States, Work
from .requestor import Requestor
from .printeractor import PrinterActor
from .directory import Directory
# from restartpolicies import SupervisorRestartPolicy, WorkerRestartPolicy, RequestorRestartPolicy
from . import prettyprint
from .workersupervisor import WorkerSupervisor

 
class Pool(Actor):
    def __init__(self, n):
        super().__init__()
        directory = Directory()

        self.supervisor = WorkerSupervisor("Supervisor", directory)
        self.requestor = Requestor('Client', directory)

        directory.add_actor("supervisor", self.supervisor)
        directory.add_actor("client", self.requestor)


    def start(self):
        self.requestor.start()
        self.supervisor.start()
        self.requestor.inbox.put('start')
        gevent.joinall([self.requestor, self.supervisor])


    def get_actors(self):
        return [self.requestor, self.supervisor]
