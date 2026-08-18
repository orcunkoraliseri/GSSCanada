# 4thJ_03b — null `loc_class` / `cop_*` structure measurement

Source: job **1255285**, COMPLETED, exit 0:0, elapsed 00:01:59, output
`/speed-scratch/o_iseri/4J_null_structure_1255285.out` (279 lines). Script:
`tools/4thJ_null_structure.py`. Table `/speed-scratch/o_iseri/4J/outputs_step2/run_20260817-strata/harmonised.parquet`,
2,024,068 rows, 51 columns. This document is a faithful transcription of that output for the author
to apply the pre-registered rule against. **It contains no recommendation and no verdict on D-S3-4 /
D-S3-5.**

---

## Part 1 — extent, confirmed

| country | rows | diaries | null_loc_rows | null_loc_diaries | null_cop_rows | null_cop_diaries | both_null |
|---|---:|---:|---:|---:|---:|---:|---:|
| ES | 446,547 | 19,140 | 0 | 0 | 0 | 0 | 0 |
| IT | 1,010,140 | 38,260 | 8,007 | 3,388 | 0 | 0 | 0 |
| UK | 567,381 | 15,854 | 16,793 | 5,485 | 68,464 | 9,298 | 4,804 |
| **TOTAL** | **2,024,068** | **73,254** | **24,800** | **8,873** | **68,464** | **9,298** | **4,804** |

`cop_*` flags always null together?  rows where SOME but NOT ALL six are null = **0** (confirmed
zero — every `cop_*` null row has all six flags null, none partial).

`CONFIRM-AGAINST-TASK-DOC`: loc_class null rows=24800 (expected 24800), loc diaries=8873 (expected
8873); cop null rows=68464 (expected 68464), cop diaries=9298 (expected 9298). **All four match
exactly.**

**Reading.** Null `loc_class` is **not** UK-only: Italy carries 8,007 rows in 3,388 diaries, the UK
16,793 rows in 5,485 diaries, Spain zero. Null `cop_*` **is** UK-only (0 in ES and IT). 4,804 rows are
null in both fields, all necessarily in the UK since that is the only country where `cop_*` nulls
occur at all.

---

## Part 2 — run structure

### `loc_class`

Diaries containing ≥1 null `loc_class` episode: 8,873 (all iterated).

| country | bucket | run length | n_runs | n_episodes |
|---|---|---|---:|---:|
| IT | head | 1 | 5 | 5 |
| IT | tail | 1 | 9 | 9 |
| IT | interior_agree | 1 | 911 | 911 |
| IT | interior_agree | 2 | 52 | 104 |
| IT | interior_agree | 3 | 8 | 24 |
| IT | interior_agree | 4-6 | 2 | 9 |
| IT | interior_disagree | 1 | 6,506 | 6,506 |
| IT | interior_disagree | 2 | 199 | 398 |
| IT | interior_disagree | 3 | 11 | 33 |
| IT | interior_disagree | 4-6 | 2 | 8 |
| UK | whole_diary | 2 | 1 | 2 |
| UK | whole_diary | 3 | 2 | 6 |
| UK | whole_diary | 7+ | 25 | 872 |
| UK | head | 1 | 114 | 114 |
| UK | head | 2 | 14 | 28 |
| UK | head | 3 | 18 | 54 |
| UK | head | 4-6 | 21 | 101 |
| UK | head | 7+ | 40 | 481 |
| UK | tail | 1 | 132 | 132 |
| UK | tail | 2 | 34 | 68 |
| UK | tail | 3 | 16 | 48 |
| UK | tail | 4-6 | 27 | 135 |
| UK | tail | 7+ | 64 | 975 |
| UK | interior_agree | 1 | 2,287 | 2,287 |
| UK | interior_agree | 2 | 489 | 978 |
| UK | interior_agree | 3 | 171 | 513 |
| UK | interior_agree | 4-6 | 158 | 744 |
| UK | interior_agree | 7+ | 82 | 804 |
| UK | interior_disagree | 1 | 5,145 | 5,145 |
| UK | interior_disagree | 2 | 713 | 1,426 |
| UK | interior_disagree | 3 | 177 | 531 |
| UK | interior_disagree | 4-6 | 132 | 599 |
| UK | interior_disagree | 7+ | 71 | 750 |

**Totals across countries (bucket only):**

| bucket | n_runs | n_episodes |
|---|---:|---:|
| whole_diary | 28 | 880 |
| head | 212 | 783 |
| tail | 282 | 1,367 |
| interior_agree | 4,160 | 6,374 |
| interior_disagree | 12,956 | 15,396 |

