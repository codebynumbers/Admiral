from fabric.api import env, task, run, sudo

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

    templates = [
        # TODO - template out boto config etc
        # fill template, put on file system, set owner and permissions
    ]

    @staticmethod
    def run(self):
        sudo('apt-get update')
        sudo('apt-get upgrade')

        for package in Web.packages:
            sudo('apt-get install %s' % package)

        for package in Web.pip_packages:
            sudo('pip install %s' % package)
