import yaml
import pandas as pd
import os
import sys
from otawslibs.generate_aws_session import _create_session
sys.path.append(os.path.join(os.path.dirname(__file__), 'ec2_utils_lib'))
from utils.volume_utils import fetch_volumes_and_snapshots

def main():
    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    regions = config.get("regions", [])
    aws_profile = config.get("aws_profile")
    role_arn = config.get("role_arn")

    session = _create_session(aws_profile=aws_profile, role_arn=role_arn)

    for region in regions:
        print(f"🔍 Fetching data for region: {region}")
        data = fetch_volumes_and_snapshots(session, region)

        if not data:
            print(f"⚠️ No volumes found in region: {region}")
            continue

        # 🛠️ Ab yahan pehi folder banega, jab data milega
        os.makedirs("output", exist_ok=True)

        df = pd.DataFrame(data)
        output_file = f"output/volume_snapshot_report_{region}.csv"
        df.to_csv(output_file, index=False)
        print(f"✅ Report generated for region {region}: {output_file}")

if __name__ == "__main__":
    main()
