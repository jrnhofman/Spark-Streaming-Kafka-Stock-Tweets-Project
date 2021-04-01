# Base image to start from.
FROM python:latest

RUN pip install flask requests pandas
RUN apt-get update
RUN apt-get install -y vim

ADD app.py /
ADD templates/chart_new.html /templates/
ADD static/Chart.js /static/
