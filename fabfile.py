from boto.ec2.connection import EC2Connection
from boto.ec2.blockdevicemapping import BlockDeviceType
from boto.ec2.blockdevicemapping import BlockDeviceMapping
from fabric.api import task
from node import Node
import time
import json
import pprint

@task
def launch(name, ami='ami-3d4ff254', instance_type='t1.micro', key_name='amazon2', zone='us-east-1d', security_group='quicklaunch-1', job=None):
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
        print json.dumps(instance.__dict__)
        
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
         '_placement': zone,
         'dns_name': u'ec2-107-21-159-143.compute-1.amazonaws.com',
         'instance_type': instance_type,
         'private_ip_address': u'10.29.6.45',
         'jobs':job
        }

    n = Node(i['name'], i['id'], i['image_id'], i['key_name'], i['_placement'],
            i['instance_type'], i['dns_name'], i['private_dns_name'],
            i['ip_address'], i['private_ip_address'], job)

    pprint.pprint(n.to_dict())
    _addNode(n)


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


#
# Utility methods - move these to own modules later
#
def _addNode(node):
    config = {}
    try:
        fh = open('config.json','r')
        config = json.loads(fh.read())
        fh.close()
    except:
        config['nodes'] = []

    config['nodes'].append(node.to_dict())

    fh = open('config.json','w')
    blob = json.dumps(config)
    fh.write(blob)
    fh.close()
