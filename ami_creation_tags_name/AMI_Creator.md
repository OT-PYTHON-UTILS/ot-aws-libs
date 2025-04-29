# 📘 AMI Creator - Workflow & Function Documentation

This document provides a comprehensive overview of the **AMI Creation Tool**. It describes the purpose, logic, inputs, and interactions of each module, function, and configuration in a clear, structured format.

---

## 🧭 Workflow Summary

The tool reads EC2 instance data from a CSV, checks each instance's state, creates an AMI (Amazon Machine Image), tags it with relevant metadata, and stores AMI details in an output CSV.

---

## ⚙️ Configuration File (`config.yaml`)

| Attribute        | Type   | Description                                                                                   |
|------------------|--------|-----------------------------------------------------------------------------------------------|
| `aws_region`     | String | AWS region where the resources are located.                                                  |
| `input_csv`      | Path   | Full path to the input CSV file containing instance IDs and names.                          |
| `output_csv`     | Path   | Output file to log created AMI IDs with timestamp.                                          |
| `additional_tags`| Dict   | Tags to attach to the AMI. Includes default tags and dynamically added tags like date.      |
| `role_arn`       | String | Optional IAM Role ARN for assuming a different role.                                         |
| `aws_profile`    | String | Optional AWS profile name to use with credentials.                                           |

---

## 🗂️ File Overview & Functions

### 1️⃣ `main.py`

#### 🔹 Purpose:
- Entry point of the script. Orchestrates config loading, session creation, and AMI workflow.

#### 🔸 Key Functions Used:
- `read_config()` (from `config_reader.py`)
- `_create_session()` (from `session_utils.py`)
- `read_instance_data()` (from `csv_utils.py`)
- `get_instance_state()`, `fetch_instance_tags()` (from `instance_utils.py`)
- `create_ami()`, `tag_ami()` (from `ami_utils.py`)
- `store_ami_details()` (from `csv_utils.py`)

#### 🧾 Inputs:
- Config path from environment variable `CONFIG_PATH`

---

### 2️⃣ `config_reader.py`

#### 🔹 Function: `read_config()`
#### 🔸 Purpose:
- Loads YAML configuration from file path defined in `CONFIG_PATH` env variable.
#### 📥 Input:
- None (fetches path from environment)
#### 📤 Output:
- Parsed configuration dictionary

---

### 3️⃣ `session_utils.py`

#### 🔹 Function: `_create_session()`
#### 🔸 Purpose:
- Returns a `boto3.Session` either using a profile, by assuming a role, or using default credentials.
#### 📥 Input:
- `aws_profile`: optional string
- `role_arn`: optional string
- `role_session_name`: optional session name (default: 'AssumeRoleSession')
#### 📤 Output:
- boto3 `Session` object

---

### 4️⃣ `csv_utils.py`

#### 🔹 Function: `read_instance_data()`
#### 🔸 Purpose:
- Reads instances from a CSV file with headers `InstanceID`, `InstanceName`.
#### 📥 Input:
- CSV path
#### 📤 Output:
- List of dictionaries containing instance ID and name

---

#### 🔹 Function: `store_ami_details()`
#### 🔸 Purpose:
- Appends AMI ID, AMI name, and timestamp to an output CSV.
#### 📥 Input:
- `ami_id`, `ami_name`, `output_csv`

---

### 5️⃣ `instance_utils.py`

#### 🔹 Function: `fetch_instance_tags()`
#### 🔸 Purpose:
- Retrieves existing tags for an instance
#### 📥 Input:
- EC2 client, instance ID
#### 📤 Output:
- Dictionary of tags (key-value pairs)

---

#### 🔹 Function: `get_instance_state()`
#### 🔸 Purpose:
- Returns the current state (running/stopped) of an instance
#### 📥 Input:
- EC2 client, instance ID
#### 📤 Output:
- String state

---

### 6️⃣ `ami_utils.py`

#### 🔹 Function: `create_ami()`
#### 🔸 Purpose:
- Creates an AMI from a given instance ID and AMI name
#### 📥 Input:
- EC2 client, instance ID, AMI name, `no_reboot` flag
#### 📤 Output:
- AMI ID string

---

#### 🔹 Function: `tag_ami()`
#### 🔸 Purpose:
- Applies tags to the created AMI
#### 📥 Input:
- EC2 client, AMI ID, dictionary of tags

---

## ✅ Execution Guide

```bash
# Set config path
export CONFIG_PATH=/path/to/ami_creator/config.yaml

# Run the main script
python3 ami_creator/main.py
```

---

## 📌 Notes
- Ensure IAM permissions are properly set for creating AMIs and assuming roles.
- All logs are printed on the console and stored in the output CSV.

---

