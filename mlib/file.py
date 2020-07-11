import atexit
from glob import glob
import inspect
import json
import os
from os.path import expanduser
import pathlib
from pathlib import Path
import shutil
from typing import MutableMapping
import matplotlib.image as mpimg
from PIL import Image
import htmlmin
import imageio
import numpy as np
from scipy.io import loadmat, savemat
import yaml

from mlib.boot import mlog, log
from mlib.boot.bootutil import pwd, ismac, isinstsafe, SimpleObject, cn
from mlib.boot.dicts import DefaultMutableMapping
from mlib.boot.mlog import Muffleable, warn
from mlib.boot.mutil import mypwd, err, isstr, mkdir, sort, arr, notblank, isempty, StringExtension, listkeys
from mlib.boot.stream import arrmap, listfilt
from mlib.shell import ishell
from mlib.term import log_invokation



BASE_WOLFRAM_URL = 'https://www.wolframcloud.com/obj/mjgroth'

def url(path): return File(path).url
def read(path): return File(path).read()
class File(os.PathLike, MutableMapping, Muffleable, SimpleObject):
    __npitr__ = False
    def quiet(self, quiet=True):
        self.default_quiet = quiet
        return self
    def str(self):
        path = self.abspath.replace(expanduser('~'), '~')
        return f'<File {path}>'

    def muffle(self):
        self._default_default_quiet = self.default_quiet
        self.default_quiet = True
    def unmuffle(self):
        self.default_quiet = self._default_default_quiet

    def __init__(self, abs, remote=None, mker=False, w=None, default=None, quiet=None):
        self.IGNORE_DS_STORE = False
        self._default = default
        from wolframclient.language.expression import WLFunction
        from wolframclient.language import wl
        from mlib.wolf.wolfpy import weval
        if isinstsafe(abs, File):
            self.isSSH = abs.isSSH
            abs = abs.abspath
        elif isinstsafe(abs, WLFunction):
            if str(weval(wl.Head(abs))) == 'CloudObject':
                self.isSSH = False
                url = abs[0]
                if BASE_WOLFRAM_URL not in url:
                    err(f'{BASE_WOLFRAM_URL=} not in {url=}')
                else:
                    abs = url.replace(BASE_WOLFRAM_URL, '')
            else:
                err(f'only use cloud objects, not {weval(wl.Head(abs))=}')
        elif not os.path.isabs(abs):
            self.isSSH = 'test-3' in abs
            abs = os.path.join(mypwd(), abs)
        else:
            self.isSSH = 'test-3' in abs
        self.abspath = abs
        self.wcurl = f'{BASE_WOLFRAM_URL}{abs}'
        self.relpath = os.path.relpath(abs, os.getcwd())
        self.name = os.path.basename(abs)
        _, dot_extension = os.path.splitext(abs)
        self.ext = dot_extension.replace('.', '')
        self.name_pre_ext = self.name.split('.')[0]

        self.parentDir = os.path.abspath(os.path.join(abs, os.pardir))
        self.parent = Folder(self.parentDir) if self.abspath != '/' else None

        self.parentName = os.path.basename(self.parentDir)

        # this might change so they have to be functions
        # self.isfile = os.path.isfile(self.abspath)
        # self.isdir = os.path.isdir(self.abspath)

        self.mker = mker
        if mker:
            self.mkdirs()

        if w is not None:
            self.write(w)

        self.rel = os.path.relpath(abs, pwd())

        self.default_quiet = quiet
        self._default_default_quiet = None  # for muffleing

    def __len__(self) -> int:
        if isinstsafe(self, Folder):
            return len(self.files)
        else:
            return len(self.load())
    def __iter__(self):
        if isinstsafe(self, Folder):
            return iter(self.files)
        else:
            return iter(self.load())





    @property
    def wc(self):
        from mlib.wolf.wolfpy import _WCFile
        return _WCFile(self)


    def hidden_version(self, rel_to):
        rel = self.rel_to(rel_to)
        hidden_rel = os.path.join(*[f'_{name}' for name in os.path.split(rel)])
        return Folder(rel_to)[hidden_rel]







    def rel_to(self, parent):
        parent = File(parent).abspath
        # com = os.path.commonprefix([parent, self.abspath])
        # assert com != '/'
        # return os.path.relpath(self.abspath, com)
        return os.path.relpath(self.abspath, parent)

    @property
    def url(self):
        return pathlib.Path(self.abspath).as_uri()

    @property
    def isfile(self):
        return os.path.isfile(self.abspath)

    @property
    def isdir(self): return os.path.isdir(self.abspath)

    @property
    def isdirsafe(self): return self.isdir if self.exists else '.' not in self.name

    def __fspath__(self): return self.abspath



    def zip_in_place(self):
        return self.zip_to(self)

    def zip_to(self, dest):
        if not self.default_quiet:
            mlog.log('zipping...')
        p = ishell()
        p.cd(self.parentDir)
        p.sendline('DONEVAR=DONEWITHZIP')
        p.sendline('DONEVARR=REALLYDONEWITHZIP')
        p.zip([
            '-r',
            File(dest).abspath,
            self.name
        ])
        p.echo('$DONEVAR$DONEVARR')
        p.expect('DONEWITHZIPREALLYDONEWITHZIP')
        p.close()
        return File(f'{File(dest).abspath}.zip')

    def copy_into(self, dest, overwrite=False):
        dest = Folder(dest)
        dest.mkdirs()
        return self.copy_to(dest[self.name], overwrite=overwrite)

    def copy_to(self, dest, overwrite=False):
        dest = File(dest)
        assert self.exists
        assert self.abspath != dest.abspath
        dest.mkparents()

        if overwrite and self.exists:
            dest.deleteIfExists()
        if self.isfile:
            return File(shutil.copyfile(self, dest))
        else:
            return Folder(shutil.copytree(self, dest))

    def loado(self): return self.load(as_object=True)
    def load(self, as_object=False):
        assert not self.isdir
        if not self.default_quiet:
            log('Loading ' + self.abspath, ref=1)
        if not self.exists and self._default is not None:
            self.save(self._default)
        if self.ext == 'h5':
            #     only works with datasets, not groups?
            # import pandas as pd
            # return pd.read_hdf(self.abspath)

            import h5py

            # d = {}
            def recurse_h5(ff):
                # o = f
                # subd = d
                # for k in keypath:
                #     o = o[k]
                #     subd = subd[k]
                if type(ff) == h5py.File or type(ff) == h5py._hl.group.Group:
                    ks = listkeys(ff)
                    subd = {}
                    for k in ks:
                        subd[k] = recurse_h5(ff[k])
                elif type(ff) == h5py._hl.dataset.Dataset:
                    subd = np.array(ff)
                else:
                    err(f'do not know what to do with {ff.__class__}')

                return subd




            with h5py.File(self.abspath, "r") as f:
                return recurse_h5(f)
                # List all groups
                # return {k: f[k] for k in listkeys(f)}
                # for k in listkeys(f):
                #     d[k] = f[k]
                # print(f"Keys: {f.keys()}")
                # a_group_key = list(f.keys())[0]

                # Get the data
                # data = list(f[a_group_key])
            # return d
        elif self.ext == 'edf':
            import mne
            import HEP_lib
            return HEP_lib.MNE_Set_Wrapper(mne.io.read_raw_edf(self.abspath, preload=False))
        elif self.ext in ['yml', 'yaml']:
            return yaml.load(self.read(), Loader=yaml.FullLoader)
        elif self.ext == 'set':
            import mne
            import HEP_lib
            return HEP_lib.MNE_Set_Wrapper(mne.io.read_raw_eeglab(self.abspath, preload=False))
        elif self.ext == 'json':
            j = json.loads(self.read())
            if as_object:
                import mlib.JsonSerializable as JsonSerializable
                return JsonSerializable.obj(j)
            else:
                return j
        elif self.ext.lower() in ['jpeg', 'jpg'] or self.ext == 'png':
            # return arr(Image.open(self.abspath).getdata()) #wrong shape
            return mpimg.imread(self.abspath)
        elif self.ext == 'mat':
            return loadmat(self.abspath)
        else:
            raise self.NoLoadSupportException(f'loading does not yet support .{self.ext} files')
    class NoLoadSupportException(Exception): pass
    def save(self, data, silent=None):
        import mlib.JsonSerializable as JsonSerializable
        import mlib.fig.PlotData as PlotData
        if isinstance(data, PlotData.FigData):
            data = JsonSerializable.FigSet(data)
        if isinstsafe(data, JsonSerializable.JsonSerializable):
            data = json.loads(data.to_json())
        elif isinstance(data, JsonSerializable.obj):
            data = data.toDict()
        if not silent and not self.default_quiet or (silent is False):
            log('saving ' + self.abspath)
        if self.ext in ['yml', 'yaml']:
            self.mkparents()
            self.write(yaml.dump(data, sort_keys=False))
        elif self.ext == 'json':
            self.mkparents()
            self.write(json.dumps(data, indent=4))
        elif self.ext == 'mat':
            self.mkparents()
            savemat(self.abspath, data)
        elif self.ext == 'png':
            self.mkparents()
            im_data = np.vectorize(np.uint8)(data)
            imageio.imwrite(self.abspath, im_data)
        else:
            err(f'saving does not yet support .{self.ext} files')



    def clear(self):
        assert self.isdir
        [f.delete() for f in self.files]


    def deleteIfExists(self):
        if self.exists: self.delete()
        return self

    def delete(self):
        # os.remove() removes a file.
        # os.rmdir() removes an empty directory.
        # shutil.rmtree() deletes a directory and all its contents.
        if self.isdir:
            if isempty(self.paths):
                os.rmdir(self.abspath)
            else:
                shutil.rmtree(self.abspath)
        else:
            os.remove(self.abspath)



    def mkdirs(self, mker=False):
        mkdirs(self.abspath)
        return Folder(self, mker=mker)

    def mkdir(self):
        mkdir(self.abspath)
        return Folder(self)

    def touch(self):
        Path(self.abspath).touch()

    def mkparents(self):
        mkdirs(self.parentDir)

    def moveinto(self, new):
        File(new).mkdirs()
        assert File(new).isdir
        shutil.move(self.abspath, File(new).abspath)

    def moveto(self, new):
        assert not File(new).isdir
        shutil.move(self.abspath, File(new).abspath)



    @property
    def edition_wolf_dev(self): return self.parent[f'{self.name}_wolf_dev']
    @property
    def edition_wolf_pub(self): return self.parent[f'{self.name}_wolf']
    @property
    def edition_git(self): return self
    @property
    def edition_local(self): return self.parent[f'{self.name}_local']




    def join(self, *paths): return os.path.join(self, *paths)




    @log_invokation()
    def backup(self):
        if not self.exists:
            warn(f'cannot back up {self}, which does not exist')
            return
        backup_folder = self.parent['backups'].mkdir()
        assert backup_folder.isdir
        i = 0
        while True:
            i += 1
            backup_file = backup_folder[f'{self.name}.backup{i}']
            if not backup_file.exists:
                backup_file.write(self.read())
                break



    def resolve(self, nam):
        nam = str(nam)
        resolved_is_file = '.' in nam
        resolved = File(
            self.join(nam),
            mker=False if resolved_is_file else self.mker
        )
        if self.mker and not resolved.exists and not resolved_is_file:
            resolved.mkdir()
        if resolved.isdirsafe: return Folder(resolved, mker=self.mker)
        return resolved

    def respath(self, nam): return self.resolve(nam).abspath
    def glob(self, g): return arr([File(m) for m in glob(self.join(g))])
    @property
    def folders(self): return listfilt(
        lambda f: f.isdir,
        self.files
    )

    @property
    def files(self): return self.paths.map(File)
    @property
    def paths(self):
        a = arr(
            [self.join(name) for name in sort(os.listdir(self.abspath))]
        )
        if self.IGNORE_DS_STORE:
            a = a.filtered(
                lambda n: File(n).name != '.DS_Store'
            )
        return a

    def __getattr__(self, item):
        if not self.exists or self.isdir:
            raise AttributeError
        data = self.load(as_object=True)
        return data.__getattribute__(item)

    # def __setattr__(self, key, value):
    #     if self.exists():
    #         data = self.load(as_object=True)
    #     else:
    #         data = obj({})
    #     log('saving ' + str(key))  # +' to ' + str(value)
    #     data.__setattr__(key, value)
    #     self.save(data.__dict__)
    #     log('saved ' + str(key))  # +' to ' + str(value)

    def __getitem__(self, item):
        data = self.load()
        return data[item]

    def __delitem__(self, key):
        assert self.exists
        data = self.load()
        if not self.default_quiet:
            log(f'deleting {key}')
        del data[key]
        self.save(data)
        if not self.default_quiet:
            log(f'deleted {key}')



    def __setitem__(self, key, value):
        if self.exists:
            data = self.load()
        else:
            data = {}
        if not self.default_quiet:
            log('saving ' + str(key))  # +' to ' + str(value)
        data[key] = value
        self.save(data)
        if not self.default_quiet:
            log('saved ' + str(key))  # +' to ' + str(value)

    def msecs(self):
        return os.path.getmtime(self.abspath)

    @property
    def exists(self):
        return os.path.isfile(self.abspath) or os.path.isdir(self.abspath)

    def open(self):
        from mlib.km import openInSafari
        return openInSafari(self)

    def read(self):
        with open(self.abspath, 'r') as file:
            return file.read()
    def readlines(self, fun=None):
        lines = arrmap(StringExtension, arr(self.read().split('\n')))
        if fun is not None:
            lines = arrmap(fun, lines)
        return lines

    def appendln(self, s):
        self.append(s + '\n')

    def append(self, s):
        with open(self.abspath, "a") as myfile:
            myfile.write(s)

    def write_lines(self, lines, trailing_nl=False):
        self.write('\n'.join(lines))

    def write(self, s):
        import os
        self.mkparents()
        if not os.path.isfile(self.abspath):
            open(self.abspath, 'a').close()
        with open(self.abspath, 'w') as file:
            if not isstr(s):
                s = str(s)
            return file.write(s)

    def deleteAllContents(self):
        if self.exists: [f.delete() for f in self.files]

    def names(self, keepExtension=True):
        nams = []
        path = self.abspath
        while path != '/' and len(path) > 0:
            head, tail = os.path.split(path)
            if '.' in tail and keepExtension is False:
                tail = tail.split('.')[0]
            nams.append(tail)
            # if head == '/': break
            path = File(head).abspath
        return arr(list(reversed(nams)))


