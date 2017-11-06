from config import Config
from shippable_adapter import ShippableAdapter
import json
import subprocess
import threading
import time
import uuid

class Executor():
    def __init__(self, script, job_envs_path):
        self.script = script
        self.config = Config(job_envs_path)

        self.shippable_adapter = ShippableAdapter(
            self.config['SHIPPABLE_API_URL'],
            self.config['BUILDER_API_TOKEN']
        )

        # Consoles
        self.console_buffer = []
        self.console_buffer_lock = threading.Lock()
        # Console state
        self.current_group_info = None
        self.current_group_name = None
        self.current_cmd_info = None
        self.show_group = None

    def execute(self):
        proc = subprocess.Popen(
            self.script,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        exit_code = 0
        for line in iter(proc.stdout.readline, ''):
            success = self.handle_console_line(line)
            if success == True or success == False:
                if not success:
                    exit_code = 1
                break

        proc.kill()

        # Flush any remaining consoles
        self.flush_console_buffer()
        return exit_code

    def get_timestamp(self):
        return int(time.time() * 1000000)

    def handle_console_line(self, line):
        timestamp = self.get_timestamp()
        line_split = line.split('|')
        if line.startswith('__SH__GROUP__START__'):
            self.current_group_info = line_split[1]
            self.current_group_name = '|'.join(line_split[2:])
            self.current_group_info = json.loads(self.current_group_info)
            self.show_group = self.current_group_info.get('is_shown', True)
            if self.show_group == 'false':
                self.show_group = False
            console_out = {
                'consoleId': self.current_group_info.get('id'),
                'parentConsoleId': 'root',
                'type': 'grp',
                'message': self.current_group_name,
                'timestamp': timestamp,
                'isShown': self.show_group
            }
            self.handle_console_output(console_out)
        elif line.startswith('__SH__CMD__START__'):
            self.current_cmd_info = line_split[1]
            current_cmd_name = '|'.join(line_split[2:])
            self.current_cmd_info = json.loads(self.current_cmd_info)
            parent_id = self.current_group_info.get('id') if \
                self.current_group_info else None
            console_out = {
                'consoleId': self.current_cmd_info.get('id'),
                'parentConsoleId': parent_id,
                'type': 'cmd',
                'message': current_cmd_name,
                'timestamp': timestamp,
            }
            if parent_id:
                self.handle_console_output(console_out)
        elif line.startswith('__SH__CMD__END__'):
            current_cmd_end_info = line_split[1]
            current_cmd_end_name = '|'.join(line_split[2:])
            current_cmd_end_info = json.loads(current_cmd_end_info)
            parent_id = self.current_group_info.get('id') if \
                self.current_group_info else None
            is_success = False
            if current_cmd_end_info.get('exitcode') == '0':
                is_success = True
            console_out = {
                'consoleId': self.current_cmd_info.get('id'),
                'parentConsoleId': parent_id,
                'type': 'cmd',
                'message': current_cmd_end_name,
                'timestamp': timestamp,
                'timestampEndedAt': timestamp,
                'isSuccess': is_success,
                'isShown': self.show_group
            }
            if parent_id:
                self.handle_console_output(console_out)
        elif line.startswith('__SH__GROUP__END__'):
            current_grp_end_info = line_split[1]
            current_grp_end_name = '|'.join(line_split[2:])
            current_grp_end_info = json.loads(current_grp_end_info)
            is_success = False
            if current_grp_end_info.get('exitcode') == '0':
                is_success = True
            console_out = {
                'consoleId': self.current_group_info.get('id'),
                'parentConsoleId': 'root',
                'type': 'grp',
                'message': current_grp_end_name,
                'timestamp': timestamp,
                'timestampEndedAt': timestamp,
                'isSuccess': is_success,
                'isShown': self.show_group
            }
            self.handle_console_output(console_out)
        elif line.startswith('__SH__SCRIPT_END_SUCCESS__'):
            return True
        elif line.startswith('__SH__SCRIPT_END_FAILURE__'):
            return False
        else:
            parent_id = self.current_cmd_info.get('id') if \
                self.current_cmd_info else None
            console_out = {
                'consoleId': str(uuid.uuid4()),
                'parentConsoleId': parent_id,
                'type': 'msg',
                'message': line,
                'timestamp': timestamp,
            }
            if parent_id:
                self.handle_console_output(console_out)

        return None

    def handle_console_output(self, console_out):
        with self.console_buffer_lock:
            self.console_buffer.append(console_out)

        if len(self.console_buffer) > self.config['CONSOLE_BUFFER_LENGTH']:
            self.flush_console_buffer()

    def flush_console_buffer(self):
        if len(self.console_buffer) == 0:
            print 'No logs to flush'
        else:
            with self.console_buffer_lock:
                for console in self.console_buffer:
            		req_body = {
                        'buildJobId': self.config['BUILD_JOB_ID'],
                        'buildJobConsoles': self.console_buffer
            		}

            self.shippable_adapter.post_build_job_consoles(
                self.config['BUILD_JOB_ID'], req_body)

            del self.console_buffer
            self.console_buffer = []
