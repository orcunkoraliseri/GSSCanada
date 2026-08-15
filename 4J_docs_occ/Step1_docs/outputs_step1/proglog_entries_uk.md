# Progress-log entries — UK, Step 1 (2026-08-14/15)

Two append-ready sections, written as finished entries in the style of the existing log. The
manager appends each to its own document; neither has been written to
`4thJ_01_corpusAcquisition.md` or `4thJ_01_corpusAcquisition_val.md` by this employee session, per
the work order.

---

## for `4thJ_01_corpusAcquisition.md`

### 2026-08-14/15 — UK executed. 1.2 and 1.3 done, 1.1 executed for the archive already in hand

Employee task: `../Prompts/4thJ_employee_step1_uk_2026-08-14.md`. Scope: UKTUS 2014-15 (UKDA SN
8128), work items 1.2 and 1.3 plus the full Step 1 validation battery on the archive the author had
already downloaded and delivered to the workstation. Nothing was acquired, downloaded or registered
for by this session.

**1.1 (partial, as scoped).** The delivery
(`Datasets/UK-TUS-20260815T031737Z-1-001.zip`, a Google Drive export wrapper around the actual UKDS
zip) was unpacked to `_local_runs/4J/raw/uk/`, mirroring Spain's `raw/spain/` layout (archives kept,
`unpacked/` beside them). Every archive and every one of the 17 delivered files was md5'd; the inner
UKDS zip's filename is itself a content-addressed SHA-256 and this session's independent SHA-256
recomputation matches it, a second, stronger integrity signal on top of md5. Recorded in
`outputs_step1/acquisition_manifest_uk.json` — a **fragment**, not a write to the shared
`acquisition_manifest.json`, so the parallel Italy session was not overwritten; the manager merges
it. DOI `http://doi.org/10.5255/UKDA-SN-8128-1` and licence (End User Licence, UKDS EUL) are both
taken verbatim from the delivered `UKDA_Study_8128_Information.htm` and `read8128.htm`; no literal
download URL is printed anywhere in the delivery and is recorded `NOT FOUND` rather than guessed.

**1.2 — codebooks read.** `outputs_step1/codebook_facts_uk.md`, every fact cited to a UKDA data
dictionary, the CTUR processing report or the NatCen/NISRA technical report, by printed page.
Fifteen findings recorded in full there. The four the manager flagged in advance were all confirmed,
measured, and in one case corrected:

* **`eptime` is minutes, `tid` is the START slot** (F-UK-1) — established two independent ways
  (a documented Stata-code equivalence and a direct row-level cross-check), not assumed.
* **Three secondary activities exist** (`What_Oth1/2/3`, F-UK-2), coverage 27.75 % / 2.72 % / 0.23
  %. All three carried (`act2_raw`, `act2_extra_uk_2`, `act2_extra_uk_3`), none merged, none dropped.
* **Two diary weights**, both carried (`weight_dia_a`, `weight_dia_b`); the contract's single
  `weight_dia` is populated from `dia_wt_a`, the documented default for diary/event-level analysis
  (CTUR p. 13, NATCEN p. 31, both cited), and the choice is flagged pre-registration-relevant per
  the work order.
* **Nine co-presence fields**, all emitted as named columns. `WithMiss` is genuine missingness;
  🔴 **`WithNA` turned out NOT to be a missingness flag for this wave** — it is a UK2000-01
  backward-compatibility concordance marker, since 2014-15 (unlike 2000-01) *does* code co-presence
  for sleep/work/education episodes (F-UK-4). Recorded so Step 2/3 do not misread it.

Two findings the work order did not anticipate, both surfaced by measurement rather than assumed
away: a single undocumented activity code (`4276`) appears once in 587,632 episodes with no label
anywhere in the delivered dictionary (F-UK-9); and the location field (`WhereWhen`) carries its own
missingness sentinel (`-9`, 1.211 % of episodes) that the intermediate-record contract has no
three-state provision for, the same shape of gap as the secondary-activity one but for `loc_raw`
(F-UK-15) — **both left for the manager to close, not resolved here.**

UK weights turned out to be **normalised (mean ≈ 1.000)**, not raw expansion factors like Spain's
`FACTORF` — roughly 60 % of real UK diary and individual weights are strictly below 1.0 (F-UK-13),
which matters directly for `G1.7d` below.

The activity and location code lists were transcribed from the UKDA data dictionary's own value
labels into `crosswalk_source_uk_activity.csv` (277 codes) and `crosswalk_source_uk_location.csv`
(35 codes), matching the Spanish files' shape.

