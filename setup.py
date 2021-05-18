import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

options = {"build_exe": {"includes": "atexit"}}

executables = [Executable("devsat.py", base=base)]

setup(
    name="browser",
    version="1.0.1.4 LTS",
    description="Sample cx_Freeze PyQt5 script",
    options=options,
    executables=executables,
)
# instruction 
# install cs_freeze with 
...
pip install cx-Freeze
...

# python setup.py build
