from subprocess import Popen, PIPE
import schedule
import time
import yaml
import os
import shutil


def execute_command(cmd, print_output=True):
    process = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    output, error = process.communicate()

    if process.returncode != 0:
        print(f"Error executing command: {cmd}")
        print(error.decode())
        return None

    if print_output:
        print(output.decode())

    return output.decode()


def check_for_changes(repo, work_dir):
    # Remove the directory and its contents
    print(f"Cleaning working directory {work_dir}...")
    if os.path.exists(work_dir) and work_dir.startswith("/tmp/"):
        shutil.rmtree(work_dir)

    # Create the directory and its parent directories if they don't exist
    os.makedirs(work_dir, exist_ok=True)

    # clone repo into work_dir
    print("Cloning repository...")
    cmd = f"git clone {repo} {work_dir}"
    execute_command(cmd)

    # list files in work_dir
    cmd = f"tree {work_dir}"
    execute_command(cmd)

    # build the project
    print("Building project...")
    cmd = f"scripts/run-build.sh {work_dir}"
    execute_command(cmd)


def main():
    print("Starting worker...")

    with open("./worker/config.yaml", "r") as stream:
        try:
            config = yaml.safe_load(stream)
            repo = config["repo"]
            work_dir = config["work_dir"]
        except yaml.YAMLError as exc:
            print(exc)
            return

    print(f"Repo: {repo} {work_dir}")
    check_for_changes(repo, work_dir)

    # Polling to be added later
    # schedule.every(1).minutes.do(check_for_changes, repo, work_dir)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
