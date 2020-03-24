# THis actor will send events for showing in the wepage
from .actors import Actor, States, Work
from flask_sse import sse
from flask import current_app
import app
import requests
import os
from flask import request

class WebActor(Actor):
    def __init__(self, name="WebActor"):
        super().__init__()
        self.name = name
        self.state = States.Idle
        self.url = os.getenv("SEND_URL")
        print("WebActor init")

    def start(self):
        Actor.start(self)

    def receive(self, message):
        # only for debug
        print("************RECEIVE WEB ACTOR")
        
        # Send message to sse route
        if os.getenv("SEND_WEB")=='NO_SEND':
            print("NO_SEND")
        else:
            r = requests.get(self.url + '/' + message)