class Folder(File):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.exists:
            assert self.isdir, f'{self} is not a dir'
    def __getitem__(self, item):
        assert self.isdirsafe
        return self.resolve(item)
    def __setitem__(self, key, value):
        assert self.isdir
        raise NotImplementedError('need have class for FileData object (not File, but FileData...)')
    def __getattr__(self, item):
        # undo File's override. We don't want to load from Folders
        raise AttributeError

    def make_webpage(self, htmlDoc, resource_root, resource_root_rel):
        self.deleteAllContents()
        from mlib.web.js import JS
        from mlib.web.css import CSS
        self[f'{htmlDoc.name}.html'].write(
            htmlmin.minify(htmlDoc.getCode(resource_root, resource_root_rel), remove_empty_space=True)
        )

        css = CSS(htmlDoc.stylesheet)
        css += htmlDoc.style
        # with Temp('temp.css') as f:
        #     f.write(htmlDoc.stylesheet)
        self['style.css'].write(css.output())
        # \
        # .write(
        # lesscpy.compile(f.abspath, minify=True),
        # )

        mlibjs = File(inspect.getfile(JS)).parent['mlib.js'].read()
        platformjs = File(inspect.getfile(JS)).parent['platform.js'].read()
        self['mlib.js'].write(JS(mlibjs, onload=False).output())
        self['platform.js'].write(JS(platformjs, onload=False).output())


