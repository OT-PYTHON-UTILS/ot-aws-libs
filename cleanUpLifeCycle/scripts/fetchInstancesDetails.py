import boto3
import csv
import yaml
import os
from otawslibs import generate_aws_session

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def fetchInstancesDetails(session, tags=None):
    ec2_client = session.client('ec2')
    
    # Fetch all instances
    all_instances = ec2_client.describe_instances()['Reservations']
    
    instance_details = []
    instance_ids = []

    for reservation in all_instances:
        for instance in reservation['Instances']:
            instance_tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
            
            # Match ANY tag (OR logic)
            if any(k in instance_tags and instance_tags[k] == v for k, v in tags.items()):
                instance_info = {
                    'Instance ID': instance['InstanceId'],
                    'Instance Type': instance['InstanceType'],
                    'Instance State': instance['State']['Name'],
                    'Attached Volumes': [vol['Ebs']['VolumeId'] for vol in instance.get('BlockDeviceMappings', [])],
                    'Tags': instance_tags
                }
                instance_details.append(instance_info)
                instance_ids.append(instance['InstanceId'])  # Collect instance IDs for tagging

    print("Fetched Instances:", instance_details)  # Debugging print
    return instance_details, instance_ids

def apply_tags(ec2_client, instance_ids, tags):
    if not instance_ids:
        print("No instances found. Skipping tag application.")
        return

    if not tags:
        print("No tags provided. Skipping tag application.")
        return

    tag_list = [{'Key': k, 'Value': v} for k, v in tags.items()]
    
    try:
        ec2_client.create_tags(Resources=instance_ids, Tags=tag_list)
        print(f"Successfully applied tags: {tags} to instances: {instance_ids}")
    except Exception as e:
        print(f"Error applying tags: {e}")

def update_csv(file_path, instance_details):
    fieldnames = ['Instance ID', 'Instance Type', 'Instance State', 'Attached Volumes', 'Tags']
    
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for instance in instance_details:
            instance['Attached Volumes'] = ', '.join(instance['Attached Volumes'])
            instance['Tags'] = str(instance['Tags'])
            writer.writerow(instance)

def main():
    config_path = '/home/khushimalhotra/Desktop/Office/cleanUpLifeCycle/config/config.yaml'
    config = load_config(config_path)
    
    if config.get('fetchInstancesDetails', {}).get('enabled', 'no').lower() != 'yes':
        print("Fetching instances details is disabled in config.")
        return
    
    session = generate_aws_session._create_session(config['aws_profile'], config['role_arn'])
    ec2_client = session.client('ec2')

    tags = config.get('fetchInstancesDetails', {}).get('tags', {})
    print("Filters being used for tag-based search:", tags)  # Debugging print
    
    instance_details, instance_ids = fetchInstancesDetails(session, tags)
    
    output_file = config.get('fetchInstancesDetails', {}).get('output_file', 'instances_details.csv')
    update_csv(output_file, instance_details)
    print(f"Instance details saved to {output_file}")

    # Apply new tags if enabled in config.yaml
    if config.get('fetchInstancesDetails', {}).get('implement_tags', 'no').lower() == "yes":
        new_tags = config.get('fetchInstancesDetails', {}).get('new_tags', {})
        print(f"Applying tags: {new_tags} to instances: {instance_ids}")
        apply_tags(ec2_client, instance_ids, new_tags)
    else:
        print("Tagging is disabled in config.yaml.")

if __name__ == "__main__":
    main()
