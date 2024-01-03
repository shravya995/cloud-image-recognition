import boto3

# Create SQS client
sqs = boto3.client('sqs')

queue_url = 'https://sqs.us-east-1.amazonaws.com/697190715831/myQueue.fifo'

# Send message to SQS queue
import random

i = random.randint(0,10000)
response = sqs.send_message(
    QueueUrl=queue_url,
    MessageGroupId=str(i),
    MessageAttributes={
        'Title': {
            'DataType': 'String',
            'StringValue': str(i)
        },
        'Author': {
            'DataType': 'String',
            'StringValue': str(i)
        },
        'WeeksOn': {
            'DataType': 'Number',
            'StringValue': str(i)
        }
    },
    MessageBody=(
        'Information about current NY Times fiction bestseller for '
        'week of 12/11/2016.' + str(i)
    )
)

print(response['MessageId'])