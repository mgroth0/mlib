from threading import Thread

import os

from mlib.boot.lang import isinstsafe
from mlib.file import File
from mlib.shell import shell
from mlib.term import log_invokation
def reloadIdeaFilesFromDisk(): return kmscript("C9729AC7-D386-4225-A097-92D78AFFB3AE")

@log_invokation(with_args=True, invoke_only=True)
def openInSafari(url):
    if isinstsafe(url, File): url = url.url
    return kmscript(
        idd="FF3E0AC0-67D2-4378-B65A-1EF0FB60DCE7",
        param=url
    )
def activateIdea(): return kmscript("9932B71F-CF20-45B0-AD44-CCFAC92C081C")
def activateLast(): return kmscript("F92ADC3D-4745-40C2-843D-E62624604C66")
def kmscript(idd, param=None, nonblocking=False):
    var = ""
    if param is not None:
        var = f' with parameter "{param}"'
    osascript(
        f'tell application \"Keyboard Maestro Engine\" to do script \"{idd}\"{var}', nonblocking=nonblocking)
def applescript(script):
    return osascript(script)
def osascript(script, nonblocking=False):
    if nonblocking:
        def fun():
            shell("osascript -e '" + script + "'").interact()
        Thread(target=fun).start()
    else:
        os.system("osascript -e '" + script + "'")
def showInPreview(imageFile=None): kmscript("83575D89-FCCD-4F0A-8573-752C0EFDB881", imageFile)

class Safari:
    def open(self, other):
        openInSafari(other)
Safari = Safari()
