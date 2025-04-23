import csv
import time

def read_instance_data(csv_file):
    instances = []
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            instances.append({'InstanceID': row['InstanceID'], 'InstanceName': row['InstanceName']})
    return instances

def store_ami_details(ami_id, ami_name, output_csv):
    with open(output_csv, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([ami_id, ami_name, time.strftime('%Y-%m-%d %H:%M:%S')])
