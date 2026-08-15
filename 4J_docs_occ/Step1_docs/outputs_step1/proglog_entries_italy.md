# Progress-log entries — Italy, Step 1

Written 2026-08-15 by the employee session running
`Prompts/4thJ_employee_step1_italy_2026-08-14.md`. Two sections below, each written as a
finished, append-ready entry in the style of the existing log. **The manager appends these**;
per the work order this employee does not edit `4thJ_01_corpusAcquisition.md` or
`4thJ_01_corpusAcquisition_val.md` directly, because the UK employee is appending to the same
two files in parallel.

---

## for `4thJ_01_corpusAcquisition_val.md`

### 2026-08-15 — Italy executed. Fourteen gates: eleven scored (ten PASS, one FAIL), three `NOT CHECKED`. Coverage clause **SATISFIED** on the ten PASSing gates

Runner: `../tools/4thJ_gates_step1_italy.py`. Reader: `../tools/4thJ_read_italy.py`. Full output in
`outputs_step1/gate_report_step1_italy.txt`. One country, so this is a partial round by
construction (`V1.a` fires, correctly — Italy alone, per the work order's scope).

**Baseline: 11 scored, 10 PASS, 1 FAIL (`G1.6`), 3 `NOT CHECKED` (`G1.7b`, `G1.7c`, `G1.8`).**

| Gate | Result | Detail |
|---|---|---|
| G1.1 | PASS | 1,077,657 episodes against ISTAT's own stated 1,077,657 (`!Leggimi.html`, "Totale record" — this delivery, unlike what the task prompt assumed, does print its own count) |
| G1.2 | PASS | 0 of 41,229 diaries fail to sum to 1,440 min |
| G1.3 | PASS | 0 of 1,077,657 episode durations are not multiples of 10 |
| G1.4 | PASS | no `catpri`/`cluogo`/`catcon` code outside its own transcribed list; `act2_raw` states (IT): not_recorded 0, recorded_and_blank 819,659, recorded_with_value 257,998 |
| G1.5 | PASS | 1,077,657 episodes represented against 1,077,657 delivered, zero unexplained drops |
| **G1.6** | 🔴 **FAIL** | every archive's md5 matches on recomputation, but **no per-file source URL is printed anywhere in this delivery** (the files were handed to the author by ISTAT directly, not fetched by an employee session from a live link) — `url` is honestly recorded `NOT FOUND` rather than fabricated, and `G1.6`'s literal threshold requires one. This is a real gate failure, not a bug: see the finding below |
| G1.7a | PASS | all present weights strictly positive and finite; distinct values weight_dia 18,045, weight_ind 16,199 (both > 1); 0 respondents unmatched |
| G1.7b | 🔴 NOT CHECKED | permanently — Nota_metodologica-2013.pdf p.12 calibrates to 32 known regional totals including sex × 9 age classes, same circularity family as Spain |
| G1.7c | 🔴 NOT CHECKED | `coefin`/`coefi2` exist only in `Individui.txt`; no cross-file restatement exists to check |
| G1.7d | PASS | observed min 21.1595, max 35,070.5290, 34,240 distinct values, bounds [1.0, 1e8) |
| G1.8 | 🔴 NOT CHECKED | two independent reasons: (1) same sex×age calibration circularity as `G1.7b`; (2) no published Italian age×sex population table for 2013-14 exists anywhere in this delivery at all — a stronger absence than Spain's, which at least had a narrowing reference |
| G1.9 | PASS | measured 1 diary day per respondent, codebook states 1 |
| G1.10 | PASS | 1 distinct `mode`, 1 distinct `scheme` |
| G1.11 | PASS | independent recount from raw `DiarioGiornaliero.txt` (own column resolution, no episode reconstruction needed — Italy ships native episodes): 257,998 non-blank `catcon`; emitted table: 257,998 non-blank `act2_raw` |

#### Coverage clause: SATISFIED

Every gate that PASSes on the real data (all 10) was made to fall by at least one perturbation.
`G1.6` (baseline FAIL) and the three `NOT CHECKED` gates are outside the clause by construction —
the clause only binds gates that PASS.

| Gate | Made to fall by |
|---|---|
| G1.1 | drop_last_5pct_rows, delete_one_episode, drop_over_65 |
| G1.2 | drop_last_5pct_rows, delete_one_episode, duration_30_to_25 |
| G1.3 | duration_30_to_25 |
| G1.4 | act_to_99Z, act2_to_99Z |
| G1.5 | drop_last_5pct_rows, delete_one_episode, reader_skips_silently, drop_over_65 |
| G1.7a | weight_negative_one, weight_constant |
| G1.7d | weight_divide_1e4 |
| G1.9 | declare_italy_2_days |
| G1.10 | second_mode_value |
| G1.11 | drop_last_5pct_rows, drop_over_65, act2_rewrite_nonblank_to_blank |

The null perturbation moved nothing (failing set unchanged from baseline — the one baseline FAIL,
`G1.6`, stayed failed for the same reason, not a new one). `act_to_99Z`/`act2_to_99Z`,
`reader_skips_silently`, `weight_negative_one`, `weight_constant`, `weight_divide_1e4`,
`declare_italy_2_days`, `second_mode_value` and `act2_rewrite_nonblank_to_blank` each attributed
cleanly to exactly the gate named for them. `drop_last_5pct_rows`, `delete_one_episode`,
`duration_30_to_25` and `drop_over_65` each moved more than their named gate, all by the same
row-removal/row-rewrite collateral mechanism the Spanish round already documented (any row that
disappears moves `G1.5` and, here, `G1.11` too, since `G1.11`'s reference is fixed against the
unperturbed raw file). `corrupt_archive_byte` could not demonstrate anything: `G1.6` was already
FAILing at baseline for an unrelated reason (missing URL), so a perturbation aimed at it has
nowhere to shake it from — recorded, not hidden.

#### 🔴 The `G1.6` finding: this delivery has no per-file source URL to record, and it was not invented

`acquisition_manifest_italy.json` records every archive's md5 (all four recomputed matches) and a
date, but `url = "NOT FOUND"` for every entry, per the work order's explicit instruction: *"If the
delivery does not print its own source URL, record what it does print and mark the rest `NOT
FOUND` — do not reconstruct a plausible ISTAT URL from memory."* Unlike Spain, these four files were
never downloaded by an employee session from a live link — they were provided to the author
directly and placed on this workstation. Two general (non-per-file) URLs the delivery *does* print
are recorded in the manifest's `entry_point_note`. `G1.6`'s threshold, read literally, requires a
URL, and none exists to give it honestly. **This is reported as a real `FAIL`, not worked around**
— the alternative (fabricating a plausible URL, or quietly exempting `G1.6` the way `G1.7b`/`G1.7c`/
`G1.8` are exempted) would each be a threshold move this employee was told not to make.

#### What did not attribute (row-removal/row-rewrite collateral, same mechanism as Spain)

| Perturbation | Expected | Also moved |
|---|---|---|
| drop_last_5pct_rows | G1.1 | G1.2, G1.5, G1.11 |
| delete_one_episode | G1.2 | G1.1, G1.5 |
| duration_30_to_25 | G1.3 | G1.2 |
| drop_over_65 | G1.8 (pre-registered coverage case; G1.8 NOT CHECKED for Italy) | G1.1, G1.5, G1.11 |

#### Vacuity guards

`V1.a` fired, as it must: one country of four. `V1.b`/`V1.c`/`V1.d` behaved as specified (see the
full report for the printed inputs and the reader's own refusal log).

---

## for `4thJ_01_corpusAcquisition.md`

### 2026-08-15 — Italy executed. Work items 1.1 (Italy row only), 1.2 and 1.3 done. **The second country file in paper 4 exists.**

**1.1 — registered, not acquired by this session.** `uso_tempo_2013_IT.zip` and
`Nota_metodologica-2013.pdf` (38 pp. as delivered) were provided directly to the author by ISTAT on
2026-08-14 and copied into `_local_runs/4J/raw/italy/` by this employee session on 2026-08-15, all
four archives hashed on the local copy and reconciled byte-for-byte against the originals in
`4J_docs_occ/Datasets/IT TUS/` before unpacking. Fragment written to
`outputs_step1/acquisition_manifest_italy.json` (Italy entry only; `acquisition_manifest.json`
itself was not touched, per the work order, because the UK employee is working in the same file in
parallel). 🔴 **No per-file download URL exists anywhere in this delivery** — these files were never
fetched by a live download, so `url` is recorded `NOT FOUND` rather than invented; this is why
`G1.6` fails (see the validation entry above).

🔴 **Licence finding: this is ISTAT's mIcro.STAT public-use file, not the mFR.**
`Nota_metodologica.pdf` (the excluded 2023 volunteering module) describes an *mFR* (*File di
microdati per la ricerca*) release; the 2013-14 diary is a **different and more restricted
product**, ISTAT's own open mIcro.STAT public-use file — stated on the cover pages of
`Nota_metodologica-2013.pdf` and `uso_tempo_DescrizioneFile_Individuo__Anno 2013.pdf`, and
explained on the latter's p.3: the mFR carries higher informational content and requires a
justified request and the President of ISTAT's authorisation; mIcro.STAT does not. This bears on
Step 5's release decision and is recorded in `codebook_facts_italy.md`, finding F-IT-1.

The 2023 volunteering pair (`Nota_metodologica.pdf`, `UsoTempo_2023_IT.zip`) was hashed, copied
into the workspace, and recorded as present and explicitly excluded — not unpacked, not read.

**1.2 — codebook read.** `outputs_step1/codebook_facts_italy.md`, every fact cited to a Tracciato
HTML row, a classification file, a questionnaire page, or a methodology page. **Fourteen findings**,
`F-IT-1` through `F-IT-14`, recorded in full in the codebook. The five things the work order flagged
as "already measured" were all confirmed independently from ISTAT's own documentation: tab-delimited
with a header row (not fixed-width); native episodes with explicit clock start/end times and a
04:00 diary-day wrap (measured: exactly one wrap-episode per diary, all 41,229 diaries then sum to
exactly 1,440 minutes); `catcon` is a genuinely separate, coarser 2-digit/34-modality classification
from `catpri`'s 3-digit/146-code list (`F-IT-3`); eight co-presence fields, whose value domain
(blank, or the field's own fixed ordinal) had to be established by direct inspection because no
classification list documents them (`F-IT-4`); and blank is literally recorded spaces matching the
field's declared width, established the same way (`F-IT-6`, which also records that
`HelpTracciato_DELIMITED.html` does not in fact state a blank-field convention for this survey's
variables, contrary to what the task prompt assumed — read first, as instructed, and found not to
say what it was expected to say).

Two further findings change what later steps can rely on: **ISTAT's own weighting methodology is
calibrated to sex × nine age-class regional population totals** (Nota_metodologica-2013.pdf p.12),
putting `G1.7b` in the same circular family as Spain's, and narrowing what `G1.8` could ever detect
even with a reference (`F-IT-9`); and **no published Italian age×sex population table for 2013-14
exists anywhere in this delivery** — the methodology PDF is itself an incomplete excerpt (its own
page numbers jump from printed p.26 to printed p.95) — so `G1.8` cannot even run the narrowed check
(`F-IT-10`). Minimum age is **3**, not Spain's 10, with parent-proxy completion permitted for ages
3-10 (`F-IT-11`). Diary origin hour is **04:00** (QUEST-DG p.2), diary days per respondent measured
and asserted at **1**.

The activity, secondary-activity and location lists were transcribed out of ISTAT's own
classification HTML files into `crosswalk_source_italy_activity.csv` (146 leaf codes — 145
three-digit plus one genuine two-digit leaf, `90`, stored in the field as `"90 "` with a trailing
space rather than zero-padded, finding `F-IT-5`), `crosswalk_source_italy_activity2.csv` (34 codes,
`catcon`'s own list), and `crosswalk_source_italy_location.csv` (53 codes), so that gate `G1.4` has
a reference ISTAT wrote. All three lists were verified to cover the delivered file's observed
alphabet exactly (after the `catpri` right-strip finding `F-IT-5` is applied).

**1.3 — reader written and run.** `../tools/4thJ_read_italy.py`.

* File shape is **two flat tab-delimited files with a header row** (`DiarioGiornaliero`,
  `Individui`), joined on `profam`+`proind`. Not relational in Spain's eight-file sense, and not
  fixed-width — the parser was written to resolve every column by name, never by position, and to
  refuse (not assume) any unrecognised value.
* The diary is delivered as **native episodes** with explicit `oraini`/`minini`/`orafin`/`minfin`.
  No slot reconstruction. `duration_min` is computed with an explicit 04:00 wrap: exactly one
  episode per diary (41,229 of 41,229) wraps past midnight in naive clock arithmetic, and adding
  1,440 minutes to that one episode alone closes every diary to exactly 1,440.
* **41,229 diary respondents, 1,077,657 episodes**, 26.14 episodes per diary.
* Every respondent has exactly one diary day, measured, not assumed.
* `outputs_step1/episodes_italy.parquet` and `outputs_step1/parse_report_italy.txt`.
* **Zero rows dropped, zero unparsed, zero unexplained.** `act2_raw` (from `catcon`) is carried in a
  nullable pandas `string` column: not_recorded 0, recorded_and_blank 819,659, recorded_with_value
  257,998 — Italy fields `catcon` on every row, so (as for Spain) no Italian episode is ever "not
  recorded."
* All eight co-presence fields are carried as their own named columns
  (`cop_extra_it_daso` … `cop_extra_it_aperco`), following the Spanish precedent of never folding a
  recorded flag into another — none of Italy's eight maps unambiguously onto Spain's five-slot
  scheme, so all eight are carried as country-extras rather than a partial, guessed mapping.
* The join against `Individui` for `weight_ind` (`coefin`) and `weight_dia` (`coefi2`) is measured
  clean: **0 episodes unmatched to a non-blank diary weight**, of 1,077,657.

**1.4 — not done, and not ours.** Unchanged from the Spanish entry: the Eurostat entity-recognition
enquiry is the author's, in person.
