"""
Delay/Doppler energy map (the CAF -- cross-ambiguity function).

For each Doppler hypothesis, the residual is compensated for that
frequency shift and cross-correlated against the reference signal via
FFT; the magnitude of the result at each delay forms one row of the map.
"""
import numpy as np

from . import config as cfg


def delay_search_grid():
    return np.arange(0, cfg.DELAY_SEARCH_MAX + 1)


def doppler_search_grid():
    return np.arange(cfg.DOPPLER_SEARCH_MIN, cfg.DOPPLER_SEARCH_MAX + 1, 1)


def compute_caf_map(residual, x, delay_search=None, doppler_search=None):
    """Returns a 2D array [doppler_idx, delay_idx] of correlation magnitude."""
    if delay_search is None:
        delay_search = delay_search_grid()
    if doppler_search is None:
        doppler_search = doppler_search_grid()

    n = len(x)
    t = np.arange(n) / cfg.FS
    X_fft = np.fft.fft(x, n=n)
    X_fft_conj = np.conj(X_fft)

    caf = np.zeros((len(doppler_search), len(delay_search)))
    for i, fd in enumerate(doppler_search):
        demod = residual * np.exp(-1j * 2 * np.pi * fd * t)
        R_fft = np.fft.fft(demod, n=n)
        corr = np.fft.ifft(R_fft * X_fft_conj)
        caf[i, :] = np.abs(corr[delay_search])
    return caf
