from .actors import Actor, States, Work
# from actors import Actor, States, Work
from .printeractor import PrinterActor
import gevent 
import time

class Aggregator(Actor):
    # def __init__(self, name, directory):
    def __init__(self, name):
        Actor.__init__(self)
        self.name = name
        self.state = States.Idle
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

        if(self.current_time - self.last_time >= self.DELAY_TIME):

            print("TIME_TO_PRINT_PREDICTION")
            self.printer_actor.inbox.put({"text":"TIME_TO_PRINT_PREDICTION", "type":"error"})

            self.aggregate_all_predictions(self.predictions)
            self.reinit()
            self.last_time = self.current_time

        # Exemplu
        # "PREDICTED_WEATHER:SNOW"
        prediction = message
        #TODO: 
        # 1. din prediction de scos "PREDICTED_WEATHER"
        # 2. append prediction to self.predictions (self.predictions.apped(prediction))
                


        # TODO DIANA:
        # client = self.directory.get_actor("client")
        # client.inbox.put("PREDICTED_WEATHER_FINAL:" + predicted_weather)
        self.state = States.Idle

    # TODO:
    def aggregate_all_predictions(self, predictions):
        # TODO: correct result calculated from predictions
        result = "RESULT"
        self.print_result(result)

    def get_printer_actor(self):
        return self.printer_actor

    def print_result(self, text):
        self.printer_actor.inbox.put({"text":text, "type":"green_header"})


# print(time.clock())


# aggregator_actor = Aggregator("Aggregator actor")
# aggregator_actor.start()