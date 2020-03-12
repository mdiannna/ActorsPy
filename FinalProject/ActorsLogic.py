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
 

cnt_test = 0


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

# TODO: test
# TODO: use (Finite) Capacity Scheduling algorithm 
# production must be equal to demand
# if queue has > 5 data =>5 lucratori & increasing size
# if queue has < 1-3 data => 2 lucratori


class VariableActorsStrategy:
    def __init__(self, n):
        if n <= 1:
            raise Exception("Indexer count must be >= 1")

        self.max_capacity = n
        self.queue = Queue(maxsize=n)
        # self.queue.put(i)


        for i in range(0, n):
            self.queue.put(i)


    # TODO: change the status of worker from active to inactive?? and then restart them???
    # sau fix asa de gindit cum sa apara noi workeri
    def next(self, demand_size):
        if demand_size <=3:
            value = self.queue.get()
            # value.stop()
            if(self.queue.empty()):
                # value.start()

                self.queue.put(value)

        if demand_size >3 and demand_size <5:
            value = self.queue.get()
            if(self.queue.empty()):
                self.queue.put(value)
            value = self.queue.get()
            if(self.queue.empty()):
                self.queue.put(value)
            value = self.queue.get()
            if(self.queue.empty()):
                self.queue.put(value)

        if demand_size >=5 and demand_size < 7:
            value = self.queue.get()
            self.queue.put(value)        
        # TODO: add workers until max_capaciry
        if demand_size >=7:
            value = self.queue.get()
            self.queue.put(value)

            # new_worker = Worker("Worker-%d" % self.queue.qsize())
            # new_worker.start()
            # self.workers.append(new_worker)


        return value

    def lastDemand(self):
        pass



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

    # def restart(self):
    #     self.state = States.Running
    #     self.running = True
    
    def get_state(self):
        return self.state

class Requestor(Actor):
    def __init__(self, name):
        Actor.__init__(self)
        self.name = name
        self.state = States.Idle

    def loop(self, supervisor):
        global cnt_test

        while True:
            self.state = States.Running
            gevent.sleep(.5)
            print("...Requesting work...")
            
            if(cnt_test>=10):
                cnt_test =0
                supervisor.inbox.put('PANIC')
            else:
                supervisor.inbox.put('Some work.')

            cnt_test += 1

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

    def get_name(self):
        return self.name


MAX_WORK_CAPACITY_SUPERVISOR = 10

class WorkerSupervisor(Actor):
    def __init__(self, name, workers):
        Actor.__init__(self)
        self.name = name
        self.workers = workers
        # self.supervisor_strategy = RoundRobinIndexer(len(workers))
        self.supervisor_strategy = VariableActorsStrategy(len(workers))
        self.state = States.Idle
        
        self.demandWorkQueue = Queue(maxsize=MAX_WORK_CAPACITY_SUPERVISOR)


    def start(self):
        Actor.start(self)

        for w in self.workers:
            w.start()

    def receive(self, message):
        if -1 == len(self.workers) - 1:
            raise Exception("Supervisor received work but no workers to give it to!")

        if MAX_WORK_CAPACITY_SUPERVISOR <= self.demandWorkQueue.qsize():
            raise Exception("Supervisor received work but no workers to give it to!")

        # print("demandWorkQueue size:")
        # print(self.demandWorkQueue.qsize())

        self.demandWorkQueue.put(message)
        print(self.demandWorkQueue.qsize())


        # if(self.demandWorkQueue.qsize()>5):
        #     new_worker = Worker("Worker-%d" % self.queue.qsize())
        #     new_worker.start()
        #     self.workers.append(new_worker)


        index = self.supervisor_strategy.next(self.demandWorkQueue.qsize())
        # index = self.supervisor_strategy.next()
        print("Sending work to worker %s [%d]" % (self.workers[index].name, self.inbox.qsize()))

        current_actor = self.workers[index]
        




        # ////////////////
        # IF MESSAGE==PANIC
        if(message=='{"message": panic}' or message=="panic" or message=="PANIC"):
            print("PANIC")
            name = current_actor.get_name()

            worker_to_be_restarted = Worker(name)
            worker_to_be_restarted.start()

            current_actor.stop()

            print("killed worker %s" % name)
            
            self.workers[index] = worker_to_be_restarted
            # print(worker_to_be_restarted)
            # print(worker_to_be_restarted.get_state())
            print(self.workers[index])
            # directory.add_actor("client", requestor)

            # /////////////////////////////

        print(self.workers[index].get_state())

        # directory.add_actor(worker_to_be_restarted.get_name, worker_to_be_restarted)
        self.workers[index].inbox.put(message)
        # worker_to_be_restarted.inbox.put(message)
        # current_actor.inbox.put(message)

        self.demandWorkQueue.get()


class Directory:
    def __init__(self):
        self.actors = {}

    def add_actor(self, name, actor):
        self.actors[name] = actor

    def get_actor(self, name):
        if name in self.actors:
            return self.actors[name]


# ROuter sau RoundRobin Distributor
# de facut restartPolicy separat
# in caz ca eroare - trebuie policy de restartat supervisor si client  (requestor)
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

    # de ascuns in ceva abstract - sa nu se vada ca e gevent
    gevent.joinall([requestor, supervisor])

directory = Directory()
# gevent.joinall([gevent.spawn(go)])

pool = Pool(10) # try 2, 3, 5, 8...
gevent.joinall([gevent.spawn(pool.start)])