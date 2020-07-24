from mlib.file import File, pwdf
from mlib.host import Host, HostProject
from mlib.shell import shell, SSHExpectProcess

class VagrantMachine(Host):

    # , remove=False
    def __init__(self, keep_up, restart, rebuild):
        super().__init__(
            home='/home'
        )
        self.vagrantfile = File('Vagrantfile')
        if not self.vagrantfile:
            self.myinit()
        self._isup = None
        self.keep_up = keep_up
        self.restart = restart
        self._destroy = rebuild
        # self._remove = remove



    def isup(self):
        if self._isup is not None:
            return self._isup
        else:
            status = self.status()
            self._isup = ('The VM is powered off' not in status) and (
                    'The environment has not yet been created' not in status)
        return self._isup

    def init(self, box: str):
        # shell(f'cd {dir.abspath}').interact()
        shell(f'vagrant init {box}').interact()
    def myinit(self, box='singularityware/singularity-2.4', syncdir=True):
        assert not self.vagrantfile.exists
        self.vagrantfile.write('''
# -*- mode: ruby -*-
# vi: set ft=ruby :

''')
        self.vagrantfile.appendln('Vagrant.configure("2") do |config|')
        self.vagrantfile.appendln(f'config.vm.box = "{box}"')
        if syncdir:
            self.vagrantfile.appendln(f'config.vm.synced_folder ".", "/home/{pwdf().name}"')
        self.vagrantfile.appendln("config.disksize.size = '10GB'")
        self.vagrantfile.appendln('end')

    def upifhalted(self):
        if not self.isup():
            self.up()
    def up(self):
        assert not self.isup()
        shell('vagrant up').interact()
        self._isup = True
    __enter__ = up
    def haltifup(self, force=False):
        if self.isup():
            self.halt(force=force)
    def halt(self, force=False):
        if (not self.keep_up) or force:
            assert self.isup()
            shell('vagrant halt').interact()
            self._isup = False
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.halt()
    def destroy(self, force=False):
        force = ' -f' if force else ''
        shell(f'vagrant destroy{force}').interact()
        self._isup = False
    # def remove_box(self):
    #     shell('vagrant box remove').interact()
    def status(self):
        return shell('vagrant status').all_output()
    def global_status(self):
        shell('vagrant global_status').interact()




    # vagrant ssh -- -t "{command}"
    def ssh_login(self):
        return SSHExpectProcess(f'vagrant ssh')

    def send(self, *files, project_name):
        for f in files:
            f: File
            # I am currently not sending vagrant files over scp because home dir is bound in vagrantfile
            assert f.parent.abspath == self.vagrantfile.parent.abspath



    def startup(self):
        if self.restart:
            self.haltifup()
        if self._destroy: self.destroy(force=True)
        # if self._remove: self.remove_box()
        self.upifhalted()
    def shutdown(self):
        self.halt()

class VagrantHostProject(HostProject):
    def pre_run(self, SW, p):
        # because of the file getting doubled in bound directory thing
        p.sendatprompt('cd ..')
