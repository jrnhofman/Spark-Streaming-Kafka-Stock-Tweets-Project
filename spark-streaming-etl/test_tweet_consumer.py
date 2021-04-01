import json

from kafka import KafkaConsumer

topic_name = 'TWEETS'

consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers=['broker:9092'],
    auto_offset_reset='latest',
    enable_auto_commit=True,
    auto_commit_interval_ms=5000,
    fetch_max_bytes=128,
    max_poll_records=100,

    value_deserializer=lambda x: json.loads(x.decode('utf-8')))

for message in consumer:
    tweets = json.loads(json.dumps(message.value))
    print(tweets)
