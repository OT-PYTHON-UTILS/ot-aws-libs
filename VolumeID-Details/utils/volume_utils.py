import boto3

def fetch_volumes_and_snapshots(session, region):
    ec2 = session.client("ec2", region_name=region)

    volumes = ec2.describe_volumes()["Volumes"]
    
    data = []

    for vol in volumes:
        volume_id = vol["VolumeId"]
        volume_type = vol.get("VolumeType", "-")
        size = vol.get("Size", "-")
        iops = vol.get("Iops", "-")
        throughput = vol.get("Throughput", "-")
        snapshot_id = vol.get("SnapshotId", "-")
        state = vol.get("State", "-")

        instance_id = "-"
        instance_name = "-"

        attachments = vol.get("Attachments", [])
        if attachments:
            instance_id = attachments[0].get("InstanceId", "-")
            try:
                instance_details = ec2.describe_instances(InstanceIds=[instance_id])
                tags = instance_details["Reservations"][0]["Instances"][0].get("Tags", [])
                instance_name = next((tag["Value"] for tag in tags if tag["Key"] == "Name"), "-")
            except Exception:
                instance_name = "-"

        data.append({
            "Region": region,
            "Volume ID": volume_id,
            "Type": volume_type,
            "Size In GiB": size,
            "IOPS": iops,
            "Throughput": throughput,
            "Snapshot ID": snapshot_id,
            "Volume state": state,
            "Instance ID": instance_id,
            "Instance Name": instance_name
        })

    return data
