import pandas as pd
import yaml
import sys
import os
from otawslibs.generate_aws_session import _create_session
sys.path.append(os.path.join(os.path.dirname(__file__), 'ec2_utils_lib'))
from ec2_utils.ec2_utils import fetch_instances, extract_instance_data
from ec2_utils.cloudwatch_utils import fetch_cpu_utilization
from ec2_utils.filters import should_include_instance

# Load configuration from YAML
with open('config.yaml') as f:
    config = yaml.safe_load(f)

# Create AWS session
session = _create_session(
    aws_profile=config.get('aws_profile'),
    role_arn=config.get('role_arn')
)

data = []

# Iterate over regions specified in the config
for region in config['regions']:
    print(f"Checking region: {region}")
    
    # Fetch instances for the region
    response = fetch_instances(session, region)
    
    if not response.get('Reservations'):
        print(f"No reservations found in region {region}")
        continue

    print(f"Regions: {config['regions']}")
    
    # Process instances in each reservation
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            print(f"Processing instance: {instance['InstanceId']}")

            # Filter instances by tags if configured
            if config['filter_by_tags'] and not should_include_instance(instance, config['tags'], config['match_all_tags']):
                print(f"Skipping instance {instance['InstanceId']} due to tag filter.")
                continue

            # Extract instance data
            instance_data = extract_instance_data(instance)
            print(f"Extracted instance data: {instance_data}")

            # Add region and volume info to instance data
            instance_data['Region'] = region
            instance_data['Volume ID'] = instance['BlockDeviceMappings'][0]['Ebs']['VolumeId'] if instance['BlockDeviceMappings'] else '-'
            instance_data['Storage (GB)'] = instance['BlockDeviceMappings'][0]['Ebs'].get('VolumeSize', '-') if instance['BlockDeviceMappings'] else '-'
            instance_data['Pricing'] = 'On-Demand'  # Simplified pricing info for demo

            # Fetch CPU utilization data
            min_cpu, max_cpu, avg_cpu = fetch_cpu_utilization(
                session,
                instance['InstanceId'],
                region,
                config['cpu_utilization']['period'],
                start=config['cpu_utilization'].get('start'),
                end=config['cpu_utilization'].get('end'),
                last_n_days=config['cpu_utilization'].get('last_n_days')
            )

            # Add CPU data to instance data
            instance_data['CPU Min'] = min_cpu
            instance_data['CPU Max'] = max_cpu
            instance_data['CPU Avg'] = avg_cpu

            # Append instance data to the list
            data.append(instance_data)

# Write the collected data to a CSV file
if data:
    pd.DataFrame(data).to_csv('ec2_instance_report.csv', index=False)
    print(f"Data written to ec2_instance_report.csv")
else:
    print("No data to write.")
