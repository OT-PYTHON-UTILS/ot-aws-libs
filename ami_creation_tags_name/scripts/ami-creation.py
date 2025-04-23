from ami_creator.config_reader import read_config
from ami_creator.csv_utils import read_instance_data, store_ami_details
from ami_creator.instance_utils import fetch_instance_tags, get_instance_state
from otawslibs.generate_aws_session import _create_session
from ami_creator.ami_utils import create_ami, tag_ami
from datetime import datetime
import csv

def main():
    config = read_config()

    session = _create_session(
        aws_profile=config.get('aws_profile'),
        role_arn=config.get('role_arn')
    )
    ec2_client = session.client('ec2', region_name=config['aws_region'])

    instances = read_instance_data(config['input_csv'])
    current_date = datetime.now().strftime('%Y-%m-%d')
    config['additional_tags']['Backup Date'] = current_date

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
