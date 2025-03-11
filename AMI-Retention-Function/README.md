## Automated AMI Retention Policy

This document explains the AWS Lambda function and EventBridge scheduler that automate the deletion of EC2 AMIs based on a defined retention period.

Overview
- This setup ensures that old AMIs are automatically deleted after a specified number of days. 
It includes:
- A Lambda function that scans AMIs, checks their retention period, and deletes expired ones.
- An EventBridge rule that triggers the Lambda function daily.
- Environment variables for easy configuration of retention and snapshot deletion.

![image](https://github.com/user-attachments/assets/6e8327e7-2f96-42ad-b502-4020126358a6)


## 1️⃣ Lambda Function: AMI Cleanup

Functionality:

- Fetches AMIs tagged with Backup = true.
- Reads the Stopped tag to get the AMI's creation date.
- Compares the age of the AMI with the retention period (RETENTION_DAYS).
- If the AMI is older than the retention period:
- It is deregistered (deleted).
- If SNAPSHOT_DELETION = true, associated snapshots are also deleted.

<details>
  <summary> Lambda Function Code </summary>
<br>

```shell 
import boto3
import datetime
import os

ec2_client = boto3.client('ec2')

def lambda_handler(event, context):
    retention_days = int(os.getenv("RETENTION_DAYS", 30))
    snapshot_deletion = os.getenv("SNAPSHOT_DELETION", "false").lower() == "true"
    backup_tag_key = os.getenv("BACKUP_TAG_KEY", "Backup")
    backup_tag_value = os.getenv("BACKUP_TAG_VALUE", "true")
    stopped_tag_key = os.getenv("STOPPED_TAG_KEY", "Stopped")  # Tag key for the date

    today = datetime.datetime.utcnow().date()

    # Fetch AMIs that have Backup=true
    amis = ec2_client.describe_images(
        Owners=['self'],
        Filters=[{'Name': f'tag:{backup_tag_key}', 'Values': [backup_tag_value]}]
    )['Images']

    for ami in amis:
        ami_id = ami['ImageId']
        tags = {tag['Key']: tag['Value'] for tag in ami.get('Tags', [])}

        # Ensure AMI has a Stopped tag with a valid date
        stopped_date_str = tags.get(stopped_tag_key)
        if not stopped_date_str:
            print(f"Skipping AMI {ami_id}: No '{stopped_tag_key}' tag found.")
            continue

        try:
            creation_date = datetime.datetime.strptime(stopped_date_str, "%Y-%m-%d").date()
        except ValueError:
            print(f"Skipping AMI {ami_id}: Invalid date format in '{stopped_tag_key}' tag.")
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
```
</details>

## 2️⃣ EventBridge Scheduler

Functionality:

- Automates the Lambda execution by triggering it every 24 hours.
- Ensures expired AMIs are deleted without manual intervention.
- Uses a Cron expression to define the execution schedule.

<details>
  <summary> Cron Expression </summary>
<br>

```shell
cron(0 0 * * ? *)
```
</details>

- Runs every day at 00:00 UTC.
- Ensures daily cleanup of expired AMIs.

## 3️⃣ Environment Variables  

| Variable          | Description                                             | Default Value |
|------------------|---------------------------------------------------------|--------------|
| RETENTION_DAYS   | Number of days to keep AMIs before deletion             | 30           |
| SNAPSHOT_DELETION | If `true`, deletes associated snapshots when AMI is deleted | false        |
| BACKUP_TAG_KEY   | Tag key used to identify AMIs                | Backup       |
| BACKUP_TAG_VALUE | Tag value used to identify AMIs             | true         |
| STOPPED_TAG_KEY  | Reads the Stopped tag to determine the AMI creation date.     | Stopped      |

## 4️⃣ How This Works (Flow)

Functionality

- 1️⃣ Lambda Function
Scans AMIs, checks retention, deletes expired ones

- 2️⃣ EventBridge
Triggers Lambda function every 24 hours

- 3️⃣ Environment Variables
Controls retention period & snapshot deletion

## 5️⃣ Example Workflow

- March 1, 2025:
  --- AMI created with:
  ```shell
         Backup = true
         Stopped = 2025-03-01
  ```
- March 31, 2025 (30 days later, RETENTION_DAYS = 30):
  --- Lambda function deletes AMI.
  --- If SNAPSHOT_DELETION = true, snapshots are also deleted.

- April 1, 2025:
  --- EventBridge triggers Lambda again.
  --- New expired AMIs are deleted.


## 6️⃣ Conclusion

✅ Lambda Function → Deletes AMIs automatically after RETENTION_DAYS.
✅ EventBridge → Runs Lambda daily to clean up expired AMIs.
✅ Environment Variables → Configure retention & snapshot deletion easily.

This setup ensures automated AMI lifecycle management, saving storage costs while maintaining backups for a defined period. 🚀


