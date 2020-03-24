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
from .webactor import WebActor

# from restartpolicies import SupervisorRestartPolicy, WorkerRestartPolicy, RequestorRestartPolicy
from . import prettyprint
from .workersupervisor import WorkerSupervisor

 
class Pool(Actor):
    def __init__(self):
        super().__init__()
        directory = Directory()

        self.supervisor = WorkerSupervisor("Supervisor", directory)
        self.requestor = Requestor('Client', directory)
        self.printer_actor = PrinterActor('PrinterActor')
        self.web_actor = WebActor('WebActor')

        directory.add_actor("supervisor", self.supervisor)
        directory.add_actor("client", self.requestor)
        directory.add_actor("printeractor", self.printer_actor)
        directory.add_actor("webactor", self.web_actor)


    def start(self):
        self.requestor.start()
        self.supervisor.start()
        self.printer_actor.start()
        self.web_actor.start()
        self.requestor.inbox.put('start')
        gevent.joinall([self.requestor, self.supervisor])


    def get_actors(self):
        return [self.requestor, self.supervisor]
