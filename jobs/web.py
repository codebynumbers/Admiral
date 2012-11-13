from fabric.api import run, sudo

class Web():

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

    # TODO - template out boto config etc
    # fill template, put on file system, set owner and permissions
    files = [

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
    def run(self):
        sudo('apt-get update')
        sudo('apt-get upgrade')

        for package in Web.packages:
            sudo('apt-get install %s' % package)

        for package in Web.pip_packages:
            sudo('pip install %s' % package)