Sanity check OK: bucketed count 24,800 matches the direct null-row count.

**Duration (minutes) of null episodes, per bucket:**

| country | bucket | n | median | p90 | max |
|---|---|---:|---:|---:|---:|
| IT | head | 5 | 10.0 | 10.0 | 10.0 |
| IT | tail | 9 | 30.0 | 296.0 | 360.0 |
| IT | interior_agree | 1,048 | 10.0 | 30.0 | 210.0 |
| IT | interior_disagree | 6,945 | 10.0 | 30.0 | 270.0 |
| UK | whole_diary | 880 | 10.0 | 110.0 | 1,430.0 |
| UK | head | 778 | 15.0 | 180.0 | 440.0 |
| UK | tail | 1,358 | 20.0 | 180.0 | 1,250.0 |
| UK | interior_agree | 5,326 | 10.0 | 60.0 | 540.0 |
| UK | interior_disagree | 8,451 | 10.0 | 30.0 | 350.0 |
| **TOTAL** | whole_diary | 880 | 10.0 | 110.0 | 1,430.0 |
| **TOTAL** | head | 783 | 10.0 | 180.0 | 440.0 |
| **TOTAL** | tail | 1,367 | 20.0 | 180.0 | 1,250.0 |
| **TOTAL** | interior_agree | 6,374 | 10.0 | 50.0 | 540.0 |
| **TOTAL** | interior_disagree | 15,396 | 10.0 | 30.0 | 350.0 |

**Reading.** `interior_disagree` is the largest bucket by far (12,956 runs, 15,396 episodes, 62% of
all null `loc_class` episodes) — the neighbours exist but disagree, so this is not a "no data"
problem, it is a "conflicting data" problem. `interior_agree` (6,374 episodes, 25.7%) is the only
bucket the strict rule can use, and within it run length 1 dominates (2,287 of 4,160 UK runs; 911 of
973 IT runs). `whole_diary` + `head` + `tail` together are 3,030 episodes (12.2%) with no usable
neighbour on at least one side; `whole_diary` is UK-only and its durations run long (median 10 min
but p90 110, max 1,430 — i.e. entire diaries of ~24h can be null). Most null runs are short (10–30
min median), consistent with brief unrecorded gaps rather than systematically long missing blocks,
except `whole_diary`/`tail` where the max stretches to 20+ hours.

### `cop_*` (6-bit pattern)

Diaries containing ≥1 null `cop_*` episode: 9,298 (all iterated, all UK).

| country | bucket | run length | n_runs | n_episodes |
|---|---|---|---:|---:|
| UK | whole_diary | 2 | 16 | 32 |
| UK | whole_diary | 3 | 4 | 12 |
| UK | whole_diary | 4-6 | 2 | 11 |
| UK | whole_diary | 7+ | 72 | 1,590 |
| UK | head | 1 | 857 | 857 |
| UK | head | 2 | 122 | 244 |
| UK | head | 3 | 72 | 216 |
| UK | head | 4-6 | 96 | 448 |
| UK | head | 7+ | 71 | 870 |
| UK | tail | 1 | 1,435 | 1,435 |
| UK | tail | 2 | 367 | 734 |
| UK | tail | 3 | 187 | 561 |
| UK | tail | 4-6 | 157 | 759 |
| UK | tail | 7+ | 155 | 2,561 |
| UK | interior_agree | 1 | 14,466 | 14,466 |
| UK | interior_agree | 2 | 2,708 | 5,416 |
| UK | interior_agree | 3 | 1,194 | 3,582 |
| UK | interior_agree | 4-6 | 1,010 | 4,641 |
| UK | interior_agree | 7+ | 409 | 3,961 |
| UK | interior_disagree | 1 | 10,136 | 10,136 |
| UK | interior_disagree | 2 | 2,399 | 4,798 |
| UK | interior_disagree | 3 | 1,037 | 3,111 |
| UK | interior_disagree | 4-6 | 907 | 4,211 |
| UK | interior_disagree | 7+ | 367 | 3,812 |

**Totals across countries (bucket only):**

| bucket | n_runs | n_episodes |
|---|---:|---:|
| whole_diary | 94 | 1,645 |
| head | 1,218 | 2,635 |
| tail | 2,301 | 6,050 |
| interior_agree | 19,787 | 32,066 |
| interior_disagree | 14,846 | 26,068 |

Sanity check OK: bucketed count 68,464 matches the direct null-row count.

**Duration (minutes) of null episodes, per bucket:**

