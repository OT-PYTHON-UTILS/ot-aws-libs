# 📄 Document: **Billing Report Utility**

---

## 1. 🧩 Introduction

The **Billing Report Utility** fetches the billing data for your AWS account using **AWS Cost Explorer**. It automatically gathers and processes the cost data for various services over a specified date range and outputs a **detailed Excel report** that provides a clear breakdown of costs, usage, and service contributions.

This utility allows AWS users to easily track and analyze their billing information by providing an organized report.

---

## 2. ⚙️ How it Works

- **Fetches cost data** from AWS using the **Cost Explorer API** for a given time period (start and end date).
- **Filters and processes** the data to calculate the total cost for each service and its percentage contribution to the overall total cost.
- **Writes the results to an Excel file** with detailed columns for service names, costs, and percentage contributions.

---

## 3. 🔥 Function Description

| Function Name | Description |
|:--------------|:------------|
| `fetch_cost_data(session, start_date, end_date)` | Connects to AWS Cost Explorer and fetches the cost and usage data for the specified time range. |
| `calculate_percentage_contribution(data)` | Calculates the percentage contribution of each service to the total cost. |
| `write_to_excel(data, output_file)` | Writes the processed data into an Excel file. |
| `main()` | Orchestrates the flow by reading the configuration, fetching the cost data, calculating percentages, and writing the final output to Excel. |

---

## 4. ⚙️ `config.yaml` Attributes

| Attribute            | Type    | Description |
|:---------------------|:--------|:------------|
| `start_date`         | String  | Start date of the billing period in `YYYY-MM-DD` format. |
| `end_date`           | String  | End date of the billing period in `YYYY-MM-DD` format. |
| `aws_profile`        | String  | AWS profile name to use for authentication (optional if using role ARN). |
| `role_arn`           | String  | ARN of the IAM role to assume (optional if using aws_profile). |
| `output_excel`       | String  | Path to the output Excel file where the data will be saved. |

### Example `config.yaml`

```yaml
start_date: '2025-02-01'
end_date: '2025-02-28'
aws_profile: my-aws-profile
role_arn: arn:aws:iam::123456789012:role/MyBillingRole
output_excel: 'billing_report_february.xlsx'
```

---

## 5. 🛠️ Functionalities

- Fetches cost and usage data from **AWS Cost Explorer** for a specified time period.
- Supports **AWS Profile** and **IAM Role** based authentication for accessing the Cost Explorer API.
- Calculates the **percentage contribution** of each AWS service to the total cost.
- **Writes the results to an Excel file**, with data organized in a clear, tabular format.
- **Supports different date ranges** to generate reports for various billing periods.

---

## 6. 📄 Output Example

After running the script, the generated Excel report will contain a table like this:

| Service                              | Cost (USD) | Percentage Contribution (%) |
|:-------------------------------------|:-----------|:----------------------------|
| Elastic Load Balancing               | 35.75      | 40.43                       |
| Virtual Private Cloud                | 20.16      | 22.80                       |
| Elastic Compute Cloud                | 10.58      | 7.14                        |
| Cost Explorer                        | 5.80       | 6.18                        |
| Key Management Service               | 2.00       | 2.26                        |
| Secrets Manager                       | 0.40       | 0.45                        |
| Relational Database Service          | 0.06       | 0.07                        |
| CloudWatch                           | 0.05       | 0.05                        |
| EC2 Container Registry (ECR)         | 0.01       | 0.01                        |
| Simple Storage Service               | 0.00       | 0.00                        |
| Data Transfer                        | 0.00       | 0.00                        |
| CloudFormation                       | 0.00       | 0.00                        |
| Glue                                 | 0.00       | 0.00                        |
| Simple Notification Service          | 0.00       | 0.00                        |
| Simple Queue Service                 | 0.00       | 0.00                        |
| **Total Tax**                         | **13.46**  | **15.78**                   |

**Note**: If no data is found for the given date range, the report will not be generated and a warning message will appear.

---

## 7. 🧹 Folder Structure

```
Billing-Report-Utility/
├── config.yaml
├── requirements.txt
├── modules/
│   ├── fetch_cost_data.py
│   └── save_to_excel.py
├── main.py
└── output/
    ├── (Generated Excel file here)
```

---

## 8. ✅ Installation

To install the necessary dependencies, run:

```bash
pip install -r requirements.txt
```

---

## 9. 🚀 How to Run

After installing the required dependencies, run the script by executing:

```bash
python3 main.py
```

---

## 🛡️ Summary

The **Billing Report Utility** helps AWS users generate clear and detailed billing reports for any given period.  
It fetches and processes AWS billing data from **Cost Explorer**, calculates percentage contributions for each service, and outputs the data into a clean Excel format suitable for audits, analysis, and reporting.

---