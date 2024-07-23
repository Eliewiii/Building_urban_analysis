"""
Decorators for the project
"""

import sys
import os
import threading
from functools import wraps
from contextlib import contextmanager
import subprocess


###############################
# Suppress terminal output
###############################
@contextmanager
def suppress_output():
    with open(os.devnull, 'w') as devnull:
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = devnull
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr


def suppress_terminal_output(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Redirect output streams for subprocess calls
        with suppress_output():
            return func(*args, **kwargs)

    return wrapper


###############################
# Thread lock for folder creation
###############################

folder_creation_lock = threading.Lock()


def synchronized_folder_creation(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with folder_creation_lock:
            return func(*args, **kwargs)

    return wrapper
