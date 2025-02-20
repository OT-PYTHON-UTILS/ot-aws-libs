import boto3
import csv
import yaml
import time
from botocore.exceptions import BotoCoreError, ClientError
from otawslibs import generate_aws_session

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def read_instance_ids_from_csv(csv_file):
    instance_ids = []
    try:
        with open(csv_file, mode='r') as file:
            reader = csv.DictReader(file)
            if 'InstanceId' not in reader.fieldnames:
                print("Error: 'InstanceId' column missing in CSV.")
                return []
            for row in reader:
                instance_ids.append(row['InstanceId'])
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    return instance_ids

def get_instances_by_tags(ec2_client, tags):
    filters = [{'Name': f'tag:{key}', 'Values': [value]} for key, value in tags.items()]
    try:
        response = ec2_client.describe_instances(Filters=filters)
        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.append(instance['InstanceId'])
        return instances
    except (BotoCoreError, ClientError) as e:
        print(f"Error fetching instances by tags: {e}")
        return []

def apply_tags(ec2_client, instance_ids, tags):
    try:
        tag_list = [{'Key': key, 'Value': value} for key, value in tags.items()]
        ec2_client.create_tags(Resources=instance_ids, Tags=tag_list)
        print(f"Applied tags {tags} to instances {instance_ids}")
    except (BotoCoreError, ClientError) as e:
        print(f"Error applying tags: {e}")

def terminate_instances(ec2_client, instance_ids):
    try:
        ec2_client.terminate_instances(InstanceIds=instance_ids)
        print(f"Termination initiated for instances: {instance_ids}")
    except (BotoCoreError, ClientError) as e:
        print(f"Error terminating instances: {e}")

def update_csv(csv_file, instance_ids):
    updated_rows = []
    try:
        with open(csv_file, mode='r') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames
            for row in reader:
                if row['InstanceId'] in instance_ids:
                    row['State'] = 'terminated'
                updated_rows.append(row)
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)
        print("CSV file updated with terminated instances.")
    except Exception as e:
        print(f"Error updating CSV file: {e}")

def main():
    config_path = "/home/khushimalhotra/Desktop/Office/cleanUpLifeCycle/config/config.yaml"
    config = load_config(config_path)

    # FIX: Corrected the key and string comparison
    if config.get('terminateInstances', {}).get('terminate', 'no').lower() != "yes":
        print("Instance termination is disabled in config.yaml")
        return
    
    session = generate_aws_session._create_session(config['aws_profile'], config['role_arn'])
    ec2_client = session.client('ec2')
    
    instance_ids = []
    input_type = config['terminateInstances'].get('input_type', 'csv')

    if input_type == 'csv' and 'csv_file' in config['terminateInstances']:
        instance_ids = read_instance_ids_from_csv(config['terminateInstances']['csv_file'])
    elif input_type == 'tags' and 'tags' in config['terminateInstances']:
        instance_ids.extend(get_instances_by_tags(ec2_client, config['terminateInstances']['tags']))
    
    if not instance_ids:
        print("No instances found to terminate.")
        return
    
    if config['terminateInstances'].get('implement_tags', 'no').lower() == "yes":
        apply_tags(ec2_client, instance_ids, config['terminateInstances']['new_tags'])
    
    terminate_instances(ec2_client, instance_ids)
    time.sleep(10)  # Allow AWS to process termination
    
    update_csv(config['terminateInstances']['output_file'], instance_ids)

if __name__ == "__main__":
    main()
