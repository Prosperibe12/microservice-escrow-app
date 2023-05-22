import json
import pika
from decouple import config

params = pika.URLParameters(config('AMPQ_URL'))
# credentials = pika.PlainCredentials('guest', 'guest')
# params = pika.ConnectionParameters('localhost',5672,'/',credentials=credentials, heartbeat=5)
connection  = pika.BlockingConnection(params)
channel = connection.channel()

def publish(method,body):
    properties = pika.BasicProperties(method)
    channel.basic_publish(exchange='', routing_key='app', body=json.dumps(body), properties=properties)