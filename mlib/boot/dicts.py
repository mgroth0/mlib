from abc import ABC
from collections import MutableMapping
from dataclasses import dataclass
from typing import Union

from mlib.boot.bootutil import isdictsafe, isinstsafe

class DefaultMutableMapping(MutableMapping, ABC):
    def __init__(self, d): self._d = d
    def __iter__(self): return self._d.__iter__()
    def __len__(self): return self._d.__len__()
class ProxyDictRoot(DefaultMutableMapping, ABC):
    def get_without_proxying(self, k):
        return self._d[k]

@dataclass
class SubDictProxy(MutableMapping):
    root_dict: Union[ProxyDictRoot, dict]
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