| bucket | n | median | p90 | max |
|---|---:|---:|---:|---:|
| whole_diary | 1,645 | 20.0 | 180.0 | 1,430.0 |
| head | 2,635 | 40.0 | 230.0 | 660.0 |
| tail | 6,050 | 50.0 | 290.0 | 1,250.0 |
| interior_agree | 32,066 | 20.0 | 90.0 | 720.0 |
| interior_disagree | 26,068 | 10.0 | 60.0 | 720.0 |

(Per-country breakdown is identical to the TOTAL row since `cop_*` nulls are UK-only.)

**Reading.** `interior_agree` is the largest bucket (32,066 episodes, 46.8% of all null `cop_*`
episodes), but within it more than half the runs are length 1 (14,466 of 19,787 runs), and a
substantial tail runs long (409 runs of length 7+, 3,961 episodes). `interior_disagree` is nearly as
large (26,068 episodes, 38.1%). `head`+`tail`+`whole_diary` together are 10,330 episodes (15.1%) with
no two-sided neighbour. Durations are systematically longer than for `loc_class` (medians 10–50 min
vs 10–20 min, and `tail`/`head` p90 in the 230–290 min range) — the `cop_*` gaps tend to be longer
blocks, not brief single-episode drops.

---

## Part 3 — is the missingness structured?

### `loc_class` null prevalence by `act` (top 15 by null count)

| act | null_n | share_of_null | null_rate_in_code |
|---|---:|---:|---:|
| 936 | 2,789 | 11.25% | 5.11% |
| 910 | 2,396 | 9.66% | 4.83% |
| 951 | 2,113 | 8.52% | 6.25% |
| 960 | 1,673 | 6.75% | 5.46% |
| 950 | 1,584 | 6.39% | 6.98% |
| 011 | 1,162 | 4.69% | 0.55% |
| 938 | 925 | 3.73% | 6.30% |
| 900 | 750 | 3.02% | 7.51% |
| 031 | 716 | 2.89% | 0.33% |
| 021 | 688 | 2.77% | 0.25% |
| 829 | 611 | 2.46% | 1.25% |
| 999 | 581 | 2.34% | 4.95% |
| 972 | 385 | 1.55% | 12.08% |
| 942 | 384 | 1.55% | 7.44% |
| 920 | 377 | 1.52% | 6.47% |

### `loc_class` null prevalence by `strat_day_type` / `strat_age_band`

| strat_day_type | null_n | share_of_null | null_rate_in_stratum |
|---|---:|---:|---:|
| weekday | 12,175 | 49.09% | 1.33% |
| saturday | 7,121 | 28.71% | 1.24% |
| sunday | 5,504 | 22.19% | 1.03% |

| strat_age_band | null_n | share_of_null | null_rate_in_stratum |
|---|---:|---:|---:|
| 45-54 | 4,382 | 17.67% | 1.17% |
| 35-44 | 4,190 | 16.90% | 1.20% |
| 25-34 | 3,970 | 16.01% | 1.56% |
| 55-64 | 3,868 | 15.60% | 1.28% |
| 15-24 | 3,282 | 13.23% | 1.63% |
| 65-74 | 2,381 | 9.60% | 0.93% |
| 11-14 | 1,484 | 5.98% | 1.80% |
| 75+ | 1,243 | 5.01% | 0.61% |

### `cop_*` null prevalence by `act` (top 15 by null count)

| act | null_n | share_of_null | null_rate_in_code |
|---|---:|---:|---:|
| 011 | 10,570 | 15.44% | 4.97% |
| 021 | 6,086 | 8.89% | 2.26% |
| 031 | 5,685 | 8.30% | 2.63% |
| 829 | 5,426 | 7.93% | 11.09% |
| 999 | 3,816 | 5.57% | 32.52% |
| 111 | 3,548 | 5.18% | 5.44% |
| 311 | 3,084 | 4.50% | 2.72% |
| 361 | 1,491 | 2.18% | 3.68% |
| 910 | 1,348 | 1.97% | 2.72% |
| 321 | 1,334 | 1.95% | 2.24% |
| 950 | 1,215 | 1.77% | 5.36% |
| 312 | 1,135 | 1.66% | 1.80% |
| 531 | 1,107 | 1.62% | 2.49% |
| 936 | 1,056 | 1.54% | 1.93% |
| 381 | 1,035 | 1.51% | 3.12% |

### `cop_*` null prevalence by `strat_day_type` / `strat_age_band`

