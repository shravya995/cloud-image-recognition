import boto3

ec2 = boto3.resource('ec2')

running_count = 0
stopped_count = 0
stopped_list = 0
for instance in ec2.instances.all():
    print('ID: {}, State: {}, Type: {}'.format(
        instance.id, instance.state['Name'], instance.instance_type))
    if instance.state['Name'] == 'running':
        running_count+=1
    elif instance.state['Name'] == 'stopped':
        if instance.id not in stopped_list:
            stopped_list.append(instance.id)
            stopped_count+=1
print(running_count, stopped_count, stopped_list)