class Temp(File):
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.deleteIfExists()

class TempFolder(Temp, Folder): pass
def listfiles(f): return File(f).paths()
def filename(o):
    return File(o).name
def abspath(file, remote=None): return File(file, remote=remote).abspath
def load(file):
    return File(file).load()
def mkdirs(file):
    if File(file).isfile:
        file = File(file).parentDir
    os.makedirs(file, exist_ok=True)
class SyncedFolder(File):
    def sync(self, config=None, batch=False, lpath=None):
        assert ismac()
        import google_compute
        assert google_compute.isrunning()
        google_compute.gcloud_config()
        com = ['/usr/local/bin/unison']
        f = None
        if config is not None:
            assert config == 'mitili'
            f = Temp('/Users/matt/.unison/mitili.pref')
            com += [config]
        com += '-root'
        com += self.mpath
        com += '-root'
        if lpath is None:
            lpath = self.lpath
        if not lpath[0] == '/':
            lpath.insert(0, '/')
        com += 'ssh://test-3.us-central1-a.neat-beaker-261120' + self.lpath.replace('/home/matt', '')
        if batch:
            com += '-batch'
        f.__enter__()
        f.write('''
# Some regexps specifying names and paths to ignore


ignore = Name .DS_Store
ignore = Name .git
ignore = Name .idea
ignore = Name .gradle
ignore = Name gradle
ignore = Name .pass

ignore = Name __pycache__


ignore = Path WC/log.log



ignore = Name {.*,*,*/,.*/}.mat
ignore = Name {.*,*,*/,.*/}.png
ignore = Name {.*,*,*/,.*/}.pyc





ignore = Path {figures*}
ignore = Path {venv.old}
ignore = Path {cache}
ignore = Path {src/main/kotlin}
ignore = Path {build.gradle.kts}
ignore = Path {build}
ignore = Path {_figs}
ignore = Path {images}
ignore = Path {GoogLeNet}
ignore = Path {HEP/data}
ignore = Path {nap}
ignore = Path {plot.png}
        
        ''')
        p = SSHProcess(com)

        def finishSync():
            # # this has to be called or it will block
            if p.alive():
                p.readlines()
                p.wait()
                f.__exit__()
        atexit.register(finishSync)

        p.login()

        p.interact()

        f.__exit__(None, None, None)
