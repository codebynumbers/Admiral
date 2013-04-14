import os

from fabric.api import sudo, put
from jinja2 import Environment, FileSystemLoader
from tempfile import NamedTemporaryFile


class Job(object):
    """ Base class for do things on an instance """

    # Install these packages
    packages = []
    # Install these pip packages
    pip_packages = []
    # Install templated files
    files = []
    # Create these links
    links = []
    # Add these users
    users = []
    # Add these dirs
    dirs = []    
    # Run these commands
    cmds = []

    def update_packages(self):
        """ Update packages once per run """
        sudo('echo "Running apt-get update on `hostname`"')
        sudo('apt-get update')
        sudo('apt-get upgrade -y')


    def run(self, template_vars=None):
        """ Kick off jobs """
        sudo('echo "Running jobs on `hostname`"')
        
        # Will need to pass node data for templates etc
        for package in self.packages:
            sudo('apt-get install -y %s' % package)

        for package in self.pip_packages:
            sudo('pip install %s' % package)

        cwd = os.path.dirname( __file__ )
        env = Environment(loader = FileSystemLoader('%s/templates/%s' % (cwd, self.__class__.__name__ )))
        for file in self.files:
            template = env.get_template(file['name'])
            rendered = template.render(template_vars)
            f = NamedTemporaryFile(delete=False)
            f.write(rendered)
            f.close()
            put(f.name, file['dest'], use_sudo=True)
            os.unlink(f.name)
            sudo("chown %s.%s %s" % (file['owner'], file['group'], file['dest']))
            sudo("chmod %s %s" % (file['perms'], file['dest']))
        

        # TODO links, users etc.
