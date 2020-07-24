from mlib.file import File, Temp, pwdf
from mlib.host import HostProject
from mlib.shell import shell


class Singularity:
    def __init__(self, recipe_name, simg_name=None):
        if simg_name is None:
            simg_name = pwdf().name
        self.recipe = SingularityRecipe(recipe_name, simg=simg_name)
        self.simg = self.recipe.simg
        self.img = self.recipe.img

    def command(self, *args, bind=None, writable=False, overlay=False):
        s = ['SINGULARITYENV_CONDA_HOME=/matt/miniconda3']
        s += ['singularity']
        args = list(args)
        if writable:
            args.insert(1, '--writable')
        if overlay:
            args.insert(1, '--overlay')
            args.insert(2, self.img.name)
        if bind is not None:
            s += ['-B', File(bind).abspath]
        s += args
        return ' '.join(s)

    def run_command(self, bind=None, writable=False, overlay=False):
        return self.command('run', self.simg.name, bind=bind, writable=writable, overlay=overlay)

    def exec_command(self, command_str, bind=None, writable=False, overlay=False):
        return self.command('exec', self.simg.name, command_str, bind=bind, writable=writable, overlay=overlay)

class SingularityRecipe(File):
    def __init__(self, *args, simg: str, **kwargs):
        super().__init__(
            *args, **kwargs
        )
        self.simg = SingularityImage(f'{simg}.simg')
        self.img = File(f'{simg}.img')

    def build(self, vp: HostProject, writable=False):
        writable = ' --writable' if writable else ''
        self.simg.deleteIfExists()
        # size gets doubled if I put it in bound directory... a vagrant bug I think
        with Temp(
                'sbuild',
                w=f'''
        sudo singularity build{writable} ../{self.simg.name} {self.name}
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