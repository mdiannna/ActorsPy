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
import prettyprint

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


from mysseclient import with_requests
# from mysseclient import with_urllib3
import json

import sseclient
import pprint


class Requestor(Actor):
    def __init__(self, name):
        Actor.__init__(self)
        self.name = name
        self.state = States.Idle
        
        self.url = 'http://0.0.0.0:4000/iot'
        # response = with_urllib3(url)  
        self.response = with_requests(self.url)


    def loop(self, supervisor):
        global cnt_test

        # while True:
            
        client = sseclient.SSEClient(self.response)
        for event in client.events():

            self.state = States.Running
            
            print(event)
            print(event.data)

            gevent.sleep(1)
            print("...Requesting work...")

            if(event.data=='{"message": panic}'):
              print("PANIC")
              supervisor.inbox.put('PANIC')
            else:
                # print(json.loads(event.data))
                pprint.pprint(json.loads(event.data))
                sensors_data = json.loads(event.data)["message"]
                print(sensors_data)
                supervisor.inbox.put('Some work.')

            print("----")


            
            # if(cnt_test>=10):
            #     cnt_test =0
            #     supervisor.inbox.put('PANIC')
            # else:
            #     print("Some work")
            #     supervisor.inbox.put('Some work.')

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


class PrinterActor(Actor):
    def __init__(self, name):
        Actor.__init__(self)
        self.name = name
        self.state = States.Idle

    def start(self):
        Actor.start(self)

    def receive(self, message):
        # message["text"]
        # message["type"]
        if message["type"]=="warning":
            prettyprint.print_warning(message["text"])
        if message["type"]=="warning-bold":
            prettyprint.print_warning(prettyprint.bold(message["text"]))
        if message["type"]=="error":
            prettyprint.print_error(prettyprint.bold(message["text"]))
        if message["type"]=="blue" or message["type"]=="normal":
            prettyprint.print_blue(message["text"])
        if message["type"]=="green" or message["type"]=="ok" or message["type"]=="success":
            prettyprint.print_green(message["text"])
        if message["type"]=="underline":
            prettyprint.print_underline(message["text"])
        if message["type"]=="header":
            prettyprint.print_header(message["text"])


