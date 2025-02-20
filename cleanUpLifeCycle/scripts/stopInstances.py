import boto3
import csv
import time
import yaml
import os
from datetime import datetime, timedelta
from otawslibs import generate_aws_session

def load_config(config_path="/home/khushimalhotra/Desktop/Office/cleanUpLifeCycle/config/config.yaml"):
    with open(config_path, "r") as file:
        return yaml.safe_load(file)

def get_instances_from_csv(csv_file):
    instance_ids = []
    if os.path.exists(csv_file):
        with open(csv_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                instance_ids.append(row['Instance ID'])
    return instance_ids

def get_instances_by_tags(ec2_client, tags):
    filters = [{'Name': f'tag:{k}', 'Values': [v]} for k, v in tags.items()]
    response = ec2_client.describe_instances(Filters=filters)
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append(instance['InstanceId'])
    return instances

def stopInstances(ec2_client, instance_ids, stop_duration):
    stop_info = []
    if instance_ids:
        ec2_client.stop_instances(InstanceIds=instance_ids)
        print(f"Stopping instances: {instance_ids}")

        for iid in instance_ids:
            stop_info.append({
                "Instance ID": iid,  # Ensure correct key name
                "Instance State": "stopped",  # Updating state after stopping
                "Stop Until": (datetime.now() + timedelta(days=stop_duration)).strftime('%Y-%m-%d')
            })
    return stop_info  # Return a list of dictionaries


def create_ami(ec2_client, instance_ids, retention_days):
    ami_info = []
    for instance_id in instance_ids:
        ami_name = f"Backup-{instance_id}-{int(time.time())}"
        response = ec2_client.create_image(InstanceId=instance_id, Name=ami_name, NoReboot=True)
        ami_id = response['ImageId']

        ami_info.append({
            "Instance ID": instance_id,
            "AMI ID": ami_id,
            "Retention Until": (datetime.now() + timedelta(days=retention_days)).strftime('%Y-%m-%d') if retention_days > 0 else "No Expiry"
        })
    return ami_info  # Return a list of dictionaries


def apply_tags(ec2_client, instance_ids, tags):
    tag_list = [{'Key': k, 'Value': v} for k, v in tags.items()]
    ec2_client.create_tags(Resources=instance_ids, Tags=tag_list)
    print(f"Applied tags: {tags} to instances: {instance_ids}")

def update_csv(file_path, stop_info, ami_info, post_ami_new_tags):
    # Ensure data is in list format
    stop_info = [stop_info] if isinstance(stop_info, dict) else stop_info
    ami_info = [ami_info] if isinstance(ami_info, dict) else ami_info
    all_data = stop_info + ami_info

    print("\n🔍 DEBUG: stop_info Data Structure:", stop_info)
    print("\n🔍 DEBUG: ami_info Data Structure:", ami_info)
    print("\n🔍 DEBUG: Combined Data:", all_data)

    existing_data = []
    
    # Read existing CSV if it exists
    if os.path.exists(file_path):
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            existing_data = list(reader)

    # Convert existing data into a dictionary for easy lookup
    existing_instances = {row.get("Instance ID", ""): row for row in existing_data if "Instance ID" in row}

    # Update only relevant fields without deleting old data
    for instance in all_data:
        if not isinstance(instance, dict):  
            print(f"\n❌ ERROR: Invalid data format (expected dict): {instance}")
            continue
        
        instance_id = instance.get("Instance ID")  # Use `.get()` to avoid KeyError
        if not instance_id:
            print(f"\n❌ ERROR: Missing 'Instance ID' in instance data: {instance}")
            continue  # Skip this iteration if there's no instance ID
        
        if instance_id in existing_instances:
            existing_instances[instance_id].update(instance)  # Update only relevant fields
        else:
            existing_instances[instance_id] = instance  # Add new instances if not found

    # Extract fieldnames dynamically
    fieldnames = set()
    for row in existing_instances.values():
        fieldnames.update(row.keys())

    fieldnames = sorted(fieldnames)  # Sort for consistent column ordering

    # Write updated data back to CSV
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing_instances.values())

    print(f"\n✅ Updated CSV file: {file_path}")


def main():
    config = load_config()
    if config['stopInstances']['enabled'].lower() != 'yes':
        print("Stopping instances is disabled in config.yaml")
        return
    
    # FIX: Read `aws_profile` and `role_arn` properly
    aws_profile = config.get('aws_profile', 'default')
    role_arn = config.get('role_arn', '')

    session = generate_aws_session._create_session(config['aws_profile'], config['role_arn'])
    ec2_client = session.client('ec2')
    
    instance_ids = []
    if config['stopInstances']['input_type'].lower() == 'csv':
        instance_ids.extend(get_instances_from_csv(config['stopInstances']['csv_file']))
    if config['stopInstances']['input_type'].lower() == 'tags':
        instance_ids.extend(get_instances_by_tags(ec2_client, config['stopInstances']['tags']))
    
    stop_duration = config['stopInstances']['stop_duration']
    stop_info = stopInstances(ec2_client, instance_ids, stop_duration)
    
    if config['stopInstances']['implement_tags'].lower() == 'yes':
        apply_tags(ec2_client, instance_ids, config['stopInstances']['new_tags'])
    
    ami_info = {}
    if config['stopInstances']['create_ami'].lower() == 'yes':
        ami_info = create_ami(ec2_client, instance_ids, config['stopInstances']['ami_retention'])
    
    if config['stopInstances']['post_ami_tags'].lower() == 'yes':
        apply_tags(ec2_client, instance_ids, config['stopInstances']['post_ami_new_tags'])
    
    update_csv(config['stopInstances']['output_file'], stop_info, ami_info, config['stopInstances']['post_ami_new_tags'])
    print("Instance stop process completed!")

if __name__ == "__main__":
    main()
