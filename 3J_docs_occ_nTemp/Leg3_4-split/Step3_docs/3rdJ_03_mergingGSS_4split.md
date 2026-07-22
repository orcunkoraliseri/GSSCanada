# 3rdJ Step 3 — Merge & Tiling (Leg-3 Four-Channel Split)
### THE ONE REAL GSS BUILD DELTA — append AT_RETAIL to the list-driven tiler → `retail_30min.csv`

---

## Goal

Leg 2 turned tiling into a **list-driven** operation (`tile_work_to_30min`, cloned from the proven 9-channel co-presence tiler). Leg 3 appends **one channel** (audit §9.2: "adding a 4th channel is literally one list entry"): derive the FROZEN gated `AT_RETAIL` at episode level, tile it with the identical slot math, and emit `retail_30min.csv` (`RETL30_001..048`) as a **separate, purely additive CSV**. The residential and office paths — `hetus_30min.csv`, `copresence_30min.csv`, `work_30min.csv`, `merged_episodes.*`, `hetus_wide.csv` — must remain **bit-identical** to the shipped Leg-2 outputs (hash-gated): zero risk to shipped Leg-1/Leg-2 results.

**DESIGN FREEZE note:** per the pipeline Overview, *the Leg-3 build starts here* — Steps 1–2 required no GSS build.

## Reference

- Pipeline: `../3rdJ_00_4split_Occupancy_Pipeline.md` — STEP 3 (code block = the authoritative derivation + tiler pattern)
- Spec: `../4-channel_split.md` §2.3, §3.3
- Leg-2 counterpart (template): `../../Leg2_2-split/Step3_docs/3rdJ_03_mergingGSS.md` + `3rdJ_03_mergingGSS_2split.py` (Phase J `tile_work_to_30min`, lines ~1118–1261 of the Leg-2 lineage)
- Leg-2 validator: `../../Leg2_2-split/Step3_docs/3rdJ_03_mergingGSS_2split_val.py` (Section-9 template)
- OD-1 freeze: pipeline OPEN DECISIONS §1 (2026-07-02)

## Data Source Inventory

| Artifact | Path | Role |
|---|---|---|
| `main_{cycle}.csv`, `episode_{cycle}.csv` (harmonized) | `../../Leg2_2-split/Step2_docs/outputs_step2/` | read-only inputs (identical to Leg-2 Step-3 inputs) |
| Leg-2 `outputs_step3/` (5 legacy outputs + hashes) | `../../Leg2_2-split/Step3_docs/outputs_step3/` | bit-identity reference for Delta D |

## Proposed Changes (Leg-3 Deltas)

### Delta A — Port the Leg-2 merger verbatim → [NEW] `3rdJ_03_mergingGSS_4split.py`

Clone `3rdJ_03_mergingGSS_2split.py`; Phases A–J untouched (platform-detect paths updated to `Leg3_4-split/Step3_docs/`). Dynamic row count kept (Leg-2 Delta D: loud WARN, no abort, if N ≠ 64,061 HETUS rows).

### Delta B — Episode-level AT_RETAIL derivation (FROZEN rule, OD-1)

Derived **once, before the tiling loop**, next to the existing AT_WORK line:

```python
episodes_sorted["AT_WORK"]   = (episodes_sorted["occPRE"] == 2).astype(float)      # ✅ DONE (Leg 2)
episodes_sorted["AT_RETAIL"] = (
    (episodes_sorted["occPRE"] == 5) |               # location arm: Shopping
    ((episodes_sorted["occACT"] == 4) &
     episodes_sorted["occPRE"].isin({5, 9}))         # activity arm — FROZEN 2B gate (OD-1, 2026-07-02)
).astype(float)                                       # ⚠️ PLANNED (Leg 3)
```

### Delta C — One list entry + Phase K tiler

```python
BINARY_CHANNELS = ["AT_WORK", "AT_RETAIL"]   # restaurant (occPRE == 7) = one more entry, if ever
```

`tile_retail_to_30min()` = `tile_work_to_30min` pattern **unchanged in shape**:
- 4 AM-origin slot math `(startMin − 240) % 1440`
- binary majority vote `sum_present >= 2` (144 → 48 slots)
- **1/0 encoding** (match AT_HOME/AT_WORK — NOT the co-presence 1/2 scheme; state this explicitly per the Leg-2 lesson)
- empty-slot fill: ffill/bfill (one policy across all occupancy channels)
- → emits `RETL30_001..RETL30_048` → `outputs_step3/retail_30min.csv`, shape **(N, 49)**, occID order guaranteed identical to `hetus_30min.csv`

### Delta D — Bit-identity guarantee on the legacy outputs (the conservative-variant proof)

After the run, compute SHA-256 of the 5 legacy outputs (`merged_episodes.csv`, `merged_episodes.parquet`, `hetus_wide.csv`, `hetus_30min.csv`, `copresence_30min.csv`, `work_30min.csv` — 6 files) and compare to the Leg-2 `outputs_step3/` hashes. **Any mismatch = FAIL** — the retail delta must be purely additive. (If parquet hashes prove non-deterministic across pandas versions, fall back to column-wise value equality and record it.)

