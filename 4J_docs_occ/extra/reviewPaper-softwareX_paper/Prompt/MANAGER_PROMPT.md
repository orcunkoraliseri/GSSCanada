# Manager prompt — BuildOcc peer review (SoftwareX, SOFTX-D-26-00798)

Paste this whole file as your first message to start a fresh session on this task. It is written
so a session with no memory of earlier rounds can pick this up cold.

## What this is

The user (O. K. Iseri, Concordia University) is **Reviewer 2** for a manuscript under review at
*SoftwareX*: **"BuildOcc: A Large Language Model Occupant Agent Platform for Building Energy
Research"** (Wooyoung Jung, University of Arizona), manuscript number `SOFTX-D-26-00798`, currently
suffixed by revision round (`R1`, `R2`, …). BuildOcc grounds LLM occupant agents in the American
Time Use Survey (ATUS) and is released as the `buildocc` pip package.

**Confidentiality (hard rule, from `NOTES_FOR_4J.md`).** The manuscript is under review. Do not
reuse unpublished content from it anywhere else — not in the 4J/5J research pipelines, not in any
deep-research prompt, not in any other document in this repo. The only things legitimately ours to
carry elsewhere are: (a) the manuscript's **public** reference list, and (b) **methodological
conclusions we reached ourselves** while checking it (e.g. "a KL-divergence null needs a stated n",
independent of this specific paper). This file itself, and everything in this folder, stays
confidential until the paper is published.

## Your job when invoked

The user will hand you a new round: an editorial-manager email (invitation/reminder/next-steps) and
usually a new PDF snapshot dropped in `versions/`. Sometimes it's just "read the new revision and
write review comments."

**Do this, in order:**

1. **Read the last review filed** — the highest-numbered `extra/REVIEW_SOFTX-D-26-00798R*.md`. Its
   final section names anything left open from the previous round (check there first — a new
   round often just needs that one thing verified, not a full re-review).
2. **Read the new PDF(s) in `versions/`.** The response-to-reviewers letter is usually embedded as
   the first few pages of the *reviewer* PDF for that round, followed by the manuscript itself
   (marked-up and/or clean). Read the response letter comment-by-comment against the *previous*
   review you filed — every one of your prior comments should have an explicit response.
3. **Verify, don't just trust.** This project's standing practice (see the R1 and R2 reviews) is to
   actually install the released software and check claims against the real data/code, not just
   read the author's account of it:
   - `pip install buildocc==<version stated in the manuscript's Table 1, row C1>` in a throwaway
     virtual environment (Windows has `py -3 -m venv <dir>`; Python 3.13 + pip confirmed working in
     this environment, and PyPI is reachable). Do this in the session's scratchpad directory, not
     inside the repo.
   - The installed package's data lives under
     `<venv>\Lib\site-packages\occupant_agent\data\` — `time_at_activity.csv`,
     `time_of_day_distributions.csv`, `activity_frequency_O{1-4}.csv`, `tewhere_validation.csv`,
     `mapping_coverage.csv`, `schedule_peak_hours.csv`, `README.txt`. Source lives alongside it
     (`agent/`, `grounding/`, `llm/`, `analysis/`, `environment/`, `persistence/`, `api/`,
     `mcp_server/`, `testing/`).
   - The ATUS-processing scripts that *build* those CSVs (`scripts/atus/analyze.py` etc.) are
     **not** shipped in the PyPI wheel — only their output tables are. Anything that requires
     re-deriving a number from raw ATUS microdata (e.g. the exact `TELFS`/`TERET1` stratum filters)
     cannot be checked from the installed package alone; say so plainly rather than guessing.
   - Recompute whatever table or statistic the manuscript reports, from the shipped data, with a
     short throwaway Python script (no network/API calls beyond the `pip install` itself). Compare
     your number to theirs. Report both figures if they differ, and say which parts you could and
     couldn't reproduce.
4. **Do the deep checking privately, but file a SHORT, PLAIN review.** Do all the verification in
   step 3 — install the package, recompute tables, read the source — but the filed review is not
   a lab notebook. 🔴 **Learned the hard way on R2**: the first draft was a long, equation-heavy
   document, and the user's reaction was "this is too long and technical, I think it's time to
   accept the paper" — i.e. the length itself was making a straightforward Accept look harder than
   it was. The filed `extra/REVIEW_SOFTX-D-26-00798R2.md` was rewritten to ~20 lines: one-line
   recommendation up front, 3–5 plain bullets of what was checked and confirmed, at most one
   non-blocking open item in plain words (no formulas, no script names, no code paths in the
   sentences), a one-line ratings row, and "no ethical concerns / no conflict of interest." That
   short version is the template for every future round — default to it. Only go longer if the
   user explicitly asks for the technical detail.
5. **Also save a `.txt` companion** next to every filed `.md` review, same wording, no markdown
   syntax (no `#`, `**`, backticks) — it's what gets pasted into the Editorial Manager text box.
   Regenerate it whenever the `.md` changes.
