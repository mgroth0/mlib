from abc import ABC, abstractmethod
import os
from queue import Queue, Empty
from subprocess import Popen, PIPE, STDOUT
import sys
from typing import Union

import pexpect
from pexpect import TIMEOUT

from mlib.boot.bootutil import isinstsafe, cn
from mlib.boot.mlog import log
from mlib.boot.mutil import is_non_str_itr, utf_decode, isempty, isstr
from mlib.boot.stream import listmap


class AbstractShell(ABC):
    @staticmethod
    def com_arg(a):
        if isinstsafe(a, os.PathLike):
            return a.__fspath__()
        else:
            return str(a)

    @staticmethod
    def command_list(*args):
        if len(args) == 0:
            return ['']
        elif len(args) > 1:
            return list(map(AbstractShell.com_arg, args))
        elif is_non_str_itr(args[0]):
            return list(map(AbstractShell.com_arg, args[0]))
        elif isstr(args[0]):
            return listmap(AbstractShell.com_arg, args[0].split(' '))
        else:
            return [AbstractShell.com_arg(args[0])]

    @staticmethod
    def command_str(*args): return ' '.join(AbstractShell.command_list(*args))

    def __init__(
            self,
            *command,
            silent=False
    ):
        self.command_as_str = shell.command_str(*command)
        self.command_as_list = shell.command_list(*command)
        if not silent:
            log(f'$: {self.command_as_str}')
        self.p = self._start()

    def __str__(self):
        return f'{cn(self)}{self.command_as_list}'

    @abstractmethod
    def _start(self) -> Union[pexpect.spawn, Popen]: pass
    @abstractmethod
    def wait(self): pass
    @abstractmethod
    def all_output(self): pass
    @abstractmethod
    def readlines(self): pass
    @abstractmethod
    def readline(self): pass
    @abstractmethod
    def readline_nonblocking(self, timeout=-1): pass
    @abstractmethod
    def interact(self): pass
    @abstractmethod
    def expect(self, *args): pass
    @abstractmethod
    def sendline(self, s): pass
    def bash(self, s):
        return self.sendline(f'/bin/bash -c """{shell.command_str(s)}"""')
    @abstractmethod
    def alive(self): pass
    @abstractmethod
    def close(self): pass



class ExpectShell(AbstractShell):
    def __init__(
            self,
            *command,
            silent=False,
            timeout=None,
            logfile_read=None
    ):
        super().__init__(*command, silent=silent)
        self.p.timeout = timeout
        self.p.logfile_read = logfile_read
    def _start(self):
        return pexpect.spawn(self.command_as_str, timeout=None)
    def wait(self): return self.p.wait()
    def all_output(self):
        return '\n'.join(listmap(utf_decode, self.readlines()))
    def readlines(self): return self.p.readlines()
    def readline(self): return self.p.readline()
    def readline_nonblocking(self, timeout=-1):
        line = ''
        while True:
            try:
                c = utf_decode(self.p.read_nonblocking(size=1, timeout=timeout))
                if c == '\n': return line
                else: line += c
            except TIMEOUT: return None
    def interact(self): return self.p.interact()
    def expect(self, *args): return self.p.expect(*args)
    def sendline(self, s): return self.p.sendline(s)

    def alive(self): return self.p.isalive()
    def log_to_stdout(self, fun=None, o=None):
        class MyBuffer:
            def __init__(self, funn, oo):
                self.file = sys.stdout.buffer
                self.fun = funn
                self.o = oo
            def write(self, data):
                if self.fun is not None:
                    self.fun(data, self.o)
                return self.file.write(data)
            def flush(self):
                self.file.flush()
        self.p.logfile_read = MyBuffer(fun, o)
    def close(self):
        return self.p.close()


class SPShell(AbstractShell):
    def _start(self):
        return Popen(self.command_as_list, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    def wait(self):
        return self.p.wait()
    def all_output(self):
        return '\n'.join(self.readlines())
    def readlines(self):
        (stdout, _) = self.p.communicate()
        stdout = utf_decode(stdout)
        return stdout.split('\n')
    def readline(self):
        return utf_decode(self.p.stdout.readline())
    def readline_nonblocking(self, timeout=-1):
        def enqueue_output(out, queue):
            queue.put(out.readline())
        q = Queue()
        from multiprocessing import Process
        t = Process(target=enqueue_output, args=(self.p.stdout, q), daemon=True)
        t.start()
        try:
            line = q.get(timeout=timeout)
        except Empty:
            t.terminate()
            return None
        else:
            return line

    def interact(self):
        raise NotImplementedError
    def expect(self, *args):
        raise NotImplementedError
    def sendline(self, s):
        self.p.stdin.write(s)
    def alive(self):
        return self.p.poll() is None
    def close(self):
        self.p.kill()  # same as terminate
    def print_and_raise_if_err(self):
        lines = self.readlines()
        for line in lines:
            log(f'{self}: {line}')
        if self.p.returncode != 0:
            raise Exception(f'return code not 0: {self.p.returncode}')
    def readlines_and_raise_if_err(self):
        lines = self.readlines()
        if self.p.returncode != 0:
            raise Exception(f'return code not 0: {self.p.returncode}')
        return lines

spshell = SPShell


class SSHExpectProcess(ExpectShell):
    def login(self):
        self.p.expect('passphrase')
        self.sendpass()
    def sendpass(self):
        with open('/Users/matt/.pass', 'r') as f:
            self.p.sendline(f.read()[::-1])
class InteractiveExpectShell(ExpectShell):


    def __init__(self, *command, **kwargs):
        if isempty(command):
            command = ['bash']
        super().__init__(*command, **kwargs)


    def __getattr__(self, item):
        def f(*args):
            # problem = shell.command_str(*args)
            # print(f'{problem=}')
            return self.sendline(f'{item} {shell.command_str(*args)}'.strip())
        return f

shell = ExpectShell
ishell = InteractiveExpectShell
