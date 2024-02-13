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


import sys

from pathlib import Path

from roebots.job_runner import JobRunner


if __name__ == '__main__':
    args = sys.argv[1:]

    try:
        nproc = int(args[0])
        args = args[1:]
    except ValueError as e:
        nproc = 10

    jobs = []
    for a in args:
        if Path(a).exists() and Path(a).is_file():
            with open(a, 'r') as f:
                for l in f.readlines():
                    l = l.strip()
                    if len(l) > 0 and l[0] != '#':
                        jobs.append(l)
        else:
            jobs.append(a)

    runner = JobRunner([[a for a in j.strip().split(' ') if a != ''] for j in jobs], nproc)
    print(f'Running {len(jobs)}...')
    runner.run()
    print('Done')
