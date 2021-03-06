from .printeractor import PrinterActor
from .actors import Actor, States, Work
from .mysseclient import with_requests
from .aggregator import Aggregator
from .mysseclient import with_urllib3
import requests
from .directory import Directory
from .webactor import WebActor
from gevent.queue import Queue
from enum import Enum
import gevent
from gevent import Greenlet
import json
import requests
import sseclient
import os


class Requestor(Actor):
    def __init__(self, name, directory):
        super().__init__()
        self.directory = directory
        self.name = name
        self.state = States.Idle        
        self.aggregator_actor = Aggregator("Aggregator actor", self)
        self.aggregator_actor.start()
  
        self.web_actor = WebActor()
        self.web_actor.start()
        gevent.sleep(4)
   
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
        
        self.help_url = os.getenv('EVENTS_SERVER_URL') + '/help'

        r = requests.get(self.help_url)
        print(r.json())
        # gevent.sleep(2)

    def loop(self):

        client = sseclient.SSEClient(self.response)
        for event in client.events():
            self.state = States.Running
            
            # only for debug
            # print(event.data)
            gevent.sleep(0.5)

            self.printer_actor.inbox.put({"text":"...Requesting work...", "type":"warning"})

            if(event.data=='{"message": panic}'):
              self.printer_actor.inbox.put({"text":" PANIC  ", "type":"error"})
              self.supervisor.inbox.put('PANIC')
            else:
                self.printer_actor.inbox.put({"text":json.loads(event.data), "type":"pprint"})
                sensors_data = json.loads(event.data)["message"]

                self.last_sensors_data = sensors_data
                self.supervisor.inbox.put(sensors_data)

            self.printer_actor.inbox.put({"text":"----", "type":"blue"})


    def ack(self, message):
        self.printer_actor.inbox.put({"text":"\n !! Thanks worker !!\n", "type":"success"})
        self.printer_actor.inbox.put({"text":message, "type":"header"})
        self.aggregator_actor.inbox.put(message)


    def show_final_result(self, message):
        self.printer_actor.inbox.put({"text":message, "type":"green_header"})
        self.web_actor.inbox.put(message)
        self.web_actor.inbox.put("DATA:" + str(self.last_sensors_data))


    def receive(self, message):
        # if message == "work done":
        if "PREDICTED_WEATHER_FINAL:" in message:
            gevent.spawn(self.show_final_result(message))
        elif "PREDICTED_WEATHER:" in message:
            gevent.spawn(self.ack(message))
        elif message == "start":
            self.printer_actor.inbox.put({"text":"Requestor starting...", "type":"header"})
            self.supervisor = self.directory.get_actor('supervisor')
            gevent.spawn(self.loop)


    def get_supervisor(self):
        return self.supervisor


    def get_printer_actor(self):
        return self.printer_actor
