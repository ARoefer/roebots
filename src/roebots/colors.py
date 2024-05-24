import numpy as np

ANALOGOUS = np.array([['#0CE879', '#0CF23E', '#12DB00', '#70F20C', '#B8E80C'],
                      ['#E8A40C', '#F2940C', '#DB6300', '#F2520C', '#E82F0C'],
                      ['#3769FA', '#318BDE', '#42CEF5', '#31DED5', '#37FAB9'],
                      ['#DFFA17', '#DED114', '#F4D221', '#DEA814', '#FAA717'],
                      ['#FA4612', '#DE2010', '#F51D4F', '#DE10A7', '#DD12FA'],
                      ['#FA0AF5', '#A609DE', '#7C15F5', '#3209DE', '#0A1CFA'],
                      ['#670FFA', '#220DDE', '#1B3EF5', '#0D67DE', '#0FB2FA']])

DISTINCT = np.hstack([ANALOGOUS.T[2], ANALOGOUS.T[4], ANALOGOUS.T[0], ANALOGOUS.T[3], ANALOGOUS.T[1]]).flatten()

ANALOGOUS_RGB = np.asarray([int(s[1:], base=16) for s in ANALOGOUS.flatten()]).astype('>u4').view(np.uint8).reshape(ANALOGOUS.shape + (4,))[...,1:]

DISTINCT_RGB   = np.asarray([int(s[1:], base=16) for s in DISTINCT]).astype('>u4').view(np.uint8).reshape((len(DISTINCT), 4))[..., 1:]
DISTINCT_RGBA  = np.hstack((DISTINCT_RGB, 255 * np.ones((len(DISTINCT_RGB), 1), dtype=DISTINCT_RGB.dtype)))
DISTINCT_RGBf  = DISTINCT_RGB / 255
DISTINCT_RGBAf = DISTINCT_RGBA / 255
