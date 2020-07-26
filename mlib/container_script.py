from dataclasses import dataclass
from typing import ClassVar

from mlib.file import File
@dataclass
class ContainerBashScript:
    FINISH_STR: ClassVar[str] = '__DNN_IS_FINISHED__'
    name: str
    bashscript_str: str
    def __post_init__(self):
        txt = f'''
        # mkdir /om5/user/mjgroth/dnn/docs_local
        cd /om5/user/mjgroth/dnn
        git pull
        cd /om5/user/mjgroth/mlib
        git pull
        cd /om5/user/mjgroth/dnn
        {self.bashscript_str}
        echo {self.FINISH_STR}
        '''
        self.file = File(self.name, w=txt)
