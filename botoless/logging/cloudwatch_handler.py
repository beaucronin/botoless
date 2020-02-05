import logging
import logging.handlers
from queue import Queue
import time

import boto3
import botocore.errorfactory

class CloudwatchHandler(logging.Handler):
    def __init__(self, group_name):
        super().__init__()
        self.group_name = group_name
        self.cw = boto3.client("logs")
        self.sequence_token = '1'
        self.group_exists = False
        
    def emit(self, record):
        try:
            res = self.put_event(record)
            self.sequence_token = res['nextSequenceToken']
        except Exception as e:
            # wow, what a hack - the sequence token does not appear to be in either the exception
            # or the response to DescribeLogStreams, as claimed in the boto3 docs. So we're parsing it
            # from the exception error message, which is ridiculous
            self.sequence_token = e.__dict__['response']['Error']['Message'].split()[-1]
            res = self.put_event(record)
            self.sequence_token = res['nextSequenceToken']
    
    def put_event(self, record):
        res = self.cw.put_log_events(
            logGroupName=self.group_name,
            logStreamName="default",
            sequenceToken=self.sequence_token,
            logEvents=[
                {
                    "timestamp": int(time.time() * 1000),
                    "message": record.getMessage()
                }
            ]
        )
        return res
    
    def create_group(self):
        print(f"Creating group {self.group_name}")
        self.cw.create_log_group(logGroupName=self.group_name)
        self.cw.create_log_stream(logGroupName=self.group_name, logStreamName="default")

class CloudwatchQueueHandler(logging.handlers.QueueHandler):
    
    def __init__(self, group_name):
        queue = Queue(-1)
        super().__init__(queue)
        self.listener = logging.handlers.QueueListener(queue, CloudwatchHandler(group_name))
        self.listener.start()
        print("listener started")

if __name__ == "__main__":
    q = CloudwatchQueueHandler("testgroup")
    q.setLevel(logging.INFO)
    logger = logging.getLogger("test")
    logger.addHandler(q)
    i = 0
    while True:
        logger.warning(f"test message {i}")
        i += 1
    