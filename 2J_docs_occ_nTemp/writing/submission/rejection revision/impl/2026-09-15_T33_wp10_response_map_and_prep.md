# T33 — WP10 prep: reviewer-response map, jargon inventory, move-to-SI list

Task doc and implementation state in one file. Written by the manager 2026-09-15 (plan log (as)).
Agent: Sonnet, fresh session. **Local reading and writing only. No cluster, no python on Speed.**

Status:     DONE - all three files written to `manuscript/prep/`, cross-checked against the plan and
every task doc's Status line (see Ledger/Verified below).

## Aim
Prepare the rewrite (plan §3 WP10) without writing manuscript prose. Three files, all under
`rejection revision/manuscript/prep/` (create the folder locally):

1. `response_map.md` — one row per request in plan §2 (42 rows: Reviewer 1 M1 to D20, Reviewer 2 1 to 7,
   Reviewer 3 1 to 7), columns: `ID` · `Short plain paraphrase (max 15 words, never quote the reviewer)` ·
   `Class` · `What we change` · `Where in the new manuscript (planned section, from WP10 Structure)` ·
   `Evidence task(s)` (Tnn from `impl/`) · `Status` (DONE / RUNNING / WAITING / DECLINED) · `Note`.
   Status comes from the plan Progress Log and the task docs, not from memory. Special cases already decided:
   R1-M3 envelope sensitivity = DECLINED by pre-registered rule (log (aq)), answered by the end-use gap (T07)
   and a stated limitation; R2-2 = partial measured check (T02, T09, T15).
2. `jargon_inventory.md` — for each self-defined label in the archived manuscript, the line numbers where it
   occurs and a count. Start from this list (WP10 "Plain terms") and add any other internal label you find
   (capitalised coined terms, code-like tokens, step numbers): "calibrated J3", "J3", "True-Future-Test",
   "paired frozen-frame", "frozen frame", "Tier-1", "Tier-2", "Tier-3", "FailSafe", "COLLECT_MODE",
   "DDAY_STRATA", "Step-8", "Step-9", "occACT", "gate", "PASS", "WARN", "INFO", "C-VAE", "MDLM", "SEDD",
   "calibration closure", "forecast" (count only; it is being replaced). Columns: term · count · line numbers
   · first-use line · proposed plain replacement (short, your suggestion, marked SUGGESTED).
3. `si_move_list.md` — for each item in WP10 "Move to SI" (J3 architecture detail, 40+ trial search detail,
   PASS/WARN/INFO scorecards, DX-coil fix, schedule round-trip checks, clock-alignment debugging narrative,
   donor-draw history, raking coherence cost, weekend JS floor argument), plus every gate score or JS value in
   archived §3.2 and §3.4 (R1-M2c): the archived line range, first 8 words of the paragraph, and the target
   (SI section name). Also list duplicated passages between archived §3.5 and §4.2 (R1-D14) with both line
   ranges.

## Inputs (read these; do not edit them)
- `../00_REVISION_PLAN.md` §2 (lines 61 to 128), §3 WP10 (lines 355 to 400), Progress Log from entry (aa).
- `../../archive/2J_manuscript_submission.md` (15,125 words; read in chunks with offset/limit, never whole).
- Task docs in this folder (`2026-09-15_T*.md`): read only their Status line and last ledger/decision lines.

## Rules
- Never edit `archive/`, the plan, or any task doc other than this one.
- The reviewer letter is confidential: paraphrase, never copy reviewer sentences into the new files.
- Write "NOT VERIFIED" rather than guess a status.
- No em dashes and no en dashes in the files you write.
- Do not write manuscript prose. Do not create other files.
- Append your results to "Ledger" and "Verified" below as you go; end the turn when the three files exist.

## Ledger
- Read only, no cluster jobs. Read plan sections 2 (lines 61-128) and 3 WP10 (lines 355-400), and the
  full Progress Log (lines 673-1016, entries dated 2026-09-15 through log (ar), the last entry present).
  Read the archived manuscript in chunks (offset/limit) at the section-header list, then sections 3.2,
  3.3, 3.4, 3.5, 3.6, 4.2, 4.3, 4.4. Grepped every jargon term and every SI-move term for line numbers.
  Read Status line only (and a few Ledger lines for T33/T34) from every task doc T01-T32, T34.
