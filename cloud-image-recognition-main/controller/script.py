import boto3
import math
import time
sqs = boto3.client('sqs')
ec2 = boto3.resource('ec2')
ec2Client = boto3.client('ec2')

queue_name = 'myQueue.fifo'  #queue name
queue_url = 'https://sqs.us-east-1.amazonaws.com/697190715831/myQueue.fifo'   # queu URL

prev_message_count = 0

def getEC2Data():
    print("-> counting EC2 instances")
    running_count = 0
    stopped_count = 0
    stopped_list = []
    for instance in ec2.instances.all():
        print('ID: {}, State: {}, Type: {}'.format(
            instance.id, instance.state['Name'], instance.instance_type))
        if instance.state['Name'] == 'running' or instance.state['Name'] == 'pending':                               # counting the number of EC2s that are running
            running_count+=1
        elif instance.state['Name'] == 'stopped':                             # counting the number of EC2s that are stopped
            if instance.id not in stopped_list:
                stopped_list.append(instance.id)
                stopped_count+=1
    print("-> number of running EC2 instances: ", running_count )
    print("-> number of stopped EC2 instances: ", stopped_count )
    print("-> stopped EC2 instances: ", stopped_list)
    return running_count, stopped_count, stopped_list

while True:
    print("-> Counting number of messages..")
    queue_attributes = sqs.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['All'])  # fetching information of all the EC2s
    message_count = int(queue_attributes['Attributes']['ApproximateNumberOfMessages'])
    print("-> Number of messages: ", message_count)
    if message_count == 0:
        running_count, stopped_count, stopped_list = getEC2Data()
        if running_count == 0 and stopped_count > 0:
            response = ec2.instances.filter(InstanceIds = stopped_list).terminate()
            print(response)
    if message_count > prev_message_count:

        
        running_count, stopped_count, stopped_list = getEC2Data()   # fetch counts of EC2s

        ec2_needed_count = min(20, math.ceil(message_count/10.0))   # total number of EC2s needed
        if running_count < ec2_needed_count:
            need_count = ec2_needed_count - running_count           # number of more EC2s needed
            if stopped_count > 0:
                print("-> starting a existing EC2 instance")
                if need_count <= stopped_count:
                    stopped_list = stopped_list[:need_count]
                need_count = max(0, need_count-stopped_count)       # numebr of EC2s needed more after starting the stopped EC2s
                ec2Client.start_instances(InstanceIds=stopped_list)
            if need_count > 0:
                print("-> creating an EC2 instance")
                instances = ec2.create_instances(                   # starting "need_count" number of EC2s with the provided image ID
                    ImageId="ami-09c6ef0459a2ff40e",
                    MinCount=need_count,
                    MaxCount=need_count,
                    InstanceType="t2.micro"
                )
    prev_message_count = message_count
    time.sleep(0.1)


