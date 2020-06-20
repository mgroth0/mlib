from mlib.boot import mutil

mutil.mparray.__iadd__ = mutil.append

class ArrayOf:
    def __init__(self,arr):
        self.arr = arr

    def __getattr__(self, name):

        return mutil.arrayfun(lambda x: eval('x.' + name) ,self.arr)

        # if some_predicate(name):
        # # ...
        # else:
        #     # Default behaviour
        #     raise AttributeError

def _arrayofFun(arr):
    return ArrayOf(arr)

mutil.mparray.arrayof = _arrayofFun
mutil.mparray.flatn = mutil.flatn