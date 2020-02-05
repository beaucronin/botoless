import boto3 

def resource(service_name):
    return boto3.resource(service_name)

def client(service_name):
    return boto3.client(service_name)
