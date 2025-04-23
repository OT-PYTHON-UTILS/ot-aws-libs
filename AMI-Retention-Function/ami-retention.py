import boto3
import datetime
import os

ec2_client = boto3.client('ec2')

def lambda_handler(event, context):
    retention_days = int(os.getenv("RETENTION_DAYS", 30))
    snapshot_deletion = os.getenv("SNAPSHOT_DELETION", "false").lower() == "true"
    backup_tag_key = os.getenv("BACKUP_TAG_KEY", "Backup")
    backup_tag_value = os.getenv("BACKUP_TAG_VALUE", "true")
    backupdate_tag_key = os.getenv("backupdate_TAG_KEY", "Backup Date")  # Tag key for the date

    today = datetime.datetime.utcnow().date()

    # Fetch AMIs that have Backup=true
    amis = ec2_client.describe_images(
        Owners=['self'],
        Filters=[{'Name': f'tag:{backup_tag_key}', 'Values': [backup_tag_value]}]
    )['Images']

    for ami in amis:
        ami_id = ami['ImageId']
        tags = {tag['Key']: tag['Value'] for tag in ami.get('Tags', [])}

        # Ensure AMI has a Backup Date tag with a valid date
        backup_date_str = tags.get(backupdate_tag_key)
        if not backup_date_str:
            print(f"Skipping AMI {ami_id}: No '{backupdate_tag_key}' tag found.")
            continue

        try:
            creation_date = datetime.datetime.strptime(backup_date_str, "%Y-%m-%d").date()
        except ValueError:
            print(f"Skipping AMI {ami_id}: Invalid date format in '{backupdate_tag_key}' tag.")
            continue

        age = (today - creation_date).days

        # Delete AMI if it exceeds retention period
        if age >= retention_days:
            print(f"Deleting AMI {ami_id} (Created: {creation_date}, Age: {age} days)")

            # Get associated snapshots
            snapshot_ids = [bdm['Ebs']['SnapshotId'] for bdm in ami.get('BlockDeviceMappings', []) if 'Ebs' in bdm]

            # Deregister the AMI
            ec2_client.deregister_image(ImageId=ami_id)
            print(f"AMI {ami_id} deregistered successfully.")

            # Delete snapshots if enabled
            if snapshot_deletion:
                for snapshot_id in snapshot_ids:
                    ec2_client.delete_snapshot(SnapshotId=snapshot_id)
                    print(f"Snapshot {snapshot_id} deleted successfully.")

    return {"status": "Success"}
