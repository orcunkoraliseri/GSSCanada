# Progress Log fragment — location crosswalk and co-presence crosswalk

### Step 2, work items 2.2 and 2.3. Employee output, for the manager to merge into
### `4thJ_02_harmonisation.md`'s own Progress Log. This file is not itself that log.

---

## What was built

Six files were produced in `outputs_step2/`: `crosswalk_location.csv`, `outdoor_at_home.csv`,
`crosswalk_copresence.csv`, `crosswalk_unmapped_location.md`, `copresence_availability.md`, and this
progress-log fragment.

**`crosswalk_location.csv`** maps every national location code from the three delivered source
crosswalks (`crosswalk_source_spain_location.csv`, 20 codes; `crosswalk_source_uk_location.csv`, 35
codes; `crosswalk_source_italy_location.csv`, 53 codes — 108 codes total) explicitly, by label, to
one of the four target classes `at_home`, `other_place`, `private_transport`, `public_transport`.
No code was tested by numeric range, per D-S2-3. 102 codes were mapped (Spain 19, UK 33, Italy 50);
6 were left unmapped because their own label was genuinely undecidable between two or more of the
four classes (Spain's `00`, the UK's `90` and `99`, Italy's `97`, `98` and `99`) and are listed in
`crosswalk_unmapped_location.md` instead of guessed. Every one of the four target classes is
non-empty for every country (1/11/6/1 for Spain; 1/12/10/10 for the UK; 2/34/7/7 for Italy, in
at_home/other_place/private_transport/public_transport order) — no (country × class) cell is zero,
so there is nothing to flag loudly for G2.11 at this stage.

Seven mapping rows needed a written rule rather than being a direct label match: Spain's `10`
("place not specified" → `other_place`) and `30` ("transport mode not specified" → `private_transport`,
on the codebook's own structural placement inside the 30-39 private block rather than the label's
wording); the UK's `0` and `10` (both "unspecified location" variants → `other_place`); Italy's `12`
("Casa propria, spazi aperti" → `at_home`, reproducing the D-S2-4 merge that Spain's single code 11
already performs), `49` ("place not specified" → `other_place`) and `55` ("Gommone, barca", a small
private craft → `private_transport`, by its placement in the private-means block against the
separately-listed "Nave"/ship in the public block).

**`outdoor_at_home.csv`** lists four activity codes, shared between the Spanish and Italian
numbering (per D-S2-11), as the explicit `OUTDOOR_AT_HOME` exclusion list for the indoor rule
`indoor_presence = (LOC == 11) AND (ACT not in OUTDOOR_AT_HOME)`: `322` (garden/exterior cleaning),
`341` (gardening/plant care), `342` (yard/farmyard animal care — a judgement call, documented
below), and `344` (walking the dog). Work-at-home is deliberately not in this list, per D-S2-4. UK
activity codes were not used anywhere in this file, since the UK's numbering is a separate list
(D-S2-11) crosswalked by the other employee working on the activity crosswalks.

**`crosswalk_copresence.csv`** has 54 rows: 12 for Spain (6 fields × 2 values), 22 for the UK (9
fields, with `WithMother` and `WithFather` each carrying 4 rows — 2 for their `cop_parent` mapping
and 2 for their own `EXTRA:cop_extra_uk_*` audit trail — and the other 7 fields carrying 2 rows
each), and 20 for Italy (8 fields, with `cmadre` and `cpadre` each carrying 4 rows for the same
reason, `cfrate` carrying 2 rows as `EXTRA:cop_extra_it_siblings` only, and the other 5 fields
carrying 2 rows each). The six bit positions `{0,1,2,3,4,5}` are each used by exactly one shared
flag, confirmed by direct count (self-check 5 below). Spain's value map — `1 = yes`, `6 = no` — is
written explicitly on every Spanish row and confirmed by self-check 7. The UK's `WithMother` /
`WithFather` and Italy's `cmadre` / `cpadre` both survive as their own `EXTRA:` rows in addition to
their `cop_parent` rows, per the hard rule that an OR that discards its inputs cannot be audited.
The UK's `WithMiss` is tagged `NOT_A_PRESENCE_FLAG` (genuine missingness across all six flags,
never a presence category); `WithNA` is tagged `EXTRA:cop_extra_uk_na` (a backward-compatibility
marker, explicitly not missingness, per F-UK-4 and CTUR p. 10 §5.1).

**`crosswalk_unmapped_location.md`** carries the six unmapped codes with per-code reasons, the seven
judged mapping rows with their rules restated, and the per-country / per-class count tables.

