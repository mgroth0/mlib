import atexit

from mlib.boot import log
from mlib.boot.dicts import ProxyDictRoot, RecursiveSubDictProxy
from mlib.boot.lang import isdictsafe, enum, listkeys
from mlib.boot.mlog import warn, err
from mlib.file import File, write_webloc
from mlib.term import log_invokation

class Database(ProxyDictRoot):
    offline_mode = False

    @log_invokation()
    def __init__(self, file, just_sync_at_end=True):
        file = File(file, quiet=True)
        file.backup()
        super().__init__(file)
        self.file = self._d
        assert file.ext == 'json'
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

        self.just_sync_at_end = just_sync_at_end
        if just_sync_at_end:
            atexit.register(self.push)
        file.backup()

    def _hard_reset(self):
        self.file.save({})

    def __setitem__(self, key, value):
        self._d.__setitem__(key, value)
        if not self.just_sync_at_end:
            self.push()

    def __delitem__(self, key):
        self._d.__delitem__(key)
        if not self.just_sync_at_end:
            self.push()

    def __getitem__(self, k):
        if not self.just_sync_at_end:
            self.pull()
        r = self._d.__getitem__(k)
        if isdictsafe(r):
            r = RecursiveSubDictProxy(self, k)
        return r

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
