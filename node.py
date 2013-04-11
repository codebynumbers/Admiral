class Node(object):
    """ Object representing an EC2 node """

    # list of job names
    jobs = []

    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.id = kwargs['id']
        self.image_id = kwargs['image_id']
        self.key_name = kwargs['key_name']
        self.zone = kwargs['zone']
        self.instance_type = kwargs['instance_type']
        self.dns_name = kwargs['dns_name']
        self.private_dns_name = kwargs['private_dns_name']
        self.ip_address = kwargs['ip_address']
        self.private_ip_address = kwargs['private_ip_address']
        self.user = kwargs['user']
        if kwargs.get('job'):
            self.add_job(kwargs['job'])

    def to_dict(self):
        return {
            'name': self.name,
            'id': self.id,
            'image_id': self.image_id,
            'key_name': self.key_name,
            'zone': self.zone,
            'instance_type': self.instance_type,
            'dns_name': self.dns_name,
            'private_dns_name': self.private_dns_name,
            'ip_address': self.ip_address,
            'private_ip_address': self.private_ip_address,
            'user': self.user,
            'jobs': self.jobs
        }            


    def add_job(self, job):
        if job not in self.jobs:
            self.jobs.append(job)
