# 4J — MANAGER RESUME PROMPT

### Hand this to the next session as its first message. Fixed path, edited in place, never duplicated.
#### Last updated: 2026-08-15, after the Steps 4-9 audit, the four-fold Step 4 rewrite, Speed job 1245620, the Step 1 gate re-run that closed Spain, the arrival of the UK and Italian data, both parallel Step 1 rounds returning, and **the M-1 to M-5 decision round — Step 1 is now a SIXTEEN-gate specification and the next employee round is written and ready to run on Speed**.

---

## 🔴🔴 AUTHOR DECISION 16, 2026-08-15: **FRANCE IS EXCLUDED. THE CORPUS IS THREE COUNTRIES.**

*"Maintenant nous n'avons pas la France, et quand elle va venir je ne sais pas — exclure France sur les
plans et continuer. Je ne veux pas attendre une ou deux semaines de plus."* Progedo demande n°38663 has
no published turnaround and no arrival date. **The project does not wait on it.**

**The corpus is Italy 2013-14, Spain 2009-10, UK 2014-15. All three are built.** This amends decisions
6 and 11; it does not reopen 5, 13 or 15. Full text in the parent plan's progress log, last entry.

| Was | Is |
|---|---|
| Four countries | 🔴 **Three** |
| Four-fold rotation, LOCO trains on three | 🔴 **Three-fold, LOCO trains on TWO** |
| 6 Leg-5 + 4 Leg-4 jobs | 🔴 **5 Leg-5 + 3 Leg-4** |
| Step 8: four populations | 🔴 **three** |
| `V1.a` / `V2.a` FAIL below 4 | 🔴 **below 3** |
| C4: four countries, trains on three | 🔴 **C4: three, trains on two** |
| Step 2 age floor 11 (France's minimum) | 🔴 **10** (Spain's), by the same rule re-evaluated |

🔴 **`V1.a` moving 4 → 3 is the one change that must not be read as a gate fix.** It is decision 6 in
executable form and it moved **only** because the author moved decision 6, in writing, on a dated line.
**It is not a `--single-country` flag and it is not a precedent.** Every other guard keeps its
threshold.

✅ **The pre-named fold does NOT move: still held-out SPAIN.** The alphabetical-ISO rule (ES, FR, GB,
IT) returns ES with or without France, so the pre-registration written before anything was trained
survives untouched. 🔴 Had the rule selected France, the honest move would have been to re-run the rule
and say so loudly — never to slide to the next-best fold.

🔴 **If France arrives later — decided now, because deciding it later is the defect.**

* **Before any fold has been SCORED:** re-admit it in full, the corpus returns to four, every count
  above reverts. **This is the only window in which France can become training data.**
* **After the first fold is scored:** the design is frozen by decision 11. France becomes an **extra
  held-out country, reported separately** as an out-of-design transfer test. Never a fourth fold, never
  averaged into the rotation.
* **The window closes at Step 6's first score, not Step 4's first submission.** The two dates are weeks
  apart and the tempting reading is the later one.

**What this unblocks, and it is the point:** `V1.a` stops firing, **Step 1 becomes closable** as soon
as the sixteen-gate re-run passes, and **Step 2 is no longer blocked**. 🔴 **The critical path is now
entirely ours** — Step 1 re-run → Step 2 → Step 3 → training — with no queue in another institution on
it.

**What gets worse, stated rather than netted off:** LOCO on two training countries is the thinnest
version of this test that is still a test. C4 is rewritten. Track A rises in value again: 3 → 17 is a
larger multiple than 4 → 17.

**And still true:** there is no `corpus.jsonl` yet, because Steps 2 and 3 have not run. **Free capacity
on Speed does not shorten the path. Do not start a training job to use up an allocation.**

---

## YOUR ROLE

You are the **manager** on paper 4 (4J). You plan, you vet, you write specifications and employee
prompts. **You do not implement.** One employee round has run — Step 1 on Spain, 2026-08-14 — and its
output is in `../Step1_docs/outputs_step1/`. The next moves are the three remaining acquisitions, four
decisions the Spanish file forced, and one gate that has to be redesigned.

Read `../4thJ_00_HETUS_LLM_Pipeline.md` before doing anything else. It is 1,800 lines and it is the
only authority. `../4thJ_00_HETUS_LLM_Pipeline_Overview.md` is the map; the step folders
`../Step0_docs/` to `../Step9_docs/` are the working specifications.

---

## THE PAPER, IN FIVE LINES

Fine-tune **one open-weight LLM** on HETUS-harmonised time-use diary microdata so that it generates
activity-resolved occupant schedules for **any** country in the framework, and test that claim by
**holding one country out of training entirely**. Output drives EnergyPlus residential archetypes.

It exists because paper 1 (CENTUS, *Energy and Buildings* 357, 117155) **claimed HETUS
standardisation as the route to cross-national transfer and never tested it.** That untested sentence
is this paper.

---

## 🔴 STATE: SPAIN, THE UK AND ITALY ARE BUILT — **AND THAT IS NOW THE WHOLE CORPUS**

🔴 **Read the decision-16 block above first.** Everything below this line was written while France was
still expected, and where it says *"`V1.a` fires on three of four"* or *"France is the only acquisition
left"*, **that is superseded**. It is kept because the reasoning about the deliveries, the gates and
the heterogeneities is all still live — only France's status changed.

Updated 2026-08-14. **Step 1 has been executed on Spain, end to end.** The INE *Encuesta de Empleo del
Tiempo* 2009-2010 is downloaded and hashed, its codebooks are transcribed with citations, the reader
is written, and `episodes_spain.parquet` exists: **19,295 diaries, 2,778,480 slots, 430,754 episodes,
zero unparsed rows.** ✅ **The gate battery has since been redesigned and re-run, 2026-08-14:
fourteen gates, thirteen scored, thirteen PASS, `G1.7b` permanently `NOT CHECKED`, and the coverage
clause SATISFIED — every scored gate was made to fall by something in the set.** Output:
`../Step1_docs/outputs_step1/gate_report_step1_spain.txt`.

🔴 **Step 1 is nonetheless NOT done, and now for one reason only: `V1.a` fires on one country of
four.** That is the correct behaviour and it stays until the UK, France and Italy files exist. Nothing
inside the specification is outstanding. **Do not read "Spain's battery is green" as "Step 1 passed".**

### ✅ 2026-08-14, later the same day — the UK and Italian data ARRIVED. France is in the post.

The author delivered three items to `../Datasets/`. The manager inspected all three:

* **UK — complete.** UKDS **SN 8128**, UKTUS 2014-15, tab release, End User Licence. 587,632 lines in
  `uktus15_diary_ep_long.tab` and 11,422 in `uktus15_individual.tab`, both including the header, with
  all six data dictionaries and the NatCen and CTUR technical reports.
