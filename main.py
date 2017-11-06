import os
from executor import Executor
import sys

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Missing script name'
        sys.exit(1)
    elif len(sys.argv) < 3:
        print 'Missing job ENVs path'
        sys.exit(1)
    else:
        script_path = sys.argv[1]
        job_envs_path = sys.argv[2]

    ex = Executor(script_path, job_envs_path)
    ex.execute()
    os._exit(ex.exit_code)
