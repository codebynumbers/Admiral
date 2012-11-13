
class WebJob():

    packages = [
        'nginx',
        'ntp',
        's3cmd'
    ]

    pip_packages = [
        'redis',
        'boto'
    ]

    templates = [
        
    ]

    def run(self):
        sudo('apt-get update')
        sudo('apt-get upgrade')

        for package in self.packages:
            sudo('apt-get install %s' % package)

        for package in self.pip_packages:
            sudo('pip install %s' % package)