6. **Never post or submit anything to Editorial Manager yourself.** Write the files and tell the
   user where they are; posting to the journal is the user's action, not yours.

## Status as of R2 — filed as Accept

R2 was filed as **Accept** (`extra/REVIEW_SOFTX-D-26-00798R2.md` + `.txt`). Every R1 point was
independently confirmed fixed by installing `buildocc==1.0.1` and checking the shipped data/source
directly (see git history / this file's earlier version for the full technical trail if it's ever
needed again — it is not in the filed review). One thing was flagged but kept non-blocking: a
Tier-1 "sampling null" number in Table 6 did not reproduce at the reported magnitude when
recomputed from the same public formula and the same shipped data (came out 2–3× higher); this did
not change the paper's qualitative conclusion, so it was written up as one plain sentence asking
the author to double-check it, not as a blocking issue. If a new round's response letter touches
Table 6, redo that same recomputation from `time_at_activity.csv` and compare — but again, report
the outcome in one short sentence, not a re-derivation.

## Folder map

- `versions/` — one reviewer PDF per round (`_reviewer.pdf` = R0/original, `_R1_reviewer.pdf`,
  `_R2_reviewer.pdf`, …). Each bundles the response-to-reviewers letter + the revised manuscript.
- `extra/REVIEW_SOFTX-D-26-00798R*.md` (+ matching `.txt`) — the filed reviews, one per round,
  short and plain per the rule above. **Read the latest before doing anything else.**
- `extra/REVIEW_annex_detailed_evidence.md` — longer-form evidence backing the R1 review.
- `NOTES_FOR_4J.md` / `NOTES_FOR_4J_longform.md` — what this review taught us that's *useful for our
  own* 4J HETUS pipeline (gate design, null-comparison discipline, baseline choices). This is a
  one-way export of our own conclusions **out** of the review, never a channel for manuscript
  content to flow **in** to anywhere else. Update it only when reviewing this paper surfaces a
  genuinely new lesson for our own work — don't force an entry every round.
- `deepResearch/` — external literature research done *before* this manuscript was assigned to us
  (occupancy-model lineage, divergence metrics, LLM reproducibility, etc.), used to write informed
  review comments. Not manuscript-derived; safe to reuse elsewhere per the confidentiality rule
  above.
- `verification/` — early (R1-era) standalone verification scripts. Newer verification scripts are
  written fresh per round in the session scratchpad and referenced (not necessarily kept) from the
  review doc; check here first in case a script already does what you need.
- `REVIEW_v2_onepage.md` / `.docx` — a condensed, EM-form-friendly version of the R1 review. Not
  regenerated automatically; only recreate an equivalent if the user asks for a submittable/condensed
  version of a new round's review.

## Reminders

- This is a side task living inside the 4J HETUS project folder, but it is **not** the 4J pipeline.
  Don't let review work leak into 4J gate design except through the deliberate one-way export into
  `NOTES_FOR_4J.md` described above.
- Chat replies to the user should stay short and in plain English (repo-wide rule, see
  `CLAUDE.md`) — and now confirmed for this task too: the **filed review doc itself** should stay
  short and plain by default, not just the chat reply. Keep the technical depth in your own
  checking, not on the page.
- Never fabricate a reproduction result. If a claim can't be checked from the installed package
  (e.g. it needs the private ATUS microdata or the GitHub repo rather than the PyPI wheel), say so
  instead of guessing.
