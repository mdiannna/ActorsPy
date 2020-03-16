$ docker pull alexburlacu/rtp-server

Merge:
$ sudo docker container run --publish 4000:4000 --detach alexburlacu/rtp-server 
$ curl http://127.0.0.1:4000/iot
$ python3 app.py 

Nu merge: 
$ docker-compose up


