from .. import resource, full_name

sqs = resource('sqs')

def get_queue(name):
    queue_full_name = full_name(name)
    if queue_full_name not in queues:
        queues[queue_full_name] = sqs.get_queue_by_name(QueueName=queue_full_name)
    return queues[queue_full_name]


def send_message(queue_name, message, delay_seconds=0):
    """Send a message on a queue with the body as a JSON-serialized object"""
    queue = sqs_get_queue(queue_name)
    queue.send_message(MessageBody=json.dumps(message), DelaySeconds=delay_seconds)
