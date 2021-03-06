from mlib.boot import log
from mlib.file import File, pwdf
from mlib.host import HostProject, Host
from mlib.term import log_invokation


class Singularity:
    def __init__(self, recipe_name, simg_name=None):
        if simg_name is None:
            simg_name = pwdf().name
        self.recipe = SingularityRecipe(recipe_name, simg=simg_name)
        self.simg = self.recipe.simg
        self.img = self.recipe.img

    def command(self, *args, run_args, bind=None, writable=False, overlay=False):
        s = ['SINGULARITYENV_CONDA_HOME=/matt/miniconda3']
        s += ['singularity']
        args = list(args)
        # NVIDIA binaries may not be bound with --writable
        args.insert(1, '--nv')  # gpu support
        if writable:
            args.insert(1, '--writable')
        if overlay:
            args.insert(1, '--overlay')
            args.insert(2, self.img.name)
        if bind is not None:
            for fromm, to in bind:
                args.insert(1, '-B')
                args.insert(2, f'{fromm}:{to}')
        s += args
        s += run_args
        return ' '.join(s)

    def run_command(self, run_args, bind=None, writable=False, overlay=False):
        return self.command('run', self.simg.name, run_args=run_args, bind=bind, writable=writable, overlay=overlay)

    def exec_command(self, command_str, run_args, bind=None, writable=False, overlay=False):
        return self.command('exec', self.simg.name, command_str, run_args=run_args, bind=bind, writable=writable,
                            overlay=overlay)

class SingularityRecipe(File):
    def __init__(self, *args, simg: str, **kwargs):
        super().__init__(
            *args, **kwargs
        )
        self.simg = SingularityImage(f'{simg}.simg')
        self.img = File(f'{simg}.img')

    @log_invokation
    def build(self, vp: HostProject, writable=False):
        writable = ' --writable' if writable else ''
        self.simg.deleteIfExists()
        # size gets doubled if I put it in bound directory... a vagrant bug I think
        # with Temp(
        #         'sbuild',
        #         w=f'''
        # sudo singularity build{writable} {self.simg.name} {self.name}
        # # --force
        # '''):
        # shell('chmod +x sbuild').interact()
        # p = vp.ssh('sudo ./sbuild')

        # can no longer do the temp sbuild file since I may be doing this command in open mind and would have to send over the sbuild file... not worth it
        p = vp.ssh()
        if isinstance(vp, Host):
            p.sendatprompt('cd dnn')
        build_command = f'sudo singularity -v build{writable} {self.simg.name} {self.name}'
        log(f'{build_command=}')
        p.log_to_stdout()
        p.sendatprompt(build_command)
        p.prompt()
        log("About to do weird prompt")
        p.prompt()  # no idea why we need to expect prompt twice here but we do or else process is closed early
        log("finished weird prompt")
        p.close()

        if isinstance(vp, Host):
            vp.tick_job_finish()
        else:
            vp.host.tick_job_finish()
        return self.simg

class SingularityImage(File):
    pass
