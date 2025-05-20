import os
import shlex
import shutil
import subprocess


TERMINATOR = "\x1b[0m"
WARNING = "\x1b[1;33m [WARNING]: "
INFO = "\x1b[1;33m [INFO]: "
HINT = "\x1b[3;33m"
SUCCESS = "\x1b[1;32m [SUCCESS]: "


def run_setup():
    print("Performing initial commit.")
    subprocess.run(shlex.split("git add ."))
    subprocess.run(shlex.split("git commit -m 'Initial commit' --quiet"))

    if not shutil.which("sam"):
        print("Error: AWS SAM CLI is not installed. Please install it and try again.")
        exit(1)

    print("Running AWS SAM build and validate...")
    subprocess.run(shlex.split("make validate"))
    subprocess.run(shlex.split("make build"))
    print("AWS Lambda template build and setup complete.")


def init_git_repo():
    print(INFO + "Initializing git repository..." + TERMINATOR)
    print(INFO + f"Current working directory: {os.getcwd()}" + TERMINATOR)
    subprocess.run(shlex.split("git -c init.defaultBranch=main init . --quiet"))
    print(SUCCESS + "Git repository initialized." + TERMINATOR)


def configure_git_remote():
    repo_url = "{{ copier__repo_url }}"
    if repo_url:
        print(INFO + f"repo_url: {repo_url}" + TERMINATOR)
        command = f"git remote add origin {repo_url}"
        subprocess.run(shlex.split(command))
        print(SUCCESS + f"Remote origin={repo_url} added." + TERMINATOR)
    else:
        print(
            WARNING
            + "No repo_url provided. Skipping git remote configuration."
            + TERMINATOR
        )

def log_next_steps():
    print(
        HINT
        + "Next steps:"
        + "\n1. Run 'cd {{ copier__project_name }}' to enter the project directory"
        + "\n2. Run 'make setup' to run dynamodb locally and create the database"
        + "\n3. Then run 'make build' to build the lambda function"
        + "\n4. Then run 'make deploy' to deploy the lambda function"
        + "\n5. To remove the local setup, run 'make down'"
        + "\nRefer to README.md for more details."
        + TERMINATOR
    )

def main():
    init_git_repo()
    configure_git_remote()
    run_setup()
    log_next_steps()


if __name__ == "__main__":
    main()
