
# This module contains all necessary functions for managing a server session,
# such as creating/getting/deleting key-pairs, security-groups, instances, and Elastic IP addresses

import os
import csv
import boto.ec2

CREDENTIALS_FILE = 'credentials.csv'

KEY_PAIR_NAME = 'key-pair'
KEY_PAIR_FILE = 'key-pair.pem'
SECURITY_GROUP_NAME = 'csc326-group33'
SECURITY_GROUP_DESCRIPTION = 'csc326-group33'


# ------------------------- connection -------------------------

def establish_connection():
    with open(CREDENTIALS_FILE) as csv_file:
        csv_text = csv.reader(csv_file)

        header = True
        for line in csv_text:
            if header: header = False
            else:
                access_key_id = line[2]
                secret_access_key = line[3]

    return boto.ec2.connect_to_region('us-east-1', aws_access_key_id=access_key_id,
                                                    aws_secret_access_key=secret_access_key)


# ------------------------- key-pair -------------------------

def create_key_pair(connection):
    key_pair = connection.create_key_pair(KEY_PAIR_NAME)
    key_pair.save('.')
    return key_pair

def delete_key_pair(connection):
    connection.delete_key_pair(KEY_PAIR_NAME)

def delete_key_pair_file(): # remove 'key-pair.pem' from the current directory
    os.remove(KEY_PAIR_FILE)


# ------------------------- security-group -------------------------

def create_security_group(connection):
    security_group = connection.create_security_group(name=SECURITY_GROUP_NAME,
                                                        description=SECURITY_GROUP_DESCRIPTION)
    security_group.authorize('ICMP', -1, -1, '0.0.0.0/0')
    security_group.authorize('TCP', 22, 22, '0.0.0.0/0')
    security_group.authorize('TCP', 80, 80, '0.0.0.0/0')

    return security_group

def get_security_group(connection):
    security_group_list = connection.get_all_security_groups()
    return security_group_list[0]

def get_all_security_group(connection):
    return connection.get_all_security_groups()

def delete_security_group(connection, security_group_name=SECURITY_GROUP_NAME):
    connection.delete_security_group(security_group_name)


# ------------------------- instance -------------------------

def run_instance(connection):
    reservation_instance = connection.run_instances(image_id='ami-8caa1ce4',
                                                    key_name=KEY_PAIR_NAME,
                                                    security_groups=[SECURITY_GROUP_NAME],
                                                    instance_type='t1.micro')
    return reservation_instance.instances[0]

def start_instance(connection, instance):
    connection.start_instances([instance.id])

def stop_instance(connection, instance):
    connection.stop_instances([instance.id], force=True)

def get_instance(connection): # get a pending/running/stoppping/stopped instance
    reservation_instance_list = connection.get_all_reservations()

    for reservation in reservation_instance_list:
        for instance in reservation.instances:
            if instance.state != 'terminated' and instance.state != 'shutting-down':
                return instance

def get_all_instances(connection): # get all pending/running/stoppping/stopped instances
    instance_list = []
    reservation_instance_list = connection.get_all_reservations()

    for reservation in reservation_instance_list:
        for instance in reservation.instances:
            if instance.state != 'terminated' and instance.state != 'shutting-down':
                instance_list.add(instance)

    return instance_list

def check_instance_status(instance): # returns either pending/running/stopping/stopped
    return instance.state

def terminate_instance(connection, instance):
    connection.terminate_instances(instance.id)

def terminate_all_instances(connection):
    reservation_instance_list = connection.get_all_reservations()

    for reservation in reservation_instance_list:
        for instance in reservation.instances:
            if instance.state != 'terminated' and instance.state != 'shutting-down':
                connection.terminate_instances(instance.id)


# ------------------------- IP address -------------------------

def allocate_associate_Elastic_IP_address(connection, instance):
    address = connection.allocate_address()
    address.associate(instance.id)
    return address

def release_Elastic_IP_address(address):
    address.release()

def get_IP_address(instance):
    return instance.ip_address

def get_Elastic_IP_address(address):
    return address.public_ip

def get_Elastic_IP_address_instance_ID(address):
    return address.instance_id
