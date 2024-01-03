import boto3

sqs = boto3.client('sqs')

queue_name = 'myQueue.fifo'
queue_url = 'https://sqs.us-east-1.amazonaws.com/697190715831/myQueue.fifo'

queue_attributes = sqs.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['All'])
message_count = queue_attributes['Attributes']['ApproximateNumberOfMessages']

print(message_count)