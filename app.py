from flask import Flask, render_template, request, jsonify
from pusher import Pusher
from flask_sse import sse

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

def create_app():
  # create flask app
  app = Flask(__name__)

  app.secret_key = 'secret'
  with app.app_context():
    # app.config["REDIS_URL"] = "redis://localhost"
    app.config["REDIS_URL"] = "redis://0.0.0.0"
    app.register_blueprint(sse, url_prefix='/stream')
    # app.register_blueprint(sse, url_prefix='/receive-sse-sensor-data')
  # app.app_context() .push()

  return app

app = create_app()



# @app.route('/test-receive-events')
# def test_receive_events():
#   return render_template('test_receive_events.html')

@app.route('/')
def index():
  return render_template('test_receive_events.html')


@app.route('/send/<message>')
def send_message(message):
    for i in range(1, 10):
      sse.publish({"message": message}, type='greeting')
      gevent.sleep(2)
    return "Message sent!"


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

  
