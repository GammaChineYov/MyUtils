# git_utils.py
from git import Repo

def clone_repo(remote_repo_url, local_repo_dir):
    return Repo.clone_from(remote_repo_url, local_repo_dir)

def commit_and_push(repo_dir, commit_message):
    repo = Repo(repo_dir)
    if repo.is_dirty():
        repo.git.add(all=True)
        repo.index.commit(commit_message)
        repo.git.push()
    else:
        print("No changes to commit.")

def pull_latest(repo_dir):
    repo = Repo(repo_dir)
    repo.remotes.origin.pull()