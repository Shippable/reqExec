"""
Config required to execute a script
"""

import logging

class Config(dict):
    """
    Initialize default and job specific config
    """
    def __init__(self, script_path, job_envs_path):
        dict.__init__(self)
        self['SCRIPT_PATH'] = script_path

        with open(job_envs_path) as job_envs:
            for env in job_envs:
                key, value = env.split('=', 1)
                value = value.strip()
                if value[0] == '"' and value[-1] == '"':
                    value = value[1:-1]
                if value[0] == "'" and value[-1] == "'":
                    value = value[1:-1]
                self[key] = value

        expected_envs = [
            'SCRIPT_PATH',
            'SHIPPABLE_API_URL',
            'BUILDER_API_TOKEN',
            'BUILD_JOB_ID',
            'RUN_MODE',
            'BUILD_DIR'
        ]

        for env in expected_envs:
            if env not in self.keys():
                raise Exception('Config key {0} missing'.format(env))

        self['CONSOLE_BUFFER_LENGTH'] = 20
        self['CONSOLE_FLUSH_INTERVAL_SECONDS'] = 3
        self['SHIPPABLE_API_RETRY_INTERVAL'] = 3
        self['LOG_LEVEL'] = logging.WARNING
        if self['RUN_MODE'] == 'beta':
            self['LOG_LEVEL'] = logging.INFO
        elif self['RUN_MODE'] == 'dev':
            self['LOG_LEVEL'] = logging.DEBUG

        # New build runner switch/params
        self['IS_NEW_BUILD_RUNNER_SUBSCRIPTION'] = \
            self.get('IS_NEW_BUILD_RUNNER_SUBSCRIPTION') == 'true'
        self['MAX_LOG_LINES_TO_FLUSH'] = \
            int(self.get('MAX_LOG_LINES_TO_FLUSH', 20))
        self['MAX_LOGS_FLUSH_WAIT_TIME_IN_S'] = \
            float(self.get('MAX_LOGS_FLUSH_WAIT_TIME_IN_S', 3))
        self['LOGS_FILE_READ_WAIT_TIME_IN_S'] = \
            float(self.get('LOGS_FILE_READ_WAIT_TIME_IN_S', 0.1))
