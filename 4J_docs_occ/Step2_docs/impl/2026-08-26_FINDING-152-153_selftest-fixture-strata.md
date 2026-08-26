# FINDING 152 discharged, FINDING 153 filed — the `--selftest` fixture now carries the strata

**Date:** 2026-08-26
**Tool:** `tools/4thJ_gates_step2.py` (backup of the pre-patch file: `tools/4thJ_gates_step2.py.bak_f152`)
**Scope:** additive, CPU-only, local. `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` untouched.
**Nothing here moves a threshold, edits a checker, or changes any gate's verdict on real data.**

---

## 1. The defect (FINDING 152, filed 2026-08-26 during the `D-S2-20` work)

`build_synthetic_country` / `build_fixtures` predate the D-S2-18 round and never
built the five `STRATA_COLUMNS` or their six `STRATA_RAW_COLUMNS`. The first
strata perturbation therefore did not report a missing-column FAIL — it
**crashed**:

```
File "tools/4thJ_gates_step2.py", line 1517, in apply_perturbation
    current = h.loc[mask_diary, "strat_day_type"].dropna()
KeyError: 'strat_day_type'
```

Seen firing on the unpatched file before any edit was made.

**A crash is not a FAIL.** Because `run_sweep` iterates `PERTURBATIONS` in order
and the crash is unhandled, everything after `strat_day_type_wrong_grain` was
unreachable — `italy_hh_type_prefix`, `italy_age_band_split`, and **all six
sweep-level acceptance tests**. The battery reported nothing at all, not a
partial result.

🔴 The tool's own `--help` text asserted the opposite — *"the synthetic fixture
was NOT extended with strat_* columns for the D-S2-18 round, so G2.17 always
reports missing-column FAILs under --selftest"*. G2.17 **does** carry
`missing_cols` handling that would have produced exactly that FAIL, so the
written expectation was reasonable; it was simply never run. The help text has
been corrected rather than deleted, so the superseded claim stays visible.

## 2. The fix — four additive edits

| # | where | what |
|---|---|---|
| 1 | new `_strata_pairs_for_country()` above `build_synthetic_country` | reads real `(target_band, source_value)` pairs out of the shipped `crosswalk_strata.csv` |
| 2 | `build_synthetic_country`, after the weight columns | assigns the 5 strata + 6 raw carriers, **once per diary** |
| 3 | `build_fixtures`, after `final_cols` is composed | appends the strata so the `harm[final_cols]` reindex stops dropping them |
| 4 | `build_fixtures`, at the Step 1 write | strips the strata back off before `episodes_<country>.parquet` |

Two design points that are load-bearing, not cosmetic:

* **Nothing is invented.** Every band and every raw code is read out of the real
  `crosswalk_strata.csv`. `V2.j` FAILs on any parquet band absent from that file
  and `G2.18 (b)` reads the same file, so a made-up band would have manufactured
  a defect the real table does not have.
* **Assignment is per person-day, not per episode.** `G2.17 (b)` audits exactly
  that grain. See the control in §4.
* **Edit 4 exists because the real `episodes_<country>.parquet` carries no
  `strat_*` column** — verified against all three: Spain has `EDAD`, the UK and
  Italy have nothing. Banding is Step 2's own work item, so a Step 1 fixture
  shipping harmonised bands would misrepresent the input under audit.

## 3. Result — the battery now runs end to end

At `--n-diaries 1200` (the default):

| acceptance test | result |
|---|---|
| 1 — all perturbations ran; `null` moved nothing | **22 ran: True**, null moved nothing: **True** |
| 2 — each perturbation felled its named gate | **21 FIRED**, 1 DID NOT FIRE (`shift_sleep_budget` → G2.10, NOT CHECKED by design) |
| 2b — M-7 sub-clause attribution | **4 of 4 FIRED**, every counter from a baseline of 0 |
| 3 — must-stay-clean | **1 violation** (see §5) |
| 3b — sub-clause must-stay-clean | **0 violations** |
| 4 — coverage | gates that PASS at baseline and were NEVER made to fall: **`[]`** → **PASS** |
| 5 — NOT CHECKED carry a reason | `['G2.10']`, reason printed, excluded from the 17-gate tally |

The four strata rows, all from a clean baseline:

```
null_strat_econ_status     -> G2.17 (a)  baseline_counter=0 perturbed_counter=13 [FIRED]
strat_day_type_wrong_grain -> G2.17 (b)  baseline_counter=0 perturbed_counter=1  [FIRED]
italy_hh_type_prefix       -> G2.18 (a)  baseline_counter=0 perturbed_counter=6  [FIRED]
italy_age_band_split       -> G2.18 (b)  baseline_counter=0 perturbed_counter=1  [FIRED]
```

`G2.17` and `G2.18` both **PASS at baseline** on the fixture, so all four rows
are falsifiable at gate level — not merely at sub-clause level.

## 4. Controls — the fixture was seen failing before it was trusted

A validation fixture written carelessly passes silently. Three controls were
injected into throwaway copies of the tool and run; the copies were deleted.

