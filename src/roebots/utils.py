import numpy as np
import os

def real_quat_from_matrix(frame):
    diag = np.diag(frame)[:3]
    tr   = diag.sum()

    i = diag.argmax()
    s_coeff = np.full(3, -1) if tr <= 0 else np.ones(3)
    s_coeff[i] = 1

    S = np.sqrt(1.0 + (diag * s_coeff).sum()) * 2

    # Lower and upper corner in order (1, 0), (2, 0), (2, 1)
    #                                 (0, 1), (0, 2), (1, 2)
    m = np.vstack((frame[np.tril_indices(3, -1)], 
                   frame[np.triu_indices(3,  1)]))

    if tr <= 0:
        v_coeff = np.ones((2, 3))
        v_coeff[1 - int(i == 1), 2 - i] = -1
    else:
        v_coeff = np.asarray(((1, -1, 1), (-1, 1, -1)))

    temp_v = np.hstack(((m * v_coeff).sum(axis=0) / S, (0.25 * S,)))

    if tr > 0:
        return (temp_v[2], temp_v[1], temp_v[0], temp_v[3])
    elif i == 0:
        return (temp_v[1], temp_v[2], temp_v[3], temp_v[0])
    elif i == 1:
        return (temp_v[0], temp_v[3], temp_v[2], temp_v[1])
    
    return (temp_v[3], temp_v[0], temp_v[1], temp_v[2])


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
