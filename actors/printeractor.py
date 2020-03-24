from .actors import Actor, States, Work
from . import prettyprint
import pprint

class PrinterActor(Actor):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.state = States.Idle

    def start(self):
        Actor.start(self)

    def receive(self, message):
        # message["text"]
        # message["type"]
        if message["type"]=="warning":
            prettyprint.print_warning(message["text"])
        if message["type"]=="warning-bold":
            prettyprint.print_warning(prettyprint.bold(message["text"]))
        if message["type"]=="error":
            prettyprint.print_error(prettyprint.bold(message["text"]))
        if message["type"]=="blue" or message["type"]=="normal":
            prettyprint.print_blue(message["text"])
        if message["type"]=="green" or message["type"]=="ok" or message["type"]=="success":
            prettyprint.print_green(message["text"])
        if message["type"]=="underline":
            prettyprint.print_underline(message["text"])
        if message["type"]=="header":
            prettyprint.print_header(message["text"])
        if message["type"]=="green_header":
            prettyprint.print_header(prettyprint.green(message["text"]))
        if(message["type"]=="pprint"):
            print("!!!")
            pprint.pprint(message["text"]["message"])
