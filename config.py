# For docker-compose:
# config = {
# 	# "REDIS_URL": "redis://0.0.0.0",
# 	"REDIS_URL": "redis://cache",
# 	'EVENTS_SERVER_URL': 'http://patr:4000',
# 	"SEND_URL": 'http://0.0.0.0:5000'  + '/send',
# }

# For runnung locally:
config = {
	"REDIS_URL": "redis://0.0.0.0",
	# "REDIS_URL": "redis://cache",
	# 'EVENTS_SERVER_URL': 'http://patr:4000',
	'EVENTS_SERVER_URL': 'http://0.0.0.0:4000',
	"SEND_URL": 'http://0.0.0.0:5000'  + '/send',
}