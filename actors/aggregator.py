from .actors import Actor, States, Work
# from actors import Actor, States, Work
from .printeractor import PrinterActor
import gevent 
import time
import copy
from .helpers import most_frequent

class Aggregator(Actor):
    # def __init__(self, name, directory):
    def __init__(self, name, requestor):
        Actor.__init__(self)
        self.name = name
        self.state = States.Idle
        self.requestor = requestor
        self.printer_actor = PrinterActor("Aggregator_printer")
        self.printer_actor.start()
        self.last_time = time.time()
        self.current_time = time.time()
        # self.directory = directory
        self.reinit()
        # 4 sec delay
        self.DELAY_TIME = 5
        print("Aggregator init")

    def start(self):
        Actor.start(self)

    def reinit(self):
        self.predictions = []


    def receive(self, message):
        # print("Received message:" + message)
        self.printer_actor.inbox.put({"text":"Received message:" + message, "type":"warning"})
        self.state = States.Running

        self.current_time = time.time()
        print("current_time", self.current_time)

        if(self.current_time - self.last_time >= self.DELAY_TIME ):
            print("TIME_TO_PRINT_PREDICTION")
            self.printer_actor.inbox.put({"text":"TIME_TO_PRINT_PREDICTION", "type":"error"})
            print("!!!!!!!!", self.predictions)

            if(len(self.predictions)>0):

                # self.aggregate_all_predictions(self.predictions.copy())
                predicted_weather = self.aggregate_all_predictions(copy.copy(self.predictions))
                requestor = self.get_requestor()
                requestor.inbox.put("PREDICTED_WEATHER_FINAL:" + predicted_weather)
            self.reinit()
            self.last_time = self.current_time
 
        ############################################
        # Exemplu
        # Valori posibile
        # 'SNOW'
        # "WET_SNOW"
        # "BLIZZARD"
        # "SLIGHT_RAIN"
        # "HEAVY_RAIN"
        # "HOT"
        # "CONVECTION_OVEN"
        # "WARM"
        # "SLIGHT_BREEZE"
        # "CLOUDY"
        # "MONSOON"

        
        prediction = message  # "PREDICTED_WEATHER:SNOW"

        prediction = prediction.replace("PREDICTED_WEATHER:", "")
        self.predictions.append(prediction)


        #####################################
        # TODO DIANA:
        
        self.state = States.Idle



    def aggregate_all_predictions(self, predictions):
        # predictions este o lista de tip ["SNOW", "SUN", "CLOUD", "CLOUD", "SUN"]
        # TODO: correct result calculated from predictions
        print("PREDICTIONS:")
        print(predictions)
        # result = predictions[0]
        result = most_frequent(predictions)
        self.print_result(result)
        return result
    
    def get_printer_actor(self):
        return self.printer_actor

    def print_result(self, text):
        self.printer_actor.inbox.put({"text":text, "type":"green_header"})

    def get_requestor(self):
        return self.requestor