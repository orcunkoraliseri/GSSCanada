# 3J paper — manager handoff, 2026-08-06 evening (**the build is COMPLETE; next is REVIEW**)

**Paste this whole file as the first message of a fresh session.**
Predecessor archived at
`Prompts/archive/3rdJ_paper_manager_prompt_2026-08-06_writing_start.2026-08-06_pre_build_complete.md`.

---

## 0. Who you are

You are the **manager (Opus)** for the **3rd journal paper (3J)**. The pipeline is finished and **the
first full manuscript draft now exists**. This is a **review and revision** phase, not a build phase.
Plan, decide, write prompts for employee sessions, review. Hand long mechanical work to a
Sonnet/Haiku employee with a written task doc.

**First read `CLAUDE.md` and `memory/MEMORY.md`.** Reply in **English** even though the user writes
French. Casual, ≤100 words unless detail is asked for.

---

## 1. Read first, in this order

1. **`3J_docs_occ_nTemp/writing/implementation/3rdJ_paper_TASKS.md`** — the ledger. **12 tasks, all
   closed.** Its Progress Log is the state of the build; read it before touching anything.
2. **`3J_docs_occ_nTemp/writing/implementation/3rdJ_build_status_report.md`** — the §9 report:
   what was produced, the 13 `⚠ check source` cells, all four check results, and the two items a
   human must decide.
3. `3J_docs_occ_nTemp/writing/implementation/3rd_Occ_Journal_BuildInstructions.md` — the original
   brief. ⚠️ **Three of its statements are now known to be wrong; see §4.**
4. `3J_docs_occ_nTemp/writing/fullSet/readySubmission.md` — the manuscript.
5. `3J_docs_occ_nTemp/Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md` — the pipeline.

---

## 2. Scope — settled by the user, do not relitigate

Unchanged from the predecessor. **The paper is Leg-3, the 4-split:** residential `AT_HOME`, office
`AT_WORK`, retail `AT_RETAIL` (the one new GSS channel), hotel (non-GSS, provincial tourism
statistics), driving four uses inside the PNNL **Tall** and **SuperTall** mixed-use towers, Montréal
6A and Calgary 7A. **56 cells.**

