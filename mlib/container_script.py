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
        {self.bashscript_str}
        echo {self.FINISH_STR}
        '''
        self.file = File(self.name, w=txt)