**`copresence_availability.md`** carries the country × flag grid (all eighteen cells `recorded` —
no country fails to record any of the six shared flags after the D-S2-8 widening), the seven
country-extra columns, the children-flag divergence table (Spain under-10 / UK 0-7 / Italy
unbounded) with the required prohibition on cross-country comparison, the "explicit missing is not
zero" section anchored on the UK's `WithMiss`, the `WithOtherYK` open item, and two sections added
because the work order named this file for them even though its own header list is otherwise
co-presence-specific: the ES/IT location-merge asymmetry (D-S2-4) and the "codes considered and
rejected" list for `outdoor_at_home.csv`.

---

## Judgement calls and what was decided

* **Six location codes were left unmapped rather than guessed**, because their own label conflates
  two of the four target classes (place vs. transport, or private vs. public transport) with no
  further basis in the codebook to resolve which. This is the direct analogue of D-S2-3's own
  argument against `RL02`'s numeric-range rule: a code whose label does not commit to a class is not
  made to commit by picking the "likely" one.
* **Seven location codes needed a written rule.** Two patterns recur: "X not specified" residual
  codes were classed by what they explicitly rule out (a transport qualifier rules out `at_home`;
  a "(not travelling)" qualifier rules out both transport classes) rather than by what they leave
  ambiguous; and Italy's code `12` was classed `at_home` specifically to reproduce Spain's D-S2-4
  merge, not despite it.
* **Code `342` in `outdoor_at_home.csv` was included on a cross-country label inference, not a
  self-evident single-country label.** Spain's `Cuidado de animales domésticos` is ambiguous on its
  own (could mean pets, which are plausibly indoor); Italy's label at the same numeric position,
  `Cura degli animali da cortile/allevamento`, explicitly names yard/farmyard animals. Because
  Spain and Italy share the same activity numbering under D-S2-11, Italy's fuller label was read as
  disambiguating Spain's terser one for the *same* code, and both were included. This is flagged as
  a judgement call, not presented as certain, in `copresence_availability.md`'s "codes considered
  and rejected" section, alongside the codes I did *not* include on the same reasoning style
  (construction/repair codes without an "exterior"/"esterne" qualifier, and pet-care codes without a
  yard/farmyard qualifier).
* **No "outdoor construction and repair of the dwelling" code was found and included.** Neither the
  Spanish nor the Italian activity list carries a construction/repair code that is unambiguously
  outdoor by its own label (Italy's `352` is, if anything, evidence the opposite way — it explicitly
  says repairs *inside* ("nella") the dwelling). Rather than force a match, this is recorded as a
  gap: the prompt's example category has no clean code to point to in either delivered list.
* **`crosswalk_copresence.csv`'s `national_definition_verbatim` column is not uniformly a literal
  primary-source quote.** See "What I did not verify" below — this is the single most important
  limitation of this deliverable and it is stated plainly rather than smoothed over.

---

## What I could not do, and why

I could not reproduce literal LAYOUT/METH Spanish text or literal TRACC-DG Italian text for the
per-flag co-presence definitions (beyond field names, Spain's `1`/`6` coding, and Italy's
empirically-established blank/ordinal domain, all of which *are* cited to a specific document
location). The delivered file set for this task (`Step1_docs/outputs_step1/`) contains
`codebook_facts_spain.md`, `codebook_facts_italy.md`, `codebook_facts_uk.md` and
`open_items_uk_withother_and_spain_asecu.md`, but not the underlying LAYOUT workbook (`DISEnOS DE
REGISTRO EET 2009 2010.xlsx`), the METH PDF, or the Italian TRACC-DG/HTML files themselves — a
`Glob` search of the whole `4J_docs_occ` tree for `DISEnOS*` and for any `crosswalk_source_*_
copresence*` file returned nothing. For the UK, by contrast, the open-items file *does* reproduce
literal `Pos.=N` DD variable-label text for all nine co-presence columns, so the UK's
`national_definition_verbatim` entries in `crosswalk_copresence.csv` are genuine verbatim quotes,
not paraphrase. For Spain and Italy, where I lacked the primary document, I wrote the field name
(itself verbatim) plus the best-attributed gloss available from `codebook_facts_*.md` or from
`4thJ_02_harmonisation.md`'s own D-S2-8/D-S2-9 findings (e.g. Spain's `MENOR` = "minors under 10 who
live with you"), and I labelled each such entry explicitly as not a literal LAYOUT/METH/TRACC-DG
sentence, rather than presenting it as one. I judged this preferable to either fabricating Spanish
or Italian codebook prose (forbidden outright) or leaving the column blank (which the work order
does not permit — "Not a paraphrase" implies a value is expected, not that an absent one is
acceptable). This is recorded here as a real gap in what this deliverable can support, and the
manager should treat every Spanish and Italian `national_definition_verbatim` cell other than the
field name itself as unverified against the primary source until someone opens the actual LAYOUT
workbook, METH PDF, or TRACC-DG file.

