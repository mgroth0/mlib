from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from mlib.boot import log
from mlib.container_script import ContainerBashScript
from mlib.file import pwdf
from mlib.term import log_invokation

@dataclass
class Host(ABC):
    home: str
    def __post_init__(self):
        self.n = None
    def ssh(self, command=None):
        p = self.ssh_login()
        p.setprompt()
        p.sendatprompt(f'cd {self.home}')
        if command is not None:
            p.sendatprompt(command)
        return p
    @abstractmethod
    def ssh_login(self): pass

    @abstractmethod
    def send(self, *files, project_name): pass

    @abstractmethod
    def startup(self): pass
    @abstractmethod
    def shutdown(self): pass
    def init_njobs(self, n):
        if n > 0:
            self.startup()
        self.n = n
    def tick_job_finish(self):
        self.n -= 1
        assert self.n >= 0
        if self.n == 0:
            self.shutdown()


class HostProject(ABC):

    def __init__(self, host: Host, name: str = None):
        self.host = host
        if name is None:
            name = pwdf().name
        self.name = name

    def send(self, *files):
        if len(files) > 0:
            self.host.send(*files, project_name=self.name)

    def get(self, *files):
        if len(files) > 0:
            self.host.get(*files, project_name=self.name)

    def rm(self, *names):
        self.ssh_commands(*[f'rm {name}' for name in names])

    def ssh_commands(self, *lines):
        p = self.ssh()
        for line in lines:
            p.sendatprompt(line)
        p.prompt()
        p.close()

    def ssh(self, command=None):
        p = self.host.ssh()
        p.sendatprompt(f'mkdir {self.name}')
        p.sendatprompt(f'cd {self.name}')
        if command is not None:
            p.sendatprompt(command)
        return p

    def pre_run(self, SW, p,srun: Optional[str]): pass

    @log_invokation
    def run(self, SW,srun: Optional[str]):
        RUN_IN_VAGRANT = False
        from mlib.open_mind import OpenMindBashScript  # should really make a super class
        SW: OpenMindBashScript
        p = self.ssh()
        self.pre_run(SW, p,srun)
        # p.sendatprompt(f'sudo bash {SW.name}')
        from mlib.open_mind import OpenMindProject

        if isinstance(self, OpenMindProject):
            if RUN_IN_VAGRANT:
                log('upping')
                p.sendatprompt('vagrant up')
                log('sshing')
                p.sendatprompt('vagrant ssh')
                log('setting prompt')
                p.setprompt()
                log('cding')
                # p.prompt()  # an extra prompt expect like in the build process i think
                p.sendatprompt('cd ../dnn')
        log('bashing')
        p.sendatprompt(
            f'bash {SW.name}')  # why was I using sudo??? ohhhh I might have been using sudo in order to have write access to files? yes!! I was suing sudo because that is the only way files are writable!
        log('returning')
        return p


    def finish_process(self, p, SW):
        if SW.interact:
            p.interact()
        else:
            p.pipe_and_close_on(ContainerBashScript.FINISH_STR, close_fun=lambda p: p.sendline('exit'))
        self.host.tick_job_finish()
