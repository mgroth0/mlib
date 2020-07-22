from abc import ABC
from collections import MutableMapping
from dataclasses import dataclass
from typing import Union

from mlib.boot.lang import isinstsafe, isdictsafe, isstr
from mlib.boot.mlog import err


class DefaultMutableMapping(MutableMapping, ABC):
    def __init__(self, d): self._d = d
    def __iter__(self): return self._d.__iter__()
    def __len__(self): return self._d.__len__()
class ProxyDictRoot(DefaultMutableMapping, ABC):
    def get_without_proxying(self, k):
        return self._d[k]
class PermaDict(DefaultMutableMapping):
    def __init__(self, file):
        from mlib.file import File
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

@dataclass
class SubDictProxy(MutableMapping):
    root_dict: Union[ProxyDictRoot, dict, PermaDict]
    key: str

    def __post_init__(self):
        self._pull()
    def _pull(self):
        if isinstsafe(self.root_dict, ProxyDictRoot):
            self._sub_dict = self.root_dict.get_without_proxying(self.key)
        else:
            self._sub_dict = self.root_dict[self.key]
    def _push(self):
        self.root_dict[self.key] = self._sub_dict
    def __setitem__(self, k, v):
        self._pull()
        r = self._sub_dict.__setitem__(k, v)
        self._push()
        return r
    def __delitem__(self, k):
        self._pull()
        r = self._sub_dict.__delitem__(k)
        self._push()
        return r
    def __getitem__(self, k):
        self._pull()
        return self._sub_dict.__getitem__(k)
    def __len__(self):
        self._pull()
        return len(self._sub_dict)
    def __iter__(self):
        self._pull()
        return self._sub_dict.__iter__()
class RecursiveSubDictProxy(SubDictProxy, ProxyDictRoot):
    def __getitem__(self, k):
        r = super().__getitem__(k)
        if isdictsafe(r):
            r = RecursiveSubDictProxy(self, k)
        return r

class ImmutableMapping(DefaultMutableMapping, ABC):
    def __setitem__(self, key, value): raise Exception('cfg is immutable')
    def __delitem__(self, key): raise Exception('cfg is immutable')

class DefaultImmutableMapping(ImmutableMapping):
    def __getitem__(self, val): return self._d[val]


class CaseInsensitiveDict(dict):
    @classmethod
    def _k(cls, key):
        assert isstr(key)
        return key.lower()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._convert_keys()
    def __getitem__(self, key):
        return super().__getitem__(self.__class__._k(key))
    def __setitem__(self, key, value):
        super().__setitem__(self.__class__._k(key), value)
    def __delitem__(self, key):
        return super().__delitem__(self.__class__._k(key))
    def __contains__(self, key):
        return super().__contains__(self.__class__._k(key))
    def has_key(self, key):
        return super().has_key(self.__class__._k(key))
    def pop(self, key, *args, **kwargs):
        return super().pop(self.__class__._k(key), *args, **kwargs)
    def get(self, key, *args, **kwargs):
        return super().get(self.__class__._k(key), *args, **kwargs)
    def setdefault(self, key, *args, **kwargs):
        return super().setdefault(self.__class__._k(key), *args, **kwargs)
    def update(self, E=None, **F):
        if E is None:
            E = {}
        super().update(self.__class__(E))
        super().update(self.__class__(**F))
    def _convert_keys(self):
        for k in list(self.keys()):
            v = super().pop(k)
            self.__setitem__(k, v)
