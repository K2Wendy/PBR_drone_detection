"""
A single, unified trial runner and a generic parameter sweep, used by
every test script. Earlier drafts of this simulation had three near-
identical copies of this logic (one per test script); consolidating it
here means a bug fix or behavioural change only needs to be made once.
"""
import numpy as np

from . import config as cfg
from .signal import make_reference, make_surveillance
from .cancellation import cancel_dsi
from .caf import compute_caf_map, delay_search_grid, doppler_search_grid
from .cfar import cfar_detect


def run_single_trial(rng, target_db, fd_hz, tap_delays, target_delay, offset=0.0, alpha=cfg.CFAR_ALPHA_DEFAULT):
    """
    Runs one trial end-to-end: build the scene, cancel clutter, compute the
    energy map, apply CA-CFAR detection, and check whether the target was
    found.

    tap_delays: array of delays used by the cancellation filter. Pass
                pbr_sim.cancellation.integer_tap_delays(n) for a plain
                integer grid, or fractional_tap_delays(max_delay, spacing)
                for a finer grid (Test 5).
    offset: shared fractional offset applied to the whole scene (Test 5).
            Leave at 0.0 for Tests 1-4.

    Returns (target_hit: bool, n_false_alarms: int, residual_power: float).
    """
    delay_search = delay_search_grid()
    doppler_search = doppler_search_grid()

    x = make_reference(rng)
    y = make_surveillance(x, rng, target_db, fd_hz, target_delay, offset=offset)
    residual = cancel_dsi(x, y, tap_delays)
    residual_power = float(np.mean(np.abs(residual) ** 2))

    caf = compute_caf_map(residual, x, delay_search, doppler_search)
    detect_mask = cfar_detect(caf, alpha=alpha)

    delay_idx = int(np.argmin(np.abs(delay_search - target_delay)))
    doppler_idx = int(np.argmin(np.abs(doppler_search - fd_hz)))

    d0, d1 = max(doppler_idx - cfg.DOPPLER_TOL, 0), min(doppler_idx + cfg.DOPPLER_TOL, detect_mask.shape[0] - 1)
    r0, r1 = max(delay_idx - cfg.DELAY_TOL, 0), min(delay_idx + cfg.DELAY_TOL, detect_mask.shape[1] - 1)
    target_hit = bool(detect_mask[d0:d1 + 1, r0:r1 + 1].any())

    ed0 = max(doppler_idx - cfg.EXCLUDE_DOPPLER, 0)
    ed1 = min(doppler_idx + cfg.EXCLUDE_DOPPLER, detect_mask.shape[0] - 1)
    er0 = max(delay_idx - cfg.EXCLUDE_DELAY, 0)
    er1 = min(delay_idx + cfg.EXCLUDE_DELAY, detect_mask.shape[1] - 1)
    mask_copy = detect_mask.copy()
    mask_copy[ed0:ed1 + 1, er0:er1 + 1] = False
    n_false_alarms = int(mask_copy.sum())

    return target_hit, n_false_alarms, residual_power


def run_sweep(kwargs_for_level, levels, seed_offset, n_trials=cfg.N_TRIALS, verbose=True):
    """
    Runs n_trials independent trials at each level in `levels`, where
    kwargs_for_level(level) returns a dict of keyword arguments for
    run_single_trial (minus `rng`).

    Returns a list of per-level result dicts with detection rate, mean
    false alarms, and mean residual power.
    """
    results = []
    for level_idx, level in enumerate(levels):
        rng = np.random.default_rng(1000 * seed_offset + level_idx)
        n_success = 0
        fa_counts = []
        res_powers = []
        for _ in range(n_trials):
            kwargs = kwargs_for_level(level)
            hit, n_fa, res_pow = run_single_trial(rng, **kwargs)
            n_success += int(hit)
            fa_counts.append(n_fa)
            res_powers.append(res_pow)

        rate = n_success / n_trials
        result = {
            "level": level,
            "rate": rate,
            "detections": n_success,
            "trials": n_trials,
            "mean_false_alarms": float(np.mean(fa_counts)),
            "mean_residual_power": float(np.mean(res_powers)),
        }
        results.append(result)
        if verbose:
            print(f"  level={level}: {n_success}/{n_trials} ({rate * 100:.0f}%), "
                  f"mean false alarms={result['mean_false_alarms']:.2f}, "
                  f"mean residual power={result['mean_residual_power']:.6f}")
    return results