* **Italy — complete, and the wave is confirmed.** `Nota_metodologica-2013.pdf` states *"Periodo di
  riferimento: anno 2013-2014"*. 1,077,658 diary lines, 44,867 individual lines, record layouts and
  code lists inside the zip. 🔴 The accompanying `UsoTempo_2023_IT.zip` is the **volunteering module of
  a later wave and contains no diary at all** — excluded, and recorded as excluded.
* **France — NOT data.** The zip holds one PDF, the author's Progedo request receipt, **demande
  n°38663, submitted 2026-08-14, under review.** The requested item is the right one and is better
  than the national file: `[lil-1065] Emploi du temps (version pour Eurostat) - 2009-2010`.

**`V1.a` therefore goes from 1 of 4 to 3 of 4 and keeps firing.** It clears only when France lands.

🔴 **Reading the two new layouts turned up three heterogeneities the specification does not yet
cover.** All three are the manager's to close and none is an employee's to decide:

1. **Spain is the only slot-level file.** Italy and the UK are native episodes with explicit times, so
   Spain's first-of-run reconstruction has no analogue there. Step 9 was specified on 2026-08-14 to
   calibrate on **slots** — for IT and UK those slots must be rebuilt onto a grid, and that
   reconstruction is currently unwritten.
2. **Secondary activity is not one thing.** Spain: one, on the primary's 3-digit list. Italy: one, on a
   **coarser 34-code list** (`catcon`, confirmed a separate classification and not a truncation of
   `catpri` — F-IT-3). UK: **three** (`What_Oth1/2/3`). The record contract carries one `act2_raw`.
   Both employees were told to carry everything and decide nothing, and both did. ✅ **Three of the four
   coverage rates F-ES-6 closes on are now measured:** Spain 80,800 of 430,754 episodes (18.8 %), Italy
   257,998 of 1,077,657 (23.9 %), UK 163,105 / 15,968 / 1,353 of 587,632 (27.75 % / 2.72 % / 0.23 %).
3. **Co-presence sets differ** — Spain 6, Italy 8 (it splits mother from father, where Spain has a
   single `PADRES`), UK 9 including explicit `WithMiss`/`WithNA` missingness fields. `COP` needs a real
   cross-national rule at Step 2, not the Spain-shaped one.

Also: **the UK ships two diary weights**, `dia_wt_a` and `dia_wt_b`. Which one is used is
pre-registration-relevant and is **unmade**.

**Two employees ran in parallel on 2026-08-14 and BOTH RETURNED, 2026-08-15**, against
`4thJ_employee_step1_uk_2026-08-14.md` and `4thJ_employee_step1_italy_2026-08-14.md`: codebook facts →
reader → full fourteen-gate battery, per country. Because they ran concurrently, **neither wrote to
`acquisition_manifest.json` or to either Step 1 progress log** — each emitted a fragment
(`acquisition_manifest_<country>.json`, `proglog_entries_<country>.md`) and **the manager merges them.
Those two merges are still OUTSTANDING.** Results below.

🔴 **Each employee had to establish `G1.7b`'s fate from its OWN country's weighting methodology.**
Circularity is a property of the source and does not transfer from Spain. The same applied to whether
`G1.8` narrows. **Both did so, with their own page citations** — ISTAT `Nota_metodologica-2013.pdf`
p. 12 for Italy, NatCen p. 31 §7.4 for the UK. Neither inherited Spain's verdict.

### ✅ 2026-08-15 — THE UK AND ITALIAN BATTERIES ARE IN. Neither is clean, and that is the point.

Artefacts: `../Step1_docs/outputs_step1/gate_report_step1_uk.txt` and `..._italy.txt`. **Fourteen gates
each, eleven scored each.**

| | Italy | UK |
|---|---|---|
| PASS | 10 | 9 |
| FAIL on real, unperturbed data | 1 — `G1.6` | 2 — `G1.4`, `G1.7a` |
| `NOT CHECKED` | `G1.7b`, `G1.7c`, `G1.8` | `G1.7b`, `G1.7d`, `G1.8` |
| Coverage clause | SATISFIED | SATISFIED for the 9 that PASS |
| Episodes | 1,077,657 (41,229 diaries, 1/respondent) | 587,632 (16,533 person-days, 8,274 people, 2/respondent) |

**The `NOT CHECKED` sets differ by country and each difference is a real property of the delivery, not
a copied verdict:** Italy's `G1.7c` cannot run because `coefin`/`coefi2` exist in exactly one file, so
there is no cross-file restatement to compare; the UK's `G1.7c` **PASSES** because its weights are
restated in three files and were compared bit-identically, 0 mismatches of 16,533. The UK's `G1.7d`
cannot run because the delivery is tab-delimited with free-text decimals and ships no fixed-width
layout to check magnitudes against.

🔴 **What the manager verified personally against the raw files, rather than trusting the reports:**

* **Italy `G1.1`'s reference is genuinely external.** ISTAT's `!Leggimi.html` states `1077657` and
  `44866`; both match the parsed counts exactly. This is the one Italian gate whose reference does not
  come from the file it audits.
* **UK `4276` is real** — that activity code occurs **exactly once in 587,632 rows** and is labelled
  nowhere in the delivered dictionary. A genuine data defect.
* **UK `-9` in `WhereWhen` occurs 7,117 times, 1.211 %** — and `-9` in `What_Oth1` occurs **424,527**
  times, which is precisely the "recorded and blank" figure the reader reports. 🔴 **So the reader maps
  `-9` to blank for the three secondary-activity columns and leaves it raw in `loc_raw`. Half of the
  UK's `G1.4` failure is our own reader treating one sentinel two ways, not bad data.** See open item
  M-1 below.
* The gate runner prints "51 columns" for a 50-column file: `read_raw_tab` appends its own `_key`
  column before the count. Cosmetic, not a defect. Column resolution is by name throughout.

**Not verified independently, and recorded as such:** the perturbation batteries themselves, Italy's
`G1.2`/`G1.11` arithmetic, and every codebook citation beyond the two above. They are read from the
artefacts, which is the standard, but they were not re-derived.

### ✅ 2026-08-15 — THE FIVE MANAGER ITEMS ARE DECIDED. M-1 to M-5. **Step 1 is now SIXTEEN gates.**

Written into `../Step1_docs/4thJ_01_corpusAcquisition.md` (new section "CONTRACT CHANGES M-1 to M-5")
and its validation document (gate table, perturbation table, progress log). 🔴 **Do not reopen them
and do not re-derive them.**

