#!/usr/local/bin/python3
import os
from subprocess import call, check_call, run
import pwd

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
        check_call('chown -R beatsight:beatsight %s/%s' % (log_dir, dirname), shell=True)
        check_call('chmod -R 0755 %s/%s' % (log_dir, dirname), shell=True)

    # get around of supervisor log permission bug
    # issue: https://github.com/Supervisor/supervisor/issues/123
    for filename in ['beatsight.log', 'core.out.log', 'script.log', 'task.log']:
        check_call('touch %s/%s/%s' % (log_dir, app, filename), shell=True)
        check_call('chown -R beatsight:beatsight %s/%s/%s' % (log_dir, app, filename), shell=True)

def chown_data_dir():
    # Define the directories to check
    directories = ['/data/repos', '/data/stats', '/data/temp-repos']
    for directory in directories:
        if not os.path.isdir(directory):
            continue

        try:
            # Get the current owner of the directory
            owner = pwd.getpwuid(os.stat(directory).st_uid).pw_name
            # Check if the owner is not 'beatsight'
            if owner != 'beatsight':
                print(f"Changing ownership of {directory} to beatsight")
                # Change ownership recursively
                run(['chown', '-R', 'beatsight', directory], check=True)
        except Exception as e:
            print(f"Error processing chown {directory}: {e}")
