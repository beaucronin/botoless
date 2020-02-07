import logging
import logging.handlers
from queue import Queue
import time
import copy

import boto3
import botocore.errorfactory

from botoless.logging.config import LOGGING_CONFIG

class CloudwatchHandler(logging.Handler):
    @staticmethod
    def config(group_name):
        print(f'Configuring CloudwatchHandler to use group {group_name}')
        conf = copy.deepcopy(LOGGING_CONFIG)
        conf['handlers']['cloudwatch']['group_name'] = group_name
        logging.config.dictConfig(conf)
    
    def __init__(self, group_name, logger_named_streams=True):
        super().__init__()
        self.group_name = group_name
        self.cw = boto3.client("logs")
        self.sequence_token = None
        self.named_streams = logger_named_streams
        self.confirmed_streams = set()
        
        self.maybe_create_group()
        
    def emit(self, record):
        try:
            res = self.put_record(record)
        except Exception as e:
            # wow, what a hack - the sequence token does not appear to be in either the exception
            # or the response to DescribeLogStreams, as claimed in the boto3 docs. So we're parsing it
            # from the exception error message, which is ridiculous
            print(e)
            self.sequence_token = e.__dict__['response']['Error']['Message'].split()[-1]
            res = self.put_record(record)
            self.sequence_token = res['nextSequenceToken']
    
    def put_record(self, record):
        stream_name = "default"
        if self.named_streams:
            stream_name = record.name
        res = self.put_event(stream_name, record.getMessage())
    
    def put_event(self, stream_name, message):
        created = self.maybe_create_stream(stream_name)
        # self.maybe_fetch_sequence_token()
        timestamp = int(time.time() * 1000)
        if self.sequence_token and not created:
            res = self.cw.put_log_events(
                logGroupName=self.group_name,
                logStreamName=stream_name,
                sequenceToken=self.sequence_token,
                logEvents=[{ "timestamp": timestamp, "message": message }]
            )
        else:
            res = self.cw.put_log_events(
                logGroupName=self.group_name,
                logStreamName=stream_name,
                logEvents=[{ "timestamp": timestamp, "message": message }]
            )
            
        self.sequence_token = res['nextSequenceToken']
        return res
    
    def maybe_fetch_sequence_token(self):
        if self.sequence_token:
            return
        self.fetch_sequence_token()
        
    def fetch_sequence_token(self):
        res = self.cw.describe_log_streams(
            logGroupName=self.group_name, 
            limit=1)
        if 'logStreams' in res:
            if len(res['logStreams']) > 0:
                self.sequence_token = res['logStreams'][0]['uploadSequenceToken']
                print(f"Fetched sequence token {self.sequence_token}")
                return
        print("can't set sequence token - no log streams found")
        
    
    def maybe_create_group(self):
        if self.check_group_exists():
            return
        self.create_group()
    
    def check_group_exists(self):
        res = self.cw.describe_log_groups(logGroupNamePrefix=self.group_name)
        if 'logGroups' in res:
            for lg in res['logGroups']:
                if lg['logGroupName'] == self.group_name:
                    return True
        return False
    
    def create_group(self):
        print(f"Creating group {self.group_name}")
        self.cw.create_log_group(logGroupName=self.group_name)

    def maybe_create_stream(self, stream_name):
        if stream_name in self.confirmed_streams:
            return False
        if self.check_stream_exists(stream_name):
            self.confirmed_streams.add(stream_name)
            return False
        self.create_stream(stream_name)        
        self.confirmed_streams.add(stream_name)
        return True
    
    def check_stream_exists(self, stream_name) -> bool:
        res = self.cw.describe_log_streams(
            logGroupName=self.group_name,
            logStreamNamePrefix=stream_name
        )
        if 'logStreams' in res:
            for ls in res['logStreams']:
                if ls['logStreamName'] == stream_name:
                    return True
        return False
    
    def create_stream(self, stream_name):
        print(f'Creating stream {stream_name}')
        self.cw.create_log_stream(logGroupName=self.group_name, logStreamName=stream_name)
        
        
class CloudwatchQueueHandler(logging.handlers.QueueHandler):
    
    def __init__(self, group_name):
        queue = Queue(-1)
        super().__init__(queue)
        self.listener = logging.handlers.QueueListener(queue, CloudwatchHandler(group_name))
        self.listener.start()
        print("listener started")

if __name__ == "__main__":
    import logging.config
    import time
    
    CloudwatchHandler.config("testgroup3")
    logger = logging.getLogger("foo3")
    i = 0
    while True:
        print(i)
        logger.debug(f"test debug {i}")
        logger.warning(f"test warning {i}")
        logger.info({"level": "info", "msg": { "a": "b"}})
        time.sleep(1)
        i += 1
    