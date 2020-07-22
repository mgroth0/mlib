import asyncio
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
import threading

from mlib.boot import log
from mlib.fun import track_progress
AIO_LOOP = asyncio.new_event_loop()
asyncio.set_event_loop(AIO_LOOP)

# noinspection PyUnusedLocal
def testInPools(f, li, af,
                test_multiprocess=True,
                test_threadpool=True,
                test_async=True
                ):
    # TODO: make this a decorator?

    t1 = log('Starting No Pool Test')
    f = track_progress(f)
    r = list(f(li))
    t2 = log('\tFinished No Pool Test')
    log(f'\t\ttotal time: {t2 - t1}s')

    if test_multiprocess:
        t1 = log('Starting CPU Pool Test')
        with Pool() as p:
            r = p.map(f, li)
        t2 = log('\tFinished CPU Pool Test')
        log(f'\t\ttotal time: {t2 - t1}s')

    if test_threadpool:
        t1 = log('Starting Thread Pool Test')
        with ThreadPool() as p:
            r = p.map(f, li)
        t2 = log('\tFinished Thread Pool Test')
        log(f'\t\ttotal time: {t2 - t1}s')

    # if test_async:
    #     from asyncio_pool import AioPool
    #     t1 = log('Starting AIO Pool Test')
    #     pool = AioPool()
    #     coro = pool.map(af, li)
    #     fut = asyncio.gather(coro)
    #     r = asyncio.get_event_loop().run_until_complete(fut)
    #     t2 = log('\tFinished AIO Pool Test')
    #     log(f'\t\total time: {t2 - t1}s')

    # TODO: add Wolfram concurrency
    # TODO: add GPU parallelism
    # TODO: add Java Multithreading? (no GIL)





def run_in_daemon(target):
    threading.Thread(target=target, daemon=True).start()

def run_in_thread(target, **kwargs):
    t = threading.Thread(target=target, **kwargs)
    t.start()
    return t
