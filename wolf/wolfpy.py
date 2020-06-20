import logging
from wolframclient.evaluation import WolframLanguageSession
from wolframclient.language import wl

from mlib.boot.mlog import log
from mlib.boot.mutil import File, strcmp, err, pwdf, log_invokation
from mlib.boot.bootutil import ismac

class WolfPy:
    MADE = False
    def __init__(self):
        # err('dont use this for now')
        if self.MADE:
            raise Exception('just use one wl kernel')
        self.MADE = True
        if ismac():
            self.session = WolframLanguageSession(
                kernel_loglevel=logging.DEBUG,
                # kernel_loglevel=logging.FATAL,
            )
        else:
            self.session = WolframLanguageSession(
                kernel_loglevel=logging.DEBUG,
                # kernel_loglevel=logging.FATAL,

                kernel='/home/matt/WOLFRAM/Executables/WolframKernel'
            )

    def __enter__(self):
        pass
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.terminate()

    def terminate(self): self.session.terminate()
    def eval(self, s):
        ev = self.session.evaluate_wrap_future(wl.UsingFrontEnd(s))
        ev = ev.result()
        if ev.messages is not None:
            for m in ev.messages:
                err(m)
        return ev.result

    def __getattr__(self, name):
        return weval(name)

    def export(self, filename, wlstuff, *args):
        log(f'exporting to {filename}..')
        self.eval(wl.Export(filename, wlstuff, *args))
        log(f"created {filename}")

    def cloud_get(self, name):
        return self.eval(wl.CloudGet(name))

    def cloud_put(self, name, value):
        return self.eval(wl.CloudPut(name, value))

    def cloud_export(self, wlstuff, *args, format="PNG", url=None):
        myargs = []
        if url is not None:
            myargs.append(wl.CloudObject(url))
        exp = wl.CloudExport(wlstuff, format, *myargs, *args)
        co = self.eval(exp)
        return co


    def cloud_deploy(self, wlstuff, url=None, public=False, *args):
        myargs = []
        if url is not None:
            myargs.append(url)
        if public:
            myargs.append(wl.Rule(wl.Permissions, "Public"))
        exp = wl.CloudDeploy(wlstuff, *myargs, *args)
        co = self.eval(exp)
        return co

    def push_file(self, fromm):
        return self.copy_file(fromm, fromm)

    @log_invokation()
    def copy_file(self, fromm, to, permissions='Private'):
        tos = File(to).names()
        flag = True
        while flag:
            if strcmp(tos[0], pwdf().name, ignore_case=True):
                flag = False
            tos = tos[1:]

        if File(fromm).isdir():
            if self.eval(wl.DirectoryQ(wl.CloudObject(wl.FileNameJoin(tos)))):
                log('cloud dir exists. deleting.')
                self.eval(wl.DeleteDirectory(wl.CloudObject(wl.FileNameJoin(tos)), wl.Rule(wl.DeleteContents, True)))
            return self.eval(wl.CopyDirectory(
                File(fromm).abspath,
                wl.CloudObject(wl.FileNameJoin(tos), wl.Rule(wl.Permissions, permissions))
            ))
        else:
            return self.eval(wl.CopyFile(
                File(fromm).abspath,
                wl.CloudObject(wl.FileNameJoin(tos), wl.Rule(wl.Permissions, permissions))
            ))



WOLFRAM = WolfPy()
def weval(arg): return WOLFRAM.eval(arg)
