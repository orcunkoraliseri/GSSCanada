# 3J paper - manager handoff, 2026-08-07 (**the draft has now been READ; this is the fix round**)

**Paste this whole file as the first message of a fresh session.**
Predecessor archived at
`Prompts/archive/3rdJ_paper_manager_prompt_2026-08-06_build_complete.2026-08-07_pre_review_round.md`.
This file's own pre-pause copy is at
`Prompts/archive/3rdJ_paper_manager_prompt_2026-08-07_review_round.2026-08-07_pre_pause.md`.

---

## P. PAUSE MARKER - read this before anything else
*(unnumbered on purpose so the section numbers every cross-reference below relies on do not shift)*

**2026-08-07, ~10:45. The user moved to a different project. This round was opened and then paused
with ZERO manuscript edits made.** Nothing below has been executed. Everything in sections 1 to 9 is
still exactly as true as it was when the round opened, with the four corrections in 0.2.

### P.1 The two user decisions in section 1 are STILL OPEN

Neither was answered. **Ask again in the first message, then proceed on the rest without waiting** -
both are decoupled from the mechanical work.

1. **The two disputed DOIs** (section 1.1). Still carrying `**DOI DISPUTED, DO NOT SUBMIT UNTIL
   RESOLVED**` in `Chapter_01_Introduction.md`. Still not swapped. Ten seconds of user clicking.
2. **SI Tables B1 / C1 - keep, cut, or rewrite** (section 1.2).

A third, from section 6 item 4: **the front-matter `[confirm]` placeholders** (department, ORCIDs,
CRediT split, funding) also need the user and were not asked for. Ask for all three at once.

### P.2 🔴 State on disk at pause - what went stale, measured today

Measured 2026-08-07 10:45, not carried forward from a report:

| artefact | recorded where | value at pause |
|---|---|---|
| `writing/fullSet/3J_full_manuscript.md` | build report said 2,186 lines / `c68924293b...` | **2,276 lines**, md5 `53abd5f6875dc8e2bf51882b2044a101`, mtime 2026-08-06 22:29:37 |
| `writing/fullSet/readySubmission.md` | R1 said 1,733 lines / `fcb14eda...` | **1,785 lines**, md5 `f65161de8d255e50e3be2991d2c184de`, mtime 2026-08-06 22:29:37 |
| Step-9 frozen gates | quoted as 17/10/3 | **confirmed from `outputs_step9_deliverable/step9_gates.json` itself: 30 gates, PASS 17 / INFO 10 / FAIL 3** |

Verification commands, so the next session can re-measure rather than trust this table:
`(Get-FileHash <file> -Algorithm MD5).Hash` locally, `wc -l` for lines (**never** PowerShell
`Measure-Object -Line`), and for the gate tally
`py -3 -c "import json,collections;d=json.load(open(r'<path>\step9_gates.json'));print(collections.Counter(g['status'] for g in d))"`.

Three consequences, and the first one costs real time if missed:

- 🔴 **EVERY LINE NUMBER IN `3rdJ_R1_readthrough_review.md` IS STALE.** It read a 1,733-line file;
  the file is now 1,785 lines. The figure-placement and double-caption fixes in section 5 landed
  *after* R1 was written. **Locate R1's findings by their quoted text, never by its line numbers.**
  The findings themselves are unaffected - only the coordinates moved.
- **R1's scope-note complaint is resolved.** R1 flagged that someone had edited `readySubmission.md`
  without its sibling. Both files now carry the **same mtime to the second**, which is consistent with
  one `assemble_3J.py` pass. They are still intentionally different in content (the strip); that is
  section 3's design, not drift.
- **Two R1 findings are already DONE. Confirmed on disk at pause, not taken from a report:**
  `grep -c '!\['` on `readySubmission.md` returns **15**, so 5.3 (seven schematics absent from the
  body) is closed; `grep -n '^\*\*Table '` returns all ten captions **including `**Table 4.**`**, so
  5.1 is closed by the loss check in section 4. Do not re-open either. Read R1 with section 5 of this
  file open beside it.
- **R1 5.4 is still open and the same grep shows why:** Table 6 is captioned at line **587**, Tables 3,
  4 and 5 at **791 / 823 / 1091**. Three chapters early, exactly as section 6 item 3 says.

