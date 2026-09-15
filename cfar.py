"""
CA-CFAR ("cell averaging constant false alarm rate") threshold detection.

For each cell in the energy map, a local noise/clutter level is estimated
from surrounding training cells (excluding a few guard cells close to the
cell itself), and the cell is flagged as a detection if its value exceeds
alpha times that local level.

This is a simplified, illustrative implementation, not a production-ready
detector: false alarms are counted per cell, not per connected cluster.
"""
import numpy as np

from . import config as cfg


def integral_image(a):
    """2D prefix sum, with a leading row/column of zeros, for fast window sums."""
    ii = np.zeros((a.shape[0] + 1, a.shape[1] + 1))
    ii[1:, 1:] = np.cumsum(np.cumsum(a, axis=0), axis=1)
    return ii


def window_sum(ii, r0, r1, c0, c1, shape):
    """Sum of a[r0:r1+1, c0:c1+1], clipped to the valid range, via prefix sum ii."""
    r0c, c0c = max(r0, 0), max(c0, 0)
    r1c, c1c = min(r1, shape[0] - 1), min(c1, shape[1] - 1)
    if r0c > r1c or c0c > c1c:
        return 0.0, 0
    s = ii[r1c + 1, c1c + 1] - ii[r0c, c1c + 1] - ii[r1c + 1, c0c] + ii[r0c, c0c]
    count = (r1c - r0c + 1) * (c1c - c0c + 1)
    return s, count


def cfar_detect(caf, alpha=cfg.CFAR_ALPHA_DEFAULT,
                 train_delay=cfg.CFAR_TRAIN_DELAY, train_doppler=cfg.CFAR_TRAIN_DOPPLER,
                 guard_delay=cfg.CFAR_GUARD_DELAY, guard_doppler=cfg.CFAR_GUARD_DOPPLER):
    """Computes a CA-CFAR threshold for each cell; returns a boolean detection mask."""
    shape = caf.shape
    ii = integral_image(caf)
    detect_mask = np.zeros(shape, dtype=bool)

    for i in range(shape[0]):
        for j in range(shape[1]):
            full_sum, full_n = window_sum(ii, i - train_doppler, i + train_doppler,
                                           j - train_delay, j + train_delay, shape)
            guard_sum, guard_n = window_sum(ii, i - guard_doppler, i + guard_doppler,
                                             j - guard_delay, j + guard_delay, shape)
            train_n = full_n - guard_n
            if train_n <= 0:
                continue
            local_level = (full_sum - guard_sum) / train_n
            if caf[i, j] > alpha * local_level:
                detect_mask[i, j] = True
    return detect_mask
