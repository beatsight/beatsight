#!/usr/local/bin/python3
import os
from subprocess import call, check_call


def get_env():
    """
    Function to read enviroment variables.
    :return: dict
    """
    env_vars = os.environ
    # Print each environment variable
    for key, value in env_vars.items():
        print(f"{key}: {value}")

    environ = {}
    environ['home_dir'] = env_vars['HOME_DIR']
    environ['log_dir'] = env_vars['LOG_DIR']
    environ['app_dir'] = env_vars['INSTALL_DIR']
    return environ

def write_file(template, path):
    """
    Write file.
    :param template: file content
    :param path: file path with name
    :return: None
    """
    with open(path, "wb") as output:
        output.write(template)
    output.close()

def initialize_logdir(app='beatsight'):
    """create log directory for app
            /var/log/supervisor
            /var/log/nginx
    """
    conf = get_env()

    log_dir = conf['log_dir']
    for dirname in ['supervisor', app, 'nginx']:
        check_call('mkdir -p %s/%s' % (log_dir, dirname), shell=True)
        check_call('chown -R ubuntu:ubuntu %s/%s' % (log_dir, dirname), shell=True)
        check_call('chmod -R 0755 %s/%s' % (log_dir, dirname), shell=True)

    # get around of supervisor log permission bug
    # issue: https://github.com/Supervisor/supervisor/issues/123
    for filename in ['beatsight.log', 'core.out.log', 'script.log', 'task.log']:
        check_call('touch %s/%s/%s' % (log_dir, app, filename), shell=True)
        check_call('chown -R ubuntu:ubuntu %s/%s/%s' % (log_dir, app, filename), shell=True)
