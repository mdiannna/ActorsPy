import gevent
from gevent.queue import Queue
from gevent import Greenlet
from actor2 import Actor

class Pinger(Actor):
    def receive(self, message):
        print(message)
        pong.inbox.put('PANIC')
        gevent.sleep(0)

class Ponger(Actor):
    def __init__(self):
        super(Ponger, self).__init__()
        self.cnt =1
        Greenlet.__init__(self)

	# pentru fiecare task - un actor calculeaza, altul forecast etc, metoda receive
    def receive(self, message):
        print(message)
    
        # TODO:
        # if(message=='PANIC'):
        #     self.stop()
        #     return

        ping.inbox.put('pong')
        gevent.sleep(1)
        self.cnt = self.cnt + 1

        if(self.cnt>3):
            self.stop()
            ping.kill()

    # def send(self, message, address):


ping = Pinger()
pong = Ponger()

ping.start()
pong.start()

ping.inbox.put('start')
gevent.joinall([ping, pong])