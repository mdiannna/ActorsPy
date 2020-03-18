import gevent
from gevent.queue import Queue
from enum import Enum
from gevent import Greenlet
# from ..mysseclient import with_requests
# from ...mysseclient import with_requests
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

# class SupervisorRestartPolicy(Actor):
        
#     OneForOneStrategy(maxNrOfRetries = 10, withinTimeRange = 1 minute) {
#       case _: ArithmeticException      => Resume
#       case _: NullPointerException     => Restart
#       case _: IllegalArgumentException => Stop
#       case _: Exception                => Escalate
#     }

     
# in caz ca eroare - trebuie policy de restartat supervisor si client  (requestor)
class Pool(Actor):
    def __init__(self, n):
        # Actor.__init__(self)
        super().__init__()
        directory = Directory()

        self.supervisor = WorkerSupervisor("Supervisor", directory)
        self.requestor = Requestor('Client', directory)

        directory.add_actor("supervisor", self.supervisor)
        directory.add_actor("client", self.requestor)

        # self.supervisor_restart_policy = SupervisorRestartPolicy()

    def start(self):
        self.requestor.start()
        self.supervisor.start()
        self.requestor.inbox.put('start')
        gevent.joinall([self.requestor, self.supervisor])

    def get_actors(self):
        return [self.requestor, self.supervisor]


###################
# main
###################
# IF using actor => this message might not appear at the beginning of the project
# printer_main = PrinterActor("Printer actor")
# printer_main.start()
# printer_main.inbox.put({"text":"Program started", "type":"header"})

prettyprint.print_header("Program started")

# gevent.joinall([gevent.spawn(go)])

# pool = Pool(10) # try 2, 3, 5, 8...
# gevent.joinall([gevent.spawn(pool.start)])