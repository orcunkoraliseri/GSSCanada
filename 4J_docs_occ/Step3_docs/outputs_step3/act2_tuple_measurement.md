# ACT2 tuple-cost measurement (work item 3.2-bis)

**Status: transcription, not a re-run.** Task A's deliverable was left unwritten when Step 3 moved to
Task B. This file transcribes Speed job **1255237** (`4thJ_act2_measure.py`, second NA-fix, the run
that actually completed) exactly as printed in
`Step3_docs/impl/2026-08-17_na-fix-rerun.md` and the raw job output
`/speed-scratch/o_iseri/4J_act2_1255237.out` (re-fetched over `ssh`/read-only to recover the exact
Part A strings, which the implementation doc summarised but did not quote verbatim). **No number below
was recomputed; all are copied.**

D-S3-2 has already decided this question — `ACT2` **enters** the tuple, in the empty-field-before-LOC
form (candidate 3) — so this file is now a record of the measurement that decision was made on, not an
open question.

## Tokenizer and job

- Tokenizer / vocabulary: OLMo / dolma2 BPE. Model id actually loaded: `allenai/OLMo-2-0425-1B` — a
  **stand-in** for the paper's backbone (`allenai/Olmo-3-1025-7B`), stated as such and not re-derived:
  it carries an identical vocabulary and is far smaller to download.
- vocab_size reported by the tokenizer: 100278. transformers version 5.15.0.
- Speed job ID: **1255237** (`sbatch -p ps --mem=16G -t 7-00:00:00`, COMPLETED, elapsed 00:01:38, exit
  0). venv `/speed-scratch/o_iseri/envs/4j_tok`. Script run: `/speed-scratch/o_iseri/4thJ_act2_measure.py`
  (a copy of `tools/4thJ_act2_measure.py`, second NA-fix applied at line 335 — see
  `Step3_docs/impl/2026-08-17_na-fix-rerun.md` for the fix itself).
- Data: `/speed-scratch/o_iseri/4J/outputs_step2/run_20260817-strata/harmonised.parquet`, 2,024,068
  rows, 73,254 distinct diaries, columns read: `country, hid, pid, diary_day, episode_index,
  duration_min, act, loc_class, act2, cop_alone, cop_partner, cop_children, cop_parent, cop_other_hh,
  cop_other_persons`.
- Bit order for `COP` packing read live from `crosswalk_copresence.csv`'s `bit_position` column, never
  hard-coded: `{'cop_alone': 0, 'cop_partner': 1, 'cop_children': 2, 'cop_parent': 3, 'cop_other_hh': 4,
  'cop_other_persons': 5}`.

## Sentinel verification

`43` distinct legal `ACT2` target codes read live from `crosswalk_activity_secondary.csv`'s
`target_code_2d` column:

```
01 02 03 11 12 13 20 21 22 30 31 32 33 34 35 36 37 38 39 41 42 43 51 52 53 61 62 63 71 72 73
81 82 83 90 91 92 93 94 95 96 97 99
```

**`'98'` is NOT in this list** — verified before use, so the sentinel does not repeat the Spain `999`
near-miss (a perturbation that was secretly a legal code and tested nothing).

## Five candidate forms

| # | Form | Absent secondary spelled as |
|---|---|---|
| 0 | `DUR,ACT,LOC,COP` — baseline, four elements | — |
| 1 | `DUR,ACT,ACT2,LOC,COP` | declared 2-digit sentinel `'98'` |
| 2 | `DUR,ACT,LOC,COP,ACT2` | declared 2-digit sentinel `'98'` |
| 3 | `DUR,ACT,ACT2,LOC,COP` | empty field |
| 4 | `DUR,ACT,LOC,COP,ACT2` | empty field |

## Sample

2,500 diaries, seed 42, drawn from the full 73,254. Episodes in sample: 69,418.
Per-country diary counts: `{'IT': 1313, 'ES': 648, 'UK': 539}`.
Sampled episodes: `act2` present = 16,001, absent (null-or-blank) = 53,417.
2,589 sampled episodes carried a null `cop_*` flag (treated as bit-unset, **not dropped**).

**LOC alphabet used throughout (the correct, current one):** `at_home`, `other_place`,
`private_transport`, `public_transport` — the four `crosswalk_location.csv` `target_class` strings, read
live from `harmonised.parquet`'s own `loc_class` column, not a numeric placeholder.

## PART A — in-situ worst-case sweep

