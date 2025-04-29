def create_ami(ec2_client, instance_id, ami_name, no_reboot):
    response = ec2_client.create_image(InstanceId=instance_id, Name=ami_name, NoReboot=no_reboot)
    return response['ImageId']

def tag_ami(ec2_client, ami_id, tags):
    tag_list = [{'Key': k, 'Value': v} for k, v in tags.items()]
    ec2_client.create_tags(Resources=[ami_id], Tags=tag_list)
