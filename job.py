from fabric.api import run, sudo, put
from jinja2 import Template, Environment, FileSystemLoader
from tempfile import NamedTemporaryFile
import os

class Job(object):

    # Instll these packages
    packages = []

    # Install these pip packages
    pip_packages = []

    # install templated files
    files = []

    # Create these links
    links = []

    # Add these users
    users = []

    # Add these dirs
    dirs = []    
    
    # Run these commands
    cmds = []

    def run(self, config=None):
        
        # Will need to pass node data for templates etc

        sudo('apt-get update')
        sudo('apt-get upgrade')

        for package in self.packages:
            sudo('apt-get install -y %s' % package)

        for package in self.pip_packages:
            sudo('pip install %s' % package)

        cwd = os.path.dirname( __file__ )
        env = Environment(loader = FileSystemLoader('%s/templates/%s' % (cwd, self.__class__.__name__ )))
        for file in self.files:
            template = env.get_template(file['name'])
            rendered = template.render(config)
            f = NamedTemporaryFile(delete=False)
            f.write(rendered)
            f.close()
            put(f.name, file['dest'], use_sudo=True)
            os.unlink(f.name)
            sudo("chown %s.%s %s" % (file['owner'], file['group'], file['dest']))
            sudo("chmod %s %s" % (file['perms'], file['dest']))
        

        # TODO links, users etc.
