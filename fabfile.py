from boto.ec2.connection import EC2Connection
from boto.ec2.blockdevicemapping import BlockDeviceType
from boto.ec2.blockdevicemapping import BlockDeviceMapping
from fabric.api import env, task, run, settings, sudo, local
from node import Node
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
    
        pprint.pprint(n.to_dict())
        addNode(n)    

    else:
        print('Instance status: ' + status)
        return

@task
def mockLaunch(name, ami='ami-3d4ff254', instance_type='t1.micro', key_name='amazon2', zone='us-east-1d', security_group='quicklaunch-1', job=None):
    """ Simulate a node launch for dev purposes """

    i = {
         'name': name,
         'key_name': key_name,
         'public_dns_name': u'ec2-107-21-159-143.compute-1.amazonaws.com',
         'ip_address': u'107.21.159.143',
         'private_dns_name': u'ip-10-29-6-45.ec2.internal',
         'id': u'i-e2a5559d',
         'image_id': ami,
         'placement': zone,
         'dns_name': u'ec2-107-21-159-143.compute-1.amazonaws.com',
         'instance_type': instance_type,
         'private_ip_address': u'10.29.6.45',
         'user':user,
         'jobs':job
        }

    n = Node(i['name'], i['id'], i['image_id'], i['key_name'], i['placement'],
            i['instance_type'], i['dns_name'], i['private_dns_name'],
            i['ip_address'], i['private_ip_address'], i['user'], job)

    pprint.pprint(n.to_dict())
    addNode(n)


@task
def listNodes():
    """ List configured nodes """
    config = {}
    try:
        fh = open('config.json','r')
        config = json.loads(fh.read())
        fh.close()
    except:
        config['nodes'] = []

    for node in config['nodes']:
        print node['name'], node['ip_address'], node['jobs']    


@task
def addJob(name, job):
    """ Give node a job """
    node = findNode(name)
    if job not in node['jobs']:
        node['jobs'].append(job)
    updateConfig(name, node)
    config = loadConfig()

    for job in node['jobs']:
        # Need to run ssh-add ~/.ssh/somekey.pem for the below to work
        # TODO - need to store login with node
        with settings(host_string='%s@%s' % (node['user'], node['ip_address'])):
            # There has to be a nicer way to do this
            if job == 'web':
                jobs.web.run(config)

@task
def ssh(name):
    """ Connect to a given node """
    node = findNode(name)
    local("ssh %s@%s" % (node['user'], node['ip_address']))

#
# Utility methods - move these to own modules later
#

# Abstract config into class that auto-saves

def addNode(node):
    config = loadConfig()
    config['nodes'].append(node.to_dict())
    saveConfig(config)    

def findNode(name):
    config = loadConfig()
    for node in config['nodes']:
        if node['name'] == name:
            return node
    print "Node with name %s not found" % name
    sys.exit()


def loadConfig():
    config = {}
    try:
        fh = open('config.json','r')
        config = json.loads(fh.read())
        fh.close()
    except:
        config['nodes'] = []
    return config


def saveConfig(config):
    fh = open('config.json','w')
    blob = json.dumps(config, sort_keys=True, indent=4)
    fh.write(blob)
    fh.close()


# this is dumb, I already want a better data structure, keyed by name or id
def updateConfig(name, node):
    config = loadConfig()
    nodes = []
    for n in config['nodes']:
        if n['name'] == name:
            nodes.append(node)
        else:
            nodes.append(n)
    config['nodes'] = nodes
    saveConfig(config)

