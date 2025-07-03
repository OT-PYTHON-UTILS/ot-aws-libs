import os
import logging
from dotenv import load_dotenv
from aws_session_manager import AssumeRoleSessionManager

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Load environment variables
load_dotenv()

def setup_session():
    mode = os.getenv("MODE", "STS").upper()
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    role_arn = os.getenv("AWS_ROLE_ARN")

    if mode == "STS":
        logger.info("[MODE: STS] Using AssumeRole with session refresh logic.")
        duration_seconds = 3600
        threshold_minutes = 10
        extension_minutes = 30

        session_mgr = AssumeRoleSessionManager(
            access_key=access_key,
            secret_key=secret_key,
            role_arn=role_arn
        )

        session_mgr.main(
            duration_seconds=duration_seconds,
            threshold_minutes=threshold_minutes,
            extension_minutes=extension_minutes
        )

    elif mode == "IAM":
        logger.info("[MODE: IAM] Using static IAM credentials without assume-role.")
        # In IAM mode, we bypass assume_role and just store the credentials directly
        class StaticSessionManager:
            def __init__(self, access_key, secret_key):
                self.credentials = {
                    "aws_access_key_id": access_key,
                    "aws_secret_access_key": secret_key,
                    "aws_session_token": None  # No token needed
                }

            def get_current_credentials(self):
                return self.credentials

        session_mgr = StaticSessionManager(access_key, secret_key)

    else:
        raise ValueError(f"Invalid MODE '{mode}'. Use either 'STS' or 'IAM'.")

    return session_mgr