class SyncedDataFolder(SyncedFolder):
    def __init__(self, mpath, lpath):
        self.mpath = self.abspath
        err('used to have line: self.lpath = mlib.file.abspath')
        if ismac():
            thispath = mpath
        else:
            assert islinux()
            thispath = lpath
        super(SyncedDataFolder, self).__init__(thispath)

    def presync(self):
        lastsave = WC['lastsave']
        if lastsave == 'linux' and ismac():
            self.sync()
    def postsync(self):
        if ismac():
            self.sync()
            WC['lastsave'] = 'mac'
        else:
            WC['lastsave'] = 'linux'
class PermaDict(DefaultMutableMapping):
    def __init__(self, file):
        self.file = File(file)
        super().__init__(self.file)
        if not self.file.exists:
            self.file.save({})
        self.file.default_quiet = True
    def check(self):
        from mlib.proj.struct import GIT_DIR, GIT_IGNORE
        if not self.file.rel.startswith('_'):
            err('PermaDicts should be private (start with _)')
        if GIT_DIR.exists and (not GIT_IGNORE.exists or '/_*' not in GIT_IGNORE.read()):
            err(f'{self.file} needs to be ignored')
        if not self.file.exists:
            self.file.save({})
    def __getitem__(self, val):
        self.check()
        return self._d[val]
    def __setitem__(self, key, value):
        self.check()
        self._d[key] = value
    def __delitem__(self, key): del self.file[key]










def filelines(f, fun=None):
    return File(f).readlines(fun)
def strippedlines(f, fun=None):
    lines = File(f).readlines().filtered(
        notblank
    )
    if fun is None:
        fun = str.strip
    else:
        fun = lambda x: fun(str.strip(x))
    return arrmap(fun, lines)
def pwdf(): return Folder(pwd())


def write_webloc(file, url):
    File(file).write(f'''
    <?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>URL</key>
	<string>{url}</string>
</dict>
</plist>
''')


# @dataclass
# class HDF5(ImmutableMapping):

# def __getitem__(self, k: _KT) -> _VT_co:
#     pass