### P.3 What did NOT change while paused

No manuscript file, no figure, no check script, no gate, no band. The closure state described in the
predecessor round still holds: **no band moved, no gate verdict changed.** The board at the fixed URL
in section 8 is current; there is nothing new to publish until work resumes.

### P.4 Start here on resume

**Section 9's N6 (the figure renumbering) is the first thing to do, before any other edit touches a
chapter.** It is listed sixth there for historical reasons only; the ranking in section 6 item 2 is the
operative one. Nothing else in section 9 is safe to start in parallel with it, because it rewrites
captions and in-prose references across every results chapter.

---

## 0. Who you are

You are the **manager (Opus)** for the **3rd journal paper (3J)**. The manuscript exists, has been
stripped to a submission copy, and has now been **read end to end by one reviewer for the first
time**. This is a **fix round**. Plan, decide, write prompts for employee sessions, review. Hand long
mechanical work to a Sonnet/Haiku employee with a written task doc.

**First read `CLAUDE.md` and `memory/MEMORY.md`.** Reply in **English** even though the user writes
French. Casual, <= 100 words unless detail is asked for.

---

## 1. 🔴 Two things need the user in the first five minutes

### 1.1 A disputed DOI, resolvable in one click, currently sitting in the reference list

`RV08` reports that **both** competitor DOIs in `Chapter_01_Introduction.md` resolve to unrelated
papers:

| in the manuscript now | RV08 says it actually is | RV08's replacement |
|---|---|---|
| `10.1016/j.apenergy.2023.122247` (Doma and Ouf 2024, *Appl. Energy* 355, 122247) | a paper on hydrogen production via anion exchange membrane electrolysis | `10.1016/j.apenergy.2024.124081`, *Appl. Energy* **375**, 124081, authors **Doma, Padsala, Ouf and Eicker** |
| `10.1016/j.enbuild.2019.109562` (Buttitta and Finn 2020, *Energy & Buildings* 206, 109562) | a paper on cold environments, sleep and thermoregulation | `10.1016/j.enbuild.2019.109577`, same journal and volume, article **109577** |

**Verified offline before believing it:** `dr_L3-10` really does cite both of those DOIs
(lines 36, 38, 111, 113), so RV08 did **not** invent the error it reports. What cannot be verified
from inside this project is which DOI is correct: **both citation forms are internally consistent**
(the Elsevier article number matches the DOI suffix in each), so consistency cannot discriminate and
only opening the DOI can.

**Action for the user: open the two current DOIs.** Ten seconds each. Both references now carry
`**DOI DISPUTED, DO NOT SUBMIT UNTIL RESOLVED**` in the manuscript. They were deliberately **not**
swapped on one unverified report.

*If RV08 is right, this is the most serious thing found in the whole writing phase: the paper was
about to cite a hydrogen electrolysis paper as its closest prior work.*

### 1.2 The SI carries the project's own sprint board

The R1 review found that SI Tables **B1** and **C1** are the project's internal improvement-round
tracker, with columns like "Gates moved / Bands moved" and round labels v0 to v5. That is a
development artefact, not supplementary material for a journal. **Keep, cut, or rewrite is the
user's call**, and it is the single largest remaining block of apparatus after Table 6.

---

## 2. Scope - settled by the user, do not relitigate

**The paper is Leg-3, the 4-split:** residential `AT_HOME`, office `AT_WORK`, retail `AT_RETAIL` (the
one new GSS channel), hotel (non-GSS, provincial tourism statistics), driving four uses inside the
PNNL **Tall** and **SuperTall** mixed-use towers, Montreal 6A and Calgary 7A. **56 cells.**

🔴 **Leg-2 is a construction step, not a co-headline.** Methods and section 1.4 only.
🔴 **"four building archetypes" is a 2J phrase and is wrong here.** `f4` check C2 enforces it.
🔴 **The submission copy must be a plain paper**, no notes added during the build (user, 2026-08-06).

---

## 3. What now exists

