"""t18_filter.py -- T18 Arm N input: filter augmented_diaries.csv to CYCLE_YEAR==2022.

Task doc: 2026-09-15_T18_wp1_rebuild_2022_build.md, Brief step 2/4.
Reads the full augmented_diaries.csv (192,183 rows, all cycles) staged at
T18/input/augmented_diaries.csv and writes the CYCLE_YEAR==2022 subset (real +
synthetic kept; expected 37,008 rows = 12,336 real + 24,672 synthetic per
outputs_step6/improvement/step6_improvement_notes.md:852, cited in
2026-09-15_T13_wp1_rebuild_2022_reading.md Q4) to Arm N's own staged input tree.
Prints counts by IS_SYNTHETIC so the ACTUAL count is recorded on a compute node
(per task doc design: "record the actual count, filtered on a compute node").

No pipeline source file is imported, edited, or run by this script.

Run: /speed-scratch/o_iseri/envs/step4/bin/python t18_filter.py
"""
import os
import time
import pandas as pd
from pathlib import Path

WORKDIR = Path("/speed-scratch/o_iseri/2J_revision/T18")
IN_PATH = WORKDIR / "input" / "augmented_diaries.csv"
OUT_PATH = WORKDIR / "arm_N" / "repo" / "inputs" / "augmented_diaries.csv"

t0 = time.time()


def log(msg):
    print(f"[{time.time() - t0:7.1f}s] {msg}", flush=True)


def main():
    if not IN_PATH.exists():
        raise FileNotFoundError(f"Missing input: {IN_PATH}")
    log(f"input OK: {IN_PATH} ({IN_PATH.stat().st_size:,} bytes)")
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    log("loading augmented_diaries.csv (full, all columns, all cycles) ...")
    df = pd.read_csv(IN_PATH, low_memory=False)
    log(f"loaded {len(df):,} rows x {df.shape[1]} cols")

    assert "CYCLE_YEAR" in df.columns, "CYCLE_YEAR column missing"
    assert "IS_SYNTHETIC" in df.columns, "IS_SYNTHETIC column missing"

    cycle_counts = df["CYCLE_YEAR"].value_counts().sort_index()
    log("input CYCLE_YEAR counts (all cycles, for the record):")
    for k, v in cycle_counts.items():
        log(f"  {int(k)}: {v:,}")

    sub = df[df["CYCLE_YEAR"] == 2022].copy()
    log(f"CYCLE_YEAR==2022 rows: {len(sub):,} (expected ~37,008 per T13 Q4)")

    counts = sub["IS_SYNTHETIC"].value_counts().sort_index()
    log("2022-only IS_SYNTHETIC counts (this is Arm N's donor pool):")
    for k, v in counts.items():
        log(f"  IS_SYNTHETIC={int(k)}: {v:,}")

    log(f"writing {OUT_PATH} ...")
    tmp = str(OUT_PATH) + ".tmp"
    sub.to_csv(tmp, index=False)
    n_written = sum(1 for _ in open(tmp, encoding="utf-8")) - 1
    if n_written != len(sub):
        os.remove(tmp)
        raise RuntimeError(
            f"Row count mismatch after write: {n_written} != {len(sub)}. "
            f"Truncated tmp removed; {OUT_PATH} not written."
        )
    os.replace(tmp, str(OUT_PATH))
    log(f"WROTE {OUT_PATH}: {n_written:,} rows -- WRITE VERIFIED OK")
    log(f"output size: {OUT_PATH.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