| control | change | result |
|---|---|---|
| **A** | assign strata **per episode** instead of per diary | 🔴 **G2.17 FAILs at baseline** — `(b) non-constant groups = 600`. The whole `G2.17` row goes FAIL in every column, so both G2.17 perturbations become **unfalsifiable**: they cannot fell a gate that is already red. This is precisely the silent-pass failure mode, and the per-diary assignment is what avoids it. |
| **B** | stop excluding the `unknown` band (all three countries) | ⚪ **escalations = 0, G2.18 still PASS.** The control did **not** fire. |
| **C** | include `unknown` for `uk`/`it` but **not** `es` — i.e. asymmetric | 🔴 **escalations = 4, G2.18 FAIL at baseline**, both `italy_*` rows unfalsifiable at gate level. |

🔴 **Control B falsified the reason first written into the code comment.** The
first draft said the `unknown` exclusion was needed because "any unknown share
would fire the escalation". That is wrong. What `G2.18`'s D-S2-19 clause reacts
to is **asymmetry**, not presence — with all three countries carrying equal
shares, `0.1667 > 1.667` is false and the clause is silent. Excluding `unknown`
is simply the cheapest guarantee of symmetry. The comment was corrected to state
the three measured outcomes rather than the assumption. This is the same shape
as **FINDING 151**: the ten-times multiplier is not doing the discriminating
work it appears to be doing.

## 5. 🔴 FINDING 153 — one `must_stay_clean` verdict is a function of `--n-diaries`

`round_duration` is listed as `must_fail: G2.4, must_stay_clean: [G2.3]`. It
corrupts **exactly one diary** by a fixed absolute amount. `G2.4` counts diaries
(`diaries not summing to 1440 = 1`) and is therefore size-invariant. `G2.3` is a
**relative** statistic against the whole-country total, so the same fixed defect
is diluted by the number of diaries:

| `--n-diaries` | G2.3 max relative diff | vs the 1e-6 threshold | verdict |
|---|---|---|---|
| 60 | 1.1574074e-05 | 11.6× over | 🔴 **FAIL** — counted as a clean violation |
| 690 | 1.0064412e-06 | 1.006× over | 🔴 **FAIL** |
| 700 | 9.9206349e-07 | 0.992× under | 🟢 **PASS** |
| 1200 (default) | 5.7870370e-07 | 0.579× under | 🟢 **PASS** |

The ratio is exactly linear: `1.1574e-05 / 5.787e-07 = 20.0 = 1200 / 60`. The
crossover sits at `n ≈ 694`, and it was **measured** at 690 and 700, not only
derived.

**What this means.** The battery's own acceptance-test-3 result is not a
property of the perturbation table alone — below `n ≈ 694` the run reports 2
clean violations, at or above it reports 1. Nothing here is wrong with `G2.3`,
whose 1e-6 tolerance is pre-registered and was not touched; the point is that
**`--n-diaries` is an undeclared parameter of the verdict**, and a self-test run
at a smaller size to save time would report a violation that the default size
does not.

⚪ **Not fixed, deliberately.** Making it size-invariant would mean either
scaling the perturbation with `n` or moving `G2.3`'s threshold. The second is
forbidden outright. The first changes what the row tests and is a
pre-registration question, not a bug fix — so it is **recorded, not silenced**,
and any future `--selftest` result must be quoted with its `--n-diaries`.

## 6. The one violation that remains is the known, undischarged one

`scale_duration` fells `G2.4` (baseline PASS → perturbed FAIL) while its row
lists `G2.4` as must-stay-clean. This is the violation `D-S2-20 Q2` addressed
and **explicitly did not discharge**: scaling every episode of a 1,440-minute
diary by 1.01 necessarily breaks day closure (1,454.4), so the row cannot be
made clean on any data. The author ruled option (a) — **add** `scale_weight`
rather than edit the expectation to match the outcome (option (c), refused).

The fixture now confirms on synthetic data what was already verified on the real
parquet: **`scale_weight` fells `G2.3` while `G2.4` stays PASS**, so `G2.3`'s
detection power is demonstrated independently of `G2.4`'s.

## 7. Zero blast radius on the real run

The real, authoritative run was re-executed after the patch:

```
G2.1–G2.9, G2.11–G2.17  PASS      (16 gates)
G2.10                   NOT CHECKED (reason printed)
G2.18                   FAIL      -- (a) leak_bands=0, escalations=3 -- FELL: (a)
V2.a–V2.k               unchanged, V2.j PASS, V2.k PASS
```

Identical to the pre-patch baseline. All four edits are confined to
`_strata_pairs_for_country`, `build_synthetic_country`, `build_fixtures` and the
`--help` string — every one of them `--selftest`-only. `py_compile` clean.

The cross-tab printed by `V2.j` re-confirms the `D-S2-20 Q1(a)` errata figures a
third time: `strat_econ_status` unknown = **es 0.000 % / uk 0.519 % / it
4.243 %**.

---

## What I did NOT verify

* The six `strat_*_raw` carriers are **not read by any gate or guard** in this
  battery. They are built so the fixture's schema matches the real parquet's,
  but nothing exercises them, and `strat_season_raw` is filled with a plain
  1–4 cycle that is not claimed to be Eurostat's season coding.
* `V2.k` FAILs on the fixture by construction (its reference episode counts are
  the real table's). That is expected and unrelated to this work.
* The fixture's band *distribution* is a deterministic modulo cycle, not
  anything resembling real prevalence. It is fit for firing gates, and unfit for
  any statement about the data.
