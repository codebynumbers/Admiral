Admiral
=======

A python based AWS deployment suite, or a watered down clone of chef

This is very much a prooof-of-concept, it is nowhere near production ready.

The idea behind it is to offer the basic functionality of OpsCode Chef, 
launch a fleet of servers, install packages and deploy config files
except using Python instead of Ruby, Jinja for templating, 
fabric for server interaction, a git repo for recipe storage 
and Parse or similar service for storing fleet configuration.

Terminolgy
-----
- Node - an AWS EC2 Ubuntu instance
- Job - Like a chef role, but didn't want to confuse with fabric roles, nodes can have multiple jobs, Job class files define how to setup a node for a particular job

Getting Started Example
-----------------------

#### Add your key, if not id_rsa
```bash
ssh-add ~/.ssh/amazon2.pem 
```

#### Launch an EC2 instance with defaults and then apply the web job to it.
```python
 fab launch:name='web01',job='web'
```

The web job is just a python class that can be customized to install packages, templated configs, run commands etc.

#### List nodes
```python
 fab list
```

#### Connect to the named node
```python
 fab ssh:web01
```

#### Show the named node
```python
 fab show:web01
```

#### Terminate the named node
```python
 fab terminate:web01
```

### To Do
- Provide option to not use EBS
- Dynamically choose right class for job, ie not hardcoded
- Add a couple more sample jobs
- Fix circular import
