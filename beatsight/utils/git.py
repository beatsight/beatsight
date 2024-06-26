import subprocess
import os
import shutil

# import pygit2
# from pygit2 import clone_repository

cwd = os.getcwd()
print(f"Current working dir: {cwd}")

ssh_key = f"{cwd}/data/id_rsa"
ssh_pubkey = f"{cwd}/data/id_rsa.pub"
print("ssh keys:", ssh_key, ssh_pubkey)

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


def clone_via_ssh(repo_url, local_path, branch_name='', depth=100000, ):
    os.environ["GIT_SSH_COMMAND"] = f"ssh -i {ssh_key} -o StrictHostKeyChecking=no"

    cmd = ["git", "clone", repo_url, local_path, "--depth", str(depth)]
    if branch_name:
        cmd += ["-b", branch_name]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e}")
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
