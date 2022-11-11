import numpy as np

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
