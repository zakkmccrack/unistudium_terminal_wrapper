import subprocess
import sys


def install(package):
    ## change yay to a venv type of installation or pip --user mode
    ## venv can be more portable but needs more code
    ## pip user mode can create conflict if user has different versions of these packages
    subprocess.check_call(["yay", "-S", "--noconfirm", package])


deps = ["python-bs4", "python-requests", "python-playwright", "python-tqdm"]

for d in deps:
    print("Installing {d}...")
    install(d)

print("Installing playwright browsers...")
subprocess.run(["playwright", "install"], check=False)

print("Done.")
