#!/usr/bin/python3
import os
import sys
import time
from subprocess import check_call

from library import get_env, initialize_logdir, chown_data_dir


def main(argv):
    conf = get_env()
    initialize_logdir()
    chown_data_dir()
    os.chdir(conf['app_dir'])

    if argv[1] == 'debug':
        print('Docker image is running, you can attach into the container for debug')
        while 1:
            time.sleep(5)
    elif argv[1] == 'beatsight':
        check_call("gosu beatsight bash -c 'python3 manage.py gen_rsa_keys'", shell=True)
        check_call("gosu beatsight bash -c 'chmod 400 /data/id_rsa*'", shell=True)
        check_call("gosu beatsight bash -c 'rm -rf /tmp/gunicorn.pid'", shell=True)

        check_call("gosu beatsight bash -c 'rm -rf static/* 2> /dev/null && python3 manage.py collectstatic --noinput'", shell=True)

        # Start the container.
        check_call("supervisord -c /etc/supervisor/supervisord.conf", shell=True)
        time.sleep(5)
        check_call("tail -f /home/beatsight/logs/supervisor/*.log /home/beatsight/logs/nginx/*.log /home/beatsight/logs/beatsight/*.log | grep  -v ping", shell=True)
    elif argv[1] == 'sudo':
        command = ' '.join(argv[2:])  # Join all arguments after the first
        check_call(f"{command}", shell=True)
    else:
        # Run the command provided as the second argument
        command = ' '.join(argv[1:])  # Join all arguments after the first
        check_call(f"gosu beatsight bash -c '{command}'", shell=True)

if __name__ == "__main__":
    # main program
    main(sys.argv)
