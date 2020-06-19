import os
def ismac():
    import platform
    rr = platform.system() == 'Darwin'
    return rr
def islinux():
    import platform
    rr = platform.system() == 'Linux'
    return rr
def pwd(): return os.getcwd()
