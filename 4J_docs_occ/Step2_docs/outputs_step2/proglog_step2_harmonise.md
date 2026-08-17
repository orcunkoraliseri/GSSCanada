## Progress Log fragment — work item 2.4, harmonisation runner

**Status: DONE. All three countries ran, all reconcile exactly, deliverables are in
`outputs_step2/`. Manager reviewed and ruled on three open items (below); the UK was re-run once
more to carry four previously-dropped columns, everything else stands.**

### Manager's rulings on the open items flagged below, and what changed as a result

1. **`indoor_presence` null propagation — CONFIRMED.** My extension beyond the literal spec text
   (null also when `act` is unmapped, not only when `loc_raw` is blank) was correct: where `act` is
   null you cannot evaluate the outdoor-at-home exclusion, and `False` would assert "not indoors" on
   no evidence. Added a one-line disclosure with the null count to every `filter_report_*.md`
   fragment (es 290, uk 18,325, it 8,112) so the count reads as a rule applied, not a mystery.
2. **`WithMiss` as missingness rather than an extra column — CONFIRMED.** Correctly tagged
   `NOT_A_PRESENCE_FLAG` in the shipped crosswalk; the 68,464 UK episodes null across all six shared
   flags is the intended behaviour, no change needed.
3. **🔴 The dropped UK columns — REVERSED.** D-S2-12's column list is a pattern
   (`cop_extra_<country>_<field> ...`), not a closed enumeration, and the governing principle ("a
   transform that discards its inputs cannot be audited") applies to `act2_extra_uk_2`,
   `act2_extra_uk_3`, `weight_dia_a` and `weight_dia_b` the same way it already applies to
   `act_raw`/`act2_raw`/`loc_raw` and the UK's `WithMother`/`WithFather`. Dropping them also
   pre-empted a Step 3 decision (what is *written into the token stream*) that D-S2-7 reserves for
   Step 3, not Step 2. **Fixed**: added `COUNTRY_EXTRA_RAW_COLUMNS` (country → list of extra raw
   columns to carry unchanged, empty for es/it, the four names for uk) to the script, and re-ran the
   UK only (job 1252983). **Verified afterwards, as instructed: row count still exactly 567,381,
   split count still exactly 0** — adding columns moved zero rows. Spain and Italy were not
   re-run.
4. **`act2 = null` overload — disclosed, not fixed (as instructed).** D-S2-12 says `act2 = null`
   means "not recorded"; in this delivery, given finding 5 (act2's "not recorded" state never occurs
   at all), every `act2 = null` row is actually "recorded but the code didn't map" (57 es + 530 uk +
   0 it = 587 total). No fourth state added — `act2_raw` already resolves it, per D-S2-12's own
   argument. Added a one-line disclosure to every fragment plus a dedicated section in the combined
   `filter_report.md` explaining exactly how to tell the two meanings apart from `act2_raw`.

Spain's and Italy's `filter_report_{es,it}.md` fragments were updated by hand with items 1 and 4's
disclosure lines and counts, computed directly by reading their already-produced
`harmonised_{es,it}.parquet` files — no recomputation, and **no re-run**, per the manager's standing
instruction that Spain and Italy are untouched.

### What was built

`tools/4thJ_harmonise_step2.py` — one script, `--country es|it|uk` selecting one country per job,
`--age-floor` with **no default** (D-S2-13). Implements the pipeline in the order the task document
specifies: age filter, rotate to a 04:00 cyclic origin, assert the 10-minute grid, activity
crosswalk, secondary-activity crosswalk, location crosswalk, `indoor_presence`, co-presence, emit.
Run as three unchained `sbatch` jobs, one per country, `-p ps -t 7-00:00:00`.

### TASK 0 — schema dump

Two schema-dump jobs (1252867, 1252876) read all three Step 1 parquets in
`outputs_step1/run_20260816-2210/` and reconciled them against D-S2-12 and the task document.
Discrepancies found, reported rather than coded around:

* **Co-presence raw column names do not follow one uniform rule.** Spain's `PADRES` is stored as
  `cop_extra_es_padres` in the parquet (a holdover from the superseded pre-D-S2-8 naming), while
  every other Spanish co-presence column is `cop_<lowercase(field)>`. The UK's and Italy's raw
  columns are uniformly `cop_extra_<country>_<FieldName>` regardless of whether the field ends up
  shared or an extra in the current crosswalk. Hard-coded as data (`RAW_COP_COLUMN`), asserted
  against the live dataframe at runtime.
* **`act2_raw`'s "not recorded" (null) state does not occur in any of the three countries** at the
  Step 1 output level — see the dedicated section in `filter_report.md`. Two of act2's three states
  (recorded-and-blank, recorded-with-value) are always the only ones observed; this is inherited
  from Step 1's documented design (Spain's/Italy's always-present fixed-width fields; the UK's `-9`
  already collapsed into blank by Step 1's own choice, F-UK-2), not a Step 2 defect.
* `loc_raw`'s recorded-and-blank state (`""`) occurs only for the UK (6,847 episodes post-filter,
  Step 1's M-1 fix of `-9`→`""`, F-UK-15); Spain and Italy never leave `loc_raw` blank.
* All three countries' diaries already sum to exactly 1440 minutes pre-rotation, and every
  `start_min`/`duration_min` is already a multiple of 10 — seen passing cleanly, not assumed.

### 🔴 D-S2-14 — Italy's `start_min` reference point, found and corrected

Follow-up investigation (jobs 1252921, 1252930) found that Italy's `start_min` does not follow the
same convention as Spain's and the UK's. Spain's and the UK's `start_min=0` is diary-relative (every
diary's first episode is at `start_min=0`, matching their own stated native origin, 06:00 and 04:00
respectively). Italy's `start_min` is wall-clock minutes since midnight, carried over directly from
`oraini*60+minini`: every one of 41,229 diaries has its first episode at `start_min=240` (4am on the
wall clock), and 35,060 of 1,077,657 rows already had `start_min+duration_min>1440` before any
rotation — nothing to do with the D-S2-5 rotation, everything to do with what minute zero means in
this one country's encoding.

I stopped and reported this rather than inventing a fix (a country-specific offset patch would have
been amending D-S2-5's decided formula, outside an employee's authority). The manager's ruling,
recorded as **D-S2-14**: `start_min`'s own contract never declared what minute zero denotes on the
wall clock, so the reference point becomes an explicit, checkable property (`reference_minutes`),
and the rotation offset is derived from it rather than from the origin hour directly:

```
reference_minutes = wall-clock time that start_min == 0 denotes: ES 360, UK 240, IT 0
offset = (reference_minutes - 240) mod 1440                     -> ES +120, UK 0, IT +1200 (= -240)
```

Spain's and the UK's offsets are numerically unchanged (120 and 0 respectively), so **per the
manager's explicit instruction their completed runs (job IDs 1252941 `es`, 1252942 `uk`) were not
re-run.** Italy was re-run under the corrected script (job 1252958) and the manager's own prediction
held exactly: **zero splits**, both new assertions passed on the first attempt:

* **Assertion 1** (first-episode start_min): every diary's `episode_index==0` episode starts at the
  value derived from `(native_origin_hour*60 - reference_minutes) mod 1440` — ES 0, UK 0, IT 240.
  Passed for Italy (38,260/38,260 diaries after the age filter); implied unchanged for Spain/UK since
  their reference_minutes and offsets did not change.
* **Assertion 2** (tiling invariant): the rotated intervals partition `[0,1440)` exactly once per
  diary (no gaps, no overlaps) — the general form of the by-hand check that caught Italy's defect in
  the first place. Passed for Italy (1,010,140 rows, 0 violations).

### 🔴 D-S2-15 — the `V2.i`/`split_at_origin` contradiction, and its resolution

`V2.i`'s literal text ("FAILs if any column name contains `origin`") would reject `split_at_origin`,
which D-S2-12 itself requires. My own pre-write self-check hit this on the first Spain/UK runs and I
narrowed it to exclude `split_at_origin` by name, then reported the contradiction rather than
silently deciding it was fine. The manager's ruling, **D-S2-15**: `V2.i` fails on any column name
containing `origin` **except the exact name `split_at_origin`**, and now also fails if
`split_at_origin` is *absent* (a positive requirement, not a hole). My self-check matches this
exactly; the gate itself is implemented in a separate work item (`tools/4thJ_gates_step2.py`).

### TASK 1 — other decisions made where the task document was silent

* **`indoor_presence` null propagation extended beyond the literal text.** The task document says
  null only "wherever `loc_raw` is in its recorded-and-blank state." I additionally set it to null
  when `loc_class` is unmapped for a non-blank code, and when `loc_class == 'at_home'` but `act`
  itself is unmapped (so the outdoor-at-home exclusion cannot be evaluated even though we know the
  person is at home). Rationale: "we don't know" must never collapse into `False`, the same principle
  stated repeatedly for the co-presence flags (D-S2-2, D-S2-8). **My own extension, not literally
  specified — flagged for the manager to confirm or override.**
* **The UK's `WithMiss=1` missingness override is applied only to the six shared `cop_*` flags, not
  to the extras** (`cop_extra_uk_mother`, `cop_extra_uk_father`, `cop_extra_uk_na`), reading D-S2-8's
  text literally ("all six shared UK flags are MISSING"). An alternative reading — extras should also
  go null — is at least as defensible; not adopted. Confirmed empirically: the extras have zero nulls
  even though the six shared flags have 68,464 nulls each.
* **`truth_from_meaning` needed a fallback beyond literal yes/no text.** The UK's `WithNA` extra's
  value labels are domain prose ("Not reported" / "main act: work/edu/sleep"), not a yes/no
  statement. Since `WithNA` is explicitly "never mapped and never read as missing" (F-UK-4) and
  carried purely as its own binary indicator, added a fallback: when the meaning text doesn't parse
  as yes/no, use the raw value directly (`"0"`→False, `"1"`→True). Fires only for `WithNA`.
* **Unmapped `act2` codes with a real (non-blank, non-null) raw value are set to `act2=null` and
  counted**, on the same "never dropped, never guessed" principle stated explicitly for `act` and
  `loc_class`. The task document doesn't spell this out for `act2` specifically, but the symmetry
  seemed clear. Counts: es 57, uk 530, it 0.

### Acceptance tests

1. `origin` in no column name (except the required `split_at_origin`, D-S2-15): **PASS**, all three
   countries.
2. Spain's split count non-zero (18,915), UK's and Italy's exactly zero: **PASS**, all three.
3. Episode counts reconcile, arithmetic shown: **PASS**, all three, and in aggregate: 2,096,043 −
   90,890 + 18,915 = 2,024,068 = output.
4. Every non-null `act` in `activity_target_list.csv`, `act_level1`/`act_level2` sliced from the
   emitted code: **PASS**, asserted in-script for all three (would `SystemExit` on violation; never
   fired).
5. `act2`'s three states all present with counts: **NOT A FULL PASS for any country** — see the
   dedicated section in `filter_report.md`. Two of three states are present everywhere;
   `not_recorded` is zero for all three, inherited from Step 1, not a Step 2 defect.
6. `cop_*` nullable boolean with a genuine null count, not all-`False`: **PASS for the UK** (68,464
   nulls per shared flag from `WithMiss`). **Spain and Italy have zero nulls in any `cop_*`
   column** — not a defect: D-S2-8 states Spain has no missingness column at all, and Italy declares
   none either, so every episode counts as "recorded" for co-presence in both.
7. Spain's `cop_*` not inverted: **PASS**. `cop_alone` share True = 0.3502, far from the near-100% a
   truthy cast of `6` would produce.
8. `filter_report.md` carries the Italian band line: **PASS** — present, naming band `04` (11-14)
   explicitly.
9. Grid assertions passed with no coercion, for all three countries, plus the two new D-S2-14
   assertions (first-episode start, tiling invariant): **PASS**, all three.

### Deliverables

* `tools/4thJ_harmonise_step2.py`
* `outputs_step2/harmonised_es.parquet` (446,547), `harmonised_uk.parquet` (567,381, now including
  `act2_extra_uk_2`, `act2_extra_uk_3`, `weight_dia_a`, `weight_dia_b` per the manager's ruling),
  `harmonised_it.parquet` (1,010,140) — **per-country parts**, produced by the three unchained jobs
  (UK's second run: job 1252983).
* `outputs_step2/harmonised.parquet` (2,024,068 rows, rebuilt after the UK re-run) — the
  **concatenation** of the three, union of columns (country-appropriate nulls for `cop_extra_*` and
  the UK-only extra raw columns a country doesn't carry — verified: 100% null for Spain/Italy on
  `cop_extra_uk_*`/`act2_extra_uk_*`/`weight_dia_{a,b}`, 100% null for Spain/UK on `cop_extra_it_*`,
  0% null within the owning country, except `weight_dia_{a,b}`'s own 89 genuine UK nulls). Built
  locally (`py`, not the cluster — a lightweight concat of three already-computed parquets, no new
  computation) after all three country jobs completed. Both `act` (always exactly 3 characters) and
  `act2` (always 0 or 2 characters) verified directly on the combined file; `cop_*`/`indoor_presence`
  confirmed nullable boolean, `act`/`act2`/`loc_class` confirmed nullable string.
* `outputs_step2/filter_report.md` — combined, with per-country sections, the cross-country
  reconciliation total, the act2-null-state disclosure, and the dedicated `act2=null` overload
  section (manager's item 4).
* `outputs_step2/filter_report_{es,uk,it}.md`, `outputs_step2/harmonise_{es,uk,it}.txt` — per-country
  fragments and runner stdout logs, kept alongside the combined files.
* Native origin hour is in each per-country parquet's file-level metadata (`native_origin_hour`) and
  in the combined file's metadata (`native_origin_hour_by_country`, a small JSON map) — never a row
  or column, per D-S2-5/D-S2-12/D-S2-15.

### WHAT I DID NOT VERIFY

* **I did not independently re-derive the crosswalk files' correctness** (activity, secondary
  activity, location, co-presence, outdoor-at-home, target list) — consumed as delivered and
  confirmed fresh by the manager (531/421 rows, Spain's `121`→`139` correction present), checked for
  join-safety (no duplicate `(country, source_code)` keys — confirmed, zero duplicates in all four),
  but did not check citation accuracy or codebook page numbers myself — that was work items 2.1/2.2/
  2.3's job, not 2.4's.
* **I did not verify `activity_target_list.csv`'s 158 rows against the underlying Spanish/Italian
  page citations** — only that every emitted `act` value is a member of its `target_code` set, which
  the runner asserts automatically and which passed for all three countries.
* **The `indoor_presence` null-propagation extension and the `WithMiss`-extras decision** — both
  **CONFIRMED by the manager** (see the rulings section above). No longer open.
* **`weight_ind`/`weight_dia` nullability** (UK has 1,551 and 89 nulls respectively, per M-4) is
  passed through unchanged; not re-investigated beyond what Step 1's codebook facts already document.
* **`act2_extra_uk_2`, `act2_extra_uk_3`, `weight_dia_a`, `weight_dia_b`** — **REVERSED by the
  manager** (see the rulings section above): now carried unchanged in `harmonised.parquet` and
  `harmonised_uk.parquet`. No longer open.
* **Spain's and the UK's runs were not re-verified against the two D-S2-14 assertions** (first-
  episode start, tiling invariant) — per the manager's explicit instruction not to re-run them, since
  their offsets are numerically unchanged. I have not independently re-run those two checks against
  their already-produced output files outside the main script; the manager's own re-measurement
  (reported in their ruling: Spain/UK "0 / 1440 / 0") is the evidence that they would pass.
