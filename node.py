import time
import jobs
import pprint

from boto.ec2.connection import EC2Connection
from boto.ec2.blockdevicemapping import BlockDeviceType
from boto.ec2.blockdevicemapping import BlockDeviceMapping
from fabric.api import env, task, run, settings, sudo, local

from parse_client import ParseClient
from job import Job

class Node(object):
    """ Object representing an EC2 node """

    # list of job names
    jobs = []

    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.key_name = kwargs.get('key_name')
        self.zone = kwargs.get('zone')
        self.instance_type = kwargs.get('instance_type')
        self.user = kwargs.get('user')
        self.ami = kwargs.get('ami')
        self.security_group = kwargs.get('security_group')

        # optional
        self.instance_id = kwargs.get('instance_id')
        self.public_dns_name = kwargs.get('public_dns_name')
        self.private_dns_name = kwargs.get('private_dns_name')
        self.ip_address = kwargs.get('ip_address')
        self.private_ip_address = kwargs.get('private_ip_address')

        if kwargs.get('job'):
            self.jobs.append(kwargs['job'])
        elif kwargs.get('jobs'):
            self.jobs = kwargs['jobs']

        # Parse reference
        self.object_id = kwargs.get('objectId')

        # Experimenting
        self.ebs = False

    def to_dict(self):
        return {
            'name': self.name,
            'instance_id': self.instance_id,
            'ami': self.ami,
            'key_name': self.key_name,
            'zone': self.zone,
            'instance_type': self.instance_type,
            'public_dns_name': self.public_dns_name,
            'private_dns_name': self.private_dns_name,
            'ip_address': self.ip_address,
            'private_ip_address': self.private_ip_address,
            'user': self.user,
            'jobs': self.jobs
        }            

    def launch(self):
        '''Launch a single instance of the provided ami '''
        conn = EC2Connection()
        # Declare the block device mapping for ephemeral disks

        mapping = None
        if self.ebs:
            # TODO - toggle instance storage
            mapping = BlockDeviceMapping()
            eph0 = BlockDeviceType()
            eph1 = BlockDeviceType()
            eph0.ephemeral_name = 'ephemeral0'
            eph1.ephemeral_name = 'ephemeral1'
            mapping['/dev/sdb'] = eph0
            mapping['/dev/sdc'] = eph1
        
        # Now, ask for a reservation
        reservation = conn.run_instances(self.ami, instance_type=self.instance_type, 
                                         key_name=self.key_name, placement=self.zone, 
                                         block_device_map=mapping, security_groups=[self.security_group])
        # And assume that the instance we're talking about is the first in the list
        # This is not always a good assumption, and will likely depend on the specifics
        # of your launching situation. For launching an isolated instance while no
        # other actions are taking place, this is sufficient.
        instance = reservation.instances[0]
        print('Waiting for instance to start...')
        # Check up on its status every so often
        try:
            status = instance.update()
        except:
            pass
        while status == 'pending':
            time.sleep(5)
            try:
                status = instance.update()
            except:
                pass
        if status == 'running':
            print('New instance "' + instance.id + '" accessible at ' + instance.public_dns_name)
            # Name the instance
            conn.create_tags([instance.id], {'Name': self.name})

            # update properties
            self.instance_id = instance.id
            self.private_dns_name = instance.private_dns_name
            self.public_dns_name = instance.public_dns_name
            self.ip_address = instance.ip_address
            self.private_ip_address = instance.private_ip_address

            ParseClient.add_node(self.to_dict())

            if self.try_connect():
                self.refresh_jobs()

            return True
        else:
            print('Instance status: ' + status)
            return False

    def try_connect(self):
        tries = 0
        while True:
            try:
                tries += 1
                with settings(host_string='%s@%s' % (self.user, self.ip_address)):
                    sudo("hostname")
                return True
            except:
                time.sleep(5)
                if tries >= 10:
                    print "Unable to connect after %d tries" % tries
                    return False

    def refresh_jobs(self):
        """ Run all jobs """
        with settings(host_string='%s@%s' % (self.user, self.ip_address)):
            # Run init from Base job class, once per run
            job_obj = Job()
            job_obj.update_packages() 
            # Run all nodes jobs
            for job in self.jobs:
                self.run_single_job(job)

    def run_single_job(self, job):
        template_vars = {
            'nodes': ParseClient.all_nodes()
        }
        with settings(host_string='%s@%s' % (self.user, self.ip_address)):
            job_obj = self.get_job_module(job)
            job_obj.run(template_vars) 

    def terminate(self):
        ''' Terminate this instance '''
        conn = EC2Connection()
        try:
            conn.terminate_instances([self.instance_id])
        except:
            pass
        ParseClient.delete_node(self.name)


    def mock_launch(self):
        """ For testing """
        mock = {
             'name': self.name,
             'key_name': self.key_name,
             'ami': self.ami,
             'zone': self.zone,
             'instance_type': self.instance_type,
             'user':self.user,
             'job':self.jobs,
             'public_dns_name': u'ec2-107-21-159-143.compute-1.amazonaws.com',
             'ip_address': u'107.21.159.143',
             'private_dns_name': u'ip-10-29-6-45.ec2.internal',
             'id': u'i-e2a5559d',
             'dns_name': u'ec2-107-21-159-143.compute-1.amazonaws.com',
             'private_ip_address': u'10.29.6.45'
        }

        if ParseClient.add_node(mock):
            print "Node stored on remote"
        else:
            print "Node storage failed on remote"

    def get_job_module(self, job):
        obj = self.get_class("jobs.%s" % job)
        return obj()

    @staticmethod
    def get_class(kls):
        """ Source: http://stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname """
        parts = kls.split('.')
        module = ".".join(parts[:-1])
        m = __import__( module )
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m
 
