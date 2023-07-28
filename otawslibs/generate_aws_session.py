import boto3

def _create_session(aws_profile=None, role_arn=None):
    
    if aws_profile:
        session = boto3.Session(profile_name=aws_profile)
    elif role_arn:
        sts_client = boto3.client('sts')
        assumed_role = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName='AssumeRoleSession'
        )
        session = boto3.Session(
            aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
            aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
            aws_session_token=assumed_role['Credentials']['SessionToken']
        )
    else:
        session = boto3.Session()

    return session