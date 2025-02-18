import os
import boto3
import pandas as pd
from otawslibs import generate_aws_session
from otfilesystemlibs import yaml_manager
from botocore.exceptions import ClientError

# Environment variable to get the config file path
CONF_PATH_ENV_KEY = "CONFIG_PATH"

def load_config():
    """Load configuration from a YAML file."""
    config_file = os.getenv(CONF_PATH_ENV_KEY, "config.yaml")  # Default to 'config.yaml'
    yaml_loader = yaml_manager.getYamlLoader()
    
    try:
        config = yaml_loader._loadYaml(config_file)
        print("Config loaded successfully:", config)
        return config
    except Exception as e:
        print(f"Error loading config file {config_file}: {e}")
        return None

def get_ec2_instances(session, tags):
    """Retrieve EC2 instances that match at least one of the specified tags."""
    ec2_client = session.client("ec2")
    
    try:
        # Fetch all instances without specific filters, we will filter in code
        response = ec2_client.describe_instances()
        instances = []
        
        for reservation in response.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                instance_id = instance.get("InstanceId", "N/A")
                instance_type = instance.get("InstanceType", "N/A")
                state = instance.get("State", {}).get("Name", "N/A")
                
                # Get volumes and their sizes
                volumes = []
                for block in instance.get("BlockDeviceMappings", []):
                    volume_id = block.get("Ebs", {}).get("VolumeId", "N/A")
                    volume_size = get_volume_size(ec2_client, volume_id)  # Fetching volume size
                    volumes.append(f"{volume_id} (Size: {volume_size} GB)")
                
                instance_tags = {tag["Key"]: tag["Value"] for tag in instance.get("Tags", [])} if "Tags" in instance else {}
                
                # Check if any of the specified tags exist in the instance tags
                if any(tag in instance_tags and instance_tags[tag] == value for tag, value in tags.items()):
                    instances.append({
                        "Instance ID": instance_id,
                        "Instance Type": instance_type,
                        "State": state,
                        "Volumes": ", ".join(volumes),
                        "Tags": instance_tags
                    })
        
        print(f"Found {len(instances)} matching instances.")
        return instances
    except ClientError as e:
        print(f"Error fetching instances: {e}")
        return []

def get_volume_size(ec2_client, volume_id):
    """Retrieve the size of an EBS volume."""
    try:
        response = ec2_client.describe_volumes(VolumeIds=[volume_id])
        volume = response['Volumes'][0]
        size = volume.get('Size', 'N/A')
        print(f"Volume {volume_id} size: {size} GB")
        return size
    except ClientError as e:
        print(f"Error fetching volume size for {volume_id}: {e}")
        return 'N/A'

def save_to_csv(instances, output_file):
    """Save EC2 instance details to a CSV file."""
    if not instances:
        print("No matching instances found. Skipping CSV generation.")
        return
    
    df = pd.DataFrame(instances)
    df["Tags"] = df["Tags"].apply(lambda tags: "; ".join([f"{k}: {v}" for k, v in tags.items()]) if tags else "N/A")
    df.to_csv(output_file, index=False)
    print(f"EC2 instance details saved to {output_file}")

if __name__ == "__main__":
    config = load_config()
    
    if not config:
        print("Error: Could not load config.")
        exit(1)
    
    aws_profile = config.get("aws", {}).get("profile", "default")
    role_arn = config.get("aws", {}).get("role_arn", "")
    tags = config.get("filters", {}).get("tags", {})
    output_file = config.get("filters", {}).get("output_file", "ec2_instances.csv")
    
    print(f"Using AWS Profile: {aws_profile}, Role ARN: {role_arn}")
    print(f"Filtering EC2 instances with tags: {tags}")
    
    session = generate_aws_session._create_session(aws_profile=aws_profile, role_arn=role_arn)
    instances = get_ec2_instances(session, tags)
    save_to_csv(instances, output_file)
