import pandas as pd

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

from kafka import KafkaProducer

from get_authentication import get_authentication

auth_dict = get_authentication()
auth = OAuthHandler(auth_dict['CONSUMER_KEY'], auth_dict['CONSUMER_SECRET'])
auth.set_access_token(auth_dict['ACCESS_TOKEN'], auth_dict['ACCESS_SECRET'])

topic_name = 'TWEETS'

producer = KafkaProducer(
        bootstrap_servers=['broker:9092'])
print("Producer created")

def get_ticker_list():
    # For demonstration purposes we query tweets
    # with a couple of well-known companies
    # instead of simply querying the quote we also quote
    # the alias as most people refer to the company
    # not by its stock quote (duh!) but by the company name
    df = pd.DataFrame(columns=['Symbol']
        , data=['AAPL', 'apple', 'MSFT', 'microsoft', 'AMZN', 'amazon',
            'FB', 'facebook', 'GOOG', 'google', 'NVDA', 'nvidia', 'ADBE', 'adobe'])
    #df = pd.read_csv("NASDAQ_tickers.csv").iloc[:10]

    return ['#'+x for x in df.Symbol.values.tolist()]

class Listener(StreamListener):
    def on_status(self, raw_data):
        print(raw_data.text)
        producer.send(topic_name, str.encode(raw_data.text))
        return True

def get_tweets(lst):
    print(lst)
    while True:
        listener = Listener()
        stream = Stream(auth, listener)
        stream.filter(track=lst, stall_warnings=True)

if __name__ == "__main__":
    lst = get_ticker_list()
    get_tweets(lst)