```
writing/
  implementation/  3rdJ_paper_TASKS.md · 3rdJ_build_status_report.md
                   3rdJ_R1_readthrough_review.md          <- READ THIS SECOND
                   3rdJ_table06_evidence_restructure.md   <- spec, not executed
                   f4_prose_rules_check.py · f5_figure_check.py
  chapters/        Chapter_00 … Chapter_08 (9) + archive/
  tables/          Table_01 … Table_07 (7) + archive/
  tables/SI/       Table_A1_A2 · Table_B1 · Appendix_C + archive/
  figures/         Figure_07…11 · graphicalAbstract · 8 schematics + their .md prompts
                   fig_style.py · one generator script per schematic · make_all_figures.py
                   3rdJ_schematics_implementation_plan.md
  fullSet/         assemble_3J.py · 3J_full_manuscript.md · readySubmission.md · previous/
deepResearch_Resources/  V08 + RV08 (returned) · V07 + RV07 (returned)
```

### The two `fullSet` files are now intentionally different

`3J_full_manuscript.md` is the **working draft**, every note intact.
`readySubmission.md` is that same in-memory document put through **one deterministic transform**,
`strip_for_submission()` in `assemble_3J.py`.

The old guarantee "they cannot diverge" is retired and the build report says so. The 2J hazard is
still closed by the same argument: the difference is **a function that runs on every build and prints
a manifest of every removal**, not a hand edit. **Re-run `PYTHONIOENCODING=utf-8 py -3
writing/fullSet/assemble_3J.py` after any edit** and read the manifest.

---

## 4. 🔴 What the strip taught, and the rule that came out of it

The strip **deleted the `**Table 4.**` caption** and every check still passed. It dropped a
`## Sources` section by running from its heading to the next heading, and the caption sat inside that
span.

**The rule: a residue check and a loss check are different checks.** "Did any apparatus survive?" is
structurally blind to "did any content disappear?". The post-condition had only the first. A human
reader found it.

Both now exist in `assemble_3J.py`, and both have been **seen failing**:
- section drops also stop at the first line that is plainly content again;
- a **loss check** counts every table and figure caption before and after and names any that vanished.

A second near-miss the same night: the inline-`Source:` rule allowed a leading `**`, and on its first
run it deleted a paragraph headed `**Source of truth, and what is explicitly not the source of
truth.**` - a **caveat**, naming the stale `2ndOcc_Journal.docx` that must not be cited. It was caught
only because **every removal was diffed by hand before being accepted**. Do that again for any new
strip rule.

### 4.1 🔴 The second rule, from the schematics: the under-scoped caution

Figures 1 and 2 both asserted the residential and office paths carry forward **bit-identical**.
`Table_06_leg2_leg3_delta.md` grades that exact claim `check source` and says in its own reason column
that the prose assertion behind it **is not acceptable evidence**. Of Table 6's nine step rows, **only
Step 7 is an affirmative Yes**, and only for the base prototype geometry.

This is not a caption nit. **Table 6's Evidence column is the only thing keeping the paper's additive
claim honest, and a figure is read before a table.**

Every arm passed while it was true. `f5` C4 confirmed the label came from its prompt file - correctly,
because **the prompt file was the thing that was wrong**.

**The rule: a caution that names one arm and is silent about the other reads as clearance for the
other.** The prompt file *did* warn about the bit-identical wording. It guarded Leg-1-to-Leg-2 and
then cleared Leg-2-to-Leg-3 as "directly sourced (Step 3 note)". An under-scoped caution is more
dangerous than none, because it looks like the question was already considered.

Fixed additively; new `f5` arm **C7** reads Table 6 from disk (never a copy of its verdicts) and fails
any figure asserting bit-identity for a non-affirmative step. Seen failing on **both** of its branches
plus a **positive control** proving it still licenses the Step 7 claim - the first falsifier only
exercised the fallback path, so a second was required. Detail in
`writing/figures/3rdJ_schematics_implementation_plan.md`.

**Carry this forward:** when you write a caution, enumerate every arm it does *not* cover, or state
that it covers all of them.

---

## 5. Fixed last night, verified, do not redo

- **The retail median contradiction.** Chapter 5, the Abstract and the Discussion said **75.63 /
  5.47 % below floor**; Chapter 7 and Table 7 said **75.4 / 5.7 %**, for the same quantity. Both sides
  were internally consistent arithmetic, which is why neither looked wrong alone. Re-derived from the
  frozen CSV: 56 retail rows, `eui_CFA_kWh_m2` median **75.6260**, **5.4675 %** below. Chapter 7 and
  Table 7 corrected to **75.63 / 5.47 %**. **No band moved, no verdict changed** - retail was under
  its floor before and after. *No check in this project compares a number in one chapter against the
  same number in another chapter. That gap is still open.*
