from abc import ABC
from dataclasses import dataclass
import os

from mlib.host import Host, HostProject
from mlib.shell import scp, ssh



@dataclass
class RemoteHost(Host):
    hostname: str
    use_longpass: bool = True

    def ssh_login(self):
        p = ssh(f'-t {self.hostname}')
        p.login(longpass=True)
        p.expect('Last login')
        return p

    def send(self, *files, project_name):
        files = ' '.join([f.abspath for f in files])

        # this with comma sep is some terminal magic that doesn't work through python
        # fromm = '{' + files + '}'
        p = scp(f'{files} {self.hostname}:{self.home}/{project_name}')
        p.login(longpass=self.use_longpass)
        p.interact()

    def get(self, *files, project_name):
        for f in files:
            p = scp(f'-r {self.hostname}:{self.home}/{project_name}/{f} .')
            p.login(longpass=self.use_longpass)
            p.interact()

    def startup(self): pass
    def shutdown(self): pass



class RemoteProject(HostProject, ABC):

    def __init__(self, host: RemoteHost, name: str = None):
        super().__init__(host, name)
        self.path = os.path.join(host.hostname, self.name)
