import numpy as np
import os

from scipy.spatial.transform import Rotation as ScipyRotation

def real_quat_from_matrix(frame):
    return ScipyRotation.from_matrix(frame[..., :3, :3]).as_quat()

_SEARCH_PATHS = set()

def add_search_path(path):
    _SEARCH_PATHS.add(path)

if 'ROS_PACKAGE_PATH' in os.environ:
    for rpp in os.environ['ROS_PACKAGE_PATH'].split(':'):
        add_search_path(rpp)

def res_pkg_path(rpath):
    """Resolves a ROS package relative path to a global path.

    :param rpath: Potential ROS URI to resolve.
    :type rpath: str
    :return: Local file system path
    :rtype: str
    """
    if rpath[:10] == 'package://':
        rpath = rpath[10:]
        pkg = rpath[:rpath.find('/')] if rpath.find('/') != -1 else rpath

        for rpp in _SEARCH_PATHS:
            if rpp[rpp.rfind('/') + 1:] == pkg:
                return f'{rpp[:rpp.rfind("/")]}/{rpath}'
            if os.path.isdir(f'{rpp}/{pkg}'):
                return f'{rpp}/{rpath}'
        raise Exception(f'Package "{pkg}" can not be found in search paths!')
    return rpath
