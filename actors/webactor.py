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
        # Only for debug
        # print(self.url)
        # print("WebActor init")

    def start(self):
        Actor.start(self)

    def receive(self, message):
        # only for debug
        print("************RECEIVE WEB ACTOR")
        # print("message:", message)
        # Send message to sse route
        r = requests.get(self.url + '/' + message)