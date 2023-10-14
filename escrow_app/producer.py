# import json
# import pika
# from decouple import config

# params = pika.URLParameters("")
# connection  = pika.BlockingConnection(params)
# channel = connection.channel()

# def publish(method,body):
#     properties = pika.BasicProperties(method)
#     channel.basic_publish(exchange='', routing_key='app', body=json.dumps(body), properties=properties)