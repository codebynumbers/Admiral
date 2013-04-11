from boto.ec2.connection import EC2Connection
from boto.ec2.blockdevicemapping import BlockDeviceType
from boto.ec2.blockdevicemapping import BlockDeviceMapping
from fabric.api import env, task, run, settings, sudo, local
from node import Node
from parse_client import ParseClient
import jobs
import time
import json
import pprint
import sys

@task
def launch(name, ami='ami-3d4ff254', instance_type='t1.micro', key_name='amazon2', 
           zone='us-east-1d', security_group='quicklaunch-1', user='ubuntu', job=None):
    '''Launch a single instance of the provided ami '''
    conn = EC2Connection()
    # Declare the block device mapping for ephemeral disks
    mapping = BlockDeviceMapping()
    eph0 = BlockDeviceType()
    eph1 = BlockDeviceType()
    eph0.ephemeral_name = 'ephemeral0'
    eph1.ephemeral_name = 'ephemeral1'
    mapping['/dev/sdb'] = eph0
    mapping['/dev/sdc'] = eph1
    # Now, ask for a reservation
    reservation = conn.run_instances(ami, instance_type=instance_type, 
                                     key_name=key_name, placement=zone, 
                                     block_device_map=mapping, security_groups=[security_group])
    # And assume that the instance we're talking about is the first in the list
    # This is not always a good assumption, and will likely depend on the specifics
    # of your launching situation. For launching an isolated instance while no
    # other actions are taking place, this is sufficient.
    instance = reservation.instances[0]
    print('Waiting for instance to start...')
    # Check up on its status every so often
    status = instance.update()
    while status == 'pending':
        time.sleep(5)
        status = instance.update()
    if status == 'running':
        print('New instance "' + instance.id + '" accessible at ' + instance.public_dns_name)
        # Name the instance
        conn.create_tags([instance.id], {'Name': name})

        n = Node(name, instance.id, instance.image_id, instance.key_name, instance.placement,
                instance.instance_type, instance.dns_name, instance.private_dns_name,
                instance.ip_address, instance.private_ip_address, user, job)

        if ParseClient.add_node(n.to_dict()):
            print "Node stored on remote"
            pprint.pprint(n.to_dict())
        else:
            print "Node storage failed on remote"
    
        job_status = addJob(name, job)
        while job_status == 'pending': 
            time.sleep(5)
            job_status = addJob(name, job)
            if job_status == 'complete':
                print 'Job init complete'
    else:
        print('Instance status: ' + status)
        return

@task
def mockLaunch(name, ami='ami-3d4ff254', instance_type='t1.micro', key_name='amazon2', 
           zone='us-east-1d', security_group='quicklaunch-1', user='ubuntu', job=None):
    """ Simulate a node launch for dev purposes """

    i = {
         'name': name,
         'key_name': key_name,
         'public_dns_name': u'ec2-107-21-159-143.compute-1.amazonaws.com',
         'ip_address': u'107.21.159.143',
         'private_dns_name': u'ip-10-29-6-45.ec2.internal',
         'id': u'i-e2a5559d',
         'image_id': ami,
         'zone': zone,
         'dns_name': u'ec2-107-21-159-143.compute-1.amazonaws.com',
         'instance_type': instance_type,
         'private_ip_address': u'10.29.6.45',
         'user':user,
         'job':job
        }

    n = Node(**i)
    try:
        if ParseClient.add_node(n.to_dict()):
            print "Node stored on remote"
            pprint.pprint(n.to_dict())
        else:
            print "Node storage failed on remote"
    except Exception as e:
        print "Error: %s" % e

@task
def list():
    """ List configured nodes """
    ParseClient.all_nodes()
    for node in ParseClient.all_nodes():
        print node.name, node.ip_address, node.jobs    


@task
def addJob(name, job):
    """ Give node a job """
    node = ParseClient.get_node(name)
    if job not in node.jobs:
        node.jobs.append(job)

    if ParseClient.update_node(name, node.to_dict()):
        print "Node updated on remote"

    try:
        for job in node.jobs:
            # Need to run ssh-add ~/.ssh/somekey.pem for the below to work
            # TODO - need to store login with node
            with settings(host_string='%s@%s' % (node['user'], node['ip_address'])):
                    # TODO - git list of jobs from jobs dir
                if job == 'web':
                    j = jobs.web()
                    j.run(config)
    except Exception as e:
        return 'pending'
    return 'complete'

@task
def ssh(name):
    """ Connect to a given node """
    node = ParseClient.get_node(name)
    local("ssh %s@%s" % (node.user, node.ip_address))
