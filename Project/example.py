import gevent
from gevent.queue import Queue
from gevent import Greenlet
from actor import Actor

class Pinger(Actor):
    def receive(self, message):
        print(message)
        pong.inbox.put('ping')
        gevent.sleep(0)

class Ponger(Actor):
    # pentru fiecare task - un actor calculeaza, altul forecast etc, metoda receive
    def receive(self, message):
        print(message)
        ping.inbox.put('pong')
        gevent.sleep(1)

    # def send(self, message, address):


ping = Pinger()
pong = Ponger()

ping.start()
pong.start()

ping.inbox.put('start')
gevent.joinall([ping, pong])