**1.3 — reader written and run.** `../tools/4thJ_read_uk.py`.

* File shape is **six flat tab-delimited files**, not relational in Spain's sense. The UK ships
  **native episodes** (`tid` = start slot, `eptime` = duration in minutes) — the reader reconstructs
  nothing, the opposite of the Spanish reader's slot-collapsing.
* Two files read: `uktus15_diary_ep_long.tab` (587,632 episodes) and `uktus15_individual.tab`
  (11,421 people, demographics and `ind_wt`). Four files deliberately not read, with reasons
  (F-UK-14): `uktus15_household.tab`, `uktus15_diary_wide.tab`, `uktus15_wksched.tab`, and
  `uktus15_dv_time_vars.tab` (read only by the gate runner, independently, for `G1.7c`).
* **8,274 distinct people, 16,533 (person, diary_day) diaries, 587,632 episodes.** Every diary sums
  to exactly 1,440 minutes, 0 exceptions. Diary days per respondent measured at max 2 (design), with
  8,259 of 8,274 people completing both.
* 🔴 `diary_day` is populated from the survey's own 1st/2nd-day ordinal (`daynum`), **not** a
  day-of-week code as it is for Spain — 3 of 8,259 two-day respondents land on the same day of week
  on both their days, so only `daynum` is collision-free (F-UK-6). This means `diary_day` carries a
  different *kind* of value across the two countries' emitted tables; flagged for Step 2/3.
* Three-state secondary-activity handling implemented with a pandas nullable `string` dtype, exactly
  as the reconstructed-vs-native distinction requires. Weight columns converted to `float64`, with
  the delivery's own literal blank-space sentinel (not `-9`, not empty string) mapped to `NaN` and
  counted, never silently coerced (F-UK-8): 89 episode rows / 2 person-days for the diary weights,
  1,551 episode rows / 23 people for the individual weight.
* `outputs_step1/episodes_uk.parquet` (587,632 rows, 32 columns) and
  `outputs_step1/parse_report_uk.txt`. **Zero rows dropped, zero unparsed, zero unexplained** — the
  reader raises and emits nothing on any condition it cannot explain.

**1.1, remainder — not this session's to do.** Transfer to `/speed-scratch` was not attempted; this
task ran entirely on the local workstation per the work order, and the cluster was not touched at
all.

**1.4 — not done, and not this employee's.**

---

## for `4thJ_01_corpusAcquisition_val.md`

### 2026-08-14/15 — first run on the UK. Eleven gates scored, nine PASS, two FAIL on real data, three NOT CHECKED. Coverage clause SATISFIED for the nine PASSing gates.

Runner: `../tools/4thJ_gates_step1_uk.py`, importing nothing from `4thJ_read_uk.py`; both scripts'
column declarations are printed side by side at the top of every run for a human to compare by eye.
Full output in `outputs_step1/gate_report_step1_uk.txt`. One country, so `V1.a` fires, as it must.

**Baseline: 11 scored (9 PASS, 2 FAIL), 3 NOT CHECKED.**

| Gate | Result | Detail |
|---|---|---|
| G1.1 | PASS | 587,632 episode rows against UKDA's own "Number of cases" (587,632) |
| G1.2 | PASS | 0 of 16,533 (person, diary_day) diaries fail to sum to 1,440 min |
| G1.3 | PASS | 0 of 587,632 durations are not multiples of 10 |
| G1.4 | 🔴 **FAIL** | genuine, on real data: one undocumented activity code (`4276`, F-UK-9) in `act2_raw`, and the `-9` location sentinel (F-UK-15) surfacing in `loc_raw` since it is outside the transcribed location list |
| G1.5 | PASS | parse report states zero unexplained drops; 587,632 represented against 587,632 delivered |
| G1.6 | PASS | outer + inner archive + 17 delivered files, every md5 recomputed from disk matches |
| G1.7a | 🔴 **FAIL** | genuine, on real data: 2 of 16,533 diaries and 23 of 8,274 people have the delivery's own blank-weight sentinel (F-UK-8), so presence is not 100 % |
| G1.7b | NOT CHECKED | NATCEN p. 31 confirms both diary weights are calibrated to age/sex margins — same circularity as Spain's retired G1.7b, established independently for the UK, not inherited (F-UK-11); no population table is shipped either way |
| G1.7c | PASS | `dia_wt_a`/`dia_wt_b` bit-identical (raw strings) between `uktus15_diary_ep_long.tab` and `uktus15_dv_time_vars.tab`, both read independently by the gate runner, 0 mismatches across 16,533 person-days — **live and checkable for the UK**, unlike the "single-file" case the spec anticipated |
| G1.7d | NOT CHECKED | no fixed-width layout exists anywhere in the UK delivery for any weight (tab-delimited free-text decimals) — no reference to check the upper bound against. Diagnostic printed: UK weights are **normalised, mean ≈ 1.000**, 60.3 % below 1.0 — the pre-registered "≥ 1.0" clause would misfire on a normalised weighting convention, a specification question flagged for the manager (F-UK-13), not a threshold moved here |
| G1.8 | NOT CHECKED | no published UK age × sex table is shipped in the delivery (two independent, both-sufficient reasons recorded: no table at all, and calibration circularity if one existed) |
| G1.9 | PASS | measured max 2 diary days per respondent (8,259 of 8,274 complete both), codebook states 2 |
| G1.10 | PASS | 1 distinct `mode`, 1 distinct `scheme` |
| G1.11 | PASS | independent recount from raw `uktus15_diary_ep_long.tab` (own column resolution, own `-9`→blank mapping) matches the emitted table exactly for all three secondary-activity columns: 163,105 / 15,968 / 1,353 |

