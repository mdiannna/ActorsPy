from .supervisorrestartpolicy import SupervisorRestartPolicy
# from .requestorrestartpolicy import RequestorRestartPolicy
import gevent
from gevent.queue import Queue
from enum import Enum
from gevent import Greenlet


class Directory:
    def __init__(self):
        self.actors = {}
        self.supervisor_restart_policy = SupervisorRestartPolicy()
        # self.requestor_restart_policy = RequestorRestartPolicy()

    def add_actor(self, name, actor):
        self.actors[name] = actor

    def get_actor(self, name):
        if name in self.actors:
            return self.actors[name]

    def get_actors_names(self):
        result = []
        for name in self.actors:
            result.append(name)
        return result
            
    def __repr__(self):
        return str(self.get_actors_names())

    def remove_actor(self, actor):
        gevent.kill(actor)

    def restart_supervisor(self, supervisor):
        name = supervisor.get_name()

        if name in self.actors:
            supervisor_to_restart = self.actors[name]
            
        new_supervisor = self.supervisor_restart_policy.restart(supervisor)

        self.actors[name] = new_supervisor.get_name()
        return new_supervisor

    def restart_requestor(self, requestor):
        name = requestor.get_name()

        if name in self.actors:
            requestor_to_restart = self.actors[name]
        
        new_requestor = self.requestor_restart_policy.restart(requestor)

        self.actors[name] = new_requestor.get_name()
        return new_requestor
