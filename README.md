Admiral
=======

A python based AWS deployment suite, or a watered down clone of chef

This is very much a prooof-of-concept, it is nowhere near production ready.

The idea behind it is to offer the basic functionality of OpsCode Chef, 
launch servers, install packages and deploy config files except with
Python instead of Ruby, Jinja for templating, fabric for deployment 
server interaction and a git repo for recipe storage and cluster configuration.

Getting Started Example
=======================

Add your key, if not id_rsa

 ssh-add ~/.ssh/amazon2.pem 

Launch an EC2 instance with defaults and then apply the web job to it.

 fab launch:name='web01',job='web'

The web job is just a python class that can can be eaily customized to install packages, templated configs, run commands etc.

List nodes

 fab list

Connect to the named node
 
 fab ssh:web01
