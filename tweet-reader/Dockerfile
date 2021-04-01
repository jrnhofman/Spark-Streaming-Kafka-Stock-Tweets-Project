# Base image to start from.
FROM python:latest

RUN pip install tweepy kafka-python pandas
RUN apt-get update
RUN apt-get install -y vim

ADD tweet_producer.py /
ADD get_authentication.py /
# Credentials
ADD twitter.txt /
