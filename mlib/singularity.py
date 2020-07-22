from mlib.boot import log
from mlib.file import File, Temp, pwdf
from mlib.host import HostProject
from mlib.shell import shell


class Singularity:
    def __init__(self, recipe_name, simg_name=None):
        if simg_name is None:
            simg_name = pwdf().name
        self.recipe = SingularityRecipe(recipe_name, simg=simg_name)
        self.simg = self.recipe.simg

    @staticmethod
    def command(*args, bind=None, writable=False):
        s = ['singularity']
        if writable:
            args = list(args)
            args.insert(1, '--writable')
        if bind is not None:
            s += ['-B', File(bind).abspath]
        s += args
        return ' '.join(s)

    def run_command(self, bind=None, writable=False):
        return self.command('run', self.simg.name, bind=bind, writable=writable)

    def exec_command(self, command_str, bind=None, writable=False):
        return self.command('exec', self.simg.name, command_str, bind=bind, writable=writable)

class SingularityRecipe(File):
    def __init__(self, *args, simg: str, **kwargs):
        super().__init__(
            *args, **kwargs
        )
        self.simg = SingularityImage(f'{simg}.simg')

    def build(self, vp: HostProject, writable=False):
        writable = ' --writable' if writable else ''
        self.simg.deleteIfExists()

        with Temp(
                'sbuild',
                w=f'''
        sudo singularity build{writable} {self.simg.name} {self.name}
        #--force
        '''):
            shell('chmod +x sbuild').interact()
            p = vp.ssh('sudo ./sbuild')
            p.log_to_stdout()
            p.prompt()
            p.close()

        vp.host.tick_job_finish()
        return self.simg

class SingularityImage(File):
    pass
