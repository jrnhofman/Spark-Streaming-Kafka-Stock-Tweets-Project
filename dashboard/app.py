from flask import Flask, Markup, render_template, jsonify, request
import requests
import ast
import pandas as pd

app = Flask(__name__)

info_pd = pd.DataFrame(columns=['tickers','timestamps','stock_prices','tweet_counts'])
timestamps = []
stock_prices = []
tweet_counts = []
tickers = []

@app.route('/')
def line():
    global info_pd
    global timestamps, stock_prices, tweet_counts, tickers
    return render_template('chart_new.html', title='Stocks and tweets over time', labels=timestamps, values=stock_prices)

@app.route('/refreshData')
def refresh_graph_data():
    global info_pd
    global timestamps, stock_prices, tweet_counts, tickers
    print("timestamps: " + str(timestamps))
    print("stock_prices: " + str(stock_prices))
    print("tweet_counts: " + str(tweet_counts))
    print("tickers: " + str(tickers))
    return jsonify(sLabel=timestamps, sData=stock_prices, sTickers=tickers, sTweetCounts=tweet_counts)

@app.route('/updateData', methods=['POST'])
def update_data():
    global info_pd
    global timestamps, stock_prices, tweet_counts, tickers
    if not request.form or 'ticker_ts_str' not in request.form:
        return "error",400

    tickers_inc = ast.literal_eval(request.form['tickers'])
    timestamps_inc = ast.literal_eval(request.form['ticker_ts_str'])
    stock_prices_inc = ast.literal_eval(request.form['price'])
    tweet_counts_inc = ast.literal_eval(request.form['n_tweets'])
    print("tickers received: " + str(tickers_inc))
    print("timestamps received: " + str(timestamps_inc))
    print("stock prices received: " + str(stock_prices_inc))
    print("tweet counts received: " + str(tweet_counts_inc))

    # For debugging purposes I'm putting the data in a DF as well
    for i,t in enumerate(tickers_inc):
        for j,ts in enumerate(timestamps_inc[i]):
            tmp_pd = pd.DataFrame(
                columns=['tickers','timestamps','stock_prices','tweet_counts']
                , data=[[t, ts, stock_prices_inc[i][j], tweet_counts_inc[i][j]]])
            info_pd = info_pd.append(tmp_pd, ignore_index=True)

    info_pd = info_pd.drop_duplicates()
    print(info_pd)

    # Updating the lists that get send to the live dashboard
    tweet_counts = []
    stock_prices = []
    tickers = sorted(info_pd.tickers.unique())
    timestamps = sorted(info_pd.timestamps.unique())
    for i, t in enumerate(tickers):
        tweet_counts.append([])
        stock_prices.append([])
        for j, ts in enumerate(timestamps):
            try:
                tweet_counts[i].append(info_pd[(info_pd.tickers==t) & (info_pd.timestamps==ts)]['tweet_counts'].iloc[0])
                stock_prices[i].append(info_pd[(info_pd.tickers==t) & (info_pd.timestamps==ts)]['stock_prices'].iloc[0])
            except IndexError:
                tweet_counts[i].append(0)
                stock_prices[i].append(0)

    return "success", 201

if __name__ == "__main__":
    # within the docker network available as {container_dns}:<port>
    app.run(host='0.0.0.0', debug=True, port=9001)

