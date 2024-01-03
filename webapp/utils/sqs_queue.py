import json


# Function to create an SQS request queue
def create_sqs_request_queue(sqs, user_session, image_name):
    try:
        response = sqs.get_queue_url(QueueName="RequestQueue.fifo")

        response = sqs.send_message(
            QueueUrl=response["QueueUrl"],
            MessageBody=json.dumps(
                {"user_session": user_session, "image_name": image_name}
            ),
            DelaySeconds=0,
            MessageAttributes={
                "Title": {
                    "DataType": "String",
                    "StringValue": "Queue Message",
                },
                "Author": {
                    "DataType": "String",
                    "StringValue": "Quiz on Friday",
                },
            },
            MessageGroupId=image_name,
        )

        return response
    except Exception as e:
        print(e)


# Function to read messages from the SQS response queue
def read_sqs_messages(sqs):
    queue_url = sqs.get_queue_url(QueueName="ResponseQueue.fifo")
    messages = sqs.receive_message(
        QueueUrl=queue_url["QueueUrl"],
        AttributeNames=["SentTimestamp"],
        MessageAttributeNames=["All"],
        VisibilityTimeout=10,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=20,  # Adjust the wait time as needed
    ).get("Messages", [])

    return messages, queue_url


# Function to delete a specific message from an SQS queue
def delete_sqs_message(sqs, queue_url, receipt_handle):
    sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
