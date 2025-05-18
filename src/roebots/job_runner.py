"""
 Copyright (c) 2024 Adrian Röfer, Robot Learning Lab, University of Freiburg

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/>.
 """


import os
import signal
import sys
import time

from subprocess import Popen
from pathlib    import Path
from threading  import RLock


class JobRunner():
    def __init__(self, jobs, n_processes=100, exit_on_fail=False, report_failures=True) -> None:
        self.jobs      = []
        for j in jobs:
            job = []
            # Primitive expansion of paths with * in them
            for a in j:
                if '*' in a:
                    p = Path(a)
                    job += [str(f) for f in p.parent.glob(p.name)]
                else:
                    job.append(a)
            self.jobs.append(job)

        self._processes = []
        self._n_proc    = n_processes
        self._exit_on_fail = exit_on_fail
        self._report_failures = report_failures

    def _sig_handler(self, sig, *args):
        print('Received SIGINT. Killing subprocesses...')
        for p in self._processes:
            p.send_signal(signal.SIGINT)
        
        for p in self._processes:
            p.wait()
        sys.exit(0)

    def run(self):
        signal.signal(signal.SIGINT, self._sig_handler)

        tasks = self.jobs.copy()
        should_terminate = False
        in_execution     = []
        failures         = []

        with open(os.devnull, 'w') as devnull:
            while len(tasks) > 0 and not should_terminate:
                while len(self._processes) < self._n_proc and len(tasks) > 0:
                    self._processes.append(Popen(tasks[0])) #, stdout=devnull))
                    print(f'Launched task "{" ".join(tasks[0])}"\nRemaining {len(tasks) - 1}')
                    in_execution.append(tasks[0])
                    tasks = tasks[1:]

                time.sleep(1.0)

                tidx = 0
                while tidx < len(self._processes):
                    if (returncode:=self._processes[tidx].poll()) is not None:
                        if returncode != 0:
                            failures.append(in_execution[tidx])
                            if self._exit_on_fail:
                                print(f'Terminating everything because of job failure!')
                                should_terminate = True
                                break
                        del self._processes[tidx]
                        del in_execution[tidx]
                    else:
                        tidx += 1

            print('Waiting for their completion...')
            for pidx, p in enumerate(self._processes):
                if (returncode:=p.wait()) != 0:
                    failures.append(in_execution[pidx])

            if self._report_failures:
                if len(failures) > 0:
                    print('================================\n  FAILURES:\n    {}'.format('\n    '.join([' '.join(t) for t in failures])))
                else:
                    print('================================\n  No Failures!')


# This exists because there is something wrong with Python's own job queue

class BatchJobState():
    def __init__(self, jobs):
        self._jobs = jobs
        self._idx  = 0
        self._lock = RLock()
    
    def pop_job(self):
        with self._lock:
            if self._idx >= len(self._jobs):
                raise StopIteration(f'Job queue is empty')
            
            out = self._jobs[self._idx]
            self._idx += 1
            return out


def pooled_job_processing(f_worker, jobs, n_workers, desc=None):
    from threading import Thread
    
    if desc is not None:
        from tqdm import tqdm
        pbar = tqdm(total=len(jobs), desc=desc)
    
    state = BatchJobState(jobs)

    def inner_worker(jobs):
        while True:
            try:
                job = state.pop_job()

                f_worker(*job)
                if desc is not None:
                    pbar.update(1)
            except StopIteration:
                break

    workers = []
    for _ in range(n_workers):
        workers.append(Thread(target=inner_worker, args=(jobs,)))
        workers[-1].start()

    for w in workers:
        w.join()

    if desc is not None:
        pbar.close()
