
# 📘 EC2 INSTANCE REPORTER - DOCUMENTATION


## 🧩 INTRODUCTION
--------------------------------------------------------------------------------
The EC2 Instance Reporter is a Python-based utility that fetches and reports
details of EC2 instances across multiple AWS regions. It is driven by a
configurable YAML file that allows you to:

- Filter instances by tag or ID
- Fetch CPU utilization using CloudWatch
- Generate a CSV report with all metadata
- Set time ranges using absolute or relative dates
- Use AWS named profiles for authentication

Designed for DevOps, Cloud Engineers, or FinOps teams to analyze EC2 usage.

--------------------------------------------------------------------------------

## 🗂️ DIRECTORY STRUCTURE
--------------------------------------------------------------------------------

```plaintext
ec2-reporter/
├── main.py                          # Main script to run everything
├── config.yaml                      # YAML config for controlling behavior
├── requirements.txt                 # Dependencies including Git-based utils
├── utils/                           # Modular helper functions
│   ├── __init__.py                  # Makes utils folder a package
│   ├── ec2_utils.py                 # EC2 metadata, volume & instance info
│   ├── cloudwatch_utils.py          # CPU stats via CloudWatch
│   └── filters.py                   # Filtering logic (tags or ID)
└── output/
    └── ec2_instance_report.csv      # Final output (generated after run)
```

--------------------------------------------------------------------------------

## ⚙️ CONFIG STRUCTURE (config.yaml)
--------------------------------------------------------------------------------
| **Attribute**                     | **Description**                                                                                                                         |
|------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| `regions`                          | List of AWS regions to scan for EC2 instances (e.g., `us-east-1`, `eu-west-1`).                                                         |
| `aws_profile`                      | AWS CLI profile name for authentication (required).                                                                                     |
| `role_arn` | Optional: IAM Role ARN to assume when creating the session. If `aws_profile` is not provided, this will be used to assume a role via STS. |
| `instance_ids_file`                | Path to a CSV file containing EC2 instance IDs. If not used, instances are fetched by tags.                                             |
| `filter_by_tags`                   | Boolean (`true/false`) to enable or disable tag-based filtering.                                                                        |
| `match_all_tags`                   | If `true`, only instances that match all tags will be fetched. If `false`, instances match any tag.                                     |
| `tags`                             | Dictionary of tags (key-value pairs) to filter EC2 instances (e.g., `{"Environment": "production"}`).                                   |
| `cpu_utilization.period`           | Time period (in seconds) for CPU utilization stats (e.g., `300` for 5 minutes).                                                         |
| `cpu_utilization.start`            | Optional: Absolute start date in ISO 8601 format (`YYYY-MM-DDTHH:MM:SSZ`) for CPU statistics.                                           |
| `cpu_utilization.end`              | Optional: Absolute end date in ISO 8601 format (`YYYY-MM-DDTHH:MM:SSZ`) for CPU statistics.                                             |
| `cpu_utilization.last_n_days`      | Optional: If start and end are not provided, the number of past days to fetch CPU data for.                                               |


--------------------------------------------------------------------------------

## 🔧 EACH MODULE’S ROLE
--------------------------------------------------------------------------------

### ☁️ cloudwatch_utils.py → get_cpu_utilization(...)
#### Functionality:
- Fetches CPU stats from CloudWatch
#### Input:
- session, region, instance_id, start_time, end_time, period

#### Behavior:
- If start & end are given → uses absolute time range
- If last_n_days is given → generates relative window (e.g., 7 days ago → now)

#### Output:
- Returns a dictionary with:
  --CPU Min
  --CPU Max
  --CPU Avg

#### Notes:
- Skips instance if it’s stopped
- Handles pagination (if needed)

### 💻 ec2_utils.py → fetch_instances(...)
#### Functionality:
- Retrieves EC2 instance metadata and volume info

#### Input:
- session, region
- Optional: instance_ids_file, filter_by_tags, tags

#### Behavior:
- If instance_ids_file is given → fetches by those instance IDs
- If filter_by_tags: true:
- match_all_tags = true → instance must match all tags
- match_all_tags = false → instance can match any tag

#### Output:
- List of EC2 instances (as dictionaries)

### 🧹 filters.py → filter_instances_by_tags(...)
#### Functionality:
- Applies tag-based filters to EC2 instance list

#### Behavior:
- Supports both AND and OR logic via match_all_tags

### 🧠 main.py
#### Functionality:
- Reads config.yaml
- Creates session via _create_session(...) (supports aws_profile or role_arn)
- Iterates through all regions
- Fetches EC2 instance info
- For each instance:
  --Gets volume and EBS details
  --Gets CloudWatch CPU stats
