"""
Shared configuration constants for the passive bistatic radar (PBR)
simulation package.

Editing values here affects every script that uses the package, since
they all import from this single source of truth instead of redefining
their own copies.
"""

# --- Sampling / scene ---
FS = 4000  # normalized "sample rate" (abstract units, not a literal RF sample rate)
N = 4000   # samples per trial (1 second of observation at FS=4000)

# Clutter model: direct path + five multipath reflections, decaying amplitude
CLUTTER_DELAYS = [0, 2, 5, 9, 14, 20]
CLUTTER_AMPS = [1.0, 0.7, 0.5, 0.35, 0.25, 0.15]

# Two target placements used across the test suite
TARGET_DELAY_SEPARATED = 30  # away from the clutter spread (0-20) -- used in Test 1, 2, 5
TARGET_DELAY_OVERLAP = 12    # inside the clutter/filter span -- used in Test 3, 4

NOISE_STD = 0.05  # receiver noise (std of real and imaginary parts)

# --- Search grids for the delay/Doppler energy map ---
DELAY_SEARCH_MAX = 50          # search delays 0..50
DOPPLER_SEARCH_MIN = -200      # search Doppler -200..200 Hz, 1 Hz steps
DOPPLER_SEARCH_MAX = 200

N_TRIALS = 30  # independent trials per parameter level

DELAY_TOL = 1     # tolerance (samples) for a correctly detected delay
DOPPLER_TOL = 3   # tolerance (Hz) for a correctly detected Doppler

# --- Cancellation filter sizing ---
SUFFICIENT_TAPS = max(CLUTTER_DELAYS) + 1  # = 21: minimum integer taps to span the clutter
FIXED_TAPS = SUFFICIENT_TAPS + 3           # = 24: "comfortable margin" level used as a fixed setting
MAX_TAP_DELAY = float(FIXED_TAPS - 1)      # = 23.0: same reach, used to size fractional grids

# --- CA-CFAR detection parameters ---
CFAR_TRAIN_DELAY = 6      # half-width of the training window (delay axis)
CFAR_TRAIN_DOPPLER = 6    # half-width of the training window (Doppler axis)
CFAR_GUARD_DELAY = 1      # half-width of the guard area (delay axis)
CFAR_GUARD_DOPPLER = 1    # half-width of the guard area (Doppler axis)
CFAR_ALPHA_DEFAULT = 9.0  # default threshold factor (tuned empirically)

# Exclusion area around the true target when counting false alarms
EXCLUDE_DELAY = 3
EXCLUDE_DOPPLER = 6