Every legal `ACT2` code, plus the absent case, swept against a representative episode
(`DUR=30, ACT=311, COP=22`) across every observed `loc_class` value. Reported: the maximum token count
and the exact string that reaches it.

| candidate | form | worst case (tokens) | argmax `loc` | argmax `act2` | exact string |
|---|---|---:|---|---|---|
| 0 | `DUR,ACT,LOC,COP` — baseline, four elements | **9** | `at_home` | `'01'` (n/a — no ACT2 field) | `30,311,at_home,22;` |
| 1 | `DUR,ACT,ACT2,LOC,COP`, sentinel `'98'` | **11** | `at_home` | `'01'` | `30,311,01,at_home,22;` |
| 2 | `DUR,ACT,LOC,COP,ACT2`, sentinel `'98'` | **11** | `at_home` | `'01'` | `30,311,at_home,22,01;` |
| 3 | `DUR,ACT,ACT2,LOC,COP`, empty field | **11** | `at_home` | `'01'` | `30,311,01,at_home,22;` |
| 4 | `DUR,ACT,LOC,COP,ACT2`, empty field | **11** | `at_home` | `'01'` | `30,311,at_home,22,01;` |

Per episode, `ACT2` costs a flat **+2 tokens** in every placement and every absent-encoding — Part A
cannot discriminate among candidates 1–4 at all. That discrimination only shows up per diary (Part B),
because 77 % of episodes have no secondary activity and the absent-encoding therefore dominates.

## PART B — real diaries (n=2,500), median/p99/max tokens per diary

| cand | form | n | median | p99 | max |
|---|---|---:|---:|---:|---:|
| 0 | `DUR,ACT,LOC,COP` — baseline, four elements | 2500 | 225.0 | 559.0 | 716 |
| 1 | `DUR,ACT,ACT2,LOC,COP` — absent = sentinel `'98'` | 2500 | 275.0 | 685.0 | 877 |
| 2 | `DUR,ACT,LOC,COP,ACT2` — absent = sentinel `'98'` | 2500 | 275.0 | 685.0 | 878 |
| 3 | `DUR,ACT,ACT2,LOC,COP` — absent = empty field | 2500 | 238.0 | 580.0 | 751 |
| 4 | `DUR,ACT,LOC,COP,ACT2` — absent = empty field | 2500 | 257.0 | 627.1 | 808 |

**Against `G3.5`'s pre-registered band as it stood at the time of this job** (median ≤ 220, p99 ≤ 400 —
the band that rejected six-character binary `COP` packing at 225, before any real record existed):
every candidate, including the no-`ACT2` baseline, **EXCEEDS** the band on both median and p99. The
band was broken before `ACT2` was considered at all — the same finding appeared independently in the
`COP` re-verification job (1255223). `G3.5`'s band was subsequently re-based by the author (D-S3-3,
2026-08-17 night) to median ≤ 300 / p99 ≤ 700 / max ≤ 1024, for reasons recorded in
`4thJ_03_serialisation.md`'s "2026-08-17 (night)" entry — that re-basing is a separate decision from
`ACT2` entering the tuple and is not re-derived here.

## What decided D-S3-2

- **The `'98'`-sentinel forms (1, 2) cost +50 tokens/diary median (+22 % over the 225.0 baseline)** —
  paid on every one of the 53,417 absent episodes in the sample.
- **The empty-field form placed before `LOC` (candidate 3) costs +13 tokens/diary median (+5.8 %),
  +21 at p99** — the cheapest way to admit `ACT2`.
- Placement matters only for the empty-field forms: before `LOC` (+13) is cheaper than after `COP`
  (+32). The two sentinel forms are identical (275.0) because the field is never empty in that
  encoding, so position cannot change how the BPE merges around it.

The author decided (D-S3-2, 2026-08-17 evening): **`ACT2` enters the tuple as an empty-field slot
before `LOC`** — candidate 3, `DUR,ACT,ACT2,LOC,COP` — on this measurement.

## Note on baseline discrepancy between the two 2026-08-17 jobs

This job (1255237) reports a no-`ACT2` baseline of 225.0/559.0; the `COP` re-verification job (1255223)
reports 217.5/519.1 for its cheapest candidate. **Not a contradiction** — the two jobs sample different
diary populations: `4thJ_cop_reverify.py` excludes the 8,873 diaries containing a null-`loc_class`
episode, while `4thJ_act2_measure.py` does not. The two tables are not to be read as one table.

## Deliverables this file closes

The table, the exact in-situ strings, the sweep, and the worst case — all above, transcribed from job
1255237 and its Part A/B stdout, no number recomputed.
