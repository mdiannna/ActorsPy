from .supervisorrestartpolicy import SupervisorRestartPolicy
import gevent
from gevent.queue import Queue
from enum import Enum
from gevent import Greenlet

class Directory:
    def __init__(self):
        self.actors = {}
        self.supervisor_restart_policy = SupervisorRestartPolicy()

    def add_actor(self, name, actor):
        self.actors[name] = actor

    def get_actor(self, name):
        if name in self.actors:
            return self.actors[name]

    def remove_actor(self, actor):
        gevent.kill(actor)

    # TODO: restart_requestor??
    def restart_supervisor(self, supervisor):
        name = supervisor.get_name()

        if name in self.actors:
            supervisor_to_restart = self.actors[name]
        
        # new_supervisor = WorkerSupervisor(name)
        new_supervisor = self.supervisor_restart_policy.restart(supervisor)

        self.actors[name] = new_supervisor.get_name()
        return new_supervisor

