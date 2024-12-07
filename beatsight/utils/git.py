"""
This file is part of Beatsight.

Copyright (C) 2024-2025 Beatsight Ltd.
Licensed under the GNU General Public License v3.0.
"""

import logging
import subprocess
import os
import shutil

from django.conf import settings
# import pygit2
# from pygit2 import clone_repository

logger = logging.getLogger(settings.LOGNAME)

cwd = os.getcwd()
ssh_key = f"{settings.BEATSIGHT_DATA_DIR}/id_rsa"
ssh_pubkey = f"{settings.BEATSIGHT_DATA_DIR}/id_rsa.pub"
# logger.info(f"ssh keys: {ssh_key}, {ssh_pubkey}", )

# keypair = pygit2.Keypair("git", ssh_pubkey, ssh_key, "")
# callbacks = pygit2.RemoteCallbacks(credentials=keypair)


class RepoDoesNotExist(Exception):
    ...

class BranchDoesNotExist(Exception):
    ...

class CheckoutBranchError(Exception):
    ...

class LocalRepoExists(Exception):
    ...


def clone_via_ssh(repo_url, local_path, branch_name='', depth=-1):
    os.environ["GIT_SSH_COMMAND"] = f"ssh -i {ssh_key} -o StrictHostKeyChecking=no"

    cmd = ["git", "clone", repo_url, local_path]
    if depth > 0:
        cmd += ["--depth", str(depth)]
    if branch_name:
        cmd += ["-b", branch_name]

    try:
        logger.info(f'clone_via_ssh: {cmd}')
        res = subprocess.run(cmd, check=True)
        logger.debug(res)
    except subprocess.CalledProcessError as e:
        logger.exception(f"Error cloning repository: {e}")
        raise RepoDoesNotExist

def test_repo_and_branch(repo_url, name, branch_name):
    print(f"test_repo_and_branch {repo_url}, {name}, {branch_name}")
    local_path = os.path.join(settings.TMP_REPO_DATA_DIR, name)

    if os.path.exists(local_path):
        shutil.rmtree(local_path)

    clone_via_ssh(repo_url, local_path, depth=1)

    # Change directory to the cloned repository
    old_cwd = os.getcwd()
    os.chdir(local_path)

    try:
        subprocess.run(["git", "fetch", "origin", branch_name], check=True)
        print(f"Fetched the '{branch_name}' branch successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error fetching the '{branch_name}' branch: {e}")
        raise BranchDoesNotExist
    finally:
        os.chdir(old_cwd)

def full_clone_repo_with_branch(repo_url, name, branch_name):
    logger.info(f"full_clone_repo_with_branch {repo_url}, {name}, {branch_name}")
    local_path = os.path.join(settings.REPO_DATA_DIR, name)
    if os.path.exists(local_path):
        # raise LocalRepoExists
        shutil.rmtree(local_path)

    clone_via_ssh(repo_url, local_path, branch_name=branch_name)
    return local_path

def switch_repo_branch(repo_path, branch):
    print(f"switch_repo_branch {repo_path} {branch}")

    err, cur_branch = get_current_branch(repo_path)
    if err:
        return err, False

    if cur_branch == branch:
        return '', True

    os.environ["GIT_SSH_COMMAND"] = f"ssh -i {ssh_key} -o StrictHostKeyChecking=no"

    # Change directory to the cloned repository
    old_cwd = os.getcwd()
    os.chdir(repo_path)

    err = ''
    res = True
    try:
        subprocess.run(["git", "fetch", "origin", f"{branch}:{branch}"], check=True)
        subprocess.run(["git", "checkout", branch], check=True)
    except subprocess.CalledProcessError as e:
        err = f"Error change branch to '{branch}: {e}"
        res = False
        logger.exception(err)
    finally:
        os.chdir(old_cwd)
    return err, res

def rename_current_branch(repo_path):
    # Change directory to the cloned repository
    old_cwd = os.getcwd()
    os.chdir(repo_path)
    # Get the current Git branch
    try:
        subprocess.run(['git', 'branch', '-M', 'tmp'], check=True)
        return '', True
    except subprocess.CalledProcessError as e:
        err = "Error: Could not rename current branch."
        logger.exception(e)
        return err, False
    finally:
        os.chdir(old_cwd)

def get_current_branch(repo_path):
    # Change directory to the cloned repository
    old_cwd = os.getcwd()
    os.chdir(repo_path)
    # Get the current Git branch
    try:
        current_branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode().strip()
        return '', current_branch
    except subprocess.CalledProcessError as e:
        err = "Error: Could not determine the current Git branch."
        logger.exception(e)
        return err, ''
    finally:
        os.chdir(old_cwd)

def pull_repo_updates(repo_path, branch):
    assert repo_path, f'{repo_path} can not be empty'
    assert branch, f'{branch} can not be empty'

    os.environ["GIT_SSH_COMMAND"] = f"ssh -i {ssh_key} -o StrictHostKeyChecking=no"

    # Change directory to the cloned repository
    old_cwd = os.getcwd()
    os.chdir(repo_path)

    err = ''
    has_updates = False
    try:
        # logger.debug(os.environ["GIT_SSH_COMMAND"])
        # logger.debug(os.getcwd())

        # Execute the 'git pull' command
        result = subprocess.run(['git', 'pull', 'origin', branch],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logger.debug(result)

        # Check the exit code to see if there were any errors
        if result.returncode == 0:
            # Parse the output to detect file updates
            output = result.stdout.strip()
            if output:
                for line in output.split('\n'):
                    if line.startswith(' ') or line.startswith('Updating'):
                        # print(f"- {line.strip()}")
                        has_updates = True
                        break
        else:
            err = f"Error checking for updates: {result.stderr.strip()}"
            logger.error(err)
    except subprocess.CalledProcessError as e:
        err = f"Error executing git pull: {e}"
        logger.exception(err)
    finally:
        os.chdir(old_cwd)

    return err, has_updates

def update_remote_url(repo_path, repo_url):

    # Change directory to the cloned repository
    old_cwd = os.getcwd()
    os.chdir(repo_path)

    remote_name = "origin"
    result = subprocess.run(["git", "remote", "set-url", remote_name, repo_url],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if result.returncode == 0:
        logger.info(f"{repo_path}, Remote '{remote_name}' URL updated to '{repo_url}'")
    else:
        logger.error("{repo_path} Error updating remote URL:", result.stderr.strip())

    os.chdir(old_cwd)
