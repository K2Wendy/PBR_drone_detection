"""
DSI cancellation (the adaptive/least-squares tilpasningsberegning).

A single implementation covers both the plain integer-tap filter (used
in Tests 1, 2 and 4) and the fractional-delay-aware filter (used in
Test 5): an integer grid is just tap_delays = [0, 1, 2, ..., n_taps-1],
so there is only one code path to maintain.
"""
import numpy as np

from .signal import fractional_shift


def integer_tap_delays(n_taps):
    """Convenience helper: the plain integer grid [0, 1, ..., n_taps-1]."""
    return np.arange(n_taps, dtype=float)


def fractional_tap_delays(max_delay, spacing):
    """A finer grid [0, spacing, 2*spacing, ...] covering up to max_delay."""
    n_taps = int(max_delay / spacing) + 1
    return np.arange(n_taps) * spacing


def build_design_matrix(x, tap_delays):
    """
    Builds the design matrix X, where column k is the reference signal x
    shifted by tap_delays[k] (integer or fractional). Batched via a single
    2D FFT for efficiency rather than looping fractional_shift per column.
    """
    n = len(x)
    X_fft = np.fft.fft(x)
    k = np.fft.fftfreq(n) * n
    phase = np.exp(-1j * 2 * np.pi * np.outer(tap_delays, k) / n)
    shifted_freq = phase * X_fft[None, :]
    shifted_time = np.fft.ifft(shifted_freq, axis=1)
    return shifted_time.T  # shape (n, len(tap_delays))


def cancel_dsi(x, y, tap_delays):
    """
    Removes the direct signal and static clutter paths from y via a
    least-squares fit against columns of shifted copies of x, and
    returns the residual (y minus the fitted estimate).

    tap_delays: array of delays (integer or fractional) to fit against.
                Use integer_tap_delays(n) for a plain integer-grid filter,
                or fractional_tap_delays(max_delay, spacing) for a finer
                grid.
    """
    X = build_design_matrix(x, tap_delays)
    w, *_ = np.linalg.lstsq(X, y, rcond=None)
    y_hat = X @ w
    return y - y_hat
