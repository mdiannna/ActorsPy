# For docker-compose:
config = {
	"REDIS_URL": "redis://cache",
	'EVENTS_SERVER_URL': 'http://patr:4000',
	"SEND_URL": 'http://0.0.0.0:5000'  + '/send',
	"SEND_WEB": "SEND",
}

# For running locally:
# config = {
# 	"REDIS_URL": "redis://0.0.0.0",
# 	'EVENTS_SERVER_URL': 'http://0.0.0.0:4000',
# 	"SEND_URL": 'http://0.0.0.0:5000'  + '/send',
# 	# "SEND_WEB": "NO_SEND",
# 	"SEND_WEB": "SEND",
# }