import multiprocessing
import time
from multiprocessing import Process, Queue
import os
import asyncio
import database_io
import main
from pyppeteer import launch

PROCESS_N = None


def info():
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())


def loading_process(name, eq, oq, lock):
    info()
    a = main.AsyncGetHTML(entryQueue = eq, outputQueue = oq, lock = lock)
    a.start()


if __name__ == '__main__':
    t_s = time.time()
    info()
    db = database_io.DatabaseIO()
    all_url = db.get_all_web_obj()

    eq = Queue()
    oq = Queue()
    [eq.put(i) for i in all_url]
    lock = multiprocessing.Lock()

    if PROCESS_N is None:
        PROCESS_N = os.cpu_count()
    process = [Process(target = loading_process, args = (i, eq, oq, lock)) for i in range(PROCESS_N)]

    [p.start() for p in process]
    [p.join() for p in process]

    t_e = time.time()

    print("耗时 %s 秒" % (t_e - t_s))
