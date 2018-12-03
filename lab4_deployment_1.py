
# This is part 1 of a deployment script that launches an AWS instance,
# copy files to the server, and launches the frontend after it is started.

# This part creates an AWS instance, copies over part 2 of the script and runs it.

import os
import csv
import boto.ec2
import paramiko

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

    # delete_key_pair_file
    try:
        os.remove(KEY_PAIR_FILE)
    except:
        pass

    # create_key_pair
    try:
        key_pair = connection.create_key_pair(KEY_PAIR_NAME)
        key_pair.save('.')
        print('Key-Pair created!')
    except:
        print('Key-Pair already exists!')

    # create_security_group
    try:
        security_group = connection.create_security_group(name=SECURITY_GROUP_NAME,
                                                            description=SECURITY_GROUP_DESCRIPTION)
        security_group.authorize('ICMP', -1, -1, '0.0.0.0/0')
        security_group.authorize('TCP', 22, 22, '0.0.0.0/0')
        security_group.authorize('TCP', 80, 80, '0.0.0.0/0')
        print('Security group created!')
    except:
        print('Security group already exists!')

    # run_instance
    reservation_instance = connection.run_instances(image_id='ami-8caa1ce4',
                                                    key_name=KEY_PAIR_NAME,
                                                    security_groups=[SECURITY_GROUP_NAME],
                                                    instance_type='t1.micro')
    instance = reservation_instance.instances[0]
    print('Instance started!')

    # check_instance_status
    while instance.state != 'running':
        sleep(1)

    # allocate_associate_Elastic_IP_address
    address = connection.allocate_address()
    address.associate(instance.id)
    print('IP address obtained!')

    # ssh to the instance and run lab4_deployment_2.py on it
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_stdin = ssh_stdout = ssh_stderr = None

        # copy lab4_deployment_2.py to the remote machine
        os.system("scp -i key_pair.pem lab4_deployment_2.py ubuntu@" + address + ":~/")

        # run lab4_deployment_2.py on the remote machine
        ssh.connect(address, username="ubuntu", key_filename=KEY_PAIR_FILE)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("python lab4_deployment_2.py")

        print('Setup successful!')
        print('The public DNS is http://' + address + ':8080')
        print('The instance ID is ' + instance.id)
        print('Goodbye!')
    except:
        print('Setup failed! Exiting...')
        raise
