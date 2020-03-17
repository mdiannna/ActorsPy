$ docker pull alexburlacu/rtp-server

Works:
1. $ sudo docker container run --publish 4000:4000 --detach alexburlacu/rtp-server 
2. $ curl http://127.0.0.1:4000/iot
3.  $ python3 app.py 

Doesn't work:
- $ docker-compose up


