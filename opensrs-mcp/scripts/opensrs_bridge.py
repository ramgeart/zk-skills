import sys
import json
import urllib.request
import urllib.parse
import argparse
import xml.etree.ElementTree as ET
import hashlib

class OpenSRSClient:
    def __init__(self, username, api_key, environment='test'):
        self.username = username
        self.api_key = api_key
        # For production: https://rr-n1-tor.opensrs.net:55443/
        self.url = 'https://rr-n1-tor.opensrs.net:55443/' if environment == 'production' else 'https://horizon.opensrs.net:55443/'

    def _generate_signature(self, payload):
        # OpenSRS Signature: MD5(MD5(payload + api_key) + api_key)
        # Signature is calculated on the byte payload + api_key string
        sig1 = hashlib.md5(payload + self.api_key.encode('utf-8')).hexdigest()
        sig2 = hashlib.md5((sig1 + self.api_key).encode('utf-8')).hexdigest()
        return sig2

    def _build_xml(self, object_type, action, attributes):
        # OpenSRS is extremely picky about the order: Protocol -> Action -> Object -> Attributes
        # and specifically requires this exact XML declaration and DOCTYPE.
        
        def dict_to_xml_items(d):
            items_xml = ""
            for k, v in d.items():
                items_xml += f'          <item key="{k}">{v}</item>\n'
            return items_xml

        attr_xml = dict_to_xml_items(attributes)
        
        envelope = f"""<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<!DOCTYPE OPS_envelope SYSTEM "ops.dtd">
<OPS_envelope>
  <header>
    <version>0.9</version>
  </header>
  <body>
    <data_block>
      <dt_assoc>
        <item key="protocol">XCP</item>
        <item key="action">{action}</item>
        <item key="object">{object_type}</item>
        <item key="attributes">
          <dt_assoc>
{attr_xml}          </dt_assoc>
        </item>
      </dt_assoc>
    </data_block>
  </body>
</OPS_envelope>"""
        return envelope.strip().encode('utf-8')

    def call(self, object_type, action, attributes):
        xml_payload = self._build_xml(object_type, action, attributes)
        signature = self._generate_signature(xml_payload)
        
        headers = {
            'Content-Type': 'text/xml',
            'X-Username': self.username,
            'X-Signature': signature
        }
        
        req = urllib.request.Request(self.url, data=xml_payload, headers=headers, method='POST')
        try:
            with urllib.request.urlopen(req) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            return f"Error: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description='OpenSRS MCP Bridge')
    parser.add_argument('--username', required=True)
    parser.add_argument('--key', required=True)
    parser.add_argument('--env', default='test')
    parser.add_argument('--object', required=True)
    parser.add_argument('--action', required=True)
    parser.add_argument('--attrs', type=json.loads, default={})
    
    args = parser.parse_args()
    
    client = OpenSRSClient(args.username, args.key, args.env)
    result = client.call(args.object, args.action, args.attrs)
    print(result)

if __name__ == '__main__':
    main()