| strat_day_type | null_n | share_of_null | null_rate_in_stratum |
|---|---:|---:|---:|
| weekday | 35,394 | 51.70% | 3.87% |
| saturday | 16,900 | 24.68% | 2.94% |
| sunday | 16,170 | 23.62% | 3.03% |

| strat_age_band | null_n | share_of_null | null_rate_in_stratum |
|---|---:|---:|---:|
| 45-54 | 12,284 | 17.94% | 3.28% |
| 25-34 | 10,445 | 15.26% | 4.11% |
| 35-44 | 10,159 | 14.84% | 2.92% |
| 55-64 | 9,369 | 13.68% | 3.09% |
| 15-24 | 8,457 | 12.35% | 4.20% |
| 65-74 | 8,408 | 12.28% | 3.29% |
| 75+ | 5,158 | 7.53% | 2.52% |
| 11-14 | 4,184 | 6.11% | 5.09% |

**Reading.** No single activity code carries a majority of the null rows for either field — the
top code is 11.25% of null `loc_class` rows (936) and 15.44% of null `cop_*` rows (011); the top 5
codes together cover roughly 43% and 47% respectively. So missingness is spread across many activity
codes by raw count, not concentrated on one.

However, `null_rate_in_code` (share missing *within* that code, not share of all nulls) shows real
structure: for `cop_*`, code `999` is missing in **32.52%** of its own rows — far above every other
code in the top 15 (next highest is `829` at 11.09%) and far above the overall UK `cop_*` null rate
(~3.87% on weekdays). For `loc_class`, code `972` reaches **12.08%** and `900` reaches **7.51%**,
both well above the ~1.0–1.6% baseline seen in the day-type/age-band tables. `strat_day_type` and
`strat_age_band` breakdowns show no comparable concentration — null rates by day type and age band
stay within a narrow band (roughly 1.0–1.8% for `loc_class`, 2.5–5.1% for `cop_*`) and track diary
volume rather than a strong stratum effect.

🔴 The task doc flags travel codes specifically as a candidate mechanism (location recoverable from
activity rather than from neighbours). This output does not carry an activity-code-to-label mapping,
so **which of these numeric codes are travel codes was not checked here** — see WHAT I DID NOT
VERIFY. The elevated within-code null rate for `999` (`cop_*`) and `972`/`900` (`loc_class`) is worth
the author's attention as a possible structural signal, whatever the codes turn out to mean.

---

## Part 4 — coverage under the pre-registered strict rule

Rule (manager's, pre-registered, not applied here): imputation adopted only if it covers ≥99% of
that field's null episodes under `interior_agree` with run length ≤ 2; otherwise the explicit
`unknown` / "not reported" class covers 100% of them.

| field | imputable (strict rule) | % of all null episodes | residual | threshold |
|---|---:|---:|---:|---:|
| `loc_class` | 4,280 | 17.26% | 20,520 | 99% |
| `cop_*` | 19,882 | 29.04% | 48,582 | 99% |

No recommendation and no verdict follow from this table. The author applies the pre-registered rule.

---

## WHAT I DID NOT VERIFY

- Did not independently re-derive the four carried-over Part 1 numbers before this job ran; the
  job's own `CONFIRM-AGAINST-TASK-DOC` line (re-derived live from the parquet) matches them exactly,
  and that line is what is quoted above — not a second independent derivation by this agent.
- Did not check whether `episode_index` is contiguous / gap-free within a diary. Run-finding (and
  therefore every `head`/`tail`/`interior`/`whole_diary` classification in Part 2) assumes that
  sorting by `episode_index` gives true clock adjacency. If `episode_index` ever has gaps that skip
  an episode without a corresponding row, some episodes classified as "interior" could in fact be
  adjacent to a different, unrecorded episode in real time. Carried forward unresolved from the prior
  implementation doc.
- Did not verify `strat_day_type` / `strat_age_band` value sets or cardinality beyond what Part 3's
  own tables show (8 age bands, 3 day types, both summing correctly to the totals reported).
- Did not map `act` codes to human-readable activity labels or a HETUS/national codebook. The
  observation that codes `999` (`cop_*`) and `972`/`900` (`loc_class`) have an elevated
  null-rate-within-code is reported purely numerically; whether these specific codes are travel
  codes, "not elsewhere classified" codes, or something else was not checked.
- Did not test the script against a synthetic fixture before this run; this was its first execution,
  against the full 2,024,068-row table.
- Did not inspect the job's stdout beyond what is transcribed above (pip-install and environment
  banner lines, and the two internal sanity-check confirmations, are omitted from the tables but were
  read and are unremarkable — no warnings or errors present).
