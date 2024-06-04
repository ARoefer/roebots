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

class JobRunner():
    def __init__(self, jobs, n_processes=100) -> None:
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

        self.processes = []
        self.n_proc    = n_processes

    def _sig_handler(self, sig, *args):
        print('Received SIGINT. Killing subprocesses...')
        for p in self.processes:
            p.send_signal(signal.SIGINT)
        
        for p in self.processes:
            p.wait()
        sys.exit(0)

    def run(self):
        signal.signal(signal.SIGINT, self._sig_handler)

        tasks = self.jobs.copy()

        with open(os.devnull, 'w') as devnull:
            while len(tasks) > 0:
                while len(self.processes) < self.n_proc and len(tasks) > 0:
                    self.processes.append(Popen(tasks[0])) #, stdout=devnull))
                    print(f'Launched task "{" ".join(tasks[0])}"\nRemaining {len(tasks) - 1}')
                    tasks = tasks[1:]

                time.sleep(1.0)

                tidx = 0
                while tidx < len(self.processes):
                    if self.processes[tidx].poll() is not None:
                        del self.processes[tidx]
                    else:
                        tidx += 1

            print('Waiting for their completion...')
            for p in self.processes:
                p.wait()