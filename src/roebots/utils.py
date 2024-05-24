import numpy as np
import os

def real_quat_from_matrix(frame):
    tr = frame[0, 0] + frame[1, 1] + frame[2, 2]

    if tr > 0:
        S = np.sqrt(tr + 1.0) * 2
        qw = 0.25 * S
        qx = (frame[2, 1] - frame[1, 2]) / S
        qy = (frame[0, 2] - frame[2, 0]) / S
        qz = (frame[1, 0] - frame[0, 1]) / S
    elif (frame[0, 0] > frame[1, 1]) and (frame[0, 0] > frame[2, 2]):
        S = np.sqrt(1.0 + frame[0, 0] - frame[1, 1] - frame[2, 2]) * 2
        qw = (frame[2, 1] - frame[1, 2]) / S
        qx = 0.25 * S
        qy = (frame[0, 1] + frame[1, 0]) / S
        qz = (frame[0, 2] + frame[2, 0]) / S
    elif frame[1, 1] > frame[2, 2]:
        S = np.sqrt(1.0 + frame[1, 1] - frame[0, 0] - frame[2, 2]) * 2
        qw = (frame[0, 2] - frame[2, 0]) / S
        qx = (frame[0, 1] + frame[1, 0]) / S
        qy = 0.25 * S
        qz = (frame[1, 2] + frame[2, 1]) / S
    else:
        S = np.sqrt(1.0 + frame[2, 2] - frame[0, 0] - frame[1, 1]) * 2
        qw = (frame[1, 0] - frame[0, 1]) / S
        qx = (frame[0, 2] + frame[2, 0]) / S
        qy = (frame[1, 2] + frame[2, 1]) / S
        qz = 0.25 * S

    return (qx, qy, qz, qw)


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
