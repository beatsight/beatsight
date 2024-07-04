import pygit2
import time

def get_git_log_incrementally(repo_path, last_seen_commit):
    """
    Retrieve the Git log incrementally since the last seen commit.
    
    Args:
        repo_path (str): The path to the Git repository.
        last_seen_commit (str): The Git commit hash of the last seen commit.
    
    Returns:
        list: A list of Git commit hashes.
    """
    try:
        # Open the Git repository
        repo = pygit2.Repository(repo_path)
        
        # Get the commit object for the last seen commit
        if last_seen_commit:
            last_seen_commit_obj = repo.get(last_seen_commit)
        else:
            last_seen_commit_obj = None
        
        # Retrieve the Git log incrementally
        commit_hashes = []
        for commit in repo.walk(repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL):
            if last_seen_commit_obj and commit.id == last_seen_commit_obj.id:
                break
            commit_hashes.append(str(commit.id))
        
        return commit_hashes[::-1]
    except pygit2.GitError as e:
        print(f"Error retrieving Git log: {e}")
        return []

# Example usage
repo_path = "/beatsight-data/repos/1-sicp"
last_seen_commit = None
while True:
    new_commits = get_git_log_incrementally(repo_path, last_seen_commit)
    if new_commits:
        print("New commits:")
        for commit_hash in new_commits:
            print(commit_hash)
        last_seen_commit = new_commits[-1]
    else:
        print("No new commits")
    time.sleep(10)  # Check for new commits every minute
