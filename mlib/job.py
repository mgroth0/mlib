from abc import ABC
import json
import time
import traceback

import pexpect
from numpy import inf

from mlib.JsonSerializable import obj
from mlib.abstract_attributes import AbstractAttributes, Abstract
from mlib.boot import log
from mlib.boot.lang import isblank
from mlib.boot.stream import strs
from mlib.parallel import run_in_thread
from mlib.shell import ishell, InteractiveExpectShell, arg_str
from mlib.str import shorten_str, utf_decode, min_sec_form
from mlib.term import log_invokation, reds
class Job(AbstractAttributes, ABC):
    SUCCESS_STR = Abstract(str)
    REMOTE_FOLDER: Abstract(str)
    REMOTE_SCRIPT: Abstract(str)
    LOCAL_PY: Abstract(str)
    LOCAL_SCRIPT: Abstract(str)

    ALL_Ps = []
    TOTAL_FINISHED = 0
    TOTAL_TODO = None
    next_instance_index = 1

    @staticmethod
    def dict_to_args(d): return [f'--{k}={arg_str(v)}' for k, v in d.items()]


    def __init__(
            self,
            job_args: dict,
            job_cfg_arg: obj,
            gpus=(),
            commands=(),
            interact=False,
            remote=False,
    ):
        self.job_args = job_args
        self.remote = remote
        self.commands = commands
        self.interact = interact
        self.gpus = gpus
        self.instance_idx = Job.next_instance_index
        Job.next_instance_index += 1
        self.started = False
        self.start_time = None
        self.done = False
        self.end_time = None
        self.using_gpus = [None]
        self.last_log = None
        self.main_args = self.dict_to_args(job_args)
        cfg_j = json.dumps(job_cfg_arg.toDict()).replace('"', '\\"')
        self.main_args += [f"--cfg=\"\"\"{cfg_j}\"\"\""]









    def __str__(self): return f'Job {self.instance_idx}'



    class JobStatus:
        def __init__(self, job):
            status = 'PENDING '
            if job.started:
                status = 'RUNNING '
            if job.done:
                status = 'FINISHED'
            self.job = job
            self.status = status
            self.gpu = job.using_gpus[0]
            self.run_time_str = job.run_time_str()
            self.last = shorten_str(job.last_log,
                                    # 48
                                    inf
                                    # .replace('\n', '/n')
                                    ).strip().replace('\r', '/r')
        def __str__(self):
            return f'{self.job}\t{self.status}\tGPU={self.gpu}\t{self.run_time_str}\t\t{self.last}'

    def status(self): return Job.JobStatus(self)
    @log_invokation(with_instance=True)
    def run(self, gpus_to_use, muscle, a_sync=False):
        self.started = True
        self.start_time = time.time()
        self.using_gpus = gpus_to_use
        self.main_args += [f'--gpus={"".join(strs(gpus_to_use))}']

        if self.remote:
            # noinspection PyUnresolvedReferences
            p = google_compute.gc(AUTO_LOGIN=True)
            p.cd(f"{self.REMOTE_FOLDER}")
        else:
            p = ishell('bash')
            # class relproc(Process):
            #     def run(self):
            #         import exec.new_result_comp as nrc
            #
            # p = relproc()
        Job.ALL_Ps += [p]
        for com in self.commands: p.sendline(com)
        if self.remote:
            p: InteractiveExpectShell
            p.py(f'{self.REMOTE_SCRIPT} {" ".join(self.main_args)}')
        else:
            # p: Process
            p.sendline(f'{self.LOCAL_PY} "{self.LOCAL_SCRIPT}" {" ".join(self.main_args)}')
            # p.start()
        if self.interact: p.interact()
        else:
            string_holder = {'': ''}
            def save_last_log(data, o):
                data = utf_decode(data)
                string_holder[''] += ''
                if not isblank(data):
                    for line in reversed(data.split('\n')):
                        if not isblank(line):
                            o.last_log = line
                            break
            p.log_to_stdout(fun=save_last_log, o=self)
        if a_sync:
            run_in_thread(self.inter_p_wrap, args=(p, gpus_to_use, muscle))
        else:
            self.inter_p_wrap(p, gpus_to_use, muscle)


    def run_time_str(self):
        if self.start_time is None:
            return '...'
        elif self.end_time is None:
            return min_sec_form(time.time() - self.start_time) + '...'
        else:
            return min_sec_form(self.end_time - self.start_time)

    def inter_p_wrap(self, p, gpus_im_using, muscle):
        if not self.interact:
            log('waiting for child...')
            try:
                r = p.expect([self.SUCCESS_STR, pexpect.EOF, 'ERROR ERROR ERROR'])
            except UnicodeDecodeError as e:
                log(reds(f'got {repr(e)}'))
                print(traceback.format_exc())
                r = 2
            log({
                    0: 'run_exps got a success',
                    1: 'run_exps got an EOF... what? exiting run_exps',
                    2: 'run_exps got an error, exiting run_exps'
                }[r])
            p.close()
            log('closed child')
            if r in [1, 2]: self.explode()
        Job.TOTAL_FINISHED += 1
        print(f'Finished Job {self} ({Job.TOTAL_FINISHED}/{Job.TOTAL_TODO})')
        self.done = True
        self.end_time = time.time()
        for g in gpus_im_using: muscle.GPU_IN_USE[g] = False

    def wait(self):
        while not self.done:
            time.sleep(0.1)

    def explode(self):
        self.kill_all_jobs()
        exit(0)

    @classmethod
    @log_invokation
    def kill_all_jobs(cls):
        for p in cls.ALL_Ps:
            if p.alive(): p.close()
