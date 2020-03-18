from .actors import Actor, States, Work
from .printeractor import PrinterActor
from . import weather
import gevent 

class Worker(Actor):
    def __init__(self, name, directory):
        # Actor.__init__(self)
        super().__init__()
        self.name = name
        self.state = States.Idle
        self.printer_actor = PrinterActor("Worker_printer")
        self.printer_actor.start()
        self.directory = directory

    def receive(self, message):
        self.state = States.Running
        self.printer_actor.inbox.put({"text":"I %s was told to process '%s' [%d]" %(self.name, message, self.inbox.qsize()), "type":"blue"})


        athm_pressure, humidity, light, temperature, wind_speed = weather.aggregate_sensor_values(message)
        # only for debug:
        # print("ATHM PRESSURE:", athm_pressure)
        predicted_weather = weather.predict_weather(athm_pressure, humidity, light, temperature, wind_speed)
        # only for debug:
        # print("---")
        # print("PREDICT WEATHER:")
        # print(predicted_weather)

        gevent.sleep(3)
        client = self.directory.get_actor("client")
        client.inbox.put("PREDICTED_WEATHER:" + predicted_weather)
        self.state = States.Idle

    def get_printer_actor(self):
        return self.printer_actor

    def get_directory(self):
        return self.directory

