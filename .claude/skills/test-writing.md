---
name: test-writing
description: Test conventions for eSim — narrowest meaningful check, schema/shape/range asserts, no full-pipeline runs in tests.
scope: builder
---

# Test Writing (eSim)

eSim is a research codebase, not a service. Tests exist to catch silent regressions in data shape, schedule contracts, and pipeline boundaries — not to verify scientific correctness, which is the reporter's job.

## Where tests live

- `eSim_tests/` — all new tests.
- One test file per source module: `test_<module>.py`.
- Fixtures and reference data go in `eSim_tests/fixtures/`. Keep fixtures small (≤ ~1 MB).

## Default test types

For most edits, write one of these — not all of them:

1. **Schema test.** After running the function, the output DataFrame has exactly these columns with these dtypes.
2. **Shape test.** Schedule array has length 8760 (or 17520, or 105120) and dtype is float.
3. **Range test.** All values fall in the documented physical range (occupancy ∈ [0, 1], temp setpoint ∈ [10, 35] °C, etc.).
4. **Round-trip test.** Read → write → read produces an identical object.
5. **Smoke test.** Function runs end-to-end on a tiny fixture without raising.

A schema + range test is usually enough for data-pipeline work. A shape test is mandatory for any edit touching `*_occToBEM.py`.

## What NOT to test

- Full-year EnergyPlus runs. Too slow, not deterministic across machines.
- C-VAE training convergence. Training is run from `run_step1.py`, not a test.
- The protected ML files (`eSim_datapreprocessing.py`, `eSim_dynamicML_mHead.py`, `eSim_dynamicML_mHead_alignment.py`). Test the modules that *call* them.
- External data sources. Never network-fetch in a test.

## Style

- `pytest`, no unittest classes.
- One assertion per test where practical; if multiple, they must check the same property.
- Test names describe the property: `test_schedule_has_8760_hours`, not `test_schedule`.
- Use `pytest.fixture` for shared setup; do not import test fixtures across files via `from test_x import ...`.
- Mark slow tests with `@pytest.mark.slow` and skip them in the default `pytest` invocation. The user opts in.

## Determinism

- Seed all randomness explicitly: `np.random.seed(...)`, `torch.manual_seed(...)`, `random.seed(...)`.
- A test that depends on a specific demographic stratum should also assert the row count of that stratum, so a future data-source change is caught immediately.

## Failure messages

A failing test should tell the reader what to fix. Prefer:

```python
assert len(arr) == 8760, f"Expected 8760 hours, got {len(arr)} (off by {len(arr) - 8760})"
```

over a bare `assert len(arr) == 8760`.

## Running

- Local default: `pytest eSim_tests/ -x -q` (locally).
- Cluster: tests do not run on Speed login node. If a test must run on the cluster, include it in the sbatch script for that task.