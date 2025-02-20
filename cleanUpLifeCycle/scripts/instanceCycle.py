import subprocess
import yaml

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def main():
    config_path = "/home/khushimalhotra/Desktop/Office/cleanUpLifeCycle/config/config.yaml"
    config = load_config(config_path)

    # Step 1: Run fetchInstancesDetails.py
    print("Running fetchInstancesDetails.py...")
    subprocess.run(["python3", "fetchInstancesDetails.py"])

    # Step 2: Run stopInstances.py
    print("Running stopInstances.py...")
    subprocess.run(["python3", "stopInstances.py"])

    # Step 3: Run terminateInstances.py
    if config.get('terminateInstances', {}).get('terminate', 'no').lower() != "yes":
        print("Instance termination is disabled in config.yaml")
        return
    
    print("Running terminateInstances.py...")
    subprocess.run(["python3", "terminateInstances.py"])

if __name__ == "__main__":
    main()