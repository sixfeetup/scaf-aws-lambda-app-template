import os
import random
import shlex
import shutil
import string
import subprocess


def run_setup():
    if not shutil.which("sam"):
        print("Error: AWS SAM CLI is not installed. Please install it and try again.")
        exit(1)
    
    print("Running AWS SAM build and validate...")
    subprocess.run(shlex.split("sam validate --lint"))
    subprocess.run(shlex.split("sam build"))
    print("AWS Lambda template setup complete.")


def main():
    run_setup()


if __name__ == "__main__":
    main()
