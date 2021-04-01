import pandas as pd

stock_tickers = pd.read_csv("nasdaq_screener_1614082251766.csv")

symbols = stock_tickers[stock_tickers.apply(
    lambda x: (len(x['Symbol'])>=4)
        and (x['Symbol'].find("^")==-1)
        and (x['Symbol'].find("\\")==-1)
        , axis=1)]['Symbol']

print(symbols)

symbols.to_csv("../stock-info-reader/NASDAQ_tickers.csv", index=False)
symbols.to_csv("../spark-streaming-etl/NASDAQ_tickers.csv", index=False)
