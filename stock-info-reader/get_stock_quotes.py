import time
import requests
import pandas as pd

from kafka import KafkaProducer
from yahoo_fin import stock_info as si

MAX_RETRIES = 5
topic_name = 'STOCK_QUOTES'

starttime = time.time()

producer = KafkaProducer(
        bootstrap_servers=['broker:9092'])
print("Producer created")

def send_to_kafka(df):
    for k, row in df.iterrows():
        data_str = row.Symbol + ' ' + str(row.Price)
        print(data_str)
        producer.send(topic_name, data_str.encode())
        producer.flush()

def get_ticker_list():
    return pd.DataFrame(columns=['Symbol'], data=['AAPL', 'MSFT', 'AMZN', 'FB', 'GOOG', 'NVDA', 'ADBE'])
    #return pd.read_csv("NASDAQ_tickers.csv").iloc[:10]

def get_stock_quotes():
    tickers = get_ticker_list()
    while True:
        retries = 0
        while retries < MAX_RETRIES:
            try:
                print("GETTING QUOTES...")
                tickers['Price'] = tickers.apply(lambda x: si.get_live_price(x['Symbol']), axis=1)
                print("DONE...")
                break
            except requests.exceptions.ConnectionError:
                print("Retrying as connection timed out")
                retries += 1
        print(tickers)

        send_to_kafka(tickers)

        tickers['Price'] = None
        # sleep so we keep quoting at the same time
        # within each minute
        # this setup was for debugging but doesn't hurt so leaving it here
        time.sleep(60.0 - ((time.time() - starttime) % 60.0))

if __name__ == "__main__":
    get_stock_quotes()
