from .. import resource

s3 = resource('s3')                

def bucket_full_name(name):
    return f"{name}-{workspace}"
    

def get_bucket(name):
    full_name = f"{name}-{workspace}"
    if full_name not in buckets:
        buckets[full_name] = s3.Bucket(full_name)
    return buckets[full_name]


def put_object(bucket_name, key, payload):
    bucket = get_bucket(bucket_name)
    body = payload
    content_type = 'application/octet-stream'
    if isinstance(payload, str):
        body = payload.encode('utf-8')
        content_type = 'text/plain;charset=UTF-8'
    elif isinstance(payload, dict):
        body = json.dumps(payload).encode('utf-8')
        content_type = 'application/json'
    bucket.Object(key).put(Body=body, ContentType=content_type)


def put_url_contents_to_object(bucket_name, key, url, content_type='application/octet-stream'):
    s3_obj = get_bucket(bucket_name).Object(key)
    uf = urlopen(url)
    s3_obj.upload_fileobj(uf, ExtraArgs={'ContentType': content_type})


def put_binary_data_to_object(bucket_name, key, data, content_type='application/octet-stream'):
    b = io.BytesIO(data)
    s3_obj = get_bucket(bucket_name).Object(key)
    s3_obj.upload_fileobj(b, ExtraArgs={'ContentType': content_type})
    

def get_object(bucket_name, key):
    bucket = get_bucket(bucket_name)
    obj = bucket.Object(key).get()
    ct = obj['ContentType']
    if ct == 'text/csv':
        return obj['Body'].read().decode('utf-8')
    elif ct == 'application/json':
        return json.loads(obj['Body'].read().decode('utf-8'))
    else: 
        return obj['Body'].read()


def select_from_object(bucket_name, key, query):
    full_name = bucket_full_name(bucket_name)
    res = s3c.select_object_content(
        Bucket=full_name,
        Key=key,
        ExpressionType="SQL",
        InputSerialization={
            'CSV': {
                "FileHeaderInfo": "Use",
                "AllowQuotedRecordDelimiter": True
            }
        },
        OutputSerialization={'CSV': {}},
        Expression=query
    )
    
    result = ''
    for event in res['Payload']:
        if 'Records' in event:
            result += event['Records']['Payload'].decode('utf-8')
    return result
