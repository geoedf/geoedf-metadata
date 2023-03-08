from __future__ import print_function
import json
from json.decoder import JSONDecodeError
import pika
import sys, os

from searchable_files.extract import raster, vector, common

RMQ_HOST   = str(os.getenv('RMQ_HOST',"rabbitmq"))
RMQ_USER   = str(os.getenv('RMQ_USER',"rabbitmq"))
RMQ_PASS   = str(os.getenv('RMQ_PASS',"rabbitmq"))
RMQ_EXCHANGE = str(os.getenv('RMQ_EXCHANGE',"rabbitmq"))
RMQ_QUEUE  = str(os.getenv('RMQ_QUEUE',"geoedf-all"))

# log file with the complete message when debugging
DBG_PATH = '/tmp/debug.txt'

# listing of all processed files
LOG_PATH = '/tmp/processed.txt'

# listing of files that have failed despite 10 requeues
FAIL_PATH = '/tmp/failed.txt'

# setting to true will drop all processing, simply acknowledge
# messages and write them to debug file
# logfile will always be written to
DEBUG = False

UNSPEC_KEY = 'unknown'
RASTER_KEY = 'raster'
SHAPE_KEY  = 'shape'


# if indexing to Solr fails, the message will be requeued
# so, whenever a message is processed, we need to make sure
# the status of the filesystem is still the same
# for e.g. if processing a rename, ensure there is still a file
# with this new name
def callback(ch, method, properties, body):
    '''React to message on queue'''

    CMS_EVENT = True
    working_dir = ''
    requeued = False

    try:
        # binary message to string
        body = body.decode()
        # string to json
        data = json.loads(body)
        # print for debug
        if DEBUG:
            with open(DBG_PATH,'a+') as dbgfile:
                dbgfile.write("%s\n" % body)

            ch.basic_ack(delivery_tag=method.delivery_tag)

            return

        # first determine the hub this message originates from
        # this is useful in constructing the proxy URL for feature queries
        # but may also be used to implement different behaviors for prod vs dev
        if 'hub' in data:
            hub = data['hub']
        else:
            hub = 'dev.mygeohub.org'

        # index by item number
        paths = {}
        for item in data['paths']:
            paths[int(item['item'])] = item['name']

        # we process paths differently for CMS versus tool session events
        # tool session events contain "working-directory", while CMS events
        # have the "cwd" field; this is used to distinguish between the two
        # we use the parent in the case of CMS, and completely ignore it in
        # the case of tool sessions to account for relative paths

        if 'process' in data:
           if 'working_directory' in data['process']:
               CMS_EVENT = False
               working_dir = data['process']['working_directory']

        if data['action'] == 'rename' or data['action'] == 'renamed':
            if CMS_EVENT:
                source = os.path.join(paths[0], paths[2])
                destination = os.path.join(paths[1], paths[3])
            else: # tool session event, so use working dir
                source = os.path.normpath(os.path.join(working_dir, paths[2]))
                destination = os.path.normpath(os.path.join(working_dir, paths[3]))

            with open(LOG_PATH,'a+') as logfile:
                logfile.write('action: rename...%s to %s\n' % (source,destination))
            # only proceed if destination still exists as a file

        elif data['action'] == 'opened-file':
            if CMS_EVENT:
                filename = os.path.normpath(os.path.join(data['cwd'],paths[0]))
            else:
                filename = os.path.normpath(os.path.join(working_dir,paths[1]))
            with open(LOG_PATH,'a+') as logfile:
                logfile.write('action: open file...%s\n' % filename)
            # if this is no longer a valid file, skip
            # possibly out of date message that was requeued
            if os.path.isfile(filename):
                # some initialization
                shpfile_metadata = None
                fileext = os.path.splitext(os.path.split(filename)[1])[1]
                # extract metadata based on filetype
                # assume that metadata extractor will not raise an exception
                # a basic dictionary will be returned in the worst case
                if fileext in raster.extensions:
                    metadata = raster.getMetadata(filename)
                    # register file for preview
                else:
                    metadata = common.basicData(filename)
                # index to Solr, unless requeuing

            else: # file not found, but mount could be down, so requeue
                if not os.path.exists(os.path.dirname(filename)):
                    #directory cannot be found, likely mount is down, so requeue and wait
                    requeued = True
                    # requeue_message(ch,body)

        # acknowledge this message
        ch.basic_ack(delivery_tag=method.delivery_tag)

    # some unexpected error occurred
    # no choice but to ack this message and move on
    except JSONDecodeError:
        with open(LOG_PATH,'a+') as logfile:
            logfile.write('%s is not a properly formatted JSON message, probably a test mesage\n' % body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except:
        with open(LOG_PATH,'a+') as logfile:
            logfile.write('unexpected error processing message: %s\n' % body)
            logfile.write('Exception %s\n' % sys.exc_info()[0])
        ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":

    # Connect to our queue in RabbitMQ
    credentials = pika.PlainCredentials(RMQ_USER, RMQ_PASS)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RMQ_HOST, credentials=credentials))
    channel    = connection.channel()
    result     = channel.queue_declare(RMQ_QUEUE, durable=True)

    # Set our callback function, wait for msgs
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=RMQ_QUEUE, on_message_callback=callback)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
