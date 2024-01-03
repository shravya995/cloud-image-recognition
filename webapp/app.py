import json
import secrets

import boto3
from flask import Flask, jsonify, request, session
from utils.controller import check_ec2_instance_count, watch_sqs_queue
from utils.s3_functionalities import create_s3_bucket
from utils.sqs_queue import (
    create_sqs_request_queue,
    delete_sqs_message,
    read_sqs_messages,
)

APP = Flask(__name__)

AMI_ID = "ami-034a60a99750dce27"

# Set a secret key for session management
APP.secret_key = secrets.token_hex(8)

S3_CLIENT = boto3.client("s3")
SQS_CLIENT = boto3.client("sqs", region_name="us-east-1")
EC2_CLIENT = boto3.client("ec2", region_name="us-east-1")
EC2_RESOURCE = boto3.resource("ec2", region_name="us-east-1")

REQUEST_QUEUE = "RequestQueue.fifo"
RESPONSE_QUEUE = "ResponseQueue.fifo"

REQUEST_QUEUE_URL = SQS_CLIENT.get_queue_url(QueueName=REQUEST_QUEUE)["QueueUrl"]
RESPONSE_QUEUE_URL = SQS_CLIENT.get_queue_url(QueueName=RESPONSE_QUEUE)["QueueUrl"]

@APP.route('/',methods=['GET'])
def index():
    response = {'message':"Welcome to flask controller!"}
    return jsonify(response),200


@APP.route("/upload", methods=["POST"])  # type: ignore
def upload_image():
    if request.method == "POST":
        try:
            if "user_id" not in session:
                # Generate a 32-character (16-byte) hexadecimal token as the session key
                session["user_id"] = secrets.token_hex(16)

            user_session = session["user_id"]
            print(user_session)

            if "myfile" not in request.files:
                return jsonify({"error": "No image provided"}), 400

            image = request.files["myfile"]
            # Use a random name for the uploaded image
            image_name = image.filename

            create_s3_bucket(
                s3_client=S3_CLIENT,
                bucket_name="quiz-on-friday-input-images",
            )
            S3_CLIENT.upload_fileobj(
                image, "quiz-on-friday-input-images", image_name
            )

            # Send a message to the request queue with the session ID
            response = create_sqs_request_queue(
                sqs=SQS_CLIENT,
                user_session=user_session,
                image_name=image_name,
            )

            count = 1
            number_of_messages = watch_sqs_queue(
                sqs=SQS_CLIENT, queue_name="RequestQueue.fifo"
            )

            max_instance_count = 10

            instance_ids = check_ec2_instance_count(
                EC2_RESOURCE=EC2_RESOURCE, EC2_CLIENT=EC2_CLIENT
            )

            max_instance_count = max_instance_count - len(instance_ids)
            message_count = count + int(number_of_messages)

            print(
                f"Number of messages: {message_count}, number of EC2: {len(instance_ids)}"
            )

            for instance_id in instance_ids:
                instance = EC2_RESOURCE.Instance(instance_id)
                if instance.state["Name"] == "stopped":
                    EC2_CLIENT.start_instances(InstanceIds=[instance_id])

            while True:
                messages, queue_url = read_sqs_messages(sqs=SQS_CLIENT)
                for message in messages:
                    response_message = json.loads(message["Body"])
                    if response_message.get("user_session") == user_session:
                        # Delete the processed message from the queue
                        delete_sqs_message(
                            sqs=SQS_CLIENT,
                            queue_url=queue_url["QueueUrl"],
                            receipt_handle=message["ReceiptHandle"],
                        )
                        # Return the response to the user
                        return jsonify(response_message)

        except Exception as e:
            return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    APP.run(debug=True, threaded=True, host="0.0.0.0", port=5000)
