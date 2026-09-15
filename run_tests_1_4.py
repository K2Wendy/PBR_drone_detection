"""
Runs Test 1-4 of the PBR concept: sensitivity, number of delay taps,
speed with an overlapping target range, and flight direction relative
to the bistatic geometry.

Usage:
    python scripts/run_tests_1_4.py
"""
import json
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pbr_sim import config as cfg
from pbr_sim.cancellation import integer_tap_delays
from pbr_sim.trial import run_sweep


def main():
    t0 = time.time()
    all_results = {}

    print("=== Test 1: Sensitivity ===")
    amp_levels = [-25, -30, -35, -40, -45, -50, -55]
    all_results["test1_amplitude"] = run_sweep(
        lambda v: dict(target_db=v, fd_hz=60.0, tap_delays=integer_tap_delays(cfg.FIXED_TAPS),
                       target_delay=cfg.TARGET_DELAY_SEPARATED),
        amp_levels, seed_offset=1,
    )

    print("\n=== Test 2: Number of delay taps ===")
    taps_levels = [4, 8, 12, 16, 18, 20, 21, 24]
    all_results["test2_ntaps"] = run_sweep(
        lambda v: dict(target_db=-30.0, fd_hz=60.0, tap_delays=integer_tap_delays(int(v)),
                       target_delay=cfg.TARGET_DELAY_SEPARATED),
        taps_levels, seed_offset=2,
    )

    print("\n=== Test 3: Speed with overlapping range ===")
    doppler_levels = [0, 0.5, 1, 2, 4, 10, 20, 50]
    all_results["test3_overlap_doppler"] = run_sweep(
        lambda v: dict(target_db=-20.0, fd_hz=v, tap_delays=integer_tap_delays(cfg.FIXED_TAPS),
                       target_delay=cfg.TARGET_DELAY_OVERLAP),
        doppler_levels, seed_offset=3,
    )

    print("\n=== Test 4: Flight direction relative to geometry ===")
    fd_max = 80.0
    angle_levels_deg = [0, 30, 60, 75, 85, 88, 89, 90]
    all_results["test4_angle"] = run_sweep(
        lambda theta: dict(target_db=-20.0, fd_hz=fd_max * math.cos(math.radians(theta)),
                            tap_delays=integer_tap_delays(cfg.FIXED_TAPS), target_delay=cfg.TARGET_DELAY_OVERLAP),
        angle_levels_deg, seed_offset=4,
    )

    elapsed = time.time() - t0
    print(f"\nTotal runtime: {elapsed:.1f} seconds")

    out_path = Path(__file__).resolve().parent.parent / "results_tests_1_4.json"
    out_path.write_text(json.dumps(all_results, indent=2))
    print(f"Saved results to {out_path}")


if __name__ == "__main__":
    main()
