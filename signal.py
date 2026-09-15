"""
Signal generation for the PBR simulation: the synthetic reference signal,
the fractional-delay shift operator, and construction of the surveillance
scene (clutter + target + noise).

A single scene-construction function is used for both integer and
fractional target/clutter placement -- an integer delay is simply the
special case offset=0.0, so there is no separate "integer-only" code
path to keep in sync.
"""
import numpy as np

from . import config as cfg


def make_reference(rng, n=cfg.N):
    """Generates a broadband, complex reference signal (represents DVB-T2 content)."""
    return (rng.standard_normal(n) + 1j * rng.standard_normal(n)) / np.sqrt(2)


def fractional_shift(x, delay):
    """
    Shifts x by `delay` samples (may be non-integer) via an FFT-based phase
    rotation. This is an exact, continuous shift -- for integer delay values
    it matches simple array shifting to within floating-point precision.
    """
    n = len(x)
    X = np.fft.fft(x)
    k = np.fft.fftfreq(n) * n
    phase = np.exp(-1j * 2 * np.pi * k * delay / n)
    return np.fft.ifft(X * phase)


def make_surveillance(x, rng, target_db, fd_hz, target_delay, offset=0.0):
    """
    Builds the surveillance signal: clutter (direct path + multipath) plus
    a target reflection plus receiver noise.

    target_db: target amplitude in dB relative to the direct clutter path
               (CLUTTER_AMPS[0] = 1.0)
    fd_hz: target Doppler shift in Hz
    target_delay: target's nominal (integer) delay in samples
    offset: a shared fractional offset (0.0-1.0) applied to every path in
            the scene (clutter and target alike) -- used by Test 5 to
            probe fractional-delay ("range straddling") effects. Leave at
            0.0 for the standard, delay-aligned scenario used in Tests 1-4.
    """
    n = len(x)
    y = np.zeros(n, dtype=complex)

    for delay, amp in zip(cfg.CLUTTER_DELAYS, cfg.CLUTTER_AMPS):
        y += amp * fractional_shift(x, delay + offset)

    target_amp = 10 ** (target_db / 20.0)
    t = np.arange(n) / cfg.FS
    doppler_mod = np.exp(1j * 2 * np.pi * fd_hz * t)
    x_target = fractional_shift(x, target_delay + offset)
    y += target_amp * x_target * doppler_mod

    y += cfg.NOISE_STD * (rng.standard_normal(n) + 1j * rng.standard_normal(n)) / np.sqrt(2)
    return y
