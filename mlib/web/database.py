import atexit

from mlib.boot import log
from mlib.boot.dicts import ProxyDictRoot, RecursiveSubDictProxy, RecursiveSubListProxy, ProxyListRoot, ObjProxy
from mlib.boot.lang import isdictsafe, enum, listkeys, is_non_str_itr
from mlib.boot.mlog import warn, err
from mlib.file import File, write_webloc
from mlib.term import log_invokation


class OfflineDatabaseList(ProxyListRoot):
    @log_invokation
    def __init__(self, file, makeObjs=False):
        self.makeObjs = makeObjs
        file = File(file, quiet=True)
        file.backup()
        file.allow_autoload = True
        super().__init__(file)
        self.__dict__['file'] = self._l
        assert file.ext == 'json'
        file.backup()
    def __setitem__(self, key, value):
        self._l.__setitem__(key, value)

    def __delitem__(self, key):
        self._l.__delitem__(key)

    def __getitem__(self, k):
        r = self._l.__getitem__(k)
        if isdictsafe(r):
            r = RecursiveSubDictProxy(self, k, self.makeObjs)
            if self.makeObjs: r = ObjProxy(r)
        elif is_non_str_itr(r):
            r = RecursiveSubListProxy(self, k, self.makeObjs)
            if self.makeObjs: r = ObjProxy(r)
        return r

class OfflineDatabase(ProxyDictRoot):
    @log_invokation()
    def __init__(self, file,makeObjs = False):
        self.makeObjs = makeObjs
        file = File(file, quiet=True)
        file.backup()
        file.allow_autoload = True
        super().__init__(file)
        self.__dict__['file'] = self._d
        assert file.ext == 'json'
        file.backup()
    def __setitem__(self, key, value):
        self._d.__setitem__(key, value)

    def __delitem__(self, key):
        self._d.__delitem__(key)

    def __getitem__(self, k):
        r = self._d.__getitem__(k)
        if isdictsafe(r):
            r = RecursiveSubDictProxy(self, k, self.makeObjs)
            if self.makeObjs: r = ObjProxy(r)
        elif is_non_str_itr(r):
            r = RecursiveSubListProxy(self, k, self.makeObjs)
            if self.makeObjs: r = ObjProxy(r)
        return r


class Database(OfflineDatabase):
    offline_mode = False

    @log_invokation()
    def __init__(self, file, just_sync_at_end=True):
        self.__dict__['just_sync_at_end'] = just_sync_at_end
        super().__init__(file)
        if not self.offline_mode:
            if file.wc.exists:
                self.pull()
            else:
                if not file.exists:
                    self._hard_reset()
                self.push()
        else:
            warn(f'{self} is not preforming initial sync since {self.offline_mode=}')

        write_webloc(file.abspath.replace('.json', '.webloc'), file.wcurl)

        log(f'database url: {file.wcurl=}')

        if just_sync_at_end:
            atexit.register(self.push)

    def _hard_reset(self):
        self.file.save({})

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if not self.just_sync_at_end:
            self.push()

    def __delitem__(self, key):
        super().__delitem__(key)
        if not self.just_sync_at_end:
            self.push()

    def __getitem__(self, k):
        if not self.just_sync_at_end:
            self.pull()
        return super().__getitem__(k)

    def get_or_set_default(self, default, *keys):
        current_v = self
        for i, k in enum(keys):
            islast = i == len(keys) - 1
            if k in listkeys(current_v):
                current_v = current_v[k]
            elif islast:
                current_v[k] = default
                if not self.just_sync_at_end:
                    self.push()
                return default
            else:
                err(f'need to set root default first: {k}')

        return current_v

    def pull(self):
        if not self.offline_mode:
            self.file.wc.pull()
        else:
            warn(f'not pulling {self} because offline mode is switched one')
    def push(self):
        if not self.offline_mode:
            self.file.wc.push()
        else:
            warn(f'not pushing {self} because offline mode is switched one')
