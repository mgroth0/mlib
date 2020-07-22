from dataclasses import dataclass
from typing import List

from mlib.container_script import ContainerBashScript
from mlib.remote_host import RemoteHost, RemoteProject
from mlib.singularity import Singularity


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
            writable=False

    ) -> OpenMindBashScript:
        if bind is False:
            bind = None
        else:
            bind = self.path
        if command is None:
            command = S.run_command(bind=bind, writable=writable)
        else:
            command = S.exec_command(command, bind=bind, writable=writable)
        return OpenMindBashScript(
            f'{self.name}.simgw',
            command,
            modules=['openmind/singularity'],
            interact=interact
        )

    def pre_run(self, SW: OpenMindBashScript, p):
        [p.sendatprompt(f'module load {m}') for m in SW.modules]