- Combines all data
- Exports result to output/ec2_instance_report.csv via Pandas

### 🧩 utils/__init__.py
- Required to treat utils as a Python package

--------------------------------------------------------------------------------

## 🧪 HOW TO RUN THE PROJECT
--------------------------------------------------------------------------------

🔹 STEP 1: CLONE REPO
$ git clone https://github.com/yourusername/ec2-reporter.git
$ cd ec2-reporter

🔹 STEP 2: INSTALL DEPENDENCIES
$ pip install -r requirements.txt

🔹 STEP 3: CONFIGURE YAML
- Edit `config.yaml` to:
  - Add AWS regions
  - Choose tag or ID filtering
  - Configure CPU date range
  - Set your AWS CLI profile name

🔹 STEP 4: EXECUTE SCRIPT
$ python main.py

✅ Output will be saved in: output/ec2_instance_report.csv

--------------------------------------------------------------------------------

## 📤 FINAL OUTPUT
--------------------------------------------------------------------------------

### EC2 Instance Reporter - CSV Output Structure


The CSV output generated by the EC2 Instance Reporter will contain the following columns:

| **Column Name**    | **Description**                                                                                  |
|--------------------|--------------------------------------------------------------------------------------------------|
| `Region`           | The AWS region in which the EC2 instance is located (e.g., `us-east-1`, `eu-west-1`).            |
| `Instance ID`      | The unique identifier for the EC2 instance (e.g., `i-1234567890abcdef0`).                        |
| `Instance Name`    | The name of the EC2 instance, typically the `Name` tag value.                                    |
| `State`            | The current state of the EC2 instance (e.g., `running`, `stopped`).                              |
| `Type`             | The type of EC2 instance (e.g., `t2.micro`, `m5.large`).                                          |
| `Public IP`        | The public IP address assigned to the EC2 instance, if applicable (e.g., `54.1.2.3`).            |
| `Elastic IP`       | The Elastic IP address associated with the EC2 instance, if any.                                 |
| `Private IP`       | The private IP address of the EC2 instance (e.g., `172.31.2.3`).                                |
| `Volume ID`        | The ID of the EBS volume attached to the EC2 instance (e.g., `vol-12345678`).                    |
| `EBS Optimized`    | Whether the EC2 instance is EBS-optimized (e.g., `true`, `false`).                               |
| `Storage (GB)`     | The storage size (in GB) of the attached EBS volume.                                              |
| `ASG`              | The name of the Auto Scaling Group (ASG) to which the instance belongs, if applicable.           |
| `Pricing`          | The pricing model of the EC2 instance (e.g., `On-Demand`, `Reserved`, `Spot`).                    |
| `CPU Min`          | The minimum CPU utilization for the EC2 instance during the selected period.                     |
| `CPU Max`          | The maximum CPU utilization for the EC2 instance during the selected period.                     |
| `CPU Avg`          | The average CPU utilization for the EC2 instance during the selected period.                     |

### Example of Output:
| **Region** | **Instance ID**      | **Instance Name** | **State** | **Type**   | **Public IP** | **Elastic IP** | **Private IP** | **Volume ID**   | **EBS Optimized** | **Storage (GB)** | **ASG**     | **Pricing**  | **CPU Min** | **CPU Max** | **CPU Avg** |
|------------|----------------------|-------------------|-----------|------------|---------------|----------------|----------------|-----------------|-------------------|------------------|-------------|--------------|-------------|-------------|-------------|
| us-east-1  | i-1234567890abcdef0  | MyInstance        | running   | t2.micro   | 54.1.2.3      | -              | 172.31.2.3     | vol-12345678    | true              | 20               | MyASG       | On-Demand   | 0.5         | 1.2         | 0.8         |
| eu-west-1  | i-9876543210fedcba   | TestInstance      | stopped   | m5.large   | -             | -              | 172.31.4.5     | vol-87654321    | true              | 50               | TestASG     | On-Demand   | 0.1         | 0.3         | 0.2         |


--------------------------------------------------------------------------------

## 📘 CONCLUSION
--------------------------------------------------------------------------------

This EC2 Instance Reporter is:

✅ Flexible - YAML-driven with full control  
✅ Scalable - Supports multiple regions & accounts  
✅ DevOps Ready - Use in CI/CD or manually  
✅ Extendable - Modular design for easy plugin (e.g., cost analysis)

--------------------------------------------------------------------------------
