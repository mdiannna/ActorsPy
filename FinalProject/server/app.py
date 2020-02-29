from flask import Flask, render_template, request, jsonify
from pusher import Pusher
import uuid

# create flask app
app = Flask(__name__)
app.secret_key = 'secret'

# configure pusher object
pusher = Pusher(
  app_id='4', 
  key='secret', 
  secret='secret', 
  cluster='eu',
  ssl=True, 
  # app_id='APP_ID',
  # key='APP_KEY',
  # secret='APP_SECRET',
  # cluster='APP_CLUSTER',
  # ssl=True
)

# index route, shows index.html view
@app.route('/')
def index():
  return render_template('index.html')

# feed route, shows feed.html view
@app.route('/feed')
def feed():
  return render_template('feed.html')

# store post
@app.route('/post', methods=['POST'])
def addPost():
  data = {
    'id': "post-{}".format(uuid.uuid4().hex),
    'title': request.form.get('title'),
    'content': request.form.get('content'),
    'status': 'active',
    'event_name': 'created'
  }
  pusher.trigger("blog", "post-added", data)
  return jsonify(data)

# update or delete post
@app.route('/post/<id>', methods=['PUT','DELETE'])
def updatePost(id):
  data = { 'id': id }
  if request.method == 'DELETE':
    data['event_name'] = 'deleted'
    pusher.trigger("blog", "post-deleted", data)
  else:
    data['event_name'] = 'deactivated'
    pusher.trigger("blog", "post-deactivated", data)
  return jsonify(data)


import json
import pprint
import sseclient

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
  url = 'http://0.0.0.0:4000/iot'
  # response = with_urllib3(url)  
  response = with_requests(url)

  client = sseclient.SSEClient(response)
  for event in client.events():

    print(event)
    print(event.data)

    if(event.data=='{"message": panic}'):
      print("PANIC")
    else:
      # print(json.loads(event.data))
      pprint.pprint(json.loads(event.data))
      sensors_data = json.loads(event.data)["message"]
      print(sensors_data)
    print("----")


# run Flask app in debug mode
app.run(debug=True)