# Base image to start from.
FROM ubuntu:20.04

# Information surrounding the creator.
LABEL maintainer="jrn.hofman@gmail.com"
LABEL description="Basic Spark Streaming client that reads from the server providing the tweets."

# Update the system.
RUN apt-get update \
 && apt-get install -qq -y curl vim net-tools iputils-ping \
 && rm -rf /var/lib/apt/lists/*

# Install Python
RUN apt-get update \
 && apt-get install -y python3 \
 && apt-get install -y python3-distutils \
 && apt-get install -y python3-apt \
 && ln -s /usr/bin/python3 /usr/bin/python \
 && rm -rf /var/lib/apt/lists/*

# Install Java
RUN apt-get update \
 && apt-get install -y openjdk-11-jre \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Install Spark
RUN apt-get update \
 && apt-get install -y curl \
 && curl https://archive.apache.org/dist/spark/spark-3.0.1/spark-3.0.1-bin-hadoop2.7.tgz -o spark.tgz \
 && tar -xf spark.tgz \
 && mv spark-3.0.1-bin-hadoop2.7 /opt/spark/ \
 && rm spark.tgz

# Install requests library through pip
RUN apt-get update \
 && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
 && python get-pip.py \
 && pip install requests

# Set Spark environment
ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin

# SET WORKING DIR
WORKDIR $SPARK_HOME

# Copy files
COPY log4j.properties $SPARK_HOME/conf
COPY analyze_tweets.py $SPARK_HOME/analyze_tweets.py
COPY test_tweet_consumer.py $SPARK_HOME/test_tweet_consumer.py
COPY NASDAQ_tickers.csv $SPARK_HOME/NASDAQ_tickers.csv

ADD test_tweet_consumer.py /

RUN pip install tweepy kafka-python pandas
RUN apt-get update
RUN apt-get install -y vim

# Run commands
CMD ["bin/spark-class", "org.apache.spark.deploy.master.Master", "org.apache.spark.deploy.worker.Worker"]
