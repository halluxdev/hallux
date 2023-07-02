from subprocess import Popen, PIPE
import schedule
import time
import yaml
import os
import shutil


# Execute shell command in subprocess and return the output
def execute_command(cmd, print_output=True):
    process = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    output, error = process.communicate()

    # Check if the command returned an error
    if process.returncode != 0:
        print(f"Error executing command: {cmd}")
        print(error.decode())
        return None

    if print_output:
        print(output.decode())

    return output.decode()


# Checks for changes in a Git repository and builds the project
def check_for_changes(repo, work_dir):
    print(f"Cleaning working directory {work_dir}...")
    if os.path.exists(work_dir) and work_dir.startswith("/tmp/"):
        shutil.rmtree(work_dir)

    os.makedirs(work_dir, exist_ok=True)

    print("Cloning repository...")
    cmd = f"git clone {repo} {work_dir}"
    execute_command(cmd)

    cmd = f"tree {work_dir}"
    execute_command(cmd)

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

    # Check for changes and build the project
    check_for_changes(repo, work_dir)


if __name__ == "__main__":
    main()
