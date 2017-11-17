"""
Shippable API adapter
"""
import json
import requests

class ShippableAdapter(object):
    """
    Initialize the API URL and token
    """
    def __init__(self, api_url, api_token):
        self._api_url = api_url
        self._api_token = api_token

    def _post(self, url, body):
        """
        Generic POST request handler
        """
        headers = {
            'Authorization': 'apiToken {0}'.format(self._api_token),
            'Content-Type': 'application/json'
        }
        data = json.dumps(body)

        response = requests.post(url, data=data, headers=headers)
        print 'POST {0} completed with {1}'.format(url, response.status_code)

    def post_build_job_consoles(self, data):
        """
        Posts an array of build job consoles
        """
        url = '{0}/buildJobConsoles'.format(self._api_url)
        self._post(url, data)
