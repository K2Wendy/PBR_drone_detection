# PBR Concept Simulation

A small, self-contained simulation of the signal processing chain for a
DVB-T2-based passive bistatic radar (PBR) drone-detection concept:
reference/surveillance signal generation, DSI cancellation (integer or
fractional delay grid), the delay/Doppler energy map, and CA-CFAR
threshold detection.

## Project layout

```
pbr_sim/                   the simulation package (import this, don't run it directly)
    config.py               shared constants (scene, search grids, CFAR parameters)
    signal.py                reference/surveillance signal generation, fractional shift
    cancellation.py          DSI cancellation (integer and fractional delay grids)
    caf.py                    delay/Doppler energy map (cross-ambiguity function)
    cfar.py                   CA-CFAR threshold detection
    trial.py                  unified single-trial runner + generic parameter sweep

scripts/                    runnable drivers, one per test
    run_tests_1_4.py          Test 1 (sensitivity), 2 (delay taps), 3 (overlap speed), 4 (flight angle)
    run_test5_fractional.py   Test 5 (fractional delay grid resolution)
    run_alpha_sweep.py        CFAR threshold-factor (alpha) sensitivity analysis

requirements.txt
README.md
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running the tests

From the repository root:

```bash
python scripts/run_tests_1_4.py
python scripts/run_test5_fractional.py
python scripts/run_alpha_sweep.py
```

Each script prints progress to the console and writes its results to a
JSON file in the repository root (`results_tests_1_4.json`,
`results_test5.json`, `results_alpha_sweep.json`).

## What each test demonstrates

- **Test 1 (sensitivity):** how weak a target reflection can be, relative
  to the direct signal, before CA-CFAR detection fails.
- **Test 2 (delay taps):** how many delay taps the cancellation filter
  needs to fully remove the clutter model's multipath spread.
- **Test 3 (overlap speed):** what happens when the target's range
  coincides with the clutter/filter span and its speed approaches zero --
  the filter can no longer distinguish a stationary target from static
  clutter.
- **Test 4 (flight angle):** the same phenomenon as Test 3, reached via
  bistatic geometry instead of literal zero speed -- a fast-moving target
  flying perpendicular to the transmitter-target-receiver bisector can
  present an apparent Doppler of zero.
- **Test 5 (fractional delay grid):** a target or clutter path essentially
  never lands exactly on an integer sample delay in reality; this test
  shows that an integer-only tap grid leaves a large residual clutter
  floor as the true delay drifts off-grid, and that a modest refinement
  (0.5-sample spacing) removes the effect almost entirely.
- **Alpha sweep:** the CFAR threshold factor trades detection sensitivity
  against false-alarm rate; this script quantifies that trade-off for
  Tests 1 and 2, and confirms Tests 3/4's blind zone is independent of it.

## Reproducibility

Every sweep seeds its own `numpy.random.default_rng` per parameter level,
so re-running a script reproduces the same trials and results.

## Notes

This is a simplified, illustrative simulation for concept-evaluation
purposes, not a validated or production-ready detector implementation.
See the accompanying concept document for full methodology, results, and
interpretation.
