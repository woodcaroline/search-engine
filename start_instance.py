
# CSC326 Lab 2

# Python script for launching EC2 instance on AWS

# Note: This script assumes that:
#   1. credentials.csv (downloaded from aws.amazon.com) is in the current directory
#   2. key-pair with the name 'key-pair' has not been created
#   3. there is no file named 'key-pair.pem' inside the current directory
#   4. security-group with the name 'csc326-group33' has not been created

# See server.py for function implementations
from server import *

if __name__ == "__main__":
    connection = establish_connection()
    key_pair = create_key_pair(connection)
    security_group = create_security_group(connection)
    instance = run_instance(connection)
