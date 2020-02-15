# Python actors using gevent libev.
#
# [gevent](http://www.gevent.org/index.html)
# [libev](http://software.schmorp.de/pkg/libev.html)
#
# Jason Giedymin <jason g _at_ g mail dot com>
#
# This example serves as a simple play between four actors.
#   - 2 Workers
#   - 1 Supervisor
#   - 1 Client
#
# The client begins by looking up in a directory of who the current
# supervisor is. The supervisor is in charge of the two workers
# for the purpose of sending them work. The workers each pull
# from their mail box, does the work, and sends it to the client.
# The workers deal directly to the client.
#
# Workers take 3 seconds to do work, and since there are only two
# workers, with work being assigned every half second the
# workers cannot catch up. Changing the pool of workers to 5 helps
# meet the work demanded by the client, but not for long.
#
# The workers could have dealt directly with the supervisor, which
# then in turn dealt with the client.
#
# The workers or supervisor (if the above was true) could also have
# dealt with a directory actor, if one was created.
#
# The directory is global, meant for read-only after instantiation.
#
# To run this play, you will need to run the following:
#     pip install -U greenlet
#     pip install -U gevent
#     pip install -U enum34
#
# Then simply run `python actors.py`.
#

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

class RoundRobinIndexer:
    def __init__(self, n):
        if n <= 1:
            raise Exception("RoundRobinIndexer count must be >= 1")

        self.queue = Queue(maxsize=n)

        for i in range(0, n):
            self.queue.put(i)

    def next(self):
        value = self.queue.get()
        self.queue.put(value)
        return value

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

class Requestor(Actor):
    def __init__(self, name):
        Actor.__init__(self)
        self.name = name
        self.state = States.Idle

    def loop(self, supervisor):
        while True:
            self.state = States.Running
            gevent.sleep(.5)
            print("...Requesting work...")
            supervisor.inbox.put('Some work.')

    def ack(self):
        print("\n !! Thanks worker !!\n")

    def receive(self, message):
        if message == "work done":
            gevent.spawn(self.ack)
        elif message == "start":
            print("Requestor starting...")
            supervisor = directory.get_actor('supervisor')
            gevent.spawn(self.loop, supervisor)


class Worker(Actor):
    def __init__(self, name):
        Actor.__init__(self)
        self.name = name
        self.state = States.Idle

    def receive(self, message):
        self.state = States.Running
        print("I %s was told to do '%s' [%d]" %(self.name, message, self.inbox.qsize()))
        gevent.sleep(3)
        client = directory.get_actor("client")
        client.inbox.put("work done")
        self.state = States.Idle

class WorkerSupervisor(Actor):
    def __init__(self, name, workers):
        Actor.__init__(self)
        self.name = name
        self.workers = workers
        self.supervisor_strategy = RoundRobinIndexer(len(workers))
        self.state = States.Idle

    def start(self):
        Actor.start(self)

        for w in self.workers:
            w.start()

    def receive(self, message):
        if -1 == len(self.workers) - 1:
            raise Exception("Supervisor received work but no workers to give it to!")

        index = self.supervisor_strategy.next()
        print("Sending work to worker %s [%d]" % (self.workers[index].name, self.inbox.qsize()))

        self.workers[index].inbox.put(message)

class Directory:
    def __init__(self):
        self.actors = {}

    def add_actor(self, name, actor):
        self.actors[name] = actor

    def get_actor(self, name):
        if name in self.actors:
            return self.actors[name]

class Pool(Actor):
    def __init__(self, n):
        Actor.__init__(self)
        self.workers = []

        for i in range(0, n):
            self.workers.append(Worker("worker-%d" % i))

        self.supervisor = WorkerSupervisor("Supervisor", self.workers)
        self.requestor = Requestor('Client')

        directory.add_actor("supervisor", self.supervisor)
        directory.add_actor("client", self.requestor)

    def start(self):
        self.requestor.start()
        self.supervisor.start()
        self.requestor.inbox.put('start')
        gevent.joinall([self.requestor, self.supervisor])

    def get_actors(self):
        return [self.requestor, self.supervisor]

# If you didn't like pool
def go():
    requestor = Requestor('Client')
    worker = Worker("Worker-1")
    worker2 = Worker("Worker-2")
    supervisor = WorkerSupervisor("Supervisor", [worker, worker2])

    directory.add_actor("supervisor", supervisor)
    directory.add_actor("client", requestor)

    requestor.start()
    supervisor.start()

    requestor.inbox.put('start')

    gevent.joinall([requestor, supervisor])

directory = Directory()
# gevent.joinall([gevent.spawn(go)])

pool = Pool(2) # try 2, 3, 5, 8...
gevent.joinall([gevent.spawn(pool.start)])