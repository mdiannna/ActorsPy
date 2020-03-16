# Dockerfile - this is a comment
# https://medium.com/@doedotdev/docker-flask-a-simple-tutorial-bbcb2f4110b5

#FROM python:3.6.9
#COPY . /app
#WORKDIR /app
#RUN pip install -r requirements.txt
##RUN curl "http://0.0.0.0:4000/help"
#ENTRYPOINT ["python3"]
#CMD ["app.py"]

#FROM python:3.7-alpine
FROM python:3.6.9
WORKDIR /code
ENV FLASK_APP app.py
ENV FLASK_RUN_HOST 0.0.0.0
# RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["flask", "run"]