🔴 **The reason none could be left standing as a red FAIL, and it is the load-bearing sentence of the
whole round:** a gate that FAILs at baseline **cannot be seen falling**, so every perturbation aimed at
it reads `DID NOT FIRE`. The three baseline FAILs had silenced **five arms** — Italy's md5 arm
entirely, three of the UK's code-list arms, and the UK's **entire weight arm**. 🔴 **That is also the
most seductive argument in the file, because "clearing the FAIL restores detection power" is what
gate-shopping sounds like from the inside.** Each decision was taken on whether the *threshold was
wrong*; the restored arm is recorded as a consequence, never as the reason. **Where the threshold was
right it did not move: `G1.6b` still FAILs on Italy.**

* **M-1, the `-9` sentinel — contract fixed, gate not.** `loc_raw` gains `act2_raw`'s three states.
  `G1.4` accepts a value as not-a-code **only if the delivery's own value label declares it a
  missingness sentinel**, cited in `codebook_facts`. No rule that negative values are sentinels.
  **`4276` (F-UK-9) still FAILs, which is the test of whether the amendment disarmed anything.** New
  gate **`G1.12`** is the compensating recount, built exactly like `G1.11`.
* **M-2, `G1.6` splits.** **`G1.6a` integrity** (md5, scored everywhere, no URL needed) + **`G1.6b`
  provenance** (URL + date, **threshold unchanged, Italy still FAILs**). The FAIL is a defect in our
  own custody record, not in the file — it clears when the author supplies the URL and date the
  Italian archive came from. Manifest gains `hashed_at` and `provenance_source`. 🔴 **An attested URL
  is as good as ours; an attested hash is not.** France: record URL, date and md5 in the browser.
* **M-3, `G1.7a` re-scoped**, not widened. Positive/finite/non-constant **on rows the delivery
  weighted**, **plus** a new clause: a missing weight on a row the delivery calls **productive** is a
  FAIL. 🔴 **Spain's `G1.7d` population precedent does NOT transfer** — Spain excluded rows carrying no
  diary; the 2 UK person-days carry one that sums to 1,440. **Step 1's population is every diary the
  survey collected; nothing is dropped for lacking a weight.** Weights become nullable.
* **M-4, `G1.7d` conditioned on the declared weighting convention.** *expansion* → `[1.0, 10^width)`;
  *normalised* → `> 0` and **mean within ±1 % of 1.0**; *not declared* → `NOT CHECKED`. Not a
  loosening — `>= 1.0` is true only of an expansion weight and **false** of a normalised one. 🔴 The
  upper-bound half still needs a layout width, so it **stays `NOT CHECKED` for the UK**.
* **M-5, `weight_dia` = `dia_wt_a`.** Our unit is the person-day, which is exactly what NatCen
  documents `dia_wt_a` for and the grain CTUR's own worked example uses it at; and it is the only one
  of the two that balances **day of week**, which is load-bearing for an occupancy paper. `dia_wt_b`
  carried as `weight_dia_b`. **Freezes into `prereg.md`.** One named reopen trigger: if the unit of
  analysis ever moves from the person-day to the person, `dia_wt_b` becomes correct and the choice is
  re-taken in writing **before** anything is trained.

**Six perturbations added, and two of them audit the decisions themselves:** `loc_undeclared_sentinel`
must fell `G1.4` or M-1 disarmed the membership test; `weight_blank_on_productive_row` must fell
`G1.7a` or M-3 removed power instead of redirecting it. 🔴 **If either does not fire, the decision it
audits is reversed — not the perturbation adjusted.**

🔴 **Nothing has been re-run.** All three countries were scored against fourteen gates. **All three
batteries must be re-run against sixteen**, and no country's report may be quoted against the current
validation document until then.

**Two more UK facts that bear on Step 2, both measured:** the diary origin hour is **04:00, not
Spain's 06:00** (F-UK-5), which is live input to the still-withdrawn D-S2-1; and `diary_day` must be
the **1st/2nd-day ordinal, not the day of week** — 3 respondents share a weekday across both their
days (F-UK-6). Minimum age is **8** in the UK and **3** in Italy, against Spain's 10.

Everything else in this folder tree is still a specification, and every threshold in it is
**pre-registered rather than measured**. Also measured: the tokenizer comparison and the licence
sweep, run on Speed on 2026-08-14 (jobs 1234211, 1234216, 1234219, `../tools/`).

Artefacts: `../Step1_docs/outputs_step1/`. Raw archives are on the **local workstation**, not yet on
`/speed-scratch`; the `scp` is outstanding and the manifest records that rather than implying it was
done.

---

## DECISIONS THAT ARE CLOSED — DO NOT REOPEN THEM

| # | Decision | Where |
|---|---|---|
| — | **The trained model will never be released.** Weights and adapters both. The releasable artefact is the synthetic diary corpus (CC BY 4.0) plus code (Apache 2.0) | `RL10` |
| — | **No forecast, no temporal claim, anywhere** | Author |
| 5 | **HETUS only. No Canada, no United States** | Author, 2026-08-14 |
| 6 | ~~Four countries~~ 🔴 **AMENDED by decision 16: THREE countries, one wave each — Italy 2013-14, Spain 2009-10, UK 2014-15. France excluded** | Author, 2026-08-14; amended by the author 2026-08-15 |
| 16 | 🔴 **France is excluded. The corpus is three countries and the rotation is three-fold.** Re-admittable only before the first fold is **scored** | Author, 2026-08-15 |
| 3 | **Backbone: OLMo 3 7B.** Leg-4 is the 1B pilot (correctness only), Leg-5 is the reported model | Our own tokenizer measurement, which overruled `RL18` |
| — | **`ACT` keeps 3 digits.** All four waves share one coding generation, so nothing forces 2-digit pooling | 1A-bis |
| 11 | **No country is held out. All are, in turn** — 🔴 **THREE-fold rotation after decision 16**. All three folds reported including the worst; **design frozen once any fold is evaluated**. Pre-named fold **unchanged: held-out Spain** | Author, 2026-08-14; length amended 2026-08-15 |
| 13 | **Two reproduction tiers:** Spain alone with no credentials, and Spain + UK with two free registrations for the transfer machinery | Author, 2026-08-14 |
| 15 | **Norway is rejected.** No ACL variable and no official recode in the Sikt delivery, only SSB's 167-code national list | `RL20`, vetted V12 |

🔴 **Decision 6 is a decision about newer waves as much as older ones.** UK 2020-21, Italy 2022-23,
Spain 2024-25 and France 2024-25 are all out, and **Eurostat will not release the HETUS 2020 round
before 2027**. There is no newer obtainable corpus. See 1B-bis.

---

## NEXT ACTIONS, IN ORDER

