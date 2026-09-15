"""
Sweeps the CFAR threshold factor (alpha) across Test 1 and Test 2, and
spot-checks that Test 3/4's blind-zone result is independent of alpha.

Usage:
    python scripts/run_alpha_sweep.py
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
    alphas = [5.0, 7.0, 9.0, 12.0, 15.0]
    amp_levels = [-25, -30, -35, -40, -45, -50, -55]
    taps_levels = [4, 8, 12, 16, 18, 20, 21, 24]
    all_out = {}

    print("=== Test 1 (sensitivity) across alpha ===")
    test1_by_alpha = {}
    for alpha in alphas:
        res = run_sweep(
            lambda v: dict(target_db=v, fd_hz=60.0, tap_delays=integer_tap_delays(cfg.FIXED_TAPS),
                           target_delay=cfg.TARGET_DELAY_SEPARATED, alpha=alpha),
            amp_levels, seed_offset=int(alpha * 10) + 100, n_trials=15, verbose=False,
        )
        test1_by_alpha[str(alpha)] = res
        print(f"  alpha={alpha}: " + " ".join(f"{r['level']}dB:{r['rate'] * 100:.0f}%" for r in res))
    all_out["test1_by_alpha"] = test1_by_alpha

    print("\n=== Test 2 (delay taps) across alpha ===")
    test2_by_alpha = {}
    for alpha in alphas:
        res = run_sweep(
            lambda v: dict(target_db=-30.0, fd_hz=60.0, tap_delays=integer_tap_delays(int(v)),
                           target_delay=cfg.TARGET_DELAY_SEPARATED, alpha=alpha),
            taps_levels, seed_offset=int(alpha * 10) + 200, n_trials=15, verbose=False,
        )
        test2_by_alpha[str(alpha)] = res
        print(f"  alpha={alpha}: " + " ".join(f"{r['level']}taps:{r['rate'] * 100:.0f}%" for r in res))
    all_out["test2_by_alpha"] = test2_by_alpha

    print("\n=== Control: Test 3 and 4 at the extremes (alpha=5 and alpha=15) ===")
    doppler_levels = [0, 0.5, 1, 2, 4, 10, 20, 50]
    angle_levels_deg = [0, 30, 60, 75, 85, 88, 89, 90]
    fd_max = 80.0
    check = {}
    for alpha in [5.0, 15.0]:
        res3 = run_sweep(
            lambda v: dict(target_db=-20.0, fd_hz=v, tap_delays=integer_tap_delays(cfg.FIXED_TAPS),
                           target_delay=cfg.TARGET_DELAY_OVERLAP, alpha=alpha),
            doppler_levels, seed_offset=int(alpha * 10) + 300, n_trials=15, verbose=False,
        )
        res4 = run_sweep(
            lambda theta: dict(target_db=-20.0, fd_hz=fd_max * math.cos(math.radians(theta)),
                                tap_delays=integer_tap_delays(cfg.FIXED_TAPS),
                                target_delay=cfg.TARGET_DELAY_OVERLAP, alpha=alpha),
            angle_levels_deg, seed_offset=int(alpha * 10) + 400, n_trials=15, verbose=False,
        )
        check[str(alpha)] = {"test3": res3, "test4": res4}
        print(f"  alpha={alpha}: Test3 " + " ".join(f"{r['level']}Hz:{r['rate'] * 100:.0f}%" for r in res3))
        print(f"  alpha={alpha}: Test4 " + " ".join(f"{r['level']}deg:{r['rate'] * 100:.0f}%" for r in res4))
    all_out["test34_check"] = check

    elapsed = time.time() - t0
    print(f"\nTotal runtime: {elapsed:.1f} seconds")

    out_path = Path(__file__).resolve().parent.parent / "results_alpha_sweep.json"
    out_path.write_text(json.dumps(all_out, indent=2))
    print(f"Saved results to {out_path}")


if __name__ == "__main__":
    main()
