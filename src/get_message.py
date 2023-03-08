import json

import pika

from searchable_files.assembler import assemble_handler
from searchable_files.extractor import extract_handler

# Establish a connection to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq-server'))
channel = connection.channel()

# Declare a queue to consume from
channel.queue_declare(queue='geoedf-all')

# Define a callback function to handle received messages
def callback(ch, method, properties, body):
    print(" [x] Received %r" % body.decode())
    msg = json.loads(body.decode())
    print("Received message:", msg)
    extract_handler(msg['path'], True)
    assemble_handler("output/worker/extracted/", True)


# Consume messages from the queue
channel.basic_consume(queue='geoedf-all', on_message_callback=callback, auto_ack=True)

print('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()