**1. File the Eurostat entity-recognition enquiry with Concordia's Office of Research.**
🔴 **AUTHOR-ONLY, and as of 2026-08-15 it is the ONE item in Step 1's definition of done that nobody
here can execute.** It goes to the Office of Research in the author's own name. Everything else in
Step 1 is either done or is the sixteen-gate re-run. **Step 1 cannot be signed off until this is sent
and the date recorded** — and after decision 16 it matters more, not less: with three countries
instead of four, Track A is the only route that widens the corpus, and it now widens it 3 → 17.
It was second on the list until `RL19` came back. It is now **first**, because `RL19` established that
national routes cannot widen the corpus: of 14 candidate countries, none is Tier 0 or 1, two need the
same institutional accreditation Eurostat does, and two are secure-enclave only. **Track A is not the
slow path to more countries; it is the only one.** With four countries, leave-one-country-out trains on
three, which is limitation C4. Send the enquiry, record the date. *"A report says Concordia is not
recognised"* is already known and is not the same as having asked.

**2. ✅ ACQUISITION IS COMPLETE. Spain, the UK and Italy are done and France is out (decision 16).**
🔴 **There is no acquisition left. Do not chase Progedo and do not open a new source.** The paragraph
below is kept for its findings about the Italian delivery, which still bear on Step 5's release
decision. *(Superseded opening: "France is the only acquisition left.")* UKDS SN 8128 arrived
2026-08-14 and is built. Italy came as ISTAT's own **mIcro.STAT public-use file** — 🔴 **not** the paper-1
copy and **not** the mFR research file (F-IT-1); it carries statistical disclosure control including
**deliberately injected missingness**, and ISTAT itself warns tabulations may differ from published
figures (F-IT-2). That bears on Step 5's release decision and is not a defect to fix. France
(Progedo/ADISP, demande 38663) **needs the author in person** and is the critical path. Work item 1.1 in
`../Step1_docs/4thJ_01_corpusAcquisition.md`. **Record each md5 at download time, not later.**

The Spain round ran from `4thJ_employee_step1_spain_2026-08-14.md` in this folder; the same prompt is
the template for each remaining country. 🔴 **Each reader is written against its own codebook, after
that codebook is in hand.** The Spanish reader (`../tools/4thJ_read_spain.py`) fixes the
intermediate-record contract the other three must meet, and Spain already broke that contract once —
see next action 4.

**3. ✅ DONE, 2026-08-14. G1.7 was redesigned, the runner was rewritten, and the whole battery re-ran
clean.** Employee round from `4thJ_employee_step1_gates_rerun_2026-08-14.md`. **Fourteen gates,
thirteen scored, thirteen PASS, `G1.7b` `NOT CHECKED`, coverage clause SATISFIED.** Counts held at
19,295 / 2,778,480 / 430,754. Nothing below needs doing again; it is kept because **the reasoning is
the reusable part — the other three countries get the same treatment and the same traps are waiting.**

* **`G1.7b` is retired, not repaired** — permanently `NOT CHECKED`, both numbers still printed so the
  circularity stays visible. INE calibrates to the figure it compared against (METH p. 34, step 3).
  🔴 **Do not delete it and do not resurrect it.** A retired gate that vanishes takes its hole with it.
* **`G1.7a` kept and tightened**: present, finite, strictly positive, **and more than one distinct
  value**. A constant column is the likeliest shape of "read the wrong bytes".
* **`G1.7c` is the actual replacement — cross-file weight identity.** One weight per person, restated
  in `CINDIV`, `DIARIO1`, `DIARIO2`, `MHOGAR`, must be bit-identical in all four. 🔴 **Recomputed by
  the runner from the raw fixed-width files using the layout offsets, never from the reader's
  output** — a check fed by the reader cannot detect a reader that read the wrong column.
* **`G1.7d` — magnitude against the declared layout** (`< 1e6`, `>= 1.0`). Its reference is the LAYOUT
  document, a different artefact from the microdata, which is what `G1.7b` never had.
* **Four perturbations, each isolating one gate.** The one that matters: replace a respondent's
  `FACTORF` with **another respondent's valid `FACTORF`** — positive, in range, correctly formatted,
  invisible to every other gate. `weight × 10` is struck from the table.
* **Honest boundary now written into the doc:** no gate checks that the weights are *right*. It cannot
  be done offline; `G1.7b` only looked as if it did.

✅ **The reader now carries `act2_raw`** in a nullable pandas `string` column, three states separable
through the parquet round-trip (ES: not recorded 0, recorded-and-blank 349,954, recorded-with-value
80,800 of 430,754 episodes), and `cop_padres` is renamed `cop_extra_es_padres` per D-S2-2.

🔴 **What the round found in the SPECIFICATION rather than in the data — read this before writing the
next country's prompt, because all three would have repeated:**

* **The gate count was wrong everywhere: twelve, actually fourteen.** `G1.1`-`G1.6`, `G1.7a`-`G1.7d`,
  `G1.8`-`G1.11`. Written when `G1.11` was added and the `G1.7` split was counted as two parts, not
  four, then copied into four documents. Corrected in the validation doc's live table and status; the
  earlier progress-log entries keep the wrong number because they are append-only.
* **`G1.11`'s threshold was not implementable as written.** It said a count of *slots* must equal a
  count in the *episode* table. Those are different quantities: **11,216 episodes mix a blank and a
  non-blank `ASECU`, and 13,009 carry more than one distinct value.** Corrected to the episode-level
  identity it was always for — the runner rebuilds episodes from the raw file with its own offsets,
  split key and first-of-run rule. 🔴 **Recorded as a basis change, not folded in quietly.**
* 🔴 **`999` is a real INE code** (row 117, *"Otro empleo del tiempo no especificado"*), so the
  pre-registered `act_raw`/`act2_raw` perturbation set a **legal** code and tested nothing. Now `99Z`.
  **Check every country's out-of-list sentinel against that country's own transcribed list.** A
  sentinel that is secretly valid is a perturbation that cannot fire, which is the coverage clause's
  own failure mode hiding one level down.
* **A first-draft `G1.7d` failed the NULL perturbation** — it read `MHOGAR`'s full 25,895 rows,
  including the 6,600 non-respondent members whose `FACTORF` is an all-zero placeholder. Restricted to
  the 19,295 respondents, the population `G1.7c` already used. **Accepted as the right population, not
  a loosened bound**; those rows carry no diary and enter no corpus. 🔴 **The null case catching it is
  the system working.**

**What did not attribute:** five perturbations moved more than their named gate, all row-removal or
row-rewrite collateral through `G1.5`, now also reaching `G1.2` and `G1.11`. Correct checks, poor
attributors, for a structural reason. Recorded in the validation Progress Log, **not tuned away**.

**Still true and still the rule for the next three countries:** counts must not move when a column is
added, the runner **imports nothing from the reader** for `G1.7c`/`G1.7d`/`G1.11` and prints both
offset transcriptions, and 🔴 **if the coverage clause FAILs, that is the deliverable** — inventing a
perturbation to make it green defeats the one thing the clause does.

