import requests
import json
import urllib
from node import Node
from config import config

class ParseClient(object):

    headers = {
        'X-Parse-Application-Id': config['app_key'],
        'X-Parse-REST-API-Key': config['api_key'],
        'Content-Type': 'application/json'
    }

    @classmethod
    def add_node(cls, data):
        if cls.get_node(data['name']):
            raise Exception('A node with that name already exists')
        res = requests.post("https://api.parse.com/1/classes/Node", data=json.dumps(data), headers=cls.headers)
        return True if res.status_code == 201 else False

    @classmethod
    def get_node(cls, name):
        where = urllib.quote_plus('{"name":"%s"}' % name)
        res = requests.get("https://api.parse.com/1/classes/Node?where=%s" % where, headers=cls.headers)
        content = json.loads(res.content)
        if len(content['results']) == 0:
            return None
        return Node(**content['results'][0])

    @classmethod
    def all_nodes(cls):
        res = requests.get("https://api.parse.com/1/classes/Node", headers=cls.headers)
        content = json.loads(res.content)
        if len(content['results']) == 0:
            return []
        return [Node(**n) for n in content['results']]


    @classmethod
    def update_node(cls, name, data):
        node = cls.get_node(name)
        if node:
            res = requests.put("https://api.parse.com/1/classes/Node/%s" % node.object_id, data=json.dumps(data), headers=cls.headers)
            import pprint;pprint.pprint(res)
        return True if res.status_code == 201 else False

