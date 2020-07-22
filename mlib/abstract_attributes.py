from abc import abstractmethod, ABC, ABCMeta
from dataclasses import dataclass, asdict

from mlib.boot.mlog import err
from mlib.boot.stream import listitems

@dataclass
class STATIC_ATTS: pass

class Abstract:
    def __init__(self, mytype=None):
        self.mytype = mytype  # mytype doesnt do anything.
#         in the future I could check superclass attributes and if it is abstract, ensure the subclass att value is this type

class _AbstractAttributesMeta(ABCMeta):
    def __new__(mcs, name, bases, attrs):
        cls = super().__new__(mcs, name, bases, attrs)
        def replacement():
            raise NotImplementedError
        # for k, v in listitems(asdict(cls.STATIC)):
        #     cls.__setattr__(k, v)
        for k, v in listitems(cls.__dict__):
            if isinstance(v, Abstract):
                setattr(cls, k, property(replacement))
                if ABC not in bases:
                    err('bad')
        if ABC not in bases:
            cls.__meta_post_init__()
        return cls

    def __meta_post_init__(self):
        pass



class AbstractAttributes(ABC, metaclass=_AbstractAttributesMeta): pass
# @classmethod
# def __meta_post_init__(cls):
#     pass
# ACTUALLY USED AS A PROPERTY
# @staticmethod
# @abstractmethod
# def STATIC(cls) -> STATIC_ATTS: pass
