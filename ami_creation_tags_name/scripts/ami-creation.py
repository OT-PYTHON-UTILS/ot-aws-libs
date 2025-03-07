import boto3
import csv
import yaml
import time
import os
from datetime import datetime

def read_config():
    config_path = os.getenv("CONFIG_PATH")
    if not config_path:
        raise ValueError("CONFIG_PATH environment variable is not set.")
    
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def read_instance_data(csv_file):
    instances = []
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            instances.append({'InstanceID': row['InstanceID'], 'InstanceName': row['InstanceName']})
    return instances

def fetch_instance_tags(ec2_client, instance_id):
    response = ec2_client.describe_instances(InstanceIds=[instance_id])
    tags = response['Reservations'][0]['Instances'][0].get('Tags', [])
    return {tag['Key']: tag['Value'] for tag in tags}

def get_instance_state(ec2_client, instance_id):
    response = ec2_client.describe_instances(InstanceIds=[instance_id])
    return response['Reservations'][0]['Instances'][0]['State']['Name']

def create_ami(ec2_client, instance_id, ami_name, no_reboot):
    response = ec2_client.create_image(InstanceId=instance_id, Name=ami_name, NoReboot=no_reboot)
    return response['ImageId']

def tag_ami(ec2_client, ami_id, tags):
    tag_list = [{'Key': k, 'Value': v} for k, v in tags.items()]
    ec2_client.create_tags(Resources=[ami_id], Tags=tag_list)

def store_ami_details(ami_id, ami_name, output_csv):
    with open(output_csv, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([ami_id, ami_name, time.strftime('%Y-%m-%d %H:%M:%S')])

def main():
    config = read_config()
    ec2_client = boto3.client('ec2', region_name=config['aws_region'])
    instances = read_instance_data(config['input_csv'])
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    config['additional_tags']['stopped'] = current_date
    
    with open(config['output_csv'], mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['AMI_ID', 'AMI_Name', 'Timestamp'])
    
    for instance in instances:
        instance_id = instance['InstanceID']
        instance_name = instance['InstanceName']
        ami_name = f"{instance_name}-({instance_id})"
        
        instance_state = get_instance_state(ec2_client, instance_id)
        no_reboot = instance_state == "running"

        tags = fetch_instance_tags(ec2_client, instance_id)
        tags.update(config['additional_tags'])
        
        ami_id = create_ami(ec2_client, instance_id, ami_name, no_reboot)
        tag_ami(ec2_client, ami_id, tags)
        store_ami_details(ami_id, ami_name, config['output_csv'])
        
        print(f"Created AMI: {ami_name} ({ami_id}) with NoReboot={no_reboot}")

if __name__ == "__main__":
    main()
