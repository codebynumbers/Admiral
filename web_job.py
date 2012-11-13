from fabric.api import env, task, run, sudo

class WebJob():

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

    def run(self):
        print env.hosts
        sudo('apt-get update')
        sudo('apt-get upgrade')

        for package in self.packages:
            sudo('apt-get install %s' % package)

        for package in self.pip_packages:
            sudo('pip install %s' % package)
