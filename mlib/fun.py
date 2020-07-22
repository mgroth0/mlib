from mlib.term import Progress
def functionalize(f):
    def ff(): return f
    return ff



def do_twice(func):
    def wrapper_do_twice(*args, **kwargs):
        func(*args, **kwargs)
        func(*args, **kwargs)
    return wrapper_do_twice


def track_progress(f):
    def runAndTrackProgress(iterable):
        with Progress(len(iterable)) as p:
            for item in iterable:
                y = f(item)
                p.tick()
                yield y
    return runAndTrackProgress
