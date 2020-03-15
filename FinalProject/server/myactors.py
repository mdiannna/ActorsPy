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

from mysseclient import with_requests
# from mysseclient import with_urllib3
import json

import sseclient
import pprint

import weather

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

    # def restart(self):
    #     self.state = States.Running
    #     self.running = True
    
    def get_state(self):
        return self.state

    def get_name(self):
        return self.name





class Requestor(Actor):
    def __init__(self, name):
        Actor.__init__(self)
        self.name = name
        self.state = States.Idle
        
        self.url = 'http://0.0.0.0:4000/iot'
        # response = with_urllib3(url)  
        self.response = with_requests(self.url)

        # self.supervisor_restart_policy = SupervisorRestartPolicy()
        self.printer_actor = PrinterActor("Requestor_printer")
        self.printer_actor.start()


    def loop(self):
        # while True:
            
        client = sseclient.SSEClient(self.response)
        for event in client.events():

            self.state = States.Running
            
            # only for debug
            # print(event)
            # print(event.data)

            # gevent.sleep(1)
            # gevent.sleep(0.2)
            gevent.sleep(0.5)
            # print("...Requesting work...")
            self.printer_actor.inbox.put({"text":"...Requesting work...", "type":"warning"})


            if(event.data=='{"message": panic}'):
              #for debug
              # print("PANIC")
              self.printer_actor.inbox.put({"text":" PANIC  ", "type":"error"})
              self.supervisor.inbox.put('PANIC')
            else:
                if(event.data=='restart_supervisor'):
                    self.printer_actor.inbox.put({"text":" !!!Restart Supervisor!!! ", "type":"error"})

                    # only for debug
                    # prettyprint.print_blue("Supervisorr:" + str(self.supervisor.get_name()))

                    supervisor = directory.restart_supervisor(self.supervisor)

                    # self.supervisor = directory.get_actor('supervisor')
                    self.supervisor = supervisor
                    # Only for debug
                    # prettyprint.print_green("Supervisor:" + str(self.supervisor.get_name()))
                    # prettyprint.print_green("workers:" + str(self.supervisor.workers))
                    # prettyprint.print_green("workers:" + str(self.supervisor.workers.qsize()))
                else:
                    # print(json.loads(event.data))


                    self.printer_actor.inbox.put({"text":json.loads(event.data), "type":"pprint"})

                    # pprint.pprint(json.loads(event.data))
                    sensors_data = json.loads(event.data)["message"]
                    # print(sensors_data)
                    self.supervisor.inbox.put(sensors_data)

            # print("----")
            self.printer_actor.inbox.put({"text":"----", "type":"blue"})



    def ack(self):
        # print("\n !! Thanks worker !!\n")
        # prettyprint.print_success("\n !! Thanks worker !!\n")
        self.printer_actor.inbox.put({"text":"\n !! Thanks worker !!\n", "type":"success"})

        # self.supervisor.inbox.put('Thanks!')


    def receive(self, message):
        if message == "work done":
            gevent.spawn(self.ack)
        elif message == "start":
            self.printer_actor.inbox.put({"text":"Requestor starting...", "type":"header"})
            # print("Requestor starting...")
            self.supervisor = directory.get_actor('supervisor')
            gevent.spawn(self.loop)


class WorkerRestartPolicy():
    def restart_worker(self, current_worker):
        name = current_worker.get_name()

        worker_to_be_restarted = Worker(name)
        worker_to_be_restarted.start()

        current_worker.stop()
        return worker_to_be_restarted
        


class Worker(Actor):
    def __init__(self, name):
        Actor.__init__(self)
        self.name = name
        self.state = States.Idle
        self.printer_actor = PrinterActor("Worker_printer")
        self.printer_actor.start()

    def receive(self, message):
        self.state = States.Running
        self.printer_actor.inbox.put({"text":"I %s was told to process '%s' [%d]" %(self.name, message, self.inbox.qsize()), "type":"blue"})


        # athm_pressure, humidity, light, temperature, wind_speed = aggregate_sensor_values(message)

        # print("I %s was told to process '%s' [%d]" %(self.name, message, self.inbox.qsize()))
        gevent.sleep(3)
        client = directory.get_actor("client")
        client.inbox.put("work done")
        self.state = States.Idle


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
        if(message["type"]=="pprint"):
            print("!!!")
            pprint.pprint(message["text"]["message"])


