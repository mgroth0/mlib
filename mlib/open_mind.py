from dataclasses import dataclass
import sys
from typing import List, Optional

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
            run_args=None,
            interact=False,
            bind=False,
            writable=False,
            overlay=False

    ) -> OpenMindBashScript:
        assert run_args is not None
        if bind is False:
            bind = None
        # else:
        #     bind = self.path
        if command is None:
            command = S.run_command(run_args=run_args, bind=bind, writable=writable, overlay=overlay)
            if interact:
                command += ' --INTERACT=1'
        else:
            command = S.exec_command(command, run_args=run_args, bind=bind, writable=writable, overlay=overlay)
        return OpenMindBashScript(
            f'{self.name}.simgw',
            command,
            modules=['openmind/singularity'],
            interact=interact
        )

    def pre_run(self, SW: OpenMindBashScript, p, srun: Optional[str]):
        [p.sendatprompt(f'module load {m}') for m in SW.modules]
        # IN_POLESTAR = True
        # if not IN_POLESTAR:
        if srun is not None:
            p.sendatprompt(srun)
            p.setprompt()


class OpenMindVagrantMachine(VagrantMachine):
    # because between shells these up'ed machines dont even persits. I up it more manually in the ssh_login override
    def halt(self, force=False): pass
    def up(self): pass

    def __init__(self, keep_up, restart, rebuild, omp: OpenMindProject, srun: Optional[str]):
        super().__init__(keep_up, restart, rebuild)
        self.omp = omp
        self.srun = srun

    # vagrant ssh -- -t "{command}"
    def ssh_login(self):
        p = self.omp.ssh()
        # https://github.mit.edu/MGHPCC/OpenMind/wiki/How-to-use-Vagrant-to-build-a-Singularity-image%3F
        if self.srun:
            p.sendatprompt(self.srun)
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
        p.log_to_stdout()
        # https://github.mit.edu/MGHPCC/OpenMind/wiki/How-to-use-Vagrant-to-build-a-Singularity-image%3F
        if self.srun:
            p.sendatprompt(self.srun)
            p.setprompt()
        p.sendatprompt(command)

        p.sendatprompt('exit')
        if self.srun: p.sendatprompt('exit')
        p.close()

    def _shell_output(self, command):
        assert command is not None
        p = self.omp.ssh()


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
        if self.srun:
            p.sendatprompt(self.srun)
            p.setprompt()
        p.sendatprompt(command)
        p.sendatprompt('exit')
        if self.srun: p.sendatprompt('exit')
        p.close()
        return buf.output

    def myinit(self, box='singularityware/singularity-2.4', syncdir=True):
        raise NotImplementedError
