import subprocess

def run_command(command):
    try:
        result = subprocess.run(command, check=True, text=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f'Success: {result.stdout}')
    except subprocess.CalledProcessError as e:
        print(f'Error: {e.stderr}')

def uninstall_package(package_name):
    run_command(f"pip uninstall {package_name} -y")

def install_package(git_url):
    run_command(f"pip install git+{git_url}")

if __name__ == "__main__":
    package_name = "camel-ai"
    git_url = "https://github.com/Appointat/camel.git"
    uninstall_package(package_name)
    install_package(git_url)
