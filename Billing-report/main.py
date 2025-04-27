import yaml
import sys
import os
from otawslibs.generate_aws_session import _create_session
sys.path.append(os.path.join(os.path.dirname(__file__), 'ec2_utils_lib'))
from modules.fetch_cost_data import fetch_cost_data
from modules.generate_report import process_cost_data
from modules.save_to_excel import write_to_excel

def main():
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    aws_profile = config.get('aws_profile')
    role_arn = config.get('role_arn')
    start_date = config['billing_period']['start']
    end_date = config['billing_period']['end']
    output_excel = config['output_excel']

    # Create session
    session = _create_session(aws_profile, role_arn)

    # Fetch cost data
    cost_data = fetch_cost_data(session, start_date, end_date)

    # Process data
    df = process_cost_data(cost_data)

    # Write to Excel
    write_to_excel(df, output_excel)

    print(f"Billing report generated successfully: {output_excel}")

if __name__ == "__main__":
    main()
