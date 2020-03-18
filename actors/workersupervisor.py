from .actors import Actor, States, Work
from .worker import Worker
from gevent.queue import Queue
from .workerrestartpolicy import WorkerRestartPolicy
from .printeractor import PrinterActor

class WorkerSupervisor(Actor):

    def __init__(self, name, directory, workers_array=[]):
        # Actor.__init__(self)
        super().__init__()
        self.name = name
        self.state = States.Idle
        self.max_work_capacity = 10
        self.workers = Queue(maxsize=self.max_work_capacity)
        self.workers_cnt_id = 0
        self.worker_restart_policy = WorkerRestartPolicy()
        self.printer_actor = PrinterActor("Supervisor_printer")
        self.printer_actor.start()
  
        self.directory = directory

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
       
        self.demandWorkQueue = Queue(maxsize=self.max_work_capacity * 2)


    def add_worker(self):
        self.workers_cnt_id += 1
        new_worker = Worker("worker%d" % self.workers_cnt_id, self.directory)
        # prettyprint.print_warning("ADD WORKER %d" % self.workers_cnt_id)
        self.printer_actor.inbox.put({"text":"ADD WORKER %d" % self.workers_cnt_id, "type":'warning'})

        new_worker.start()
        self.workers.put(new_worker)


    def add_named_worker(self, name):
        self.workers_cnt_id += 1
        new_worker = Worker(name, self.directory)
        self.printer_actor.inbox.put({"text":"ADD NAMED WORKER %s" % name, "type":'warning'})

        new_worker.start()
        self.workers.put(new_worker)

    # Don't know if needed
    def add_inactive_worker(self, name):
        new_worker = Worker(name, self.directory)
        # new_worker.start()
        self.workers.put(new_worker)

    def remove_worker(self):
        worker = self.workers.get()
        self.printer_actor.inbox.put({"text":"REMOVE WORKER %s" % worker.get_name(), "type":'warning'})
        worker.stop()
        
    def get_directory(self):
        return self.directory

    def start(self):
        Actor.start(self)       

    def process_panic_message(self, current_worker):
        # print("PANIC")
        self.printer_actor.inbox.put({"text":"!!! PANIC !!!", "type":'warning-bold'})

        worker_to_be_restarted = self.worker_restart_policy.restart_worker(current_worker)

        name = current_worker.get_name()
        # worker_to_be_restarted.inbox.put(message)
        self.printer_actor.inbox.put({"text":"--killed worker %s" % name, "type":'warning'})
        self.workers.put(worker_to_be_restarted)
        self.printer_actor.inbox.put({"text":"--restarted worker %s" %worker_to_be_restarted.get_name(), "type":'warning'})

     
    def adapt_number_of_workers(self):
        # Cases when to add workers
        if(self.demandWorkQueue.qsize()>2 and (self.workers.qsize()<self.max_work_capacity)):
            self.add_worker()
        
        if(self.demandWorkQueue.qsize()>4 and (self.workers.qsize()+2<=self.max_work_capacity)):
            self.add_worker()
            self.add_worker()

        if(self.demandWorkQueue.qsize()>6 and (self.workers.qsize()+3<=self.max_work_capacity)):
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
    

    def get_printer_actor(self):
        return self.printer_actor            

    
    def receive(self, message):
        self.printer_actor.inbox.put({"text":'Receives work', "type":'normal'})       
        self.demandWorkQueue.put(message)

        self.printer_actor.inbox.put({"text": str("Demand work: %d" %self.demandWorkQueue.qsize()), "type":'green'})

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

        # IF MESSAGE==PANIC
        if(message=='{"message": panic}' or message=="panic" or message=="PANIC"):
           self.process_panic_message(current_worker)
        else:
            self.printer_actor.inbox.put({"text":"Sending work to worker %s [%d]" % (current_worker.name, self.inbox.qsize()), "type":"warning"})
            current_worker.inbox.put(message)
            self.workers.put(current_worker)

        self.adapt_number_of_workers()