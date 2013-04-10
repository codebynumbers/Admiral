from job import Job

class web(Job):

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