**4. ✅ The four Spanish findings are decided, 2026-08-14, as D-S2-1 to D-S2-4.** Written into
`../Step2_docs/4thJ_02_harmonisation.md` (new section after the decided-list), its validation doc, and
the parent plan 2A/2B/2C/3B plus the plan progress log. Findings themselves in
`../Step1_docs/outputs_step1/codebook_facts_spain.md`.

* **D-S2-1, day origin: withdrawn, not replaced.** Spain runs 06:00 to 06:00 and no 04:00 day is
  constructible from it. The origin is chosen from **four measured codebooks or not at all** — picking
  06:00 from the one country we have measured is `RL02`'s error in the other direction. **Step 2 work
  item 2.4 is blocked on it.** The Spanish reader keeps its native 06:00 indexing meanwhile.
* **D-S2-2, co-presence: five shared flags plus country extras as named columns.** `PADRES` survives
  as `cop_extra_es_padres` and is never folded into "other household members". `MENOR` maps to the
  shared "with children" flag **with its national definition recorded**, because Spain's test is
  household composition, not parenthood. Extras are not Step 5 conditioning variables and are not
  serialised into `COP` — a symbol only one country can emit leaks country identity into LOCO.
* **D-S2-3, location: no numeric range test anywhere.** `RL02`'s "10-19 / 20-39" is retracted and
  nothing replaces it; membership is code-by-code from the Step 2 crosswalk into at-home / other
  place / private transport / public transport, with public transport a class in its own right.
* **D-S2-4, code `11`: confirmed and widened.** It merges dwelling, garage, garden and plot, **and
  working from home is `11` too.** The indoor rule stands; only the 3-digit `ACT` separates "at home,
  not working" from "working at home", which Step 9 needs.

🔴 **Three of the four overturned a line the plan listed as decided, and all three came from `RL02`
rather than from a file.** Every remaining `RL02` claim about file content is a hypothesis until a
codebook confirms it — and UK, France and Italy are measured from their own codebooks, **not assumed
to match Spain either.**

Also decided 2026-08-14: **G1.7 is redesigned** (next action 3), so the only thing between Step 1 and
done is an employee round on the gate runner.

✅ **The hole D-S2-3 left is closed: `G2.11`, location class coverage**, added on the author's word
2026-08-14. Every target location class must be non-empty for every country, plus a share-based
trigger for the quiet form, guarded by `V2.e` so it cannot pass by having no classes to check. **Its
perturbation is a relabelling, not a deletion** — deleting the episodes would also break G2.4 and
prove nothing about G2.11's own power; remapping Spanish public transport to private transport leaves
ten gates green and drops only G2.11. Step 2 now has **eleven gates and twelve perturbations, none
run**. G2.8 was widened to cover the extra co-presence columns; no threshold was moved.

**Still undecided from the Spanish round: F-ES-6**, secondary activity, non-blank on 12.2 % of slots
with nowhere in the record to put it. It is a Step 3 question, not Step 2, and it is untouched.

**4-bis. ✅ `RL22` and `RL23` are back, vetted, and both are negative. Nothing is acquired.** Record in
the plan, V15 to V18.

* **Italy 2022-23 does not exist as a file.** The diary microdata has never been released and no
  release date is published; what appeared on 10 February 2026 is the voluntary-work module, which
  the documentation says excludes the diaries. **There is nothing to request.** Recheck in 2027 with
  the HETUS 2020 round, not before.
* **UK 2020-21 is obtainable and not worth having.** The accessible file is the CTUR CaDDI online
  instrument: about **36 activity categories** against roughly 250 three-digit codes in UKTUS
  2014-15, and an **individual online panel with no household clustering**, so no whole-dwelling
  co-presence. Free, Tier 2, one hour of work — and the recommendation is **not to download it**,
  because each acquisition adds a licence with destruction and reporting duties for a file that
  supports no test we have.
* ✅ **Decision 6 is now on better evidence.** UK 2020-21 is out because the file is not a HETUS-coded
  household diary, not because of the mode-plus-lockdown confound. That is checkable by a reviewer.
* 🔴 **Both reports invented a fact about our own corpus:** `RL23` says Spain fields a two-day diary.
  **We measured one**, G1.9, and INE says one. **No variable name from either report may enter a
  document or a reader** — `RL22`'s come from behind a registration wall it could not pass, `RL23`'s
  from a paper questionnaire model with no URL.
* **Do not adopt `RL23`'s "108 codes in ACL 2008".** Our Spanish 2008-generation file uses **116**
  (F-ES-5), and the report is restating `RL02` rather than measuring.

**5. ✅ STEP 2 IS UNBLOCKED, 2026-08-15.** Harmonisation consumes **every** country's
`episodes_<country>.parquet` and after decision 16 that is three, all built. ✅ **D-S2-1 is also closed
— the day origin is decided as D-S2-5: 04:00, reached by treating each diary as a cyclic day**, which
splices only Spain and splices it inside the sleep block. The age floor moves 11 → **10**, because 11
was France's minimum and the rule is *the highest of the participating minima*.

🔴 **One precondition remains and it is ours: the sixteen-gate Step 1 re-run.** M-1..M-5 changed the
record contract, so Step 2 must consume parquets written to the current contract, not the previous one.
**Step 2 does not start on stale parquets.**

*(Superseded text follows.)* ~~**5. Step 2 still cannot start.** Harmonisation consumes all four `episodes_<country>.parquet`.~~ A
four-column crosswalk built from one country and extended by assumption is precisely the defect Step 2
exists to prevent. Step 0 is closed and is a record, not a work plan. **D-S2-1 to D-S2-4 changed what
Step 2 will do; they did not unblock it.**

**6. Decisions 11, 13 and 15 are closed — do not reopen them and do not re-derive them.** Two were
author calls and one was a report, which is exactly the mix a later session is most tempted to redo.

* **11, the held-out country: four-fold rotation.** Every country is held out in turn. All four folds
  are reported **including the worst**, and **the design freezes once any fold has been evaluated.**
  A random household hold-out inside the training countries is retained as an ordinary test set and
  **is never reported as transfer.**
* **13, the reproduction path: two tiers.** Spain alone with no credentials, and Spain + UK with two
  free registrations for the transfer machinery. The UK half is the manager's implementation, not the
  author's selection, and is the part to correct if it is wrong.
* **15, Norway: NO.** `RL20` found the Sikt delivery carries only SSB's **167-category national list**,
  no ACL variable at any depth, and **no official recode table anywhere** in SSB publications, the SSB
  `Klass` database or the Sikt metadata. `RL19`'s recode claim is retracted. **Rejected on the same
  screen as UK 2000-01. The four-country corpus stands and limitation C4 stands with it.**

