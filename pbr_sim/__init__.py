"""
pbr_sim: a small, self-contained simulation of the signal processing
chain for a DVB-T2-based passive bistatic radar (PBR) drone-detection
concept -- reference/surveillance signal generation, DSI cancellation
(integer or fractional delay grid), the delay/Doppler energy map, and
CA-CFAR threshold detection.

See the scripts/ directory for runnable test drivers, and README.md for
an overview of what each test demonstrates.
"""
from . import config
from .signal import make_reference, make_surveillance, fractional_shift
from .cancellation import cancel_dsi, build_design_matrix, integer_tap_delays, fractional_tap_delays
from .caf import compute_caf_map, delay_search_grid, doppler_search_grid
from .cfar import cfar_detect, integral_image, window_sum
from .trial import run_single_trial, run_sweep

__all__ = [
    "config",
    "make_reference", "make_surveillance", "fractional_shift",
    "cancel_dsi", "build_design_matrix", "integer_tap_delays", "fractional_tap_delays",
    "compute_caf_map", "delay_search_grid", "doppler_search_grid",
    "cfar_detect", "integral_image", "window_sum",
    "run_single_trial", "run_sweep",
]
