from abc import ABC

from mlib.obj import SuperRunner

class ContainerProject(SuperRunner, ABC):
    def super_run(self):
        self.run({})