### Delta E — Validation twin

`validate_retail_30min()` cloned from `validate_work_30min()`: shape, occID alignment, values ∈ {0,1}, plus the retail-specific diurnal/night gates (full table in the val doc §11).

## Module Structure Summary

```
3rdJ_03_mergingGSS_4split.py        (Phases A–J verbatim Leg 2; + Delta B derivation;
                                     + Phase K tile_retail_to_30min; + Delta D hash gate)
3rdJ_03_mergingGSS_4split_val.py    (Leg-2 validator port + Section 11 AT_RETAIL + Section 12 bit-identity)
3rdJ_s3_4split_merge.sh             (sbatch wrapper — cluster run, -t 7-00:00:00)
3rdJ_s3_4split_valonly.sh           (sbatch wrapper — validator only)
outputs_step3/                      (7 files: 6 legacy-identical + retail_30min.csv; + reports)
```

## Expected Result

- `outputs_step3/retail_30min.csv` — (64,061 × 49), values {0,1}, 0 NaN.
- 6 legacy outputs byte-identical to Leg-2 (hash-verified).
- Expected rates (verify, don't force): weekday 12:00–14:00 weighted rate **0.06–0.10 per cycle** (dr_L3-06 CONFIRMED, central ≈ 0.079); all-day tiled mean modest (episode share ~2.1–2.3 % amplified by majority vote — retail episodes are short, so expect far less amplification than work's 7 %→14 %; a 2–8 % daily-mean band is the provisional project-chosen sanity bar, to be recorded at first run).
- `AT_RETAIL ∧ AT_HOME` ≈ 0 and `AT_RETAIL ∧ AT_WORK` ≈ 0 (mutually exclusive `occPRE` at episode level; only majority-vote edge effects can create cell-level overlap).

## Test Method

1. Local smoke: `py -3 -X utf8 3rdJ_03_mergingGSS_4split.py` on the Windows machine (inputs are local Leg-2 outputs).
2. Cluster (on the cluster, single line): `sbatch -p ps --mem=64G -t 7-00:00:00 3rdJ_s3_4split_merge.sh` — **sbatch only, never blocking srun; nothing else on the login node.**
3. `py -3 -X utf8 3rdJ_03_mergingGSS_4split_val.py` (or `3rdJ_s3_4split_valonly.sh` on the cluster) → target **0 FAIL**.
4. Inspect the headline diurnal chart per cycle × day-type: midday hump 12:00–14:00 weekday, Saturday peak 13:00–16:00, compressed QC Sunday, near-zero nights.

## Progress Log

*(append entries below — `### YYYY-MM-DD — <short description>`, with job IDs for cluster runs)*

### 2026-07-19 — Merger + retail tiler built & run LOCALLY; Delta-D bit-identity PASS

Built `3rdJ_03_mergingGSS_4split.py` (Leg-2 clone + Deltas B/C/D) + `..._val.py` + 2 sbatch wrappers. Ran locally (real Python `Python313`), ~3.5 min, no cluster needed. **All deltas closed:**

- **Delta B/C** — AT_RETAIL derived episode-level (FROZEN gated rule); Phase-K `tile_retail_to_30min` (work-tiler pattern unchanged: 4 AM-origin slot math, majority vote ≥2, **1/0 encoding**, ffill/bfill) → `outputs_step3/retail_30min.csv` **(64,061 × 49)**, RETL30_001..048, 0 NaN, values {0,1}, occID order identical to `hetus_30min.csv`. AT_RETAIL = 1.95% of cells.
- **Delta D — BIT-IDENTITY GATE PASS (the additive-safety proof).** All 6 legacy outputs SHA-256 identical to Leg-2 `outputs_step3/`, **including `merged_episodes.parquet`** (deterministic across this pandas/pyarrow): `merged_episodes.csv 32b9905d…`, `hetus_wide.csv b1bf8dc1…`, `hetus_30min.csv 6e3add7c…`, `copresence_30min.csv 9fe76f96…`, `work_30min.csv 9e5fd816…`, `merged_episodes.parquet 9b4046f1…`. Retail delta is purely additive — zero risk to shipped Leg-1/Leg-2 results.
- **Exclusivity** — AT_RETAIL∧AT_HOME = 0 cells, AT_RETAIL∧AT_WORK = 0 cells (mutually exclusive occPRE; no majority-vote edge overlap observed).
- **Weighted presence rate per cycle** — 2005 2.00% · 2010 2.14% · 2015 1.66% · 2022 1.51% (= the Step-2 gated episode-time shares; easing 2005→2022).

**11.8 all-day daily-mean band SET at first run:** observed 1.51–2.14% → episodes are short, majority-vote adds negligible amplification (contrast work's 7%→14%). The 2–8% provisional bar is generous; the real signal sits ~1.5–2.1% (recorded, WARN not FAIL). Validator verdict: **120 PASS / 13 WARN / 0 FAIL** (all 13 WARNs = rate-band edge breaches; Section-11 first-run rates recorded in the val-doc Progress Log). Reports at `outputs_step3/step3_validation_report.{html,txt}`.
