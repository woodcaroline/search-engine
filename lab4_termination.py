
# This is a termination script that shuts down an active instanceself.

import os
import csv
import boto.ec2

CREDENTIALS_FILE = 'credentials.csv'

KEY_PAIR_NAME = 'key_pair'
KEY_PAIR_FILE = 'key_pair.pem'
SECURITY_GROUP_NAME = 'csc326-group33'
SECURITY_GROUP_DESCRIPTION = 'csc326-group33'

if __name__ == "__main__":

    # establish_connection
    try:
        with open(CREDENTIALS_FILE) as csv_file:
            csv_text = csv.reader(csv_file)

            header = True
            for line in csv_text:
                if header: header = False
                else:
                    access_key_id = line[2]
                    secret_access_key = line[3]
        print('Credentials found!')
    except:
        print('Credentials not found! Exiting...')
        raise

    try:
        connection = boto.ec2.connect_to_region('us-east-1', aws_access_key_id=access_key_id,
                                                        aws_secret_access_key=secret_access_key)
        print('Connection successful!')
    except:
        print('Connection failed! Exiting...')
        raise

    try:
        instance_ID = raw_input('Enter the instance ID: ')
        connection.terminate_instances(instance_ID)

        print('Termination successful!')
        print('Goodbye!')
    except:
        print('Termination failed! Exiting...')
        raise