#### Coverage clause: **SATISFIED**, scoped correctly

Every gate that PASSes on the real data was made to fall by at least one perturbation:

| Gate | Made to fall by |
|---|---|
| G1.1 | drop_last_5pct_rows, delete_one_episode |
| G1.2 | drop_last_5pct_rows, delete_one_episode, duration_30_to_25 |
| G1.3 | duration_30_to_25 |
| G1.5 | drop_last_5pct_rows, delete_one_episode, reader_skips_silently |
| G1.6 | corrupt_archive_byte |
| G1.7c | dv_time_vars_weight_swap (isolated — no other gate moves) |
| G1.9 | declare_uk_1_day |
| G1.10 | second_mode_value |
| G1.11 | drop_last_5pct_rows, act2_rewrite_nonblank_to_blank |

`G1.7b`, `G1.7d`, `G1.8` are exempt (`NOT CHECKED`, printed on every run, never counted as a pass).

🔴 **`G1.4` and `G1.7a` are outside the clause's literal scope for a different, stated reason: they
do not PASS on real data to begin with.** They are excluded from "PASS on the real data" by
construction, not by an invented exemption — printed as such on every run, never silently dropped
from the report the way a retired gate would be.

#### 🔴 A genuine limitation this round could not avoid: five perturbations "DID NOT FIRE"

Because `G1.4` and `G1.7a` already FAIL on real, unperturbed UK data, the five perturbations
pre-registered to demonstrate their detection power (`act_to_outside_list`, `act2_to_outside_list`,
`act2_extra_2_to_outside_list` for `G1.4`; `weight_negative_one`, `weight_constant` for `G1.7a`)
cannot be observed to *newly* break a gate that was already broken. Each is reported honestly as
`DID NOT FIRE` in the perturbation table rather than credited for something it could not
demonstrate. This is a property of the real baseline data (two genuine, cited defects), not a defect
in the perturbation design, and it is not patched by pre-cleaning the input before perturbing it —
that would test a hypothetical file, not this one. Recorded as a real limitation of this round.

#### The null perturbation's literal wording needed a stated reinterpretation

"Nothing may fail" presumes a clean (all-PASS-or-NOT-CHECKED) baseline, which Spain had and the UK
does not. Implemented instead as: the null perturbation's gate verdicts must be **identical to the
baseline's**, gate by gate — which they are. The reinterpretation is stated here rather than applied
silently, per the work order's instruction that a specification/data conflict is a finding, not
something to route around quietly.

#### What did not attribute

Five perturbations moved more than the gate they were pre-registered for, all row-removal/row-rewrite
collateral, the same structural reason recorded for Spain (`drop_last_5pct_rows` → also G1.2, G1.5,
G1.11; `delete_one_episode` → also G1.1, G1.5; `duration_30_to_25` → also G1.2). None of this is
tuned away.

**Where this leaves Step 1 for the UK:** the reader and gate battery both run clean in the sense that
matters — every check computes, nothing crashes, nothing is assumed, and two real defects were found
and reported rather than hidden. `V1.a` fires on one country of four. Two specification gaps are
flagged for the manager (F-UK-2's already-known three-secondary-activities gap, plus the new
F-UK-15 location-sentinel gap) and are not resolved by this employee session.
