"""
Executor executes a script, parses consoles and posts logs
"""

from datetime import datetime
import json
import shutil
import subprocess
import tempfile
import threading
import time
import traceback
import uuid
import os
from shippable_adapter import ShippableAdapter

class Executor2(object):
    """
    Sets up attributes that will be used to execute the build
    """
    def __init__(self, config):
        # -------
        # Private
        # -------

        # Configs obtained from the job.env file
        self._config = config
        self._shippable_adapter = ShippableAdapter(config)

        # Threads
        self._logger_thread = None
        self._script_runner_thread = None

        # Error buffer state
        self._has_errors = False

        # Log directory and file
        self._temporary_log_directory = tempfile.mkdtemp()
        self._log_file_path = \
            os.path.join(self._temporary_log_directory, 'logs')
        buffer_size = 0
        self._write_log_file = open(self._log_file_path, 'w', buffer_size)
        self._read_log_file = open(self._log_file_path, 'r')

        # Console state
        self._current_group_info = None
        self._current_group_name = None
        self._current_cmd_info = None
        self._show_group = None

        # Execution error consoles
        self._error_grp = {
            'consoleId': str(uuid.uuid4()),
            'parentConsoleId': 'root',
            'type': 'grp',
            'message': 'Error',
            'timestamp': Executor2._get_timestamp(),
            'isSuccess': False
        }
        self._error_buffer = [self._error_grp]

        # ------
        # Public
        # ------

        # Assume failure by default
        self.exit_code = 1

    def __del__(self):
        shutil.rmtree(self._temporary_log_directory, ignore_errors=True)

    def execute(self):
        """
        Starts the script runner and logger threads and waits for
        them to finish.
        """

        # Instantiate script runner and logger threads
        self._script_runner_thread = \
            threading.Thread(target=self._script_runner)
        self._logger_thread = threading.Thread(target=self.logger)

        # Start both the threads.
        self._script_runner_thread.start()
        self._logger_thread.start()

        # Wait until the threads are completed
        self._script_runner_thread.join()
        self._logger_thread.join()

        if self._has_errors:
            self._flush_error_buffer()

    def _script_runner(self):
        """
        Runs the script, handles console output and finally sets the exit code
        """
        # We need to unset the LD_LIBRARY_PATH set by pyinstaller. This
        # will ensure the script prefers libraries on system rather
        # than the ones bundled during build time.
        env = dict(os.environ)
        env.pop('LD_LIBRARY_PATH', None)
        cmd = self._config['SCRIPT_PATH']
        if self._config.get('REQEXEC_SHELL'):
            cmd = [self._config['REQEXEC_SHELL'], self._config['SCRIPT_PATH']]

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=self._config['BUILD_DIR'],
                env=env
            )
        except Exception as ex:
            trace = traceback.format_exc()
            error = '{0}: {1}'.format(str(ex), trace)
            self._append_to_error_buffer(error)
            return

        try:
            for line in iter(proc.stdout.readline, ''):
                is_script_success, is_complete = self._handle_console_line(line)

                if is_script_success:
                    self.exit_code = 0

                if is_complete:
                    break
        except Exception as ex:
            trace = traceback.format_exc()
            error = '{0}: {1}'.format(str(ex), trace)
            self._append_to_error_buffer(error)

        proc.kill()

    def logger(self):
        """
        Reads from the log file and flushes consoles periodically or
        if a limit is hit
        """
        logs_to_post = {
            'buildJobId': self._config['BUILD_JOB_ID'],
            'buildJobConsoles': []
        }

        # Add a hidden version notice.
        # NOTE: Remove this once we switch to this executor completely.
        notice_console_id = str(uuid.uuid4())
        notice_message = 'Notice: Executor v2'
        logs_to_post['buildJobConsoles'].append({
            'consoleId': notice_console_id,
            'parentConsoleId': 'root',
            'type': 'grp',
            'message': notice_message,
            'timestamp': Executor2._get_timestamp(),
            'isShown': False
        })

        logs_to_post['buildJobConsoles'].append({
            'consoleId': notice_console_id,
            'parentConsoleId': 'root',
            'type': 'grp',
            'message': notice_message,
            'timestamp': Executor2._get_timestamp(),
            'timestampEndedAt': Executor2._get_timestamp(),
            'isSuccess': True,
            'isShown': False
        })

        logs_last_posted_at = datetime.now()

        while True:
            post_logs = False
            and_break = False

            log_line = self._read_log_file.readline()

            if log_line:
                try:
                    parsed_log_line = json.loads(log_line)
                    logs_to_post['buildJobConsoles'].append(parsed_log_line)
                except Exception as ex:
                    trace = traceback.format_exc()
                    error = '{0}: {1}'.format(str(ex), trace)
                    self._append_to_error_buffer(error)

                # We added a new line, if the new array length exceeds max
                # log lines, post logs.
                if len(logs_to_post['buildJobConsoles']) \
                    >= self._config['MAX_LOG_LINES_TO_FLUSH']:
                    post_logs = True
            else:
                # If the script runner is dead and there are no more logs to
                # read, attempt to post any remaining logs and break.
                if not self._script_runner_thread.isAlive():
                    post_logs = True
                    and_break = True
                # If its been a while since we posted logs, post.
                elif (datetime.now() - logs_last_posted_at).total_seconds() \
                    > self._config['MAX_LOGS_FLUSH_WAIT_TIME_IN_S'] \
                    and logs_to_post['buildJobConsoles']:
                    post_logs = True
                # Sleep a bit if there hasn't been any activity.
                else:
                    time.sleep(self._config['LOGS_FILE_READ_WAIT_TIME_IN_S'])

            # Post logs if asked and there is something to post.
            if post_logs and logs_to_post['buildJobConsoles']:
                logs_last_posted_at = datetime.now()
                data = json.dumps(logs_to_post)
                self._shippable_adapter.post_build_job_consoles(data)
                logs_to_post['buildJobConsoles'] = []

            if and_break:
                break

    def _handle_console_line(self, line):
        """
        Parses a single line of console output and pushes it to a file
        This also returns whether the console line is successful and the
        script is complete
        """
        is_script_success = False
        is_complete = False
        timestamp = Executor2._get_timestamp()
        line_split = line.split('|')
        if line.startswith('__SH__GROUP__START__'):
            self._current_group_info = line_split[1]
            self._current_group_name = '|'.join(line_split[2:])
            self._current_group_info = json.loads(self._current_group_info)
            self._show_group = self._current_group_info.get('is_shown', True)
            if self._show_group == 'false':
                self._show_group = False
            console_out = {
                'consoleId': self._current_group_info.get('id'),
                'parentConsoleId': 'root',
                'type': 'grp',
                'message': self._current_group_name,
                'timestamp': timestamp,
                'isShown': self._show_group
            }
            self._append_to_log_file(console_out)
        elif line.startswith('__SH__CMD__START__'):
            self._current_cmd_info = line_split[1]
            current_cmd_name = '|'.join(line_split[2:])
            self._current_cmd_info = json.loads(self._current_cmd_info)
            parent_id = self._current_group_info.get('id') if \
                self._current_group_info else None
            console_out = {
                'consoleId': self._current_cmd_info.get('id'),
                'parentConsoleId': parent_id,
                'type': 'cmd',
                'message': current_cmd_name,
                'timestamp': timestamp,
            }
            if parent_id:
                self._append_to_log_file(console_out)
        elif line.startswith('__SH__CMD__END__'):
            current_cmd_end_info = line_split[1]
            current_cmd_end_name = '|'.join(line_split[2:])
            current_cmd_end_info = json.loads(current_cmd_end_info)
            parent_id = self._current_group_info.get('id') if \
                self._current_group_info else None
            is_cmd_success = False
            if current_cmd_end_info.get('exitcode') == '0':
                is_cmd_success = True
            console_out = {
                'consoleId': self._current_cmd_info.get('id'),
                'parentConsoleId': parent_id,
                'type': 'cmd',
                'message': current_cmd_end_name,
                'timestamp': timestamp,
                'timestampEndedAt': timestamp,
                'isSuccess': is_cmd_success,
                'isShown': self._show_group
            }
            if parent_id:
                self._append_to_log_file(console_out)
        elif line.startswith('__SH__GROUP__END__'):
            current_grp_end_info = line_split[1]
            current_grp_end_name = '|'.join(line_split[2:])
            current_grp_end_info = json.loads(current_grp_end_info)
            is_cmd_success = False
            if current_grp_end_info.get('exitcode') == '0':
                is_cmd_success = True
            console_out = {
                'consoleId': self._current_group_info.get('id'),
                'parentConsoleId': 'root',
                'type': 'grp',
                'message': current_grp_end_name,
                'timestamp': timestamp,
                'timestampEndedAt': timestamp,
                'isSuccess': is_cmd_success,
                'isShown': self._show_group
            }
            self._append_to_log_file(console_out)
        elif line.startswith('__SH__SCRIPT_END_SUCCESS__'):
            is_script_success = True
            is_complete = True
        elif line.startswith('__SH__SCRIPT_END_FAILURE__'):
            is_script_success = False
            is_complete = True
        else:
            parent_id = self._current_cmd_info.get('id') if \
                self._current_cmd_info else None
            console_out = {
                'consoleId': str(uuid.uuid4()),
                'parentConsoleId': parent_id,
                'type': 'msg',
                'message': line,
                'timestamp': timestamp,
            }
            if parent_id:
                self._append_to_log_file(console_out)
            else:
                self._append_to_error_buffer(line)

        return is_script_success, is_complete

    def _append_to_log_file(self, console_out):
        """
        Pushes a console line to the log file
        """
        try:
            self._write_log_file.write(json.dumps(console_out) + '\n')
        except Exception as ex:
            trace = traceback.format_exc()
            error = '{0}: {1}'.format(str(ex), trace)
            self._append_to_error_buffer(error)

    def _append_to_error_buffer(self, error):
        """
        Appends an error into errors buffer after ensuring it is not empty
        """
        if not error.strip():
            return

        self._has_errors = True
        error_msg = {
            'consoleId': str(uuid.uuid4()),
            'parentConsoleId': self._error_grp['consoleId'],
            'type': 'msg',
            'message': error,
            'timestamp': Executor2._get_timestamp(),
            'isSuccess': False
        }
        self._error_buffer.append(error_msg)

    def _flush_error_buffer(self):
        """
        Flushes error buffer
        """
        req_body = {
            'buildJobId': self._config['BUILD_JOB_ID'],
            'buildJobConsoles': self._error_buffer
        }
        data = json.dumps(req_body)
        self._shippable_adapter.post_build_job_consoles(data)
        del self._error_buffer
        self._error_buffer = []

    @staticmethod
    def _get_timestamp():
        """
        Helper method to return timestamp in a format which is acceptable
        for consoles
        """
        return int(time.time() * 1000000)
