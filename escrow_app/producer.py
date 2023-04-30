import pika
from decouple import config

params = pika.URLParameters(config('AMPQ_URL'))
connection  = pika.BlockingConnection(params)
channel = connection.channel()

def publish():
    channel.basic_publish(exchange='', routing_key='app', body='Hello App')