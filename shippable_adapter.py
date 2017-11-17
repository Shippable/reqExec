"""
Shippable API adapter
"""

import logging
import time
import traceback
import requests

class ShippableAdapter(object):
    """
    Initialize the API URL and token
    """
    def __init__(self, config):
        logging.getLogger("requests").setLevel(logging.WARNING)
        requests.packages.urllib3.disable_warnings()

        self._api_url = config['SHIPPABLE_API_URL']
        self._api_token = config['BUILDER_API_TOKEN']
        self._retry_interval = config['SHIPPABLE_API_RETRY_INTERVAL']

        logging.basicConfig(level=config['LOG_LEVEL'])
        self._logger = logging.getLogger(__name__)

    def _post(self, url, data):
        """
        Generic POST request handler
        """
        headers = {
            'Authorization': 'apiToken {0}'.format(self._api_token),
            'Content-Type': 'application/json'
        }
        try:
            response = requests.post(url, data=data, headers=headers)
            if response.status_code >= 500:
                ex = 'API server error: {0} {1}'.format(
                    response.status_code, response.text)
                raise Exception(ex)
            elif response.status_code != 200:
                error = 'API {0} responded with: {1} {2}'.format(
                    url, response.status_code, response.text)
                self._logger.error(error)

        except Exception as ex:
            trace = traceback.format_exc()
            error = '{0}: {1}'.format(str(ex), trace)
            self._logger.error('Exception POSTing to %s: %s', url, error)
            time.sleep(self._retry_interval)
            self._post(url, data)

    def post_build_job_consoles(self, data):
        """
        Posts stringified json of build job consoles
        """
        url = '{0}/buildJobConsoles'.format(self._api_url)
        self._post(url, data)
