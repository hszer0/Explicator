import sys

from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup (
    name = 'Explicator',
    version = "0.0.1",
    description = "",
    executables = [Executable("main.py", base = base)])
