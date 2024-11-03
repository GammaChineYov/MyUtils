# file_utils.py
import os
import importlib.util
import shutil
from google.colab import files

def open_or_create_file(filepath):
    if not os.path.exists(filepath):
        with open(filepath, "w") as f:
            pass
    files.view(filepath)

def backup_file(filepath):
    shutil.copy(filepath, f"{filepath}.bak")

def restore_backup(filepath):
    if os.path.exists(f"{filepath}.bak"):
        shutil.copy(f"{filepath}.bak", filepath)