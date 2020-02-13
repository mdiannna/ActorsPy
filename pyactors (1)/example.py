import gevent
from gevent.queue import Queue

from actor import Actor


def raise_(err):
    raise err


def handler(msg_out):
    def __inner(self, msg_in):
        print(msg_in)
        self.system.get_actor(msg_out).inbox.put(msg_out)
        self.system.make_actor("dier", lambda self, msg: raise_(Exception))
        self.system.get_actor("dier").inbox.put("die")
        gevent.sleep(0)
    return __inner


class ActorSystem(object):
    def __init__(self):
        self._registry = {}

    def make_actor(self, name, handler):
        # system_self = self
        TempActor = type("TempActor", (Actor,), {"receive": handler, "system": self})
        actor = TempActor(name)
        self._registry[name] = actor

    def get_actor(self, name):
        return self._registry.get(name)

    def start(self):
        [actor.start() for actor in self._registry.values()]

    def shutdown(self):
        gevent.joinall(self._registry.values())


sys = ActorSystem()

sys.make_actor("pinger", handler("ponger"))
sys.make_actor("ponger", handler("pinger"))
sys.make_actor("ganger", lambda self, msg: self.system.get_actor("ponger").inbox.put("ganger"))
sys.start()

sys.get_actor("pinger").inbox.put("start")

sys.shutdown()
