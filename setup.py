from cx_Freeze import setup, Executable
from os import environ

base = None
environ['TCL_LIBRARY'] = r"E:\ProgramFiles\Python3\tcl\tcl8.6"
environ['TK_LIBRARY'] = r'E:\ProgramFiles\Python3\tcl\tk8.6'
executables = [Executable("noteidentifier.py", base=base)]

packages = ['numpy','pyaudio','sys']
options = {
    'build_exe': {
        'packages':packages,
    }
}

setup(
    name = "note",
    options = options,
    version = "1",
    description = 'note identifier',
    executables = executables)