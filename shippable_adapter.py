import requests
import json

class ShippableAdapter():
    def __init__(self, api_url, api_token):
        requests.packages.urllib3.disable_warnings()
        self.api_url = api_url
        self.api_token = api_token

    def post(self, url, body):
        headers = {
            'Authorization': 'apiToken {0}'.format(self.api_token),
            'Content-Type': 'application/json'
        }
        data = json.dumps(body)

        response = requests.post(url, data=data, headers=headers)
        print 'POST {0} completed with {1}'.format(
            url, response.status_code)

    def post_build_job_consoles(self, build_job_id, data):
        url = '{0}/buildJobConsoles'.format(self.api_url, build_job_id)
        self.post(url, data)
