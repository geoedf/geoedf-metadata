import json
import os

import pika

from searchable_files import extractor, assembler, submitter
from searchable_files.assembler import assemble_handler
from searchable_files.constants import RMQ_NAME, INDEX_ID
from searchable_files.extractor import extract_handler, yaml
from searchable_files.submitter import submit_handler

# Establish a connection to RabbitMQ rabbitmq-server
RMQ_USER = 'guest'
RMQ_PASS = 'guest'
RMQ_HOST_IP = '172.17.0.3'
RMQ_SERVICE_NAME = 'rabbitmq-service'

def get_channel():
    credentials = pika.PlainCredentials(RMQ_USER, RMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RMQ_HOST_IP, port=5672, virtual_host='/', credentials=credentials))
    channel = connection.channel()

    # Declare a queue to consume from
    channel.queue_declare(queue=RMQ_NAME)
    return channel


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body.decode())
    msg = json.loads(body.decode())
    print("Received message:", msg)

    extract_settings = extractor.Settings(yaml.load(open(extractor.SETTING_PATH)))
    assemble_settings = assembler.Settings(yaml.load(open(assembler.SETTING_PATH)))
    submit_settings = submitter.Settings(yaml.load(open(submitter.SETTING_PATH)))

    # todo better way to do error handling
    err = extract_handler(msg['uuid'], msg['publication_name'], msg['path'], True, msg['type'])
    if err is not None:
        err_msg = "failed at extrator"
        return err_msg
    err = assemble_handler(extract_settings.output_path, True)
    if err is not None:
        err_msg = "failed at assembler"
        return err_msg
    err = submit_handler(assemble_settings.output_path, INDEX_ID)
    if err is not None:
        err_msg = "failed at submitter"
        print(f'[callback] err_msg={err_msg}')
        return err_msg
    # watch_handler(submit_settings.output_path, INDEX_ID)

    print(f'[callback] success in submitter')


def consume_msg():
    with get_channel() as channel:
        # Consume messages from the queue
        channel.basic_consume(queue=RMQ_NAME, on_message_callback=callback, auto_ack=True)

        print('Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()


consume_msg()
