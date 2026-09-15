"""
Runs Test 5 of the PBR concept: probes what happens when clutter and the
target do not land exactly on the cancellation filter's delay grid, and
compares three grid resolutions (1.0, 0.5, 0.25 samples).

Usage:
    python scripts/run_test5_fractional.py
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pbr_sim import config as cfg
from pbr_sim.cancellation import fractional_tap_delays
from pbr_sim.trial import run_sweep


def main():
    t0 = time.time()
    offsets = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
    all_results = {}

    for spacing in [1.0, 0.5, 0.25]:
        tap_delays = fractional_tap_delays(cfg.MAX_TAP_DELAY, spacing)
        print(f"=== Grid resolution: {spacing} sample ({len(tap_delays)} delay taps, "
              f"covers 0-{tap_delays[-1]:.2f}) ===")
        res = run_sweep(
            lambda off: dict(target_db=-30.0, fd_hz=60.0, tap_delays=tap_delays,
                              target_delay=cfg.TARGET_DELAY_SEPARATED, offset=off),
            offsets, seed_offset=int(spacing * 100),
        )
        all_results[f"spacing_{spacing}"] = {"n_taps": len(tap_delays), "results": res}
        print()

    elapsed = time.time() - t0
    print(f"Total runtime: {elapsed:.1f} seconds")

    out_path = Path(__file__).resolve().parent.parent / "results_test5.json"
    out_path.write_text(json.dumps(all_results, indent=2))
    print(f"Saved results to {out_path}")


if __name__ == "__main__":
    main()
