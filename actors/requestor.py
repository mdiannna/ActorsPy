from .printeractor import PrinterActor
from .actors import Actor, States, Work
from .mysseclient import with_requests
from .aggregator import Aggregator
from .mysseclient import with_urllib3
import requests
from .directory import Directory
from gevent.queue import Queue
from enum import Enum
import gevent
from gevent import Greenlet
import json
import requests
import sseclient
import os
# from app import app

class Requestor(Actor):
    def __init__(self, name, directory):
        # Actor.__init__(self)
        super().__init__()
        self.directory = directory
        self.name = name
        self.state = States.Idle        
        self.aggregator_actor = Aggregator("Aggregator actor", self)
        self.aggregator_actor.start()
  
        # self.url = 'http://0.0.0.0:4000/iot'
        


        # self.url = 'http://127.0.0.1:4000/iot'
        gevent.sleep(4)
        # self.url = 'http://patr:4000/iot'

        # self.url = app.config['EVENTS_SERVER_URL'] + '/iot'
        self.url = os.getenv('EVENTS_SERVER_URL') + '/iot'
        try:
            self.response = with_requests(self.url)
            print("OK")
        except:
            print("EXCEPTION")
            self.response = with_requests(self.url)

        self.printer_actor = PrinterActor("Requestor_printer")
        self.printer_actor.start()
        self.cnt = 2
        # gevent.sleep(4)

        # Don't know why, but it throws error without this initial request
        # self.help_url = 'http://127.0.0.1:4000/help'
        # self.help_url = 'http://patr:4000/help'
        # self.help_url = app.config['EVENTS_SERVER_URL'] + '/help'
        self.help_url = os.getenv('EVENTS_SERVER_URL') + '/help'

        r = requests.get(self.help_url)
        print(r.json())
        # gevent.sleep(2)

    def loop(self):

        client = sseclient.SSEClient(self.response)
        for event in client.events():
            
            self.state = States.Running
            
            # only for debug
            # print(event)
            # print(event.data)

            # gevent.sleep(1)
            # gevent.sleep(0.2)
            gevent.sleep(0.5)



            self.printer_actor.inbox.put({"text":"...Requesting work...", "type":"warning"})


            if(event.data=='{"message": panic}'):
              #for debug
              # print("PANIC")
              self.printer_actor.inbox.put({"text":" PANIC  ", "type":"error"})
              self.supervisor.inbox.put('PANIC')
            else:
                # if(event.data=='restart_supervisor'):
                #     self.printer_actor.inbox.put({"text":" !!!Restart Supervisor!!! ", "type":"error"})

                #     # only for debug
                #     # prettyprint.print_blue("Supervisorr:" + str(self.supervisor.get_name()))

                #     supervisor = directory.restart_supervisor(self.supervisor)

                #     # self.supervisor = directory.get_actor('supervisor')
                #     self.supervisor = supervisor
                #     # Only for debug
                #     # prettyprint.print_green("Supervisor:" + str(self.supervisor.get_name()))
                #     # prettyprint.print_green("workers:" + str(self.supervisor.workers))
                #     # prettyprint.print_green("workers:" + str(self.supervisor.workers.qsize()))
                # else:

                self.printer_actor.inbox.put({"text":json.loads(event.data), "type":"pprint"})
                # for debug
                # pprint.pprint(json.loads(event.data))
                sensors_data = json.loads(event.data)["message"]
                # print(sensors_data)
                self.supervisor.inbox.put(sensors_data)

            self.printer_actor.inbox.put({"text":"----", "type":"blue"})



    def ack(self, message):
        # print("\n !! Thanks worker !!\n")
        # prettyprint.print_success("\n !! Thanks worker !!\n")
        self.printer_actor.inbox.put({"text":"\n !! Thanks worker !!\n", "type":"success"})
        self.printer_actor.inbox.put({"text":message, "type":"header"})
        self.aggregator_actor.inbox.put(message)

    def show_final_result(self, message):
        # self.printer_actor.inbox.put({"text": "FINAL RESULT AGGREGATED:", "type":"green_header"})
        self.printer_actor.inbox.put({"text":message, "type":"green_header"})

    def receive(self, message):
        # if message == "work done":
        if "PREDICTED_WEATHER_FINAL:" in message:
            gevent.spawn(self.show_final_result(message))
        elif "PREDICTED_WEATHER:" in message:
            gevent.spawn(self.ack(message))
        elif message == "start":
            self.printer_actor.inbox.put({"text":"Requestor starting...", "type":"header"})
            # print("Requestor starting...")
            self.supervisor = self.directory.get_actor('supervisor')
            gevent.spawn(self.loop)

    def get_supervisor(self):
        return self.supervisor

    def get_printer_actor(self):
        return self.printer_actor
