import boto3

def sendMessage(image_id,sqs_client):
    try:
         queue = sqs_client.get_queue_url(QueueName='Shrav-Request-Queue.fifo')
         response = sqs_client.send_message(
         QueueUrl=queue['QueueUrl'],
         DelaySeconds=0,
         MessageAttributes={
        'Title': {
            'DataType': 'String',
            'StringValue': 'Queue Message'
        },
        'Author': {
            'DataType': 'String',
            'StringValue': 'Shravya Suresh'
        }
    },
         MessageBody=(
        image_id
    ),
             MessageGroupId=image_id
)   
         print(response)
    except Exception as e:
        print("Error in sending message \n{}".format(e))
        return None


def getMessage():
    try:
        queue = sqs_client.get_queue_url(QueueName='Shrav-Request-Queue.fifo')
        response = sqs_client.receive_message(
        QueueUrl=queue['QueueUrl'],
        AttributeNames=[
        'SentTimestamp'
     ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
        'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=10
        )

        message = response['Messages'][0]
        print(message)
    except Exception as e:
        print("Error in recieving message \n{}".format(e))
        return None

def receive_and_delete_messages(queue_name,max_queue_messages,sqs_client,expected_session_id):
    queue = sqs_client.get_queue_url(QueueName=queue_name)
#     queue = sqs_client.get_queue_by_name(QueueName=queue_name)
#     messages = queue.receive_messages(MaxNumberOfMessages=10, WaitTimeSeconds=1)
    while True:
        messages_to_delete = []
        message_bodies={}
        try:
            
            response = sqs_client.receive_message(
            QueueUrl=queue['QueueUrl'],
            AttributeNames=[
            'SentTimestamp'
         ],
            MaxNumberOfMessages=max_queue_messages,
            MessageAttributeNames=[
            'All'
            ],
            VisibilityTimeout=5,
            WaitTimeSeconds=10
            )

            messages = response['Messages']
            # print(messages)
        except Exception as e:
            print("Error in recieving message \n{}".format(e))
            return None
        for message in messages:
            # process message body
            body = message['Body']
            s_id=body.split('#')[0]
            message_bodies[s_id]=body
            if s_id == expected_session_id:
            # add message to delete
                print('Match found')
                messages_to_delete.append({
                    'Id': message['MessageId'],
                    'ReceiptHandle': message['ReceiptHandle']
                })
        print('Body',message_bodies)
        # if you don't receive any notifications the
        # messages_to_delete list will be empty
        if len(messages_to_delete) == 0:
            print('Break Applied because no messages to delete')
            break
        # delete messages to remove them from SQS queue
        # handle any errors
        else:
            for delete_message in messages_to_delete:
                print('Message Delete Requested',delete_message)
                delete_response = sqs_client.delete_message(
                        QueueUrl=queue['QueueUrl'],
                        ReceiptHandle=delete_message['ReceiptHandle'])
        print('Message Bodies',message_bodies)
        print('expected_session_id',expected_session_id)
        if expected_session_id in  message_bodies:
            return message_bodies[expected_session_id]
        
    return None


# if __name__ == "__main__":

    # sendMessage(image_id,sqs_client)
#     create_queue()
    # getMessage()
