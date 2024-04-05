import json
import os
import sys

import pika
import requests
from pika.exceptions import AMQPConnectionError

from models import Message
from searchable_files import extractor, assembler, submitter
from searchable_files.assembler import assemble_handler
from searchable_files.constants import RMQ_NAME, INDEX_ID
from searchable_files.extractor import extract_handler, yaml
from searchable_files.file_manager import copy_files
from searchable_files.submitter import submit_handler

# Establish a connection to RabbitMQ rabbitmq-server
RMQ_USER = 'guest'
RMQ_PASS = 'guest'
RMQ_HOST_IP = '172.17.0.3'
RMQ_SERVICE_NAME = 'rabbitmq-service'

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

def get_channel():
    credentials = pika.PlainCredentials(RMQ_USER, RMQ_PASS)
    # local test
    # connection = pika.BlockingConnection(
    #     pika.ConnectionParameters(host=RMQ_HOST_IP, port=5672, virtual_host='/', credentials=credentials))
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RMQ_SERVICE_NAME, port=5672, virtual_host='/', credentials=credentials))
    channel = connection.channel()

    # Declare a queue to consume from
    channel.queue_declare(queue=RMQ_NAME)
    return channel


def callback(ch, method, properties, body):
    msg = Message(body)
    print("Received message:", msg)

    try:
        extract_settings = extractor.Settings(yaml.load(open(extractor.SETTING_PATH)))
        assemble_settings = assembler.Settings(yaml.load(open(assembler.SETTING_PATH)))
        submit_settings = submitter.Settings(yaml.load(open(submitter.SETTING_PATH)))
    except Exception as e:
        print(f'Error loading settings: {e}')
        return

    # copy files from staging to persistent
    if not msg.path:
        err_msg = "path of file(s) is null"
        print(f'[callback] err_msg={err_msg}')
        return err_msg

    copy_files(msg.source_dir, msg.target_dir)

    # todo better way to do error handling
    err = extract_handler(
        msg.uuid,
        msg.publication_name,
        msg.target_dir,
        True,
        msg.type,
        msg.description,
        msg.keywords
    )
    if err is not None:
        err_msg = "failed at extrator"
        print(f'[callback] err_msg={err_msg}')
        return err_msg
    err = assemble_handler(extract_settings.output_path, True)
    if err is not None:
        err_msg = "failed at assembler"
        print(f'[callback] err_msg={err_msg}')
        return err_msg
    err = submit_handler(assemble_settings.output_path, INDEX_ID)
    if err is not None:
        err_msg = "failed at submitter"
        print(f'[callback] err_msg={err_msg}')
        return err_msg
    # watch_handler(submit_settings.output_path, INDEX_ID)
    task_id_file = "output/worker_metadata/submitted/tasks.txt"
    task_id = get_task_id(task_id_file)
    # update it to portal

    update_task_id_to_portal(msg.user_jupyter_token, msg.uuid, task_id)
    print(f'[callback] success in submitter')




def get_task_id(task_id_file):
    os.chdir(ROOT_DIR)
    task_ids = set()
    with open(task_id_file) as fp:
        for line in fp:
            line = line.strip()
            if line:  # skip empty
                task_ids.add(line.strip())
    if len(task_id_file) > 0:
        return task_ids.pop()


GEOEDF_PORTAL_API_URL = "https://geoedf-portal.anvilcloud.rcac.purdue.edu/api"


def update_task_id_to_portal(jupyter_api_token, resource_id, task_id):
    """GeoEDF Portal API"""

    url = f"{GEOEDF_PORTAL_API_URL}/resource/update/"
    headers = {
        'Authorization': f'{jupyter_api_token}',
    }
    body_json = {
        "uuid": resource_id,
        "task_id": task_id,
    }
    print(f'[update_task_id_to_portal] body_json={body_json}')

    response = requests.post(url, headers=headers, json=body_json)
    if response.status_code != 200:
        print(f"Error fetching user info: {response.status_code}")
        return None
    return response.json()


def consume_msg():
    try:
        with get_channel() as channel:
            channel.basic_consume(queue=RMQ_NAME, on_message_callback=callback, auto_ack=True)

            print(' [*] Waiting for messages. To exit press CTRL+C')
            channel.start_consuming()
    except KeyboardInterrupt:
        print(' [*] Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    except AMQPConnectionError:
        print("Connection to RabbitMQ lost. Retrying...")
        # Optionally add a retry mechanism here
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    consume_msg()