- Created folder `rejection revision/manuscript/prep/` and wrote three files: `response_map.md`,
  `jargon_inventory.md`, `si_move_list.md`.

## Verified
- 42 requests confirmed in the plan's own table (Reviewer 1: 28 rows M1-M5 + D1-D20, Reviewer 2: 7,
  Reviewer 3: 7), matching the plan's stated count.
- Every task doc T01-T32 has an explicit Status line except T34 (empty Ledger, not started). Statuses
  read verbatim and carried into response_map.md; none guessed.
- "calibration closure" (the literal phrase) has zero occurrences in the archived manuscript (grep,
  whole file); "forecast" appears on 33 lines; "gate"/"gates" on 19 lines; full counts and line numbers
  for all 22 starting-list terms plus 2 extra found terms (DRIFT_MATRIX, hindcast) are in
  jargon_inventory.md.
- Sections 3.5 (lines 245-263) and 4.2 (lines 302-315) both describe the four schedule channels, the
  clock-alignment shift, and the donor-draw completion; section 3.5 already forward-references section 4
  for the clock-alignment detail and section 4.2 already back-references 3.5 for donor-draw, so the
  duplication is partial, not total (both read and compared directly, not inferred).
- No `manuscript/` folder existed before this task (checked by glob); WP10/WP11 have not started, so all
  text-only rows in response_map.md are correctly WAITING, not DONE.

## Decisions
- Where the plan's WP column already named the section (e.g. WP1 to Results occupancy-change), used that
  directly; where WP10's Structure paragraph did not name a specific subsection, used the closest named
  block (Introduction / Framework / Results / Discussion / Limitations / Figures / SI) rather than
  inventing a new one.
- Counted "count" in jargon_inventory.md as number of matching lines (ripgrep default), not number of
  raw occurrences, and said so once at the top of the file so it is not misread as occurrence count.
- For R1-M3 and R2-2/R3-5, used the special-case wording the task doc supplied verbatim rather than
  re-deriving a new status, since the task doc named these as already-decided.
- Did not attempt to resolve the two open author questions this task surfaces (D2's companion-paper
  status; whether dr_2J-10/dr_2J-11 have been run) since T33 is reading-and-mapping only, not a decision
  task.

## Next
- Manager: hand response_map.md's WAITING rows to WP10 (T34 and future WP10 text tasks) once Wave 3
  compute (T21, T26, T29, T30, T32) finishes closing the RUNNING rows.
- Manager: confirm with the author whether dr_2J-10 and dr_2J-11 have been run (affects D2 and D6 status).
- No further action needed from this task; all three prep files exist and are cross-checked against the
  plan and the task docs as of this read.

## WHAT I DID NOT VERIFY
- Did not verify the plan's Progress Log entry the task doc calls "(as)" exists; the log's last entry
  present is "(ar)" (line 1011-1016). Read through to the true end of file (line 1016) to confirm nothing
  further was missed.
- Did not open the archived manuscript's Appendix (lines 599 to end) in full; only its heading and a few
  targeted greps were read, as noted in si_move_list.md's own WHAT I DID NOT VERIFY section.
- Did not re-verify any task doc's numeric claims (e.g. T03's confidence-interval mismatch, T04's
  threshold finding); their Status lines and cited findings were taken as read, per this task's own
  reading-only scope.

## Manager review (plan log (at))
- Re-measured in the archived manuscript: "forecast" 33 lines (case-insensitive), "gate/gates" 19 lines (whole word), "calibration closure" 0, FailSafe 2, True-Future-Test 6, occACT 1. All match. (A plain `grep -c gate` gives 22 because it also hits "aggregate"; the agent's whole-word count is the right one.)
- 42 rows present (28 + 7 + 7). No reviewer sentences copied; no en or em dashes in the three files.
- Two stale cells corrected in response_map.md: M2d (T28 is submitted, JobID 1328415, not staged) and M2b (T34 is running).
- **Status: T33 DONE (accepted).**
