from xml import sax
import json
import requests

class NvdHandler(sax.ContentHandler):
    def __init__(self):
        self.entries = []

    def startElement(self, name, attrs):
        if name == 'nvd':
            return

        elem = {}
        if name != 'entry':
            parent = self.entries[-1]

            if name not in parent:
                parent[name] = elem
            else:
                if not isinstance(parent[name], list):
                    prev_elem = parent[name]
                    parent[name] = [prev_elem]
                parent[name].append(elem)
        attrs = dict(attrs.items())
        if attrs:
            elem['_attrs'] = attrs
        elem['_name'] = name

        self.entries.append(elem)

    def endElement(self, name):
        if name == 'nvd':
            return

        elem = self.entries.pop()
        if name == 'entry':
            headers = {'Content-type': 'application/json'}
            _id = elem['_attrs']['id']
            requests.post('http://localhost:5000/document/' + _id + '/',
                          data=json.dumps(elem), headers=headers)

    def characters(self, content):
        content = content.strip()
        if content:
            elem = self.entries[-1]
            if '_text' in elem:
                elem['_text'] += content
            else:
                elem['_text'] = content


requests.delete('http://localhost:5000/documents/')

filename = 'nvdcve-2.0-2014.xml'
# filename = 'small.xml'

sax.parse(filename, NvdHandler())

requests.get('http://localhost:5000/compact/')
