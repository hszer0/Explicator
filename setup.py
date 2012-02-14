from cx_Freeze import setup, Executable

target = Executable(

    script = "explicator.py",
    base = 'Win32GUI',
    targetName = "explicator.exe",
    compress = True,
    copyDependentFiles = True,
)


includefiles = ['README', 'tutorial.db', 'default.cfg']
includes = ['cairo','pango','pangocairo','gobject','atk','gio','gtk']
excludes = ['_gtkagg', '_tkagg', 'bsddb', 'curses', 'email', 'pywin.debugger',
            'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
            'Tkconstants', 'Tkinter']
packages = []
path = []

setup(
    name = 'Explicator',
    version = '0.1.2',
    description = 'Planning tool',
    author = 'Patrick Liem',
    author_email = 'hszer0@gmail.com',
    options = {'build_exe': {'excludes':excludes,'packages':packages,'include_files':includefiles, 'path':path}},
    executables = [target]
)