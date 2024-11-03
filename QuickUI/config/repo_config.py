# repo_config.py
import os
import re

def configure_repo(remote_repo_url, local_repo_root_dir="/content/drive/MyDrive/MyRepos/"):
    repo_name = re.findall(r"/([^/]+)\.git", remote_repo_url)[0]
    local_repo_dir = os.path.join(local_repo_root_dir, repo_name)
    os.makedirs(local_repo_dir, exist_ok=True)
    return remote_repo_url, local_repo_dir, repo_name

def create_symlink(source, destination):
    if not os.path.islink(destination):
        os.symlink(source, destination)
    print(f"Symlink created: {source} -> {destination}")