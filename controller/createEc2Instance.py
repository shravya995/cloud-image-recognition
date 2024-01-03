import boto3
ec2 = boto3.resource('ec2')

instances = ec2.create_instances(
        ImageId="ami-09c6ef0459a2ff40e",
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro"
    )
print(instances[0].id)