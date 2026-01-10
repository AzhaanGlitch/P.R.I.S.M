"""
Silent launcher for P.R.I.S.M
Uses pythonw.exe to run without console window
Place this file in the same directory as Main.py
"""

import subprocess
import sys
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Path to Main.py
main_script = os.path.join(script_dir, "Main.py")

# Get pythonw.exe path (same directory as python.exe, but no console)
python_dir = os.path.dirname(sys.executable)
pythonw_exe = os.path.join(python_dir, "pythonw.exe")

# If pythonw doesn't exist, fall back to python
if not os.path.exists(pythonw_exe):
    pythonw_exe = sys.executable

# Start P.R.I.S.M in tray mode without showing console
subprocess.Popen(
    [pythonw_exe, main_script, "--mode", "tray"],
    cwd=script_dir,
    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
)