I did not build `harmonised.parquet`, `filter_report.md`, `crosswalk_activity.csv`,
`crosswalk_activity_secondary.csv`, or `activity_target_list.csv` — none of these was assigned to
this task, and several (the activity crosswalks) are explicitly the other employee's work in the
same output directory, whose files I did not read, touch, or overwrite.

---

## WHAT I DID NOT VERIFY

* **The literal Spanish and Italian codebook wording for co-presence flag definitions**, as detailed
  above. This is the largest gap in this deliverable.
* **Whether any of the seven "codes considered and rejected" for `outdoor_at_home.csv` are, in
  actual respondent behaviour, mostly outdoor or mostly indoor.** The rejections are based entirely
  on label wording (absence of an "exterior"/"esterne" qualifier), not on any external evidence
  about what Spanish or Italian respondents actually do when they report these activity codes.
* **Whether `crosswalk_location.csv`'s and `crosswalk_copresence.csv`'s counts actually produce
  non-zero cells once `harmonised.parquet` exists.** The COUNTS section in
  `crosswalk_unmapped_location.md` is a source-code count (how many *codes* map to each class), not
  an episode-weighted count. G2.11 is stated on episodes, and `harmonised.parquet` has not been
  built (Step 2 remains blocked on the sixteen-gate Step 1 re-run, per this step's own STATUS and
  "WHAT BLOCKS THIS STEP" sections) — so a source-code cell being non-zero is necessary but not
  sufficient for G2.11 to pass, and this was not and could not be checked further from this task's
  inputs.
* **The exact `activity_target_list.csv` codes** — this file (D-S2-11) has not been built by anyone
  yet as far as this task could determine, so `outdoor_at_home.csv`'s four codes were checked only
  against the two national source lists, not against a shipped target vocabulary.
* **Whether the UK's activity crosswalk work (the other employee's task) uses the same code numbers
  `322`/`341`/`342`/`344` for the equivalent concepts.** Per the task instructions, UK activity codes
  were deliberately excluded from `outdoor_at_home.csv`, and I did not open any UK activity-crosswalk
  output to check this.

---

## Self-checks (run with `py`, stdlib `csv` only)

1. **Per-country location source rows = mapped + unmapped, exactly.** Spain: 20 = 19 + 1. UK: 35 =
   33 + 2. Italy: 53 = 50 + 3. All three reconcile exactly.
2. **Rows in `crosswalk_location.csv` whose `target_class` is not one of the four permitted
   strings: 0.**
3. **Distinct `target_class` values in `crosswalk_location.csv`: 4** — `at_home`, `other_place`,
   `private_transport`, `public_transport`.
4. **Empty `source_citation` in `crosswalk_location.csv`: 0.**
5. **`crosswalk_copresence.csv` non-empty `bit_position` values: exactly `{0, 1, 2, 3, 4, 5}`.** The
   `shared_flag → bit_position` mapping is one-to-one: `cop_alone→0`, `cop_partner→1`,
   `cop_children→2`, `cop_parent→3`, `cop_other_hh→4`, `cop_other_persons→5`, each appearing on
   exactly one shared-flag name.
6. **Countries with a mapped `cop_alone` row: 3** (`es`, `uk`, `it`).
7. **Spain's value map in `crosswalk_copresence.csv`, printed:** every Spanish field
   (`SOLO`, `PAREJA`, `MENOR`, `PADRES`, `OTMH`, `OTCON`) has exactly two rows, `national_value=1`
   with `national_value_meaning=yes` and `national_value=6` with `national_value_meaning=no`.
   **Confirmed in words: `6` means `no`.** A bare truthy cast of Spain's raw value would treat `6`
   as `True` and make every Spanish respondent co-present with everybody at once — this is the exact
   bug `G2.14` exists to catch, and the value map that would prevent it is written on every Spanish
   row rather than only stated once.
8. **`outdoor_at_home.csv` row count: 4** (`322`, `341`, `342`, `344`). All four `target_code`
   values are 3-character zero-padded digit strings in the shared Spanish/Italian numbering; none
   is a 4-digit UK-style code (UK activity codes in this delivery run 4 digits or use a different
   sleep code, `110`, versus the shared list's `011` — checked directly and none appear).
