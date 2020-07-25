from dataclasses import dataclass
import sys
from typing import List

from mlib.container_script import ContainerBashScript
from mlib.remote_host import RemoteHost, RemoteProject
from mlib.singularity import Singularity
from mlib.vagrant import VagrantMachine



@dataclass
class OpenMindBashScript(ContainerBashScript):
    interact: bool
    modules: List[str] = None


class OpenMind(RemoteHost):
    def __init__(self):
        super().__init__(
            hostname='mjgroth@polestar.mit.edu',
            home='/om5/user/mjgroth'
        )
OM = OpenMind()

class OpenMindProject(RemoteProject):
    def __init__(self, name=None):
        super().__init__(OM, name)

    def swrap_script(
            self,
            S: Singularity,
            command=None,
            interact=False,
            bind=False,
            writable=False,
            overlay=False

    ) -> OpenMindBashScript:
        if bind is False:
            bind = None
        else:
            bind = self.path
        if command is None:
            command = S.run_command(bind=bind, writable=writable, overlay=overlay)
        else:
            command = S.exec_command(command, bind=bind, writable=writable, overlay=overlay)
        return OpenMindBashScript(
            f'{self.name}.simgw',
            command,
            modules=['openmind/singularity'],
            interact=interact
        )

    def pre_run(self, SW: OpenMindBashScript, p):
        [p.sendatprompt(f'module load {m}') for m in SW.modules]
        IN_POLESTAR = True
        if not IN_POLESTAR:
            p.sendatprompt('srun -n 1 --mem=10G -t 60 --pty bash')


class OpenMindVagrantMachine(VagrantMachine):
    # because between shells these up'ed machines dont even persits. I up it more manually in the ssh_login override
    def halt(self, force=False): pass
    def up(self): pass

    def __init__(self, keep_up, restart, rebuild, omp: OpenMindProject):
        super().__init__(keep_up, restart, rebuild)
        self.omp = omp

    # vagrant ssh -- -t "{command}"
    def ssh_login(self):
        p = self.omp.ssh()
        # https://github.mit.edu/MGHPCC/OpenMind/wiki/How-to-use-Vagrant-to-build-a-Singularity-image%3F
        p.sendatprompt('srun -n 1 --mem=10G -t 60 --pty bash')
        p.setprompt()
        p.sendatprompt('vagrant up')
        p.sendatprompt('vagrant ssh')
        p.setprompt()
        return p

    def send(self, *files, project_name):
        raise NotImplementedError


    def _eshell(self, command):
        assert command is not None
        p = self.omp.ssh()
        # breakpoint()
        p.log_to_stdout()
        # https://github.mit.edu/MGHPCC/OpenMind/wiki/How-to-use-Vagrant-to-build-a-Singularity-image%3F
        p.sendatprompt('srun -n 1 --mem=10G -t 60 --pty bash')
        p.setprompt()
        p.sendatprompt(command)

        p.sendatprompt('exit')
        p.sendatprompt('exit')
        p.close()

    def _shell_output(self, command):
        assert command is not None
        p = self.omp.ssh()
        # breakpoint()


        class MyBuffer:
            def __init__(self):
                self.output = ''
            def write(self, data):
                self.output += data
            def flush(self):
                pass
        buf = MyBuffer()
        p.logfile_read = buf

        # p.log_to_stdout()
        # https://github.mit.edu/MGHPCC/OpenMind/wiki/How-to-use-Vagrant-to-build-a-Singularity-image%3F
        p.sendatprompt('srun -n 1 --mem=10G -t 60 --pty bash')
        p.setprompt()
        p.sendatprompt(command)
        p.sendatprompt('exit')
        p.sendatprompt('exit')
        p.close()
        return buf.output

    def myinit(self, box='singularityware/singularity-2.4', syncdir=True):
        raise NotImplementedError
