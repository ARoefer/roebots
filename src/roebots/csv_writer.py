# Copyright (c) 2024 Adrian Röfer, Robot Learning Lab, University of Freiburg
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.


from multiprocessing import RLock
from pathlib         import Path

import fcntl


class StreamedCSVWriter():
    def __init__(self, out_path : Path, columns) -> None:
        out_path = Path(out_path)

        if out_path.suffix != '.csv':
            out_path = out_path.parent / (out_path.stem + '.csv')
        
        self._columns  = columns
        self._lock     = RLock()
        
        self._out_file = open(out_path, 'w')
        self.write(self._columns)
    
    def write(self, row):
        if len(row) != len(self._columns):
            raise ValueError(f'Tried to write a row of {len(row)} items to csv, but {len(self._columns)} were expected.')

        row = ','.join([str(v) for v in row])

        with self._lock:        
            self._out_file.write(f'{row}\n')
            self._out_file.flush()


class _POSIX_FILE_MUTEX:
    def __init__(self, lock_file : Path):
        self._path_lock_file = lock_file
        if not self._path_lock_file.exists():
            self._path_lock_file.touch()

    def __enter__ (self):
        self.fp = open(self._path_lock_file)
        fcntl.flock(self.fp.fileno(), fcntl.LOCK_EX)

    def __exit__ (self, _type, value, tb):
        fcntl.flock(self.fp.fileno(), fcntl.LOCK_UN)
        self.fp.close()


class MultiProcessCSVWriter():
    def __init__(self, out_path : Path, columns):
        self._out_path = Path(out_path)

        if self._out_path.suffix != '.csv':
            self._out_path = self._out_path.parent / (self._out_path.stem + '.csv')
        
        self._columns  = columns
        self._lock     = RLock()
        self._system_lock = _POSIX_FILE_MUTEX(Path(f'{out_path}.lock'))

    def write(self, row):
        with self._lock:
            with self._system_lock:
                # Assume that the header is present when the file already exists
                write_header = not self._out_path.exists()

                with open(self._out_path, 'a') as f:
                    if write_header:
                        self._write_row(f, self._columns)
                    self._write_row(f, row)

    def _write_row(self, file, row):
        if len(row) != len(self._columns):
            raise ValueError(f'Tried to write a row of {len(row)} items to csv, but {len(self._columns)} were expected.')

        row = ','.join([str(v) for v in row])

        file.write(f'{row}\n')
        file.flush()
