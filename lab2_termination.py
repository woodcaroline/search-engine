
# CSC326 Lab 2

# Python script for terminating EC2 instance on AWS

# Note: This script assumes that:
#   1. credentials.csv (downloaded from aws.amazon.com) is in the current directory

# See server.py for function implementations
from server import *

if __name__ == "__main__":
    connection = establish_connection()
    terminate_all_instances(connection)
