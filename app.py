from flask import Flask, render_template, request, jsonify
from pusher import Pusher
import uuid
import json
import pprint
import sseclient

# import myactors
from actors import myactors
from actors import prettyprint
import gevent
from gevent.queue import Queue
import requests
import urllib3
import os

# create flask app
app = Flask(__name__)
app.secret_key = 'secret'

@app.route('/')
def index():
  return 'Hello!'


@app.route('/help-iot')
def helpIoT():
  # help_url = app.config['EVENTS_SERVER_URL'] + '/help'
  help_url = os.getenv('EVENTS_SERVER_URL')  + '/help'
  r = requests.get(help_url)
  return r.json()

# Receive weather data from sensor from rtp-server
@app.route('/receive-sse-sensor-data')
def receiveSSE():
  pool = myactors.Pool(10) # try 2, 3, 5, 8...
  gevent.joinall([gevent.spawn(pool.start)])


# run Flask app in debug mode
# app.run(debug=True, host='0.0.0.0:5000')


# os.environ['EVENTS_SERVER_URL'] = 'http://patr:4000'
os.environ['EVENTS_SERVER_URL'] = 'http://0.0.0.0:4000'



if __name__ == "__main__":
  app.run(debug=True, host='0.0.0.0')

  