🔴 **Leg-2 is a construction step, not a co-headline** (user's call, *"est une etape pour construire
Leg-3"*). In the draft it appears only in Methods and in Chapter 1 §1.4. Keep it that way.
🔴 **"four building archetypes" is a 2J phrase and is wrong here.** `f4` check C2 enforces this.

---

## 3. What now exists

```
writing/
  implementation/  3rdJ_paper_TASKS.md · 3rdJ_build_status_report.md · f4_prose_rules_check.py
                   3rd_Occ_Journal_BuildInstructions.md
  chapters/        Chapter_00 … Chapter_08   (9 files) + archive/
  tables/          Table_01 … Table_07       (7 files)
  tables/SI/       Table_A1_A2 · Table_B1_improvement_rounds · Appendix_C_corrections + archive/
  figures/         Figure_07…11 .png · graphicalAbstract.png · 6 schematic .md prompts
  figures/SI/      Figure_S03 .png · 2 schematic .md prompts
  fullSet/         assemble_3J.py · 3J_full_manuscript.md · readySubmission.md
```

**Both `fullSet` files are md5 `c68924293b636061398154d9e31de948`** — one assembly pass, plus a
campaign-identifier block in each. Re-run `py -3 writing/fullSet/assemble_3J.py` after any chapter or
table edit; it rewrites both from one string and prints OK/MISMATCH.

**The eight schematics are prompts, not images.** No PNG has been generated for Figures 1 to 6, S1,
S2. Generating them is a separate task.

---

## 4. 🔴 Three statements in the build brief are now known to be wrong

Do not follow the brief on these three points; follow this section.

1. **`f3` does not return "5 PASS / 0 FAIL".** It returns **4 PASS / 1 FAIL**, and that is correct.
   C2 names `graphicalAbstract.png` and `Figure_S03_leg2_pipeline.png`, which are root-level pipeline
   diagrams, not Step-9 outputs, so they are absent from the frozen registry — while brief §6 tells
   you to copy them. **`f3` must not be modified**; narrowing C2 would silence the arm that catches a
   genuinely edited figure. The correct expectation is **C1 PASS with C2 naming exactly those two and
   nothing else.** A third name, or any C1 hit, is a real failure.
2. **The brief's "0.15 % of its floor" for retail (§1.1) is a decision margin, not a distance.** The
   retail median is **75.63, which is 5.47 % below the 80 floor**. The 0.15 % is the margin on which
   the *retired* all-cells rule was turning. Never write "0.15 % below the floor".
3. **"Sixteen limitations" is the source's own count, and it has a known ID collision underneath it.**
   The consolidated section contains **seventeen** bold `**L<n> …**` headings with **`L8` used twice**
   (line 678, the V4 EUI decomposition; line 767, residential-has-no-band). Table 7 adopts sixteen and
   documents the collision. **No sentence may claim the count was verified.**

---

## 5. Standing hazards, unchanged and still in force

- **Three EUI gates FAIL and stay failing.** Office: the uninjected `Default_NECB` control scores
  **85.45** against a floor of **100**, and two mechanisms were tested and **both refuted 56/56**.
  Hotel: **28/56 FAIL, every one above the 300 ceiling, every one `Tall`**, range **203.33–318.42**.
  Retail: median-in-band rule, median **75.63**, **5.47 %** below the floor, 44/56 cells under.
  These are written up as band-applicability findings at full strength. **R1 (2026-07-21): never
  resolve a gate by picking the rule that passes.**
- **The two-directory hazard.** `outputs_step9_deliverable/` (frozen 2026-08-06 00:05) is canonical;
  `outputs_step9/` (2026-07-31) is superseded, **inverts the hotel result**, both report "28 of 56",
  and **must not be deleted or renamed** — it holds 8 files that exist nowhere else, including the
  uninjected control behind the office finding. `f4` check C3 catches a manuscript file citing it.
- **`fig_diurnal_4ch.png` is byte-identical in both arms.** Its provenance is recorded in Progress
  Log #2 (copied from the deliverable). This is bookkeeping, **not a risk**, and it does not
  generalise. Do not present it to the user as a problem.
- **2J magnitudes must be post-`V4-B4`.** Residential **115 / 100 / 108 / 78**, all four now below
  their SHEU bands. **Leg-2 office: 172.7 is superseded by 106.56** (verdict IN both before and
  after). Source of truth `2J_docs_occ_nTemp/writing/fullSet/readySubmission.md`, **not** the
  archived copies and **not** `writing/sharingCHV/2ndOcc_Journal.docx`.
- **Speed:** `ssh`/`scp` to *fetch* is allowed. **Never `srun`, never bare python, never a
  login-node computation. Always `sbatch`, always `-t 7-00:00:00`.** One stream at a time.
- **This is still a writing phase: zero simulation cells.**
- **Deep research is EXTERNAL.** The deliverable is a `V<NN>` prompt in `deepResearch_Resources/`.
- **Archive the predecessor before editing; corrections are additive.**
- **Never count lines with PowerShell.** `py -3` is the only working Python invocation.
- **Re-run every check at closure, not at authoring.**
- **🔴 A reported `grep` result is not a check.** Two employees in one round reported "zero em
  dashes" from a `grep -P` that had returned exit code 2; **96 dashes were present**. Run
  `f4_prose_rules_check.py` and read its output.
- **The three-artefact closure ritual, every round, unprompted:** Progress Log, this manager prompt,
  and the board republished at
  <https://claude.ai/code/artifact/0e491191-c0c7-41d0-abe7-6023a13a1213> — plus memory. Every
  decision carries a recorded reason and a written reopen trigger.

---

## 6. Six things the build changed about what the manuscript may claim

1. **The additive claim is weakened to what evidence supports.** Only Step 7 (base geometry) is
   provably bit-identical; Steps 4, 6, 9 are No; Steps 1, 2, 3, 5, 8 have no cross-leg comparison;
   `integration.py` exists in three non-matching copies. The paper says **additive by construction**
   and does **not** say *"no prior figure invalidated"*. *Reopen trigger:* an authorised cross-leg
   byte comparison re-scores this **in either direction**.
2. **Leg-2 office 172.7 → 106.56** (V4-B2). Verdict unchanged.
3. **The `L8` collision** (§4.3).
4. **The shipped checkpoint was selected by a composite score**, which this project's own principle
   forbids. Decided at `V3-H1` option C with three reopen triggers; now disclosed in Methods §3.2.
5. **Hotel is uninjected in 2005/2010/2015** (QC ground truth starts 2019), so its flatness across
   cycles is a campaign artefact. Stated in Results §5.1, not only in Limitations.
6. **Retail is 5.47 % below its floor, not 0.15 %** (§4.2).

---

## 7. What is open

### Two decisions sitting with the user, from this build
1. **`readySubmission.md` carries build apparatus.** Inlined tables bring their "Sources" and
   "Manager notes" blocks with them. Right for a working draft, wrong for a submission copy.
   Stripping is **editorial**; it was not automated because a blind strip could remove a caveat.
2. **The abstract runs 225 words** against a ~180 target (2J's shipped abstract runs 240). Trim to
   the target journal's limit once that journal is chosen.

### Two still sitting with the user from v4, not blocking
3. **Sign-off** on the interpretive sentence in the rewritten §5.2 of 2J's `readySubmission.md`.
4. **Decision** on `2J_docs_occ_nTemp/writing/sharingCHV/2ndOcc_Journal.docx`, which still carries
   the stale table as "Table 4".

### Still blocked, correctly
- `V4-C2` — needs an authorised `sbatch` validator run, not granted.
- `V4-C3` — prompt `V07_qc_hotel_occupancy_pre2019.md` is written and awaits an external run.
  🔴 This is the same fact as §6.5: the hotel channel is uninjected before 2019, and it now appears
  in Results as well as Limitations.

### The 13 `⚠ check source` cells
Enumerated in the build report. The largest cluster (6 cells) is Table 6's bit-identity column, which
only a simulation-side comparison can fill; the next (6 cells) is Table 1's competitor
characterisations, which only an **external** deep-research round can fill.

---

## 8. Suggested next round, if the user wants one

Nothing is owed. Candidates, in the order the manager would rank them:

- **R1. A read-through review pass** of `readySubmission.md` for argument flow and repetition. The
  chapters were drafted by four employees in parallel and have not been read end to end as one
  document by anybody.
- **R2. Generate the eight schematics** from the prompt files in `figures/`. Mechanical, delegable,
  and the manuscript has eight figure-shaped holes until it happens.
- **R3. The editorial strip pass** on `readySubmission.md` (§7.1) — needs the user's call first.
- **R4. A `V<NN>` deep-research prompt** covering Table 1's six competitor cells and the two ISQ /
  CBRE catalogue identifiers, so the external round can close nine `⚠ check source` cells at once.
- **R5. Choose a target journal**, which sets the abstract limit, the reference style and the figure
  count.
