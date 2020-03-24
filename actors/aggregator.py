from .actors import Actor, States, Work
from .printeractor import PrinterActor
import gevent 
import time
import copy
from .helpers import most_frequent


class Aggregator(Actor):
    def __init__(self, name, directory):
        Actor.__init__(self)
        self.name = name
        self.state = States.Idle
        self.directory = directory
        self.printer_actor = PrinterActor("Aggregator_printer")
        self.printer_actor.start()
        self.last_time = time.time()
        self.current_time = time.time()

        self.reinit()
        self.DELAY_TIME = 5
        # For debug
        print("Aggregator init")


    def start(self):
        Actor.start(self)


    def reinit(self):
        self.predictions = []


    def receive(self, message):
        self.state = States.Running
        self.current_time = time.time()
        
        if(self.current_time - self.last_time >= self.DELAY_TIME ):
                
            if(len(self.predictions)>0):
                predicted_weather = self.aggregate_all_predictions(copy.copy(self.predictions))

                self.get_printer_actor().inbox.put({"text":"PREDICTED_WEATHER_FINAL:" + predicted_weather, "type":"green_header"})
                self.get_web_actor().inbox.put("PREDICTED_WEATHER_FINAL:" + predicted_weather)

            self.reinit()
            self.last_time = self.current_time
        
        prediction = message  # example: "PREDICTED_WEATHER:SNOW"

        prediction = prediction.replace("PREDICTED_WEATHER:", "")
        self.predictions.append(prediction)

        self.state = States.Idle


    def aggregate_all_predictions(self, predictions):
        result = most_frequent(predictions)
        return result

    
    def get_printer_actor(self):
        return self.directory.get_actor('printeractor')

    def get_web_actor(self):
        return self.directory.get_actor('webactor')
        

    def print_result(self, text):
        self.self.get_printer_actor().inbox.put({"text":text, "type":"green_header"})


    def set_delay_time(self, new_delay_time):
        self.DELAY_TIME = new_delay_time


    def get_delay_time(self):
        return self.DELAY_TIME
