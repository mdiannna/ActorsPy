from flask import Flask, render_template, request, jsonify
from pusher import Pusher
import uuid
import json
import pprint
import sseclient
from actors.aggregator import Aggregator

# import myactors
from actors import myactors
from actors import prettyprint
import gevent
from gevent.queue import Queue
import requests
import urllib3
import os

# from enum import Enum
# from gevent import Greenlet

# create flask app
app = Flask(__name__)
app.secret_key = 'secret'

# def with_urllib3(url):
#     """Get a streaming response for the given event feed using urllib3."""
#     http = urllib3.PoolManager()
#     return http.request('GET', url, preload_content=False)

# def with_requests(url):
#     """Get a streaming response for the given event feed using requests."""
#     return requests.get(url, stream=True)


@app.route('/')
def index():
  return 'Hello!'

# TEST AGGREGATOR
import random
@app.route('/test-aggregator')
def testAggregator():
  aggregator_actor = Aggregator("Aggregator actor")
  aggregator_actor.start()
  aggregator_actor.inbox.put("Hello")
  PREDICTION_OPTIONS = ["SNOW", "CLOUD", "BLIZARD", "JUST_A_NORMAL_DAY", "SUN"]
  for i in range(1, 100):
    aggregator_actor.inbox.put("PREDICTED_WEATHER:" + random.choice(PREDICTION_OPTIONS))
    gevent.sleep(1)
  return "dore aggregator"



@app.route('/help-iot')
def helpIoT():
  # help_url = app.config['EVENTS_SERVER_URL'] + '/help'
  help_url = os.getenv('EVENTS_SERVER_URL')  + '/help'
  r = requests.get(help_url)
  return r.json()

# Receive weather data from sensor from rtp-server
@app.route('/receive-sse-sensor-data')
def testSSE():

  # prettyprint.print_header("Program started")

  # directory = Directory()
  # # gevent.joinall([gevent.spawn(go)])

  # pool = myactors.Pool(10) # try 2, 3, 5, 8...
  # gevent.joinall([gevent.spawn(pool.start)])


  pool = myactors.Pool(10) # try 2, 3, 5, 8...
  gevent.joinall([gevent.spawn(pool.start)])

  # -------------------


  # url = 'http://0.0.0.0:4000/iot'
  # # response = with_urllib3(url)  
  # response = with_requests(url)

  # client = sseclient.SSEClient(response)
  # for event in client.events():

  #   print(event)
  #   print(event.data)

  #   if(event.data=='{"message": panic}'):
  #     print("PANIC")
  #   else:
  #     # print(json.loads(event.data))
  #     pprint.pprint(json.loads(event.data))
  #     sensors_data = json.loads(event.data)["message"]
  #     print(sensors_data)
  #   print("----")


# run Flask app in debug mode
# app.run(debug=True, host='0.0.0.0:5000')

# app.config['EVENTS_SERVER_URL'] = 'http://patr:4000'
# os.environ['EVENTS_SERVER_URL'] = 'http://patr:4000'
# os.environ['EVENTS_SERVER_URL'] = 'http://127.0.0.1:4000'
os.environ['EVENTS_SERVER_URL'] = 'http://0.0.0.0:4000'
# app.config['EVENTS_SERVER_URL'] = 'http://127.0.0.1:4000'



if __name__ == "__main__":
  app.run(debug=True, host='0.0.0.0')

  
