# 📄 Document: **Volume Fetcher Utility**

---

## 1. 🧩 Introduction

This utility fetches details of **EBS Volumes** and their **attached Snapshots** across one or multiple AWS regions.  
It automatically handles authentication using AWS Profile or Role ARN as specified in a YAML configuration file.  

The utility generates a **separate CSV report** for each region containing complete volume details.

---

## 2. ⚙️ How it Works

- **Reads `config.yaml`** for AWS profile, Role ARN, and region list.
- **Creates a session** (either from profile or by assuming a role).
- **Iterates over each region**:
  - Fetches all volumes.
  - Checks whether the volume is attached or available.
  - If attached, fetches the **Instance ID** and **Instance Name**.
- **Outputs a CSV file** for each region where volumes are found.
- If no volumes are found in a region, **no folder or file is created** and a warning is printed.

---

## 3. 🔥 Function Description

| Function Name | Description |
|:--------------|:------------|
| `fetch_volumes_and_snapshots(session, region)` | Connects to EC2 in the given region and retrieves volume details. If volume is attached, also retrieves instance details. Returns data as a list of dictionaries. |
| `main()` | Reads configuration, creates session, calls the volume fetching function for each region, and writes output to CSV if volumes exist. |

---

## 4. ⚙️ `config.yaml` Attributes

| Attribute | Type | Description |
|:----------|:-----|:------------|
| `regions` | List of Strings | List of AWS regions where volumes will be fetched from. |
| `aws_profile` | String | Name of AWS profile from local machine credentials (optional if using role_arn). |
| `role_arn` | String | ARN of the IAM role to assume (optional if using aws_profile). |

✅ Either `aws_profile` or `role_arn` must be provided.

### Example `config.yaml`

```yaml
regions:
  - us-east-1
  - eu-west-1

aws_profile: my-aws-profile
role_arn: arn:aws:iam::123456789012:role/MyRole
```

---

## 5. 🛠️ Functionalities

- Supports **multiple AWS regions**.
- Fetches all volume details:
  - Volume ID
  - Volume Type
  - Size (GiB)
  - IOPS
  - Throughput
  - Snapshot ID
  - Volume State
  - Attached Instance ID (or "-" if not attached)
  - Attached Instance Name (or "-" if not attached)
- Handles **both** AWS **Profile** and **IAM Role** based authentication.
- Creates **separate CSV reports** per region.
- **Skips** folder creation if no volumes are found.
- **Clean output format** suitable for reports and audits.

---

## 6. 📄 Output Example

If volumes are found, a file will be created like:

```bash
output/volume_snapshot_report_us-east-1.csv
output/volume_snapshot_report_eu-west-1.csv
```

### Example CSV content:

| Region    | Volume ID          | Type | Size In GiB | IOPS | Throughput | Snapshot ID      | Volume state | Instance ID      | Instance Name |
|:----------|:-------------------|:-----|:------------|:-----|:-----------|:-----------------|:-------------|:-----------------|:--------------|
| us-east-1 | vol-0abc1234def56789a | gp3 | 100          | 3000 | 125         | snap-07e43fdbd2   | in-use       | i-0123456789abcdef | WebServer-1   |
| us-east-1 | vol-0xyz1234lmn56789b | gp2 | 50           | 1000 | -           | -                | available    | -               | -             |

If no volumes found in a region:

```bash
⚠️ No volumes found in region: us-east-1
```

and no output file or folder will be created.

---

## 7. 🧹 Folder Structure

```
VolumeID-Details/
├── config.yaml
├── requirements.txt
├── utils/
│   ├── aws_session.py
│   └── volume_utils.py
├── volume_report.py
└── output/
    ├── (Generated CSV files here)
```

---

## 8. ✅ Installation

Install required dependencies using:

```bash
pip install -r requirements.txt
```

---

## 9. 🚀 How to Run

Just execute:

```bash
python3 volume_report.py
```

---

# 🛡️ Summary

This tool helps you generate organized reports about your EBS Volumes and Snapshots,  
supports AWS Profiles and IAM Roles, and automatically handles empty regions smartly without unnecessary file clutter.

---