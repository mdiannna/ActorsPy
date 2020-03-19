# Actors Based System for Wather Prediction
This project was done for the Real Time Applications Programming Lab at the University of Moldova, Software Engineering program.

## Screenshots and demo
![Screenshot 1](https://github.com/mdiannna/ActorsPy/blob/master/screenshots_video/s1.png?raw=true)
![Screenshot 2](https://github.com/mdiannna/ActorsPy/blob/master/screenshots_video/s2.png?raw=true)
![Screenshot 3](https://github.com/mdiannna/ActorsPy/blob/master/screenshots_video/s3.png?raw=true)
![Screenshot 4](https://github.com/mdiannna/ActorsPy/blob/master/screenshots_video/s4.png?raw=true)
**Video demo here:** https://github.com/mdiannna/ActorsPy/blob/master/screenshots_video/demo3.mp4

## Setup project: 
1. If running on Ubuntu without docker, install redis package
   (Ubuntu:)
   $ apt-get install redis-server 
   
   If not, skip

2. Use docker compose:
$ docker-compose up

3. If you would like to see only the actors system + printing in console, go to
http://0.0.0.0:5000/receive-sse-sensor-data
4. If you want to see the web interface frontend, run 3. then open in another tab http://0.0.0.0:5000/


## Author
Marusic Diana, FAF-171
