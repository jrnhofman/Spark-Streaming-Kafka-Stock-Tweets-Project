# Spark Streaming Project using Kafka and Flask
Personal project, trying to bring into practice a bunch of things I encountered in various online courses, most notably the [Spark Streaming Course](https://www.udemy.com/course/taming-big-data-with-spark-streaming-hands-on/). The project aims to combine several of the (for me) pretty new techniques I have learned.

## Description
The project leverages the [Twitter developer API](https://developer.twitter.com/en) access I was granted for the course above and consists of several components, with an easy setup through Docker and Docker Compose:
- **tweet-reader** Python code that reads from the [Twitter developer API](https://developer.twitter.com/en), filtering on tweets matching a list of predefined company stock quotes and names (i.e. 'GOOG', 'Google' etc.) and sends those to a Kafka topic.
- **stock-info-reader** Python code reading from the [Yahoo Finance API](http://theautomatic.net/yahoo_fin-documentation/) recent stock quotes for the predefined companies and sends those to a Kafka topic.
- **spark-streaming-etl** Pyspark structured streaming code that reads both kafka topics and joins them to produce aggregated tweet counts and stock prices over a fixed time interval. This gets outputted to console and send to a dashboard
- **dashboard** Simple Python web app built with flask that auto-refreshes every few seconds.

Each of the above components is a separate container, forming a network together with zookeeper and a kafka broker.

## Setup

<p align="center"><img src="https://raw.githubusercontent.com/jrnhofman/Spark-Streaming-Kafka-Stock-Tweets-Project/master/images/layout.png" width="200"/></p>

## Running the application
To run the application, simply clone this repository:

`git clone git@github.com:jrnhofman/Spark-Streaming-Kafka-Stock-Tweets-Project.git`

Then start the containers by running

`docker-compose up`

After about 10 minutes you should be able to see data appearing on localhost:9001. Here is a screenshot of what it looks like when the stock market is closed:

<p align="center"><img src="https://raw.githubusercontent.com/jrnhofman/Spark-Streaming-Kafka-Stock-Tweets-Project/master/images/closed_stockmarket.png" width="200"/></p>

And when it's open:

<p align="center"><img src="https://raw.githubusercontent.com/jrnhofman/Spark-Streaming-Kafka-Stock-Tweets-Project/master/images/open_stockmarket.png" width="200"/></p>