# class SupervisorRestartPolicy(Actor):
        
#     OneForOneStrategy(maxNrOfRetries = 10, withinTimeRange = 1 minute) {
#       case _: ArithmeticException      => Resume
#       case _: NullPointerException     => Restart
#       case _: IllegalArgumentException => Stop
#       case _: Exception                => Escalate
#     }


class SupervisorRestartPolicy():
    def restart(self, supervisor):
        workers_children = []

        while(not supervisor.workers.empty()):
            worker = supervisor.workers.get()
            new_worker = worker.get_name()
            worker.stop()

            workers_children.append(new_worker)

        supervisor_name = supervisor.get_name()
        supervisor.stop()

        new_supervisor = WorkerSupervisor(supervisor_name, workers_array=workers_children)
        new_supervisor.start()
        return new_supervisor


        

class WorkerSupervisor(Actor):

    def __init__(self, name, workers_array=[]):
        Actor.__init__(self)
        self.name = name
        self.state = States.Idle
        self.max_work_capacity = 10
        self.workers = Queue(maxsize=self.max_work_capacity)
        self.workers_cnt_id = 0
        self.worker_restart_policy = WorkerRestartPolicy()
        
        if len(workers_array)>0:
            for worker_name in workers_array:
                # print("WORKER_NAME", worker_name)
                self.add_named_worker(worker_name)    
        else:
            self.add_worker()    
            self.add_worker()    
            self.add_worker()    
            self.add_worker()    
            self.add_worker()    
        
        self.printer_actor = PrinterActor("Supervisor_printer")
        self.printer_actor.start()

        self.demandWorkQueue = Queue(maxsize=self.max_work_capacity * 2)


    def add_worker(self):
        self.workers_cnt_id += 1
        new_worker = Worker("worker%d" % self.workers_cnt_id)
        prettyprint.print_warning("ADD WORKER %d" % self.workers_cnt_id)

        new_worker.start()
        self.workers.put(new_worker)

    def add_named_worker(self, name):
        self.workers_cnt_id += 1
        new_worker = Worker(name)
        # prettyprint.print_warning("ADD NAMED WORKER %s" % name)
        self.printer_actor.inbox.put({"text":"ADD NAMED WORKER %s" % name, "type":'warning'})


        new_worker.start()
        self.workers.put(new_worker)

    # Don't know if needed
    def add_inactive_worker(self, name):
        new_worker = Worker(name)
        # new_worker.start()
        self.workers.put(new_worker)

    def remove_worker(self):
        # only for debug
        # print("--qsize", self.workers.qsize())
        worker = self.workers.get()
        self.printer_actor.inbox.put({"text":"Remove worker %s" % worker.get_name(), "type":'warning'})
        # prettyprint.print_warning("Remove worker %s" % worker.get_name())
        worker.stop()
        # only for debug
        # print("--qsize", self.workers.qsize())
        


    def start(self):
        Actor.start(self)

        # for w in self.workers:
            # w.start()

    def receive(self, message):

        # if(message=="Thanks!"):
        #     return

        # print(self.printer_actor)
        self.printer_actor.inbox.put({"text":'Receives work', "type":'normal'})
            
        self.demandWorkQueue.put(message)

        self.printer_actor.inbox.put({"text": str("Demand work: %d" %self.demandWorkQueue.qsize()), "type":'green'})

        # print("Demand work: %d" %self.demandWorkQueue.qsize())
        

        if -1 == self.workers.qsize() - 1 or self.workers.empty():
            self.printer_actor.inbox.put({"text":"Supervisor received work but no workers to give it to!",
                "type":"error"})
            if self.workers.qsize() < self.max_work_capacity:
                self.printer_actor.inbox.put({"text":"Adding new worker", "type":"warning"})
                self.add_worker()
            else:
                self.printer_actor.inbox.put({"text":"Max work Capacity exceeded!!! waiting for free worker", "type":"error"})
                return

            # raise Exception("Supervisor received work but no workers to give it to!")

        

        if self.workers.empty():
            self.printer_actor.inbox.put({"text":"No active worker. Adding new worker", "type":"warning"})
            self.add_worker()

        
        
        current_worker = self.workers.get()
        message = self.demandWorkQueue.get()


        # current_task = self.demandWorkQueue.get()

        # print("Sending work to worker %s [%d]" % (current_worker.name, self.inbox.qsize()))
        self.printer_actor.inbox.put({"text":"Sending work to worker %s [%d]" % (current_worker.name, self.inbox.qsize()), "type":"warning"})

        # current_actor = self.workers[index]
        # current_actor = current_worker




        # ////////////////
        # IF MESSAGE==PANIC
        if(message=='{"message": panic}' or message=="panic" or message=="PANIC"):
            # print("PANIC")
            self.printer_actor.inbox.put({"text":"!!! PANIC !!!", "type":'warning-bold'})


            worker_to_be_restarted = self.worker_restart_policy.restart_worker(current_worker)
            
            name = current_worker.get_name()
            # worker_to_be_restarted.inbox.put(message)
            self.printer_actor.inbox.put({"text":"--killed worker %s" % name, "type":'warning'})
            self.workers.put(worker_to_be_restarted)
            self.printer_actor.inbox.put({"text":"--restarted worker %s" %worker_to_be_restarted.get_name(), "type":'warning'})
        
            # worker_to_be_restarted = Worker(name)
            # worker_to_be_restarted.start()

            # current_worker.stop()

            # print("--killed worker %s" % name)
            
            # self.workers[index] = worker_to_be_restarted
            # # print(worker_to_be_restarted)
            # # print(worker_to_be_restarted.get_state())
            # print(self.workers[index])
            # # directory.add_actor("client", requestor)

        else:
            current_worker.inbox.put(message)
            self.workers.put(current_worker)



        # Cases when to add workers
        if(self.demandWorkQueue.qsize()>2 and (self.workers.qsize()<self.max_work_capacity)):
            # self.add_worker("new_worker%d" %self.workers.qsize())
            self.add_worker()
            # print("Add new_worker_%d"%self.workers.qsize())
        
        if(self.demandWorkQueue.qsize()>4 and (self.workers.qsize()+2<=self.max_work_capacity)):
            # self.add_worker("new_worker%d" %self.workers.qsize())
            self.add_worker()
            self.add_worker()

        if(self.demandWorkQueue.qsize()>6 and (self.workers.qsize()+3<=self.max_work_capacity)):
            # self.add_worker("new_worker%d" %self.workers.qsize())
            self.add_worker()
            self.add_worker()
            self.add_worker()

        if(self.demandWorkQueue.qsize()>8):
            for i in range(1, self.demandWorkQueue.qsize()/1.5):
                if self.workers.qsize()<self.max_work_capacity:
                    self.add_worker()
                
        # Cases when to remove workers
        if (self.workers.qsize()> (self.demandWorkQueue.qsize()+ 6)):
            for i in range(self.demandWorkQueue.qsize()-self.workers.qsize()):
                if(not self.workers.empty()):
                    self.remove_worker()
        else:
            if(self.workers.qsize()>( self.demandWorkQueue.qsize()+ 4)):
                if(not self.workers.empty()):
                    self.remove_worker()
                if(not self.workers.empty()):
                    self.remove_worker()
            # else:
                # if(self.workers.qsize()>( self.demandWorkQueue.qsize()+ 2)):
                    # self.remove_worker()
            


class Directory:
    def __init__(self):
        self.actors = {}
        self.supervisor_restart_policy = SupervisorRestartPolicy()

    def add_actor(self, name, actor):
        self.actors[name] = actor

    def get_actor(self, name):
        if name in self.actors:
            return self.actors[name]

    # TODO
    # def remove_actor(self, name, actor):
    def remove_actor(self, actor):
        gevent.kill(actor)

    # def restart_actor(self, name):
    def restart_supervisor(self, supervisor):
        name = supervisor.get_name()

        if name in self.actors:
            supervisor_to_restart = self.actors[name]
        
        # new_supervisor = WorkerSupervisor(name)
        new_supervisor = self.supervisor_restart_policy.restart(supervisor)

        self.actors[name] = new_supervisor.get_name()
        return new_supervisor




    # def restart_actor(self, name, actor):
    #     gevent.kill(actor)
    #     gevent.joinall(new_actor)

    # def restart_supervisor(self, supervisor):


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

        # self.supervisor_restart_policy = SupervisorRestartPolicy()

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