**7. 🔴 Decision 14 is the only decision still open, and `RL21` proved it cannot be closed by reading.**
No published study has ever compared two or more day-to-year chaining rules on the same building with
the daily generator held fixed. No standard defines a protocol. IEA EBC Annex 66 and 79 are silent. **No
citable threshold exists**, so the 25 % figure is permanently project-chosen.

**It closes by our own experiment, in work item 7.6, or it does not close.** Three things were written
into that item and they are the reason the experiment is not what `RL17` proposed:

* **Rule 3 is swept, not fitted.** A two-day survey of 1 weekday + 1 weekend **cannot identify
  consecutive-day transitions**, so its persistence parameter cannot come from our corpus. Fitting it
  ourselves and comparing it against two rules we did not fit compares our bookkeeping against itself.
* **Record annual energy alongside peak.** `RL21` *infers* annual energy is insensitive. Measuring both
  costs nothing and converts an inference into our own number, which is what settled decision 3.
* **Compute the realistic activity-vocabulary value on held ISTAT data**, not from the report.

🔴 **No number from `RL21` may enter any document.** Its headline 15-35 % peak divergence is labelled a
measured fact in a report whose own `B1` says nobody has measured it, and it appears elsewhere in the
same report as 15-40 % and as 10-25 %. Full list in the plan document, V13.

**8. Compute the unique-sequence baseline on the held ISTAT data.** Still outstanding from the first
vetting round: `RL08`'s U > 0.98 benchmark was invented, `RL17` A7 returned `NOT FOUND`, and **Gate 6
is not trusted until the empirical value is computed on data we hold.** It shares a data source with
the activity-vocabulary value above, so the two are one job.

**8-bis. ✅ Weight pre-staging is DONE — Speed job `1245620`, 2026-08-14, 3 of 3, 33.34 GiB in eight
minutes.** `../tools/4thJ_stage_weights.sh`, partition `ps`, `sbatch`. Hashes copied into
`../Step4_docs/outputs_step4/staged_weights.json`:

| Repo | Revision |
|---|---|
| `allenai/Olmo-3-1025-7B` | `a81bae42db3975be1671e27b9c9a56da1a9f980f` |
| `allenai/OLMo-2-0425-1B` | `a1847dff35000b4271fa70afc5db10fd29fedbdf` |
| `Qwen/Qwen2.5-7B` | `d149729398750b98c0af14eb82c78cfe92750796` |

🔴 **The hashes are the deliverable, not the files.** `G4.11` fails a run whose manifest names a
checkpoint without one.

* 🔴 **A correction came out of writing it: compute nodes on `ps` DO have outbound network.** The plan's
  4F and the Step 4 document both said they did not, which implied the weights had to come down on the
  login node — an act the top rule forbids. The tokenizer jobs pip-installed and pulled from Hugging
  Face inside `sbatch`; so does 1245620. **Offline is a discipline we impose on training runs, not a
  property of the node.** Both documents are corrected.
* **`/speed-scratch` purges after 90 days**, and training is weeks away behind the UK and France
  acquisitions. **Re-run this job before the first training submission and re-read the hashes** — if a
  repo moved, the hash changes and that is exactly what the file exists to catch.

**9. Before Step 7 is sized: run the vLLM throughput comparison** on Leg-5 checkpoints. OLMo 3 7B has
**no grouped-query attention** — 32 KV heads over 32 layers gives about **512 KB per token** against
Qwen2.5-7B's 56 KB, roughly 9× and about 6× after our token saving. **That figure is arithmetic from
the config, not a benchmark**, and it must not be quoted as one.

---

## HOW THIS PROJECT WORKS — THE RULES THAT ARE NOT NEGOTIABLE

* 🔴 **Speed cluster: `sbatch` only.** Never a blocking `srun`, never bare python on the login node,
  not even a one-liner. Every job requests `-t 7-00:00:00`. Flagged three times; a fourth is account
  suspension.
* 🔴 **Deep research is external.** You never search literature or verify citations as the deliverable.
  You write the prompt file; the author runs it. Prompts and reports live in `../DeepResearchPrompts/`
  as `L<NN>` and `RL<NN>`.
* 🔴 **You never create images.** You write the prompt under
  `../writing/submission/figures/Prompts_Images/`; the author generates the figure.
* 🔴 **You never create anything that was not asked for.** If you think something is needed, ask in one
  sentence first.
* **Replies are short, plain English, one thing at a time**, even when the author writes French.
* **Progress Logs are append-only.** Never delete, reorder or reformat an existing entry.
* Never count lines with PowerShell — use `wc -l`. Verify a backup is non-empty before truncating.

---

## 🔴 HOW TO READ A RETURNED DEEP-RESEARCH REPORT

Five rounds have come back. **Every one contained content that was fabricated exactly where it
claimed to be verified**, and every one was caught by cheap offline checking. Before a single value
enters a document:

1. **Check what it says about our own work first.** It cannot see our results or our cluster. Anything
   it reports about them was quoted from the prompt or invented.
2. **A report that agrees with what you supplied has told you nothing.** `RL19`'s Part B returned the
   HETUS guidelines restated per country as though ten codebooks had been read.
3. **Make it obey an identity it cannot fake.** A DOI resolves or it does not. A licence clause exists
   or it does not. `RL19`'s Netherlands entry died the moment the DANS record was opened: restricted,
   unrequestable, superseded — against a claim of "opened in full, guess count 0".
4. **Read the negative controls as evidence, not as reassurance.** `RL19` defined "convenient" as all
   seven properties at once, so nothing could score, then reported zero. **A control that cannot fire
   is not a control** — the same vacuity we screen our own gates for.
5. **Every recommendation in the rescuing direction is a signal.** If a report concludes the data is
   obtainable, the licence permissive, the method right and the compute sufficient, treat the round as
   failed and re-run it.
6. **Salvage the route, not the table.** `RL19`'s value was a negative result plus the observation that
   no national archive ships the Eurostat-harmonised file — neither of which was its recommendation.
7. 🔴 **Check the report against itself before checking it against the world.** It is the cheapest test
   there is and it caught the worst defect in the fourth round: `RL21` reports **zero** studies
   measuring the difference between chaining rules, and then gives that difference as **15 to 35 %**,
   labelled a measured fact with high confidence. **A quantity that appears three times with three
   values, or a number that contradicts the report's own negative result, was never measured.**
8. **A report that returns the answer your prompt said it expected has told you less than it looks.**
   `L20` said a short negative was expected and `RL20` returned a short negative. That verdict is
   accepted **on its checkable details** — 167 categories, `akt1` to `akt144`, Notater 2012/03 — not on
   the report's own confidence. Write prompts that expect an answer, then believe the details rather
   than the conclusion.

The full record is V1 to V14 in the plan document. **Read V6, V11 and V13 before commissioning another
round**; they are what a failed round looks like from the inside, and V13 is what a *useful* round
looks like when its headline number is still unusable.

