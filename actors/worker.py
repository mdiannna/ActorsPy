from .actors import Actor, States, Work
# from .printeractor import PrinterActor
from . import weather
import gevent 
import json

class Worker(Actor):
    def __init__(self, name, directory):
        super().__init__()
        self.name = name
        self.state = States.Idle
        # self.printer_actor = PrinterActor("Worker_printer")
        # self.printer_actor.start()
        self.directory = directory

    def receive(self, message):
        self.state = States.Running
        self.get_printer_actor().inbox.put({"text":"I %s was told to process '%s' [%d]" %(self.name, message, self.inbox.qsize()), "type":"blue"})


        athm_pressure, humidity, light, temperature, wind_speed, timestamp = weather.aggregate_sensor_values(message)
        predicted_weather = weather.predict_weather(athm_pressure, humidity, light, temperature, wind_speed)


        sensor_data_web = {
            "atmo_pressure" : athm_pressure,
            "humidity": humidity,
            "light": light,
            "temperature" : temperature,
            "wind": wind_speed,
            "timestamp": timestamp
        }

        self.get_web_actor().inbox.put("DATA:" +str(json.dumps(str(sensor_data_web))))

        # gevent.sleep(3)
        # For debug
        # print("PUT AGGREGATOR")
        # print("PREDICTED_WEATHER:" + predicted_weather)
        self.get_aggregator_actor().inbox.put("PREDICTED_WEATHER:" + predicted_weather)
        self.state = States.Idle

    def get_printer_actor(self):
        return self.directory.get_actor('printeractor')

    def get_web_actor(self):
        return self.directory.get_actor('webactor')
    
    def get_aggregator_actor(self):
        return self.directory.get_actor('aggregator')
        
    def get_directory(self):
        return self.directory

