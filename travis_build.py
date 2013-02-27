#! /usr/bin/python
import platform
import subprocess
import sys

def _execute(cmd):
    if 0 != subprocess.call(cmd, shell=True):
        sys.exit(-1)

if __name__ == '__main__':
    if platform.python_version() < "3.3":
        _execute("pylint --rcfile=.pylintrc setup.py")
        _execute("pylint --rcfile=.pylintrc shakedown")
    _execute("nosetests -w tests")