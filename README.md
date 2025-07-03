# AWS Session Manager

A Python package for managing AWS temporary credentials and role assumption.

## Installation

bash
pip install git+https://github.com/OT-PYTHON-UTILS/ot-aws-libs.git
# to add in another project 

from aws_session_manager.session_setup import setup_session

session_mgr = setup_session()
creds = session_mgr.get_current_credentials()