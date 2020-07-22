from mlib.file import pwdf
from mlib.host import Host
from mlib.shell import SSHExpectProcess

# # _DNN_ExecConfig(LP, 'bash', interact=True, writable=True)

#
# LP = HostProject(
#     LocalHost(HOME),
#     name=pwdf().rel_to(HOME)
# )

# singularity doesnt seem able to exec on Mac, so whatever
class LocalHost(Host):
    def ssh_login(self):
        p = SSHExpectProcess('bash')
        return p
    def send(self, *files, project_name):
        for f in files:
            assert f.parent.abspath == pwdf().abspath
    def startup(self): pass
    def shutdown(self): pass
