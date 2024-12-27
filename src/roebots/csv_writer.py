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
