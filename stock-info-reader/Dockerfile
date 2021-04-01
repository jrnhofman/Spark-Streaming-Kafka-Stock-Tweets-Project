# Base image to start from.
FROM python:latest

RUN pip install kafka-python gcsfs fsspec yahoo_fin pandas tzlocal
RUN apt-get update
RUN apt-get install -y vim

ADD NASDAQ_tickers.csv /
ADD get_stock_quotes.py /
