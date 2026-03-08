import os
import json
import subprocess
from datetime import datetime

def run_git_task():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "configs", "archive_config.json")

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    git_conf = config["git_config"]
    commit_conf = config["commit_config"]
    logs = config["logs"]

    repo_path = os.path.abspath(os.path.join(base_dir, git_conf["local_path"]))

    if not os.path.exists(repo_path):
        print(logs["error"].format(error=f"Directory {repo_path} not found"))
        return

    os.chdir(repo_path)

    try:
        print(logs["start"])

        subprocess.run(["git", "config", "user.name", git_conf["author"]["name"]], check=True)
        subprocess.run(["git", "config", "user.email", git_conf["author"]["email"]], check=True)

        for target in commit_conf["target_directories"]:
            if os.path.exists(target):
                subprocess.run(["git", "add", target], check=True)

        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not status.stdout.strip():
            print(logs["no_changes"])
            return

        today = datetime.now().strftime("%Y-%m-%d")
        commit_msg = commit_conf["message_template"].format(date=today)
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)

        subprocess.run([
            "git", "push", 
            git_conf["remote_name"], 
            git_conf["branch_name"]
        ], check=True)

        print(logs["success"].format(remote=git_conf["remote_name"], branch=git_conf["branch_name"]))

    except Exception as e:
        print(logs["error"].format(error=str(e)))

if __name__ == "__main__":
    run_git_task()