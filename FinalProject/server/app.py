from flask import Flask, render_template, request, jsonify
from pusher import Pusher
import uuid

# create flask app
app = Flask(__name__)
app.secret_key = 'secret'



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