class WorkerSupervisor(Actor):
    def __init__(self, name):
        Actor.__init__(self)
        self.name = name
        self.workers = Queue(maxsize=MAX_WORK_CAPACITY_SUPERVISOR)
        # self.supervisor_strategy = RoundRobinIndexer(len(workers))
        self.supervisor_strategy = RoundRobinIndexer(2)
        # self.supervisor_strategy = VariableActorsStrategy(len(workers))
        self.state = States.Idle

        # self.add_worker("worker1")    
        # self.add_worker("worker2")    
        self.workers_cnt_id = 0

        self.add_worker()    
        self.add_worker()    

        self.printer_actor = PrinterActor("Supervisor_printer")
        self.printer_actor.start()


        self.demandWorkQueue = Queue(maxsize=MAX_WORK_CAPACITY_SUPERVISOR)

    # def add_worker(self, name):
    #     new_worker = Worker(name)
    #     new_worker.start()
    #     self.workers.put(new_worker)
    def add_worker(self):
        self.workers_cnt_id += 1
        new_worker = Worker("worker%d" % self.workers_cnt_id)
        prettyprint.print_warning("ADD WORKER %d" % self.workers_cnt_id)

        new_worker.start()
        self.workers.put(new_worker)

    # Don't know if needed
    def add_inactive_worker(self, name):
        new_worker = Worker(name)
        # new_worker.start()
        self.workers.put(new_worker)

    def remove_worker(self):
        print("--qsize", self.workers.qsize())
        worker = self.workers.get()
        print("Remove worker %s" % worker.get_name())
        worker.stop()
        print("--qsize", self.workers.qsize())
        


    def start(self):
        Actor.start(self)

        # for w in self.workers:
            # w.start()

    def receive(self, message):
        # print(self.printer_actor)
        self.printer_actor.inbox.put({"text":'Receives work', "type":'normal'})
        # print("Receives work")
        # if -1 == len(self.workers) - 1:
        if -1 == self.workers.qsize() - 1 or self.workers.empty():
            self.printer_actor.inbox.put({"text":"Supervisor received work but no workers to give it to!",
                "type":"error"})
            self.printer_actor.inbox.put({"text":"Adding new worker", "type":"warning"})
            self.add_worker()
            # raise Exception("Supervisor received work but no workers to give it to!")

        # if MAX_WORK_CAPACITY_SUPERVISOR <= self.demandWorkQueue.qsize():
            # raise Exception("Too much work!")

        # print("demandWorkQueue size:")
        # print(self.demandWorkQueue.qsize())

        # self.demandWorkQueue.put(message)
        self.demandWorkQueue.put(message)
        print("Demand work: %d" %self.demandWorkQueue.qsize())



        current_worker = self.workers.get()

        print("Sending work to worker %s [%d]" % (current_worker.name, self.inbox.qsize()))

        # current_actor = self.workers[index]
        current_actor = current_worker




        # ////////////////
        # IF MESSAGE==PANIC
        if(message=='{"message": panic}' or message=="panic" or message=="PANIC"):
            # print("PANIC")
            self.printer_actor.inbox.put({"text":"!!! PANIC !!!", "type":'warning-bold'})

            name = current_actor.get_name()

            worker_to_be_restarted = Worker(name)
            worker_to_be_restarted.start()

            current_actor.stop()

            self.printer_actor.inbox.put({"text":"--killed worker %s" % name, "type":'warning'})
            # print("--killed worker %s" % name)
            
            # self.workers[index] = worker_to_be_restarted
            # # print(worker_to_be_restarted)
            # # print(worker_to_be_restarted.get_state())
            # print(self.workers[index])
            # # directory.add_actor("client", requestor)

            self.workers.put(worker_to_be_restarted)
            # worker_to_be_restarted.inbox.put(message)
            self.printer_actor.inbox.put({"text":"--restarted worker %s" %worker_to_be_restarted.get_name(), "type":'warning'})
            # print("--restarted worker %s" %worker_to_be_restarted.get_name())
            # /////////////////////////////
        else:
            self.workers.put(current_actor)
            current_actor.inbox.put(message)

        # Only for test, to be deleted
        global cnt_test

        # THIS WORKS!!!
        # TODO:check if doesn't exceed max workers
        # if cnt_test ==5:
        if(self.demandWorkQueue.qsize()>2):
            # self.add_worker("new_worker%d" %self.workers.qsize())
            self.add_worker()
            # print("Add new_worker_%d"%self.workers.qsize())
        
        if(self.demandWorkQueue.qsize()>4):
            # self.add_worker("new_worker%d" %self.workers.qsize())
            self.add_worker()
            self.add_worker()

        if(self.demandWorkQueue.qsize()>6):
            # self.add_worker("new_worker%d" %self.workers.qsize())
            self.add_worker()
            self.add_worker()
            self.add_worker()

        if(self.demandWorkQueue.qsize()>8):
            for i in range(1, self.demandWorkQueue.qsize()/1.5):
                self.add_worker()
                
        #THIS WORKS!!!
        # TODO:check if not empty
        # if cnt_test ==6:
        if (self.workers.qsize()> (self.demandWorkQueue.qsize()+ 6)):
            for i in range(self.demandWorkQueue.qsize()-self.workers.qsize()):
                self.remove_worker()
        else:
            if(self.workers.qsize()>( self.demandWorkQueue.qsize()+ 4)):
                self.remove_worker()
                self.remove_worker()
            else:
                if(self.workers.qsize()>( self.demandWorkQueue.qsize()+ 2)):
                    self.remove_worker()
            
        

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
        # self.workers = []

        # for i in range(0, n):
        #     self.workers.append(Worker("worker-%d" % i))

        self.supervisor = WorkerSupervisor("Supervisor")
        self.requestor = Requestor('Client')

        directory.add_actor("supervisor", self.supervisor)
        directory.add_actor("client", self.requestor)

    def start(self):
        self.requestor.start()
        self.supervisor.start()
        self.requestor.inbox.put('start')
       # de ascuns in ceva abstract - sa nu se vada ca e gevent
        gevent.joinall([self.requestor, self.supervisor])

    def get_actors(self):
        return [self.requestor, self.supervisor]

# def go():
#     requestor = Requestor('Client')
#     worker = Worker("Worker-1")
#     worker2 = Worker("Worker-2")
#     supervisor = WorkerSupervisor("Supervisor", [worker, worker2])

#     directory.add_actor("supervisor", supervisor)
#     directory.add_actor("client", requestor)

#     requestor.start()
#     supervisor.start()

#     requestor.inbox.put('start')

#     # de ascuns in ceva abstract - sa nu se vada ca e gevent

#     gevent.joinall([requestor, supervisor])



###################
# main
###################
# IF using actor => this message might not appear at the beginning of the project
# printer_main = PrinterActor("Printer actor")
# printer_main.start()
# printer_main.inbox.put({"text":"Program started", "type":"header"})

prettyprint.print_header("Program started")

directory = Directory()
# gevent.joinall([gevent.spawn(go)])

pool = Pool(10) # try 2, 3, 5, 8...
gevent.joinall([gevent.spawn(pool.start)])