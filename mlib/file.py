import atexit
import json
import os
import pathlib
from pathlib import Path
import shutil
from typing import MutableMapping

import imageio
import numpy as np
from scipy.io import loadmat, savemat
import yaml

from mlib.boot import mlog, log
from mlib.boot.bootutil import pwd, ismac
from mlib.boot.mutil import isinstsafe, mypwd, err, isstr, mkdir, listmap, sort, arr, arrmap, notblank
from mlib.shell import ishell
class File(os.PathLike, MutableMapping):

    def __init__(self, abspath, remote=None, mker=False, w=None):
        if isinstsafe(abspath, File):
            self.isSSH = abspath.isSSH
            abspath = abspath.abspath
        elif not os.path.isabs(abspath):
            self.isSSH = 'test-3' in abspath
            abspath = os.path.join(mypwd(), abspath)
        else:
            self.isSSH = 'test-3' in abspath
        self.abspath = abspath
        self.relpath = os.path.relpath(abspath, os.getcwd())
        self.name = os.path.basename(abspath)
        _, dot_extension = os.path.splitext(abspath)
        self.ext = dot_extension.replace('.', '')
        self.name_pre_ext = self.name.split('.')[0]

        self.parentDir = os.path.abspath(os.path.join(abspath, os.pardir))
        if self.abspath != '/' and os.path.exists(self.parentDir):
            self.parentFile = File(self.parentDir)
        else:
            self.parentFile = None
        self.parentName = os.path.basename(self.parentDir)

        # this might change so they have to be functions
        # self.isfile = os.path.isfile(self.abspath)
        # self.isdir = os.path.isdir(self.abspath)

        self.mker = mker
        if mker:
            self.mkdirs()

        if w is not None:
            self.write(w)

        self.rel = os.path.relpath(abspath, pwd())

        self.default_quiet = None

    def __len__(self) -> int:
        return len(self.load())
    def __iter__(self):
        return iter(self.load())

    def rel_to(self, parent):
        parent = File(parent).abspath
        # com = os.path.commonprefix([parent, self.abspath])
        # assert com != '/'
        # return os.path.relpath(self.abspath, com)
        return os.path.relpath(self.abspath, parent)

    def url(self):
        return pathlib.Path(self.abspath).as_uri()

    def isfile(self):
        return os.path.isfile(self.abspath)

    def isdir(self):
        return os.path.isdir(self.abspath)

    def __fspath__(self):
        return self.abspath

    def __repr__(self):
        return '<mutil.File abspath=' + self.abspath + '>'

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

    def copy_into(self, dest):
        dest = Folder(dest)
        dest.mkdirs()
        return self.copy_to(dest[self.name])

    def copy_to(self, dest):
        dest = File(dest)
        dest.mkparents()
        if self.isfile():
            return File(shutil.copyfile(self, dest))
        else:
            return Folder(shutil.copytree(self, dest))

    def loado(self):
        return self.load(as_object=True)
    def load(self, as_object=False):
        if not self.default_quiet:
            log('Loading ' + self.abspath, ref=1)
        if self.ext == 'edf':
            import mne
            import HEP_lib
            return HEP_lib.MNE_Set_Wrapper(mne.io.read_raw_edf(self.abspath, preload=False))
        elif self.ext in ['yml', 'yaml']:
            return yaml.load(self.read(), Loader=yaml.FullLoader)
        elif self.ext == 'set':
            import HEP_lib
            return HEP_lib.MNE_Set_Wrapper(mne.io.read_raw_eeglab(self.abspath, preload=False))
        elif self.ext == 'json':
            j = json.loads(self.read())
            if as_object:
                import mlib.JsonSerializable as JsonSerializable
                return JsonSerializable.obj(j)
            else:
                return j
        elif self.ext == 'mat':
            return loadmat(self.abspath)
        else:
            err('loading does not yet support .' + self.ext + ' files')

    def save(self, data, silent=None):
        import mlib.JsonSerializable as JsonSerializable
        import mlib.FigData as FigData
        if isinstance(data, FigData.PlotOrSomething):
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
            err('saving does not yet support .' + self.ext + ' files')

    def clear(self):
        assert self.isdir()
        [f.delete() for f in self.listmfiles()]


    def deleteIfExists(self):
        if self.exists(): self.delete()
        return self

    def delete(self):
        # os.remove() removes a file.
        # os.rmdir() removes an empty directory.
        # shutil.rmtree() deletes a directory and all its contents.
        if self.isdir():
            if not self.listfiles():
                os.rmdir(self.abspath)
            else:
                shutil.rmtree(self.abspath)
        else:
            os.remove(self.abspath)

    def respath(self, nam):
        if not isstr(nam): nam = str(nam)
        path = self.resolve(nam).abspath
        if self.mker and not File(path).exists() and '.' not in nam:
            File(path).mkdir()
        return path

    def resolve(self, nam):
        resolved_is_file = '.' in nam
        if not isstr(nam): nam = str(nam)
        resolved = File(
            os.path.join(self.abspath, nam),
            mker=False if resolved_is_file else self.mker
        )
        if self.mker and not resolved.exists() and not resolved_is_file:
            resolved.mkdir()
        if resolved.exists() and resolved.isdir(): return Folder(resolved, mker=self.mker)
        return resolved

    def glob(self, g):
        import glob
        matches = glob.glob(self.abspath + '/' + g)
        return [File(m) for m in matches]

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
        assert File(new).isdir()
        shutil.move(self.abspath, File(new).abspath)

    def moveto(self, new):
        assert not File(new).isdir()
        shutil.move(self.abspath, File(new).abspath)

    def listmfiles(self):
        return listmap(File, self.listfiles())

    def listfiles(self):
        y = os.listdir(self.abspath)
        r = []
        for name in sort(y):
            r.append(os.path.abspath(os.path.join(self.abspath, name)))
        return r

    def __getattr__(self, item):
        if not self.exists() or self.isdir():
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
        assert (self.exists())
        data = self.load()
        if not self.default_quiet:
            log('deleting ' + str(key))
        del data[key]
        self.save(data)
        if not self.default_quiet:
            log('deleted ' + str(key))



    def __setitem__(self, key, value):
        if self.exists():
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

    def exists(self):
        return os.path.isfile(self.abspath) or os.path.isdir(self.abspath)

    def open(self):
        from mlib.km import openInSafari
        return openInSafari(self)

    def read(self):
        with open(self.abspath, 'r') as file:
            return file.read()
    def readlines(self, fun=None):
        lines = arr(self.read().split('\n'))
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
        basedir = os.path.dirname(self.abspath)
        if not os.path.exists(basedir):
            os.makedirs(basedir)
        if not os.path.isfile(self.abspath):
            open(self.abspath, 'a').close()
        with open(self.abspath, 'w') as file:
            if not isstr(s):
                s = str(s)
            return file.write(s)

    def deleteAllContents(self):
        if File(self.abspath).exists():
            for filename in os.listdir(self.abspath):
                file_path = os.path.join(self.abspath, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))

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
        return list(reversed(nams))
