import boto3

def fetch_instances(session, region):
    ec2 = session.client('ec2', region_name=region)
    return ec2.describe_instances()

def extract_instance_data(instance):
    tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
    return {
        'Instance ID': instance['InstanceId'],
        'Instance Name': tags.get('Name', '-'),
        'State': instance['State']['Name'],
        'Type': instance['InstanceType'],
        'Public IP': instance.get('PublicIpAddress', '-'),
        'Private IP': instance['PrivateIpAddress'],
        'EBS Optimized': instance.get('EbsOptimized', False),
        'ASG': tags.get('aws:autoscaling:groupName', '-')
    }