- **A broken cross-reference.** Results §5.1 said "Section 5.2 (Figure 10)" when §5.2's figure is
  Figure 7. Corrected.
- **All eight schematics now exist as code figures**, PDF and 300 dpi PNG, from one shared style
  module. Figure 3 renders **"3 GSS heads + 1 non-GSS side-track"** and the string "4 heads" appears
  nowhere except in comments forbidding it, verified independently of the employee's own check.
- **All 15 figures are now placed in the text.** They previously existed but had no placeholders:
  the assembler was appending seven of them to a named leftovers appendix. Placeholders inserted at
  the section each figure belongs to, and **Chapter 5's double-captioning fixed** - it had been
  captioning every result figure twice, once as a caption with no image and once as an image with no
  caption. Merged, so each figure now sits captioned once at the point that discusses it. The
  leftovers appendix is empty again.
- 🔴 **Two real defects in Figure S1, the only data figure, both originating in its prompt file.**
  Found by cross-footing against `Appendix_C_corrections.md`: (a) the four shares sum to **97.59 %**
  and **97.49 %**, not 100, because the source's fifth occupiable share, **residential-common 2.40 % /
  2.50 %**, was omitted; (b) each bar is labelled with the **gross** area while every segment is a
  share of the **occupiable** area, so a reader who multiplies gets a wrong number for every channel.
  *Proof the shares cannot be of gross:* occupiable / gross = 79.36 % and 78.59 %, which plus
  service/MEP 20.6 % and 21.4 % gives 99.96 % and 99.99 %, so the two denominators are distinct and
  the shares must be of occupiable. The correction is written into
  `figures/SI/Figure_S01_occupiable_shares.md` so it cannot be reintroduced from the prompt.
- **`V4-C3` is ANSWERED, not blocked.** `RV07` returns a documented **NOT FOUND**: no open,
  machine-readable Quebec hotel-occupancy series covering any part of 2011-2018 exists. Six portals
  searched and listed. The manuscript's existing statement (hotel uninjected pre-2019) is confirmed
  and now has a citable negative behind it. A **paid custom ISQ extraction** (*Service des demandes
  d'information*) is the only route, which is a user decision, not a block.

---

## 6. 🔴 Open findings from the R1 read-through, ranked

Full detail with line numbers and quotes in `writing/implementation/3rdJ_R1_readthrough_review.md`.
**Read it before touching the manuscript.** Ranked by what would embarrass us most in review:

1. **L8's residential central `130.6` is the midpoint of its own range.** (113.9 + 147.2) / 2 =
   130.55. The value appears **nowhere** in the deliverable CSV, which has no `info_central` column at
   all, and **Table 5 explicitly declines to state that same quantity** for that exact reason. Table 7
   prints it. The two tables contradict each other about whether the number exists. Left in place,
   because Table 7 is a declared transcription and the source doc does say it
   (`3rdJ_00_4split_Occupancy_Pipeline.md:768`); documented in Table 7 manager note 5 with a reopen
   trigger. **Only SHEU-2019 itself can settle it.** Nothing operational depends on it: the
   residential band is context only and never a PASS criterion.
2. 🔴 **THE FIGURE RENUMBERING. Do this first, in one pass, and do not do it piecemeal.** All 15
   figures are now placed, but two pairs are out of reading order because the numbers were assigned
   before the placements were known. Order of appearance is currently
   `1 2 3 4 6 5 S1 S2 10 7 8 9 11 S3`. It was **not** done last night on purpose: the figure employee
   was still writing to `figures/`, and a rename racing a generator is how files go missing.

   The mapping is a permutation, so **rename via temporary names or you will overwrite a file you
   still need**:

   | current | becomes | figure |
   |---|---|---|
   | 6 | **5** | hotel side-track (§3.4) |
   | 5 | **6** | tag-2 dispatch (§3.5) |
   | 10 | **7** | longitudinal (§5.1) |
   | 7 | **8** | per-channel EUI (§5.2) |
   | 8 | **9** | diurnal (§5.3) |
   | 9 | **10** | peak hour (§5.3) |

   Figures 1, 2, 3, 4, 11, S1, S2, S3 do not move. Touch: the `.png` and `.pdf` filenames, the
   generator scripts, the prompt `.md` files, the captions, and the in-prose references. **There are
   only 16 `Figure N` references in the whole manuscript**, so verify every one of them afterwards.
   Then re-run the assembler and confirm the leftovers appendix is still empty.
3. **Table 6 sits three chapters before Tables 3, 4 and 5** despite its number. Renumber or relocate.
   Same class of problem as the figures; consider doing both in the same pass.
4. **The front matter still carries `[confirm]` placeholders** - department, ORCIDs, CRediT split,
   funding. These need the user.
5. **95 occurrences of internal task IDs** (`dr_L3-06`, `V2-B3`, `OD-1`), the phrase "this task", and
   French `Defaut` labels survive in the submission copy, concentrated in Table 6 and SI B1/C1.
6. **L11's "18.75 % hot at peak"** does not obviously reconcile with the mechanism described in the
   same sentence. Flagged by the reviewer with explicit hedging; check it.

---

## 7. What RV08 settled, and what to do carefully with it

Six competitor cells came back **SETTLED** and item 8 came back **OUR ERROR**. Section G states that
**none of the findings weakens our positioning claim** - no prior work combines a
time-use-survey-driven, multi-channel, forecast-to-a-future-year model inside a single mixed-use
building. That is the answer we wanted, which is exactly why it should be read sceptically.

**Before filling any Table 1 cell, note these three problems found on vetting:**

- 🔴 **RV07 and RV08 disagree with each other about the Alberta series.** RV07 says
  `ABMKTMONITOR` covers **2011**-2022 (matching our own record and the V07 prompt); RV08 says
  **2010**-2022 and proposes splitting the citation at 2005-2009 / 2010-2022. **That split leaves 2010
  unsourced or double-sourced.** Settle the start year before rewriting the Chapter 2 citation.
- 🔴 **RV08 contradicts `dr_L3-10` on Buttitta and Finn's archetypes.** RV08 says four dwelling types
  (detached, semi-detached, terraced, apartment); `dr_L3-10` says **MURB** archetypes. Both are our
  own external reports and neither has been opened by us. This directly feeds the Stock-scale cell.
- **The "221 buildings" figure for Doma and Ouf is new and load-bearing for nothing.** The verdict
  (district scale, not stock scale) does not depend on it. Prefer the verdict; print the count only if
  the user wants to rely on it.
- **`RV07` Table B2's four annual Quebec occupancy rates (56.4 / 55.8 / 53.6 / 51.9 %) were not asked
  for, carry no resolvable locator** beyond a bare domain, and one row's own vintage field contradicts
  its label. **Do not cite them.** They also cannot fill the gap: they are annual, and the hotel
  channel needs monthly.

**Section F of RV08 proposes "zero uncharacterised `n/r` cells" as a target. Reject that framing.**
`NOT FOUND` is a publishable result in this project and always has been.

---

## 8. Standing hazards, unchanged

- **Three EUI gates FAIL and stay failing.** Office: uninjected `Default_NECB` control scores **85.45**
  against a floor of **100**, two mechanisms tested and **both refuted 56/56**. Hotel: **28/56 FAIL,
  every one above the 300 ceiling, every one `Tall`**, range **203.33-318.42**. Retail: median-in-band,
  median **75.63**, **5.47 %** below the floor, 44/56 under. Written up at full strength.
  **R1 (2026-07-21): never resolve a gate by picking the rule that passes.**
- **The two-directory hazard.** `outputs_step9_deliverable/` (frozen 2026-08-06 00:05) is canonical;
  `outputs_step9/` (2026-07-31) is superseded, **inverts the hotel result**, both report "28 of 56",
  and **must not be deleted or renamed** (8 unique files, including the uninjected control behind the
  office finding). `f4` C3 catches a manuscript file citing it.
- **`fig_diurnal_4ch.png` is byte-identical in both arms.** Provenance recorded in Progress Log #2.
  Bookkeeping, **not a risk**; do not present it to the user as a problem.
- **2J magnitudes must be post-`V4-B4`.** Residential **115 / 100 / 108 / 78**. **Leg-2 office 172.7 is
  superseded by 106.56** (verdict IN both ways). Source of truth
  `2J_docs_occ_nTemp/writing/fullSet/readySubmission.md`, **not** `writing/sharingCHV/2ndOcc_Journal.docx`.
- **The limitations section numbers `L8` twice.** Table 7 adopts the source's sixteen and documents
  the collision. **No sentence may claim the count was verified.**
- **Retail is 5.47 % below its floor, not 0.15 %.** The 0.15 % is the retired all-cells rule's
  decision margin.
- **`f3` returns 4 PASS / 1 FAIL and that is correct.** C2 names `graphicalAbstract.png` and
  `Figure_S03_leg2_pipeline.png`, root-level diagrams that were never Step-9 outputs. **Do not modify
  `f3`.** A third name, or any C1 hit, is a real failure.
- **`f1` and `f2` are green about `improvements/v4`, not about the manuscript.** Never report "all
  checks green" without that sentence.
- **Speed:** `ssh`/`scp` to *fetch* is allowed. **Never `srun`, never bare python, never a login-node
  computation. Always `sbatch`, always `-t 7-00:00:00`.** One stream at a time.
- **Frozen Step-9 gates: 30 total, PASS 17 / INFO 10 / FAIL 3.** Re-counted from
  `outputs_step9_deliverable/step9_gates.json` on 2026-08-07, not carried forward from a report.
- **This is still a writing phase: zero simulation cells.**
- **Deep research is EXTERNAL.** The deliverable is a `V<NN>` prompt; the user runs it.
- **Archive the predecessor before editing; corrections are additive.**
- **Never count lines with PowerShell.** `py -3` is the only working Python invocation.
- **Re-run every check at closure, not at authoring.**
- **A reported `grep` result is not a check.** Three readers in one round reported "zero em dashes"
  from a `grep -P` that had returned exit code 2; **96 dashes were present.**
- **The three-artefact closure ritual, every round, unprompted:** Progress Log, this manager prompt,
  and the board republished at
  <https://claude.ai/code/artifact/0e491191-c0c7-41d0-abe7-6023a13a1213> - plus memory. Every decision
  carries a recorded reason and a written reopen trigger.

---

## 9. Suggested next round

Nothing is owed. Ranked as the manager would.
🔴 **Execution order is not list order: do N6 FIRST, alone.** It rewrites captions and in-prose
references across every results chapter, so anything else editing a chapter at the same time will
conflict with it or be silently reverted by it. N1 through N5 all assume the renumbering has landed.

- **N1. Work `3rdJ_R1_readthrough_review.md` top to bottom.** It is the only end-to-end read this
  manuscript has had. Everything in §6 above comes from it.
- **N2. Execute the Table 6 relocation spec** (`3rdJ_table06_evidence_restructure.md`). Written, tested
  and ready; it just needs an employee.
- **N3. Fill Table 1's six competitor cells from RV08**, after settling the two contradictions in §7.
- **N4. A second read-through by a different reader**, on the fixed draft. The first one found a
  contradiction in the paper's own headline number, a deleted caption and a broken cross-reference
  that four checks and three sessions had missed. That is a strong argument for doing it twice.
- **N5. Choose a target journal**, which sets the abstract limit (currently 225 words), the reference
  style and the figure count.
- **N6. Renumber the figures.** All fifteen are now inlined, but two pairs sit out of caption order.
  Deliberately not done last night: the figure generators were still writing to `writing/figures/`
  and a rename racing a generator loses files. The permutation is recorded in §6. Do it first thing,
  before anything else edits a chapter.
- **N7. Settle `f3` C2's grown failure list.** It reported an identical "4 PASS / 1 FAIL" before and
  after the schematics landed, while its C2 list grew from **2 assets to 10**. The label was stable;
  the population was not. The eight new schematics have a *stronger* provenance than a registry entry
  (a generator script with proven md5 determinism) but not one C2 can read. Either register the eight
  md5s in `V2-G1_FROZEN_DELIVERABLE.md`, or add an additive arm for script-generated assets.
  **Do not relax C2 to make the count go back to 2.**
- **N8. Close the `f5` C4 converse gap.** C4 checks every `LABELS` entry appears in a source file, but
  not that every drawn string appears in `LABELS`. "carried forward" is drawn in Figure 2 and is
  unregistered. Harmless today, but an unregistered string is one C4 can never police. Needs a drawn
  string extractor.
