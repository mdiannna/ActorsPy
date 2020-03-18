# THis actor will send events for showing in the wepage
from .actors import Actor, States, Work
from flask_sse import sse
# from app import app
# from . import prettyprint
# import pprint
from flask import current_app
import app
import requests
import os
from flask import request

class WebActor(Actor):
    def __init__(self):
        # Actor.__init__(self)
        super().__init__()
        self.name = "WebActor"
        self.state = States.Idle
        # TODO: env var
        self.url = 'http://0.0.0.0:5000'  + '/send'
        print(self.url)

    def start(self):
        Actor.start(self)

    def receive(self, message):
        # only for debug
        print("************RECEIVE WEB ACTOR")
        # print("message:", message)
     
        r = requests.get(self.url + '/' + message)

        # app = current_app._get_current_object()
        # with app.app_context():
        # # with current_app.app_context():
        #     sse.publish({"message": message}, type='greeting')

