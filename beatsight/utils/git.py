import logging
import subprocess
import os
import shutil

from django.conf import settings
# import pygit2
# from pygit2 import clone_repository

logger = logging.getLogger(settings.LOGNAME)

cwd = os.getcwd()
ssh_key = f"{cwd}/data/id_rsa"
ssh_pubkey = f"{cwd}/data/id_rsa.pub"
# logger.info(f"ssh keys: {ssh_key}, {ssh_pubkey}", )

# keypair = pygit2.Keypair("git", ssh_pubkey, ssh_key, "")
# callbacks = pygit2.RemoteCallbacks(credentials=keypair)

tmp_repo_data_dir = '/beatsight-data/temp-repos'
if not os.path.exists(tmp_repo_data_dir):
    os.makedirs(tmp_repo_data_dir)

repo_data_dir = '/beatsight-data/repos'
if not os.path.exists(repo_data_dir):
    os.makedirs(repo_data_dir)

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
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.exception(f"Error cloning repository: {e}")
        raise RepoDoesNotExist

def test_repo_and_branch(repo_url, name, branch_name):
    print(f"test_repo_and_branch {repo_url}, {name}, {branch_name}")
    local_path = os.path.join(tmp_repo_data_dir, name)

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
    print(f"full_clone_repo_with_branch {repo_url}, {name}, {branch_name}")
    local_path = os.path.join(repo_data_dir, name)
    if os.path.exists(local_path):
        # raise LocalRepoExists
        shutil.rmtree(local_path)

    clone_via_ssh(repo_url, local_path, branch_name=branch_name)
    return local_path

def switch_repo_branch(repo_path, branch):
    print(f"switch_repo_branch {repo_path} {branch}")

    os.environ["GIT_SSH_COMMAND"] = f"ssh -i {ssh_key} -o StrictHostKeyChecking=no"

    # Change directory to the cloned repository
    old_cwd = os.getcwd()
    os.chdir(repo_path)

    try:
        subprocess.run(["git", "fetch", "origin", f"{branch}:{branch}"], check=True)
        subprocess.run(["git", "checkout", branch], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error change branch to '{branch}")
        print(e)
        raise BranchDoesNotExist
    finally:
        os.chdir(old_cwd)

def pull_repo_updates(repo_path, branch):
    os.environ["GIT_SSH_COMMAND"] = f"ssh -i {ssh_key} -o StrictHostKeyChecking=no"

    # Change directory to the cloned repository
    old_cwd = os.getcwd()
    os.chdir(repo_path)

    has_updates = False
    try:
        # Execute the 'git pull' command
        result = subprocess.run(['git', 'pull', 'origin', branch],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result)
        # Check the exit code to see if there were any errors
        if result.returncode == 0:
            # Parse the output to detect file updates
            output = result.stdout.strip()
            if output:
                for line in output.split('\n'):
                    if line.startswith(' ') or line.startswith('Updating'):
                        print(f"- {line.strip()}")
                        has_updates = True
                        break
        else:
            print("Error checking for updates:", result.stderr.strip())
    except subprocess.CalledProcessError as e:
        print("Error executing git pull:", e)
        raise e
    finally:
        os.chdir(old_cwd)

    return has_updates