---

## GATE DESIGN, IF YOU TOUCH ANY VALIDATION DOCUMENT

Read `feedback_gates_must_be_seen_failing.md` in memory first — 46 failure classes, all from real 3J
work. The three that cost the most:

* **Every gate must be seen failing.** A perturbation table where each perturbation breaks exactly one
  gate, plus a **coverage clause** that fails the probe if a passing gate was never made to fall.
* **A gate whose reference derives from the source it audits cannot fail.** At least one check per step
  must arrive through a path the defect cannot reach.
* **A check that cannot distinguish "found nothing" from "could not run" is not a check.** Print
  `NOT CHECKED`, never a pass.

Step 7's G7.1 to G7.4 are labelled **enforcement confirmations**, not gates: they cannot fall while the
grammar mask is on, and counting them in a seen-failing tally would inflate it.

---

## WHERE THINGS ARE

| Path | What |
|---|---|
| `../4thJ_00_HETUS_LLM_Pipeline.md` | The authority. Decisions, vetting record V1-V14, all ten steps, limitations, progress log |
| `../4thJ_00_HETUS_LLM_Pipeline_Overview.md` | One-screen map, ASCII step boxes, open-decision count |
| `../Step0_docs/` … `../Step9_docs/` | Per-step implementation + validation specifications, and `outputs_stepN/` |
| `../DeepResearchPrompts/` | `L01`-`L21` prompts, `RL01`-`RL21` reports, master brief, README with the vetting checklist |
| `../tools/` | The three Speed scripts that produced our own measurements |
| `../writing/submission/figures/` | The graphical abstract PNG and its prompt |

🔴 **The master brief in `DeepResearchPrompts/` is stale** — it still says five countries, multi-wave
and Canada. `L19` carries a corrections block at the top that overrides it. **Any new prompt needs the
same block** until the brief is reissued.

---

## OPEN DECISIONS

**12 of 15 fully closed.** Only **14**, the day-to-year chaining rule, is genuinely open, and it now
closes by our own experiment rather than by any further reading. See next action 7.

Separately from the fifteen: the **four Spanish findings are now decided** as D-S2-1 to D-S2-4 (next
action 4, 2026-08-14), except that **D-S2-1 has no value yet** — it closes when all four codebooks are
in hand. ✅ **The G1.7 redesign is done, implemented and re-run** (next action 3).

✅ **F-ES-6 is decided, 2026-08-14: `act2_raw` is carried, not serialised.** It is in the Step 1 record
contract and in `harmonised.parquet`, with three states kept distinct — not recorded, recorded and
blank, recorded with a value. It is **not** in the `DUR,ACT,LOC,COP` tuple, because a field only Spain
is known to record would leak country identity into leave-one-country-out. **It closes on four
measured coverage rates** in `outputs_step3/act2_coverage.md`, not on a preference. Step 3, 3.2-bis.
New gate **`G1.11`** guards it: a reader that collapses "blank" into "not recorded" moves no row and
emits no illegal code, so nothing else in the battery can see it. **Step 1 has fourteen gates**
(`G1.1`-`G1.6`, `G1.7a`-`G1.7d`, `G1.8`-`G1.11`), thirteen scored and `G1.7b` permanently
`NOT CHECKED`. ✅ **`G1.11` has now run and passed on Spain: 80,800 non-blank episodes by both the
reader and the runner's independent rebuild** — but see next action 3 for the two things it exposed,
including that its own threshold was written slot-level and had to be corrected to episode-level.

🔴 **The specification is now complete and mutually consistent all the way to the first Speed training
job**, not only to Step 3 (audit of 2026-08-14, plan progress log, twelfth entry). Steps 4 to 9 were
read **against the closed decisions and against each other** rather than against themselves, which is
how all three defects were found — each lived between two documents that were correct alone.

* ✅ **Step 4 is four folds, not one run.** It was written for a single Leg-5 run while decision 11 had
  already made it four, and **Step 6 asserted Step 4's output contract said "one adapter per fold" when
  it did not.** Author decision 2026-08-14: **the ceiling run and the Qwen comparison arm are
  single-fold.** Six Leg-5 jobs, four Leg-4 jobs. Section 4D-bis in the plan, and the whole of
  `../Step4_docs/`.
* ✅ **The pre-named fold is held-out SPAIN — confirmed by the author 2026-08-14**, by a rule fixed in
  advance (alphabetical ISO code) and taken while nothing had been trained. It freezes into `prereg.md`
  before the first Leg-5 submission and **does not move after that**. 🔴 Naming it late would point the
  full fine-tune at whichever fold the primary run did worst on, which is selecting on the outcome.
* **New deadline:** `prereg.md` freezes before the first *training* submission, not before Step 6
  scores. Gates **`G4.13`** (fold isolation, counted from the shard the trainer loaded) and **`G4.14`**
  (pre-registration md5, recomputed from disk) plus `V4.f` to `V4.h`. **Step 4 has fourteen gates.**
* ✅ **Step 9's half of F-ES-6 was missing.** Step 3 keeps `act2_raw` and names Step 9 as the reason;
  Step 9 reads *generated* diaries, which carry none. Resolved: the trigger fires from the primary
  code, `act2` calibrates `P(appliance | activity)` on the real corpus, **`G9.14`** asserts it is never
  a runtime column. 🔴 **A trigger reading an absent column does not raise — it silently never fires.**
  If `act2` is ever serialised, it must be **before `corpus.jsonl` is emitted**.
* ✅ **Step 8's campaign is bound to the folds:** four populations, not sixteen, each country simulated
  under the adapter that held it out. **`G8.16`** + `V8.g`.

**What is deliberately NOT written: `prereg.md`.** Its second hold-out's stratification depends on a
corpus that does not exist. Drafting it now and editing it later is the exact defect `G4.14` catches.

🔴 **What is still needed to reach training, REWRITTEN 2026-08-15 after decision 16 — and every item
on it is ours:**

1. **The sixteen-gate Step 1 re-run on the three countries** (prompt written, runs on Speed).
2. The two manager merges, and the Eurostat enquiry sent with a date.
3. **Step 2** — crosswalks, the 04:00 cyclic rotation (D-S2-5), the age-10 filter, eleven gates.
4. **Step 3** — serialisation to `corpus.jsonl`.
5. **`prereg.md` frozen**, then the first Leg-5 submission.

✅ **Step 1's machinery is finished and has been through all three countries.** *(Superseded: "the
France acquisition, then Step 1 on France, then Step 2, then Step 3.")*

🔴 **Updated 2026-08-15: the five manager decisions M-1 to M-5 are TAKEN**, so the specification is
ready for France before France arrives — which was the point of settling them first, since France comes
by the same hand-delivered route that made Italy's `G1.6` fail and will land in the same hole. **M-2
is what France needs**: URL, date and md5 recorded in the browser at download time, `hashed_at` and
`provenance_source` filled in. What remains outstanding is **execution, not decision** — the
sixteen-gate re-run on three countries, then France, then Step 2.

