import os
from execute import Execute

if __name__ == '__main__':
    print('Booting up reqExec')
    executor = Execute()
    print('Running reqExec script')
    exit_code=executor.run()
    print('reqExec has completed')
    os._exit(exit_code)
