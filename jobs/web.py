from fabric.api import run, sudo, put
from jinja2 import Template, Environment, FileSystemLoader
from tempfile import NamedTemporaryFile
import os

class web():

    packages = [
        'python-pip',
        'nginx',
        'ntp',
        's3cmd'
    ]

    pip_packages = [
        'redis',
        'boto'
    ]

    # TODO - template out things like boto config etc
    # fill template, put on file system, set owner and permissions
    files = [
        {
            "name":"somedomain.com",
            "dest":"/etc/nginx/sites-available/somedomain.com",
            "owner":"root",
            "group":"root",
            "perms":"644"
        }
    ]

    # Create these links
    links = [
    ]

    # Add these users
    users = [
    ]

    # Add these dirs
    dirs = [
    ]    
    
    # Run these commands
    cmds = [
    ]

    @staticmethod
    def run(config=None):
        
        # Will need to pass node data for templates etc

        sudo('apt-get update')
        sudo('apt-get upgrade')

        for package in web.packages:
            sudo('apt-get install -y %s' % package)

        for package in web.pip_packages:
            sudo('pip install %s' % package)

        cwd = os.path.dirname( __file__ )
        env = Environment(loader = FileSystemLoader('%s/../templates/web' % cwd))
        for file in web.files:
            template = env.get_template(file['name'])
            rendered = template.render(config)
            f = NamedTemporaryFile(delete=False)
            f.write(rendered)
            f.close()
            put(f.name, file['dest'], use_sudo=True)
            os.unlink(f.name)
            sudo("chown %s.%s %s" % (file['owner'], file['group'], file['dest']))
            sudo("chmod %s %s" % (file['perms'], file['dest']))
        
