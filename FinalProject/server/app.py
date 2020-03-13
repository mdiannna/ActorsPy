from flask import Flask, render_template, request, jsonify
from pusher import Pusher
import uuid
import json
import pprint
import sseclient

import myactors
import prettyprint
import gevent
from gevent.queue import Queue
# from enum import Enum
# from gevent import Greenlet

# create flask app
app = Flask(__name__)
app.secret_key = 'secret'

def with_urllib3(url):
    """Get a streaming response for the given event feed using urllib3."""
    import urllib3
    http = urllib3.PoolManager()
    return http.request('GET', url, preload_content=False)

def with_requests(url):
    """Get a streaming response for the given event feed using requests."""
    import requests
    return requests.get(url, stream=True)




# Receive weather data from sensor from rtp-server
@app.route('/receive-sse-sensor-data')
def testSSE():

  prettyprint.print_header("Program started")

  directory = Directory()
  # gevent.joinall([gevent.spawn(go)])

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
app.run(debug=True)