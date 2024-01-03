def watch_sqs_queue(sqs, queue_name):
    queue_url = sqs.get_queue_url(QueueName=queue_name)["QueueUrl"]
    queue_attributes = sqs.get_queue_attributes(
        QueueUrl=queue_url, AttributeNames=["All"]
    )
    message_count = queue_attributes["Attributes"][
        "ApproximateNumberOfMessages"
    ]

    return message_count


def check_ec2_instance_count(EC2_RESOURCE, EC2_CLIENT):
    instance_ids = []
    for instance in EC2_RESOURCE.instances.all():  # type: ignore
        instance_ids.append(instance.id)

    instance_info = EC2_CLIENT.describe_instances(InstanceIds=instance_ids)

    instance_name_value = "image-processing"

    # Extract and print the instance name from the tags.
    for reservation in instance_info["Reservations"]:
        for instance in reservation["Instances"]:
            for tag in instance.get("Tags", []):
                if tag["Key"] == "Name":
                    instance_name = tag["Value"]
                    if instance_name != instance_name_value:
                        instance_ids.remove(instance["InstanceId"])
                    print(f"Instance Name: {instance_name}")
                    break
            else:
                print("Instance Name not found")
    return instance_ids