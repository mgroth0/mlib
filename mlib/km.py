import os

from mlib.boot import log_invokation
from mlib.boot.mutil import isinstsafe
from mlib.file import File
def reloadIdeaFilesFromDisk(): return kmscript("C9729AC7-D386-4225-A097-92D78AFFB3AE")
@log_invokation()
def openInSafari(url):
    if isinstsafe(url, File): url = url.url()
    return kmscript(
        idd="FF3E0AC0-67D2-4378-B65A-1EF0FB60DCE7",
        param=url
    )
def activateIdea(): return kmscript("9932B71F-CF20-45B0-AD44-CCFAC92C081C")
def activateLast(): return kmscript("F92ADC3D-4745-40C2-843D-E62624604C66")
def kmscript(idd, param=None):
    var = ""
    if param is not None:
        var = f' with parameter "{param}"'
    osascript(
        f'tell application \"Keyboard Maestro Engine\" to do script \"{idd}\"{var}')
def osascript(script):
    os.system("osascript -e '" + script + "'")
