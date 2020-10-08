from abc import ABC, abstractmethod
from collections import MutableMapping, MutableSequence
from dataclasses import dataclass
from typing import Union, Any

from mlib.boot.lang import isinstsafe, isdictsafe, isstr, is_non_str_itr, listkeys
from mlib.boot.mlog import err
from mlib.boot.stream import listitems


class DefaultMutableList(MutableSequence, ABC):

    def __init__(self, l):
        self.__dict__['_l'] = l

    def insert(self, index: int, o) -> None:
        return self._l.insert(index, o)


    @abstractmethod
    def __getitem__(self, i):
        return self._l.__getitem__(i)
    @abstractmethod
    def __setitem__(self, i, o):
        return self._l.__setitem__(i, o)
    @abstractmethod
    def __delitem__(self, i):
        return self._l.__delitem__(i)
    def __len__(self):
        return self._l.__len__()

class DefaultMutableMapping(MutableMapping, ABC):
    def __init__(self, d): self.__dict__['_d'] = d
    def __iter__(self): return self._d.__iter__()
    def __len__(self): return self._d.__len__()


class ProxyListRoot(DefaultMutableList, ABC):
    def non_proxy_snapshot(self):
        rrr = []
        for i in range(len(self)):
            rrr.append(self.get_without_proxying(i))
        return rrr

    def get_without_proxying(self, k):
        return self._l[k]

class ProxyDictRoot(DefaultMutableMapping, ABC):
    def non_proxy_snapshot(self):
        rrr = {}
        for k in listkeys(self):
            rrr[k] = self.get_without_proxying(k)
        return rrr
    def get_without_proxying(self, k):
        return self._d[k]


class PermaList(DefaultMutableList):
    def __init__(self, file):
        from mlib.file import File
        self.file = File(file)
        self.file.allow_autoload = True
        super().__init__(self.file)
        if not self.file.exists:
            self.file.save([])
        self.file.default_quiet = True
    def __getitem__(self, val):
        return self._l[val]
    def __setitem__(self, key, value):
        self._l[key] = value
    def __delitem__(self, key): del self.file[key]

class PermaDict(DefaultMutableMapping):
    def __init__(self, file):
        from mlib.file import File
        self.file = File(file)
        self.file.allow_autoload = True
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


class SubListProxy(MutableSequence):

    def __init__(self, root_list: Union[ProxyListRoot, list, PermaList], index: Union[int, slice], makeObjs):
        self.root_list = root_list
        self.index = index
        self.makeObjs = makeObjs

    def get_without_proxying(self, k):
        return self.root_list.get_without_proxying(self.index)[k]

    def _pull(self):
        if isinstsafe(self.root_list, ProxyDictRoot) or isinstsafe(self.root_list, ProxyListRoot):
            self._sub_dict = self.root_list.get_without_proxying(self.index)
        else:
            self._sub_dict = self.root_list[self.index]
    def _push(self):
        self.root_list[self.index] = self._sub_dict
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


class SubDictProxy(MutableMapping):

    def __init__(self, root_dict: Union[ProxyDictRoot, dict, PermaDict], key: str, makeObjs: bool):
        self.root_dict = root_dict
        self.key = key
        self.makeObjs = makeObjs


    def get_without_proxying(self, k):
        return self.root_dict.get_without_proxying(self.key)[k]

    def __post_init__(self):
        self._pull()
    def _pull(self):
        if isinstsafe(self.root_dict, ProxyDictRoot) or isinstsafe(self.root_dict, ProxyListRoot):
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

class RecursiveSubListProxy(SubListProxy, ProxyListRoot):
    def __getitem__(self, k):
        r = super().__getitem__(k)
        if isdictsafe(r):
            r = RecursiveSubDictProxy(self, k, self.makeObjs)
            if self.makeObjs: r = ObjProxy(r)
        elif is_non_str_itr(r):
            r = RecursiveSubListProxy(self, k, self.makeObjs)
            if self.makeObjs: r = ObjProxy(r)
        return r

class RecursiveSubDictProxy(SubDictProxy, ProxyDictRoot):
    def __getitem__(self, k):
        r = super().__getitem__(k)
        if isdictsafe(r):
            r = RecursiveSubDictProxy(self, k, self.makeObjs)
            if self.makeObjs: r = ObjProxy(r)
        elif is_non_str_itr(r):
            r = RecursiveSubListProxy(self, k, self.makeObjs)
            if self.makeObjs: r = ObjProxy(r)
        return r


class ObjProxy:
    def __init__(self, o):
        self.__dict__['_o'] = o

    # def __array_struct__(self):
    #     return self._o.__array_struct__()

    def __len__(self):
        return self._o.__len__()

    def __iter__(self):
        return self._o.__iter__()

    def __getitem__(self, key):
        return self._o.__getitem__(key)
    def __setitem__(self, key, value):
        return self._o.__setitem__(key, value)

    def __getattr__(self, item):
        if item != "_o":
            return self._o.__getitem__(item)
        else:
            return self.__getattribute__(item)
    def __setattr__(self, key, value):
        # if isinstance(self,MutableMapping) and key in list(self._d.keys()):
        #     self.__setitem__(key, value)
        # else:
        self._o.__setitem__(key, value)
    # def __getitem__(self, k):
    #     if not self.just_sync_at_end:
    #         self.pull()
    #     r = self._d.__getitem__(k)
    #     if isdictsafe(r):
    #         r = RecursiveSubDictProxy(self, k)
    #     elif is_non_str_itr(r):
    #         r = RecursiveSubListProxy(self, k)
    #     return r




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

def set_defaults(d, **kwargs):
    for k, v in listitems(kwargs):
        if k not in d:
            d[k] = v
