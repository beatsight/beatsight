#!/usr/bin/python3
import os
import sys
import time
from subprocess import check_call

from library import get_env, initialize_logdir, initialize_data_dir


def main(argv):
    conf = get_env()
    initialize_data_dir()
    initialize_logdir()
    os.chdir(conf['app_dir'])

    if argv[1] == 'debug':
        print('Docker image is running, you can attach into the container for debug')
        while 1:
            time.sleep(5)
    elif argv[1] == 'beatsight':
        check_call("gosu ubuntu bash -c 'python3 manage.py gen_rsa_keys'", shell=True)

        check_call("gosu ubuntu bash -c 'rm -rf static/* 2> /dev/null && python3 manage.py collectstatic --noinput'", shell=True)

        # Start the container.
        check_call("supervisord -c /etc/supervisor/supervisord.conf", shell=True)
        time.sleep(5)
        check_call("tail -f /home/ubuntu/logs/supervisor/*.log /home/ubuntu/logs/nginx/*.log /home/ubuntu/logs/beatsight/*.log | grep  -v ping", shell=True)
    else:
        # Run the command provided as the second argument
        command = ' '.join(argv[1:])  # Join all arguments after the first
        check_call(f"gosu ubuntu bash -c '{command}'", shell=True)

if __name__ == "__main__":
    # main program
    main(sys.argv)