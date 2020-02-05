from .. import resource, full_name as table_full_name

dynamo = resource('dynamodb')


def put_item(table_name, item):
    full_name = table_full_name(table_name)
    table = dynamo.Table(full_name)
    table.put_item(Item=item, ReturnValues='NONE')


def increment_field(table_name, key, field, amount=1):
    full_name = table_full_name(table_name)
    table = dynamo.Table(full_name)
    res = table.update_item(
        Key=key,
        UpdateExpression="SET score = score + :a",
        ExpressionAttributeValues={ ':a': amount },
        ReturnValues='UPDATED_NEW'
    )
    atts = res['Attributes']
    return atts[field]


def dedynamo(raw_item):
    y = {}
    for k, v in raw_item.items():
        a, b = list(v.items())[0]
        if a == 'S':
            y[k] = b
        elif a == 'N':
            try:
                y[k] = int(b)
            except ValueError as e:
                y[k] = float(b)
        elif a == 'M':
            y[k] = b
    return y
