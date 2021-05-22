import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

options = {"build_exe": {"includes": "atexit", 'include_files': ["static/"]}}

executables = [Executable("devsat.py", base=base)]

setup(
    name="browser",
    version="1.0.2.1 LTS",
    description="Sample cx_Freeze PyQt5 script",
    options=options,
    executables=executables,
)

# python setup.py build

# instruction to get .exe

# 1) install cs_freeze with  "pip install cx-Freeze"


# 2) run command in terminal "python setup.py build"