class Folder(File):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.exists():
            assert self.isdir()
    def __getitem__(self, item):
        assert self.isdir()
        return self.resolve(item)
    def __setitem__(self, key, value):
        assert self.isdir()
        raise NotImplementedError('need have class for FileData object (not File, but FileData...)')
    def __getattr__(self, item):
        # undo File's override. We don't want to load from Folders
        raise AttributeError
class Temp(File):
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.deleteIfExists()
class TempFolder(Temp, Folder): pass
def listfiles(f): return File(f).listfiles()
def filename(o):
    return File(o).name
def abspath(file, remote=None): return File(file, remote=remote).abspath
def load(file):
    return File(file).load()
def mkdirs(file):
    if File(file).isfile():
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
        self.mpath = mlib.file.abspath
        self.lpath = mlib.file.abspath
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
class PermaDict(MutableMapping):
    def __init__(self, file):
        self.file = File(file)
        if not self.file.exists():
            self.file.write('{}')
        self.file.default_quiet = True
    def check(self):
        if not self.file.rel.startswith('_'):
            err('PermaDicts should be private (start with _)')
        if GIT_DIR.exists() and (not GIT_IGNORE.exists() or '/_*' not in GIT_IGNORE.read()):
            err(f'{self.file} needs to be ignored')
        if not self.file.exists():
            self.file.write('{}')
    def __getitem__(self, val):
        self.check()
        return self.file[val]
    def __setitem__(self, key, value):
        self.check()
        self.file[key] = value
    def __delitem__(self, key): del self.file[key]
    def __iter__(self): return iter(self.file)
    def __len__(self): return len(self.file)
class Config(MutableMapping):
    def __init__(self, file):
        self.file = File(file)
        if not self.file.exists(): self.file.write('''
profiles:
  proto: &proto
    -placeholder1: null
  default:
      <<: *proto
configs:
  all: &all
    -placeholder2: null
  default:
        <<: *all
'''.strip())
        self.file.default_quiet = True
        self._data = self.file.load()
    def __getitem__(self, val):
        return self._data[val]
    def __setitem__(self, key, value):
        err('cfg is immutable')
    def __delitem__(self, key): err('cfg is immutable')
    def __iter__(self): return iter(self._data)
    def __len__(self): return len(self._data)
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
