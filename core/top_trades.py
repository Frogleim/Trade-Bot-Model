import subprocess

def get_git_commit_hash():
    try:
        # Run the git command to get the latest commit hash
        commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip().decode('utf-8')
        return commit_hash
    except subprocess.CalledProcessError as e:
        print(f"Error while getting git commit hash: {e}")
        return None

if __name__ == "__main__":
    commit_hash = get_git_commit_hash()
    if commit_hash:
        print(f"Current commit hash: {commit_hash}")
