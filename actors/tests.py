# Code for testing aggregator to be tested in the app.py file
from actors.aggregator import Aggregator
import random

# @app.route('/test-aggregator')
def testAggregator():
  aggregator_actor = Aggregator("Aggregator actor")
  aggregator_actor.start()
  aggregator_actor.inbox.put("Hello")
  PREDICTION_OPTIONS = ["WET_SNOW", 'SNOW', "BLIZZARD", "SLIGHT_RAIN", "HEAVY_RAIN", "HOT", "CONVECTION_OVEN", "WARM", "SLIGHT_BREEZE", "CLOUDY", "MONSOON"]
  for i in range(1, 20):
    aggregator_actor.inbox.put("PREDICTED_WEATHER:" + random.choice(PREDICTION_OPTIONS))
    gevent.sleep(1)
  return "done aggregator"
