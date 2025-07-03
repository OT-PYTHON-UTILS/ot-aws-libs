from EC2ServiceWithRefresh import EC2ServiceWithRefresh
from aws_session_manager.session_setup import setup_session

# creates a valid session and assumes role
session_mgr = setup_session()


service = EC2ServiceWithRefresh(session_mgr)
response = service.describe_instances()

print(f"[INFO] All EC2 instances: {response}")

