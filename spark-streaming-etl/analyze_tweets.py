from pyspark.sql import SparkSession

from pyspark.sql.functions import explode, unix_timestamp
from pyspark.sql.functions import split, expr, lit
from pyspark.sql.functions import lower, col, regexp_replace
from pyspark.sql.functions import window, concat_ws
from pyspark.sql.functions import udf

from pyspark.sql.types import IntegerType, DoubleType

import requests

spark = SparkSession \
    .builder \
    .appName("TweetAndStockApp") \
    .getOrCreate()

# Reading stock quotes provided every minute
# from Kafka topic
ticker_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "broker:9092") \
    .option("subscribe", "STOCK_QUOTES") \
    .load()

tickers = (
    ticker_df
        .withWatermark("timestamp", "120 seconds")
        .select(
            col("timestamp")
            , split(col("value"), " ").getItem(0).alias("Symbol")
            , split(col("value"), " ").getItem(1).alias("Price")
        )
        .select(
            col("timestamp").alias("ticker_ts")
            , lower(col("Symbol")).alias("ticker_symbol")
            , col("Price").alias("price")
        )
)

# Reading tweets pre-filtered on hashtags
# from Kafka topic
df = (spark
    .readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "broker:9092")
    .option("subscribe", "TWEETS")
    .load()
)

def map_hashtags_to_tickers(x):
    mapper = {
        'google' : 'goog'
        , 'microsoft' : 'msft'
        , 'nvidia' : 'nvda'
        , 'facebook' : 'fb'
        , 'adobe' : 'adbe'
        , 'amazon' : 'amzn'
        , 'apple' : 'aapl'
    }
    return mapper[x] if x in mapper.keys() else x

# For demonstration purposes we query tweets
# with a couple of well-known companies
# instead of simply querying the quote we also quote
# the alias as most people refer to the company
# not by its stock quote (duh!) but by the company name
map_hashtags_to_tickers_udf = udf(map_hashtags_to_tickers)

hashtags = (df
    .withWatermark("timestamp", "120 seconds")
    .selectExpr("timestamp", "CAST(value as string) as value")
    .select(
        col("timestamp")
        , col("value").alias("tweet")
        # splitting to extract the hashtags
        , explode(split(col("value"), " ")).alias("word")
    )
    .filter(col("word").contains("#"))
    .select(col('timestamp'), col("tweet"), lower(col('word')).alias('Symbol'))
    .select(
        col('timestamp').alias('ht_ts')
        , col("tweet")
        , regexp_replace(col('Symbol'), '#', '').alias('ht_symbol')
        , lit(1).alias('cnt')
    )
    .select(
        col('ht_ts')
        , col('tweet')
        , map_hashtags_to_tickers_udf(col('ht_symbol')).alias('ht_symbol')
        , col('cnt')
    )
)

# Joining stock quotes and hashtags
# On the stock symbols (or aliases, i.e. GOOG and Google)
# This is a left join since no tweets can be produced
# within a minute of stock quote
joined = tickers.join(
    hashtags,
    expr("""
        ht_symbol = ticker_symbol
        AND
        ticker_ts <= ht_ts AND
        ticker_ts + interval 60 seconds > ht_ts
        """),
    "leftOuter"
)

# Since we want to aggregate tweet counts and stock prices
# over a window, this is not possible to do properly after
# a join, an (ugly) solution is to create a kafka topic
# with the joined data and then read it again for the agg
# which is what we do here
(joined
    .fillna({ 'cnt': 0, 'tweet': ''})
    .withColumn(
        "value"
        , concat_ws(
            ','
            , col("ticker_ts")
            , col("ticker_symbol")
            , col("price")
            , col("cnt")
            , col("tweet")
            , col("ht_ts")
        )
    )
    .writeStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "broker:9092")
    .option("topic", "JOINED_TWEETS")
    .option("checkpointLocation", "checkpoints")
    .start())

# Read the topic we just wrote back
joined_df = (spark
    .readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "broker:9092")
    # enable this if you don't want to start from scratch
    # every time you relaunch the app
    .option("startingOffsets", "earliest")
    .option("subscribe", "JOINED_TWEETS")
    .load()
)

result = (joined_df
    # decoding and splitting back to columns
    .selectExpr("CAST(value as string) as value")
    .select(
        split(col("value"), ",").getItem(0).alias("ticker_ts"),
        split(col("value"), ",").getItem(1).alias("ticker_symbol"),
        split(col("value"), ",").getItem(2).alias("price"),
        split(col("value"), ",").getItem(3).alias("cnt"),
        split(col("value"), ",").getItem(4).alias("tweet"),
        split(col("value"), ",").getItem(5).alias("ht_ts"),
    )
    # casting
    .select(
        col("ticker_ts").cast("timestamp")
        , col("ticker_symbol")
        , col("ht_ts").cast("timestamp")
        , col("price").cast(DoubleType())
        , col("cnt").cast(IntegerType())
        , col(("tweet"))
    )
    .filter(col("ticker_ts") > unix_timestamp(lit('2021-04-01 12:00:00')).cast('timestamp'))
    .withWatermark("ticker_ts", "2 minutes")
    # grouping data in 5 minute windows
    .groupBy(
        window(col("ticker_ts"), "5 minutes", "5 minutes").alias("ticker_window")
        ,col("ticker_symbol")
    )
    .agg({'price': 'avg', 'cnt': 'sum', 'tweet': 'collect_list'})
    # final result
    .select(
        col('ticker_window').start.alias('ticker_ts')
        , col('ticker_window')
        , col('ticker_symbol')
        , col('avg(price)').alias('price')
        , col('sum(cnt)').alias('n_tweets')
        , col('collect_list(tweet)').alias('tweets')
    )
)

def send_df_to_dashboard(df, epoch_id):
    if df.count() > 0:
        request_data = {'tickers': [], 'ticker_ts_str': [], 'n_tweets' : [], 'price': []}
        df_pd = df.toPandas()

        df_pd['ticker_ts_str'] = df_pd['ticker_ts'].apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S"))
        for s in df_pd.ticker_symbol.unique():
            request_data['tickers'].append(s)
            stats = df_pd[df_pd.ticker_symbol==s]
            for c in ['ticker_ts_str', 'price', 'n_tweets']:
                request_data[c].append(stats[c].values.tolist())

        request_data = {k:str(v) for k,v in request_data.items()}
        print("DATA BEING SEND")
        print(request_data)

        url = 'http://dashboard:9001/updateData'
        response = requests.post(url, data=request_data)
        print("RESPONSE")
        print(response.status_code)

# Write result to endpoint to be picked up by dashboard
result.writeStream.foreachBatch(send_df_to_dashboard).start()

# write result to console for debugging purposes
query = result \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", "false") \
    .start()

query.awaitTermination()