**12** (household-joint generation) remains deferred as scope rather than open as a question: it is
known to be feasible, about 7,000 tokens for a four-person household week. `RL21` gave it a second
reason to exist — household role coherence across consecutive days is a household-level property that
per-person generation cannot enforce.

---

## FIRST THING TO SAY IN THE NEXT SESSION

Say in one sentence that **France is excluded (decision 16), the corpus is Spain + UK + Italy and all
three are built, and the sixteen-gate Step 1 re-run is the only thing between here and Step 2**, then
ask the author what they want next. **Do not begin acquisition, do not chase France, do not start a
training job, and do not commission another research round without being asked.**

### ✅ Both employees finished, 2026-08-15. All deliverables exist and were checked on disk:

| Country | Delivered |
|---|---|
| UK | `codebook_facts_uk.md`, `episodes_uk.parquet`, `parse_report_uk.txt`, `gate_report_step1_uk.txt`, `acquisition_manifest_uk.json`, `proglog_entries_uk.md`, `crosswalk_source_uk_{activity,location}.csv`, `../tools/4thJ_read_uk.py`, `4thJ_gates_step1_uk.py` |
| Italy | the same set, Italy-named, plus the third crosswalk `crosswalk_source_italy_activity2.csv` |

Raw archives unpacked to `_local_runs/4J/raw/{uk,italy}/` — note that tree is under **`GSSCanada\`**,
the parent of `GSSCanada-main\`.

**Merge 3 of 3 is DONE — the reports were verified against the artefacts**, see the STATE block for
exactly what was re-derived and what was not. **Merges 1 and 2 are still owed and neither is optional:**

1. ✅ **MERGE 1 IS DONE, 2026-08-15.** Both `proglog_entries_<country>.md` appended verbatim into
   `4thJ_01_corpusAcquisition.md` and `4thJ_01_corpusAcquisition_val.md`, each under a manager's note
   recording that (a) they appear **after** the M-1..M-5 and decision-16 entries although they describe
   earlier work — the log is append-only and was not reordered — and (b) which of their statements are
   already superseded. 🔴 **The note also records what was NOT independently verified:** the
   perturbation batteries, Italy's `G1.2`/`G1.11` arithmetic, and every codebook citation except the
   two the manager opened personally.
2. 🔴 **MERGE 2 IS DEFERRED ON PURPOSE, not forgotten.** The sixteen-gate employee round is **editing
   the two manifest fragments right now** — M-2 adds `hashed_at` and `provenance_source` to every
   archive entry. Merging them into `acquisition_manifest.json` before that round returns would
   produce a merged file that is stale the moment it is written. **Do merge 2 after the round reports,
   from the updated fragments.**

### ✅ M-1 to M-5 are DONE, 2026-08-15. The employee round is written and ready to run on Speed.

**Prompt: `4thJ_employee_step1_gates16_rerun_2026-08-15.md`, in this folder.** Scope: `4thJ_read_uk.py`
(M-1 only), all three `4thJ_gates_step1_<country>.py`, and one full sixteen-gate re-run on Spain, the
UK and Italy. Hand it to a **fresh** employee session.

🔴 **This round is also what closes the outstanding half of work item 1.1**: TASK 0 `scp`s the three
raw trees (145 + 320 + 145 MB) from `_local_runs/4J/raw/` to `/speed-scratch/o_iseri/4J/raw/`,
**re-verifies every md5 after the transfer**, and runs **one `sbatch -p ps -t 7-00:00:00` job per
country** — three jobs, never chained, so a country that crashes does not take the other two with it.

**This is the only Speed work available today**, and it is not a training job. See the "what is safe on
three countries" block at the top of this file before anyone reaches for the allocation.

🟡 **STATUS 2026-08-16, 00:30 — the round is RUNNING on Speed. Do not resubmit it.** The employee did
TASK 0 (three raw trees copied to `/speed-scratch/o_iseri/4J/raw/`, md5s re-verified after transfer)
and submitted **three jobs, one per country, unchained**: **`1251980` = `4J_g16_es`, `1251981` =
`4J_g16_it`, `1251982` = `4J_g16_uk`**. All three were `RUNNING` at 00:01:08 elapsed. Check them with
one `sacct -j 1251980,1251981,1251982 --format=JobID,JobName,State,ExitCode,Elapsed` — **one call, not
a loop.** The first poller was killed by exactly that mistake: a bash `while ... done` loop was sent to
the login shell, which is **tcsh**, and it died on "Illegal variable name" / "done: Command not found".
The jobs were never affected. 🔴 **Read the results in this order when they land:** the two audit
perturbations (`loc_undeclared_sentinel`, `weight_blank_on_productive_row`) first, then `V1.a`, then the
sixteen gates. **If either audit perturbation reports `DID NOT FIRE`, the decision it audits is
REVERSED — M-4 or M-3 respectively — and the perturbation is not touched.**

### Still the manager's, still open: the three heterogeneities

Slot-vs-episode basis, secondary-activity arity and granularity, and the co-presence sets. **All three
are Step 2/3 specification decisions.** Both employees were instructed to carry every recorded field
and decide none of it, so the material is in `codebook_facts_uk.md` and `codebook_facts_italy.md`.
🔴 **They are Step 2 questions — and after decision 16, Step 2 DOES start on three countries**, because
three is the corpus. Decide them on paper first; they are inputs to Step 2's crosswalk, not
afterthoughts to it. *(Superseded: "Step 2 does not start on three countries.")*

🔴 **Before touching any gate again, read `feedback_read_the_gates_own_doc.md`: additive fixes only,
and a basis change is written down as a basis change.** M-2, M-3 and M-4 were each recorded as basis
changes on 2026-08-15 rather than folded in quietly; do the same for whatever comes next.

🔴 **Step 1 is still not done — but the reason has changed, and this is the last paragraph that used to
say otherwise.** `V1.a` no longer fires: three of three, after decision 16. What is outstanding is the
**sixteen-gate re-run**, the two merges and the Eurostat enquiry. **Nothing external blocks it.**

🔴 **The crosswalk warning still stands and is not repealed by decision 16.** *"A crosswalk built from
some countries and extended by assumption is precisely the defect Step 2 exists to prevent"* — that
means all **three** must be transcribed from their own codebooks, which they are. It never meant "four
or nothing".

🔴 **Do not re-derive a closed decision because the list looks short**, and **do not chase France.** It
is excluded. If it turns up unasked, read the re-admission window in the decision-16 block before doing
anything with it — before the first fold is **scored**, it can come back; after, it can only ever be an
extra held-out test.
