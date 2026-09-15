# 2J — manager prompt, to fire when the Building Simulation decision arrives

> **What this is.** A standing, paste-ready handoff for the session that handles the editor's decision
> on the 2nd journal paper. It exists so that session does **not** start from zero: everything it would
> otherwise have to rediscover — what was submitted, which numbers are canonical, which weaknesses the
> paper already admits, and which rules outrank convenience — is written down here, before the reviews
> were seen and therefore without any incentive to shade it.
>
> **How to use it.** Fill §0, paste the whole file into a new session together with the decision letter
> and the reviewer reports, and stop there. The session's first job is to triage, not to edit.
>
> **Written 2026-08-07**, the day of submission, against the files as submitted.

---

## §0 Fill this in before pasting

```
Decision letter received : ____-__-__
Editorial Manager ID     : BUIL-____-_____
Decision                 : [ ] minor revision  [ ] major revision  [ ] reject & resubmit  [ ] reject
Revision deadline        : ____-__-__          (days remaining: ____)
Handling editor          : ____________________
Number of reviewers      : ____
Reviewer reports pasted  : [ ] yes — below       [ ] attached as files at: ____________________
Editor's own requests    : ____________________________________________________________
```

**Paste the decision letter and every reviewer report verbatim below this line.** Do not summarize
them for me, do not reorder them, and do not drop the parts that look like boilerplate — the
formatting and data-availability requests hide there.

---

## §1 Your role, and the two things you must not do

You are the manager for the revision of a submitted journal manuscript. You plan, verify, and draft;
the user owns every authorial claim and every decision that changes what the paper asserts.

**Do not edit the manuscript before the triage in §3 is delivered and the user has responded to it.**
A revision that starts with edits produces a document nobody can map back to the reviewers' requests.

**Do not answer a reviewer by changing a number until you have re-derived that number from its own
source artifact.** This project has a documented history of logged before/after values that did not
survive re-derivation. A reviewer challenging a number is the worst possible moment to trust a note.

Everything else — reading, counting, checking, drafting, proposing — is yours to do without asking.

---

## §2 Frozen state: what the journal actually holds

Submitted **2026-08-07** to **Building Simulation** (Springer / Tsinghua University Press),
double-blind, via `editorialmanager.com/buil`. Editor-in-Chief **Prof. Da Yan**, Tsinghua.

Root: `2J_docs_occ_nTemp/writing/submission/`

| What the journal has | File | Size |
|---|---|---|
| Title page + cover letter | `submissionDocs/Title_Page_and_Cover_Letter.docx` | 30 paras, dated 7 Aug 2026 |
| Blinded manuscript | `submissionDocs/Blinded_Manuscript.docx` | 475 paras |
| Supplementary material | `submissionDocs/Supplementary_Material/Supplementary_Material.docx` | 795 paras, 15 tables |
| SI data | `submissionDocs/Supplementary_Material/data/S1–S8*.csv` | 8 files, 2.8 MB |

🔴 **`submissionDocs/` is frozen. Copy it, never edit it in place.** It is the only record of what the
reviewers read. The moment you edit it you lose the ability to diff their copy against yours, and every
"we have revised X" sentence in the response letter becomes unverifiable. Work in a new
`submission/revision_R1/` and diff back.

**Other copies, and their status — get this wrong and you will revise the wrong file:**

| File | Status |
|---|---|
| `submission/2J_manuscript_submission.md` / `.docx` | the **non-blinded master**, kept in sync with the blinded copy. Edit **both**. |
| `submission/submissionDocs/Blinded_Manuscript.md` | the blinded copy. Differs from master by **10 author-information lines removed + 6 lines rewritten in the third person** — and by nothing else. A multiset line diff must return exactly **16 master-only / 6 blinded-only**. Verify after every edit. |
| `writing/fullSet/2J_full_manuscript.md` | canonical **archive**, not the live document |
| `writing/chapters/Chapter_*.md` | 🔴 **stale. Never run `assemble.ps1`** — it would overwrite the live text with old chapters |
| `writing/sharingCHV/2ndOcc_Journal.docx` | 🔴 **stale (2026-08-04)**, the supervisor-sharing copy, superseded |

**Blinding, if a revised manuscript is uploaded:** the blinded file must keep zero hits on all nine
probes — `Orcun`, `Caroline`, `ORCID`, `NSERC`, `Voltage-Age`, `CRediT`, `Acknowledgement`,
`Concordia`, `orcunkoral`. The two reference-list entries naming the authors' prior published work are
intentional and stay. §1.4 is titled *"The Prior Line: The Departure Point"* in the blinded copy and
*"The Authors' Prior Line: The Departure Point"* in the master — that asymmetry is deliberate, not
drift, and the same holds for the five other de-authored phrases (§1 funnel paragraph, the Table 1
note, §1.5, §6).

---

## §3 Your first deliverable: triage, before any edit

Produce this and nothing else, then stop:

1. **One numbered row per reviewer request**, in the reviewers' own order, each quoted verbatim —
   including requests buried mid-paragraph, which is where the expensive ones hide.
2. **A class for each**, and be honest about the split:
   - **A — factual/textual.** Answerable by editing text. Cheap.
   - **B — needs a number re-derived** from an existing artifact. Cheap to check, and the check is
     mandatory before you answer.
   - **C — needs new computation.** Re-simulation, re-raking, a new sensitivity run. 🔴 **Costed and
     flagged, never started on your own initiative.** See §7 on the cluster.
   - **D — a claim the paper cannot support.** The honest answer is to narrow the claim, not to
     manufacture support for it. Say so plainly.
   - **E — you disagree with the reviewer.** Legitimate, and journals expect it. Requires the user's
     decision plus a courteous, evidenced rebuttal.
3. **The critical path**: which items are C, how long each takes, and whether they fit the deadline in
   §0. If they do not fit, say so on day one, not in week three — an extension is granted routinely
   when requested early and grudgingly when requested late.
4. **What the reviewers did *not* raise** from §6's list of known weaknesses. This matters: an item
   nobody raised can still be fixed silently in the revision, and fixing it is much cheaper than being
   caught by it at the second round.

---

## §4 Canonical numbers — quote from here, never from memory

Every figure below was read out of the submitted manuscript on 2026-08-07. If a revision changes any
of them, change it **here first**, then everywhere else.

**Data and pipeline**
- 4 GSS time-use cycles, **64,061 diaries** → augmented to **~192,183 diary-days**
- Analytical frames: **144,507 households** (2005–2015) · **144,465** (2022–2030, post-relink)
- Linkage tiers: Tier-1 **44.94%**, Tier-2 **21.39%**, Tier-3 **33.67%**, FailSafe **0.00%**
- Campaign: **6,000 paired EnergyPlus v24.2 runs**, 4 archetypes × 6 cities × 2 arms, N = 50 per cell

**Occupancy (§5.1)**
- At-home share: **62.7% (2005) · 62.3% (2010) · 64.5% (2015) · 70.6% (2022)**
- Raw 2015→2022 rise **+6.1 pp** (weekday **+6.6 pp**); **after demographic standardization the
  headline weekday break is +5.2 pp** — that is the number the paper carries
- Demographically standardized pre-COVID series: **64.2 / 64.2 / 63.3%** — i.e. flat; the pre-2015
  drift is compositional
- 2030 persistence **+2.2 to +3.9 pp** above pre-pandemic 🔴 **declared provisional in §7 — see §5**

**Energy (§5.2)**
- Annual electricity **+1.4 to +2.6%** across the break; **+0.6 to +1.2%** 2022→2030
- EUI 2022 (2030): SingleDetached **115 (116)** · MidRise **108 (108)** · OtherDwelling **100 (101)** ·
  HighRise **78 (79)** kWh/m²
- **All four sit below their SHEU regional bands** — by ≈3% (mid-rise), 12% (single-detached),
  27% (other), 31% (high-rise). One-directional, attributed to a current-code NECB 2017 / NBC 9.36
  envelope against an existing-stock survey average
- Per-dwelling-unit renormalization (×1.11): mid-rise → **≈120** (inside band); high-rise → **≈87**
  (still below)
- 🔴 These EUI values were **corrected on 2026-08-06**, before submission. An earlier version of the
  table reported **200 / 115 / 170 / 128**. All 6,000 runs were recomputed; **three of four band
  verdicts changed.** If a reviewer quotes 200/115/170/128 they are reading an older draft that
  circulated — establish which document they have before answering.

**Load shape (§5.3, §5.4)**
- Mean stock peak hour **17.70 h (2005) → 17.02 h (2030)**, band **17.0–17.7 h**; headline "~17:30"
- Δmidday share **+0.367 pp**, 95% CI **[+0.208, +0.526]**
- Δload factor **+0.0117**, 95% CI **[+0.0085, +0.0150]**
- Paired **annual energy** CI **includes zero** — stated openly; half-width averages 1.80%, worst cell 4.04%
- Equipment peak-hour shift **0 ± 1 h** (mean **−0.12 h**, σ **0.39 h**) across 24 cells
- SHEU gate: **48 of 48 cells within ±2.7%** (max **+2.33%** equipment, **+2.63%** lighting)
- Presence-only baseline plug load **6,550–6,870 kWh/hh/yr** against SHEU targets **3,139–3,700 kWh**

**Manuscript form:** abstract one paragraph **~237 words** (cap 100–250) · **6 keywords** ·
**52 references, all 52 cited, zero orphans** · 5 tables · 16 figures (7 main + 9 SI).

---

## §5 The attack surface the paper already declares

§7 is unusually candid, which is a strength — but it means the reviewers were handed a list of where
to push. Expect these, and note that the honest answer is already written:

1. 🔴 **The 2030 at-home magnitude is admitted as provisional.** The 2030 AT_HOME calibration was raked
   against the **pre-relink** 2022 reference population and never re-run after the 2026-07-09 frame
   relink. The paper says so, and says the gap as plotted is **inflated**. **This is the most likely
   Class-C request in the whole review** — "recalibrate and report the corrected magnitude". The
   qualitative finding is corroborated independently by Step-6; the number is not. Do not defend the
   magnitude; the paper already declined to.
2. **p = 1 persistence, single scenario.** Framed as a high-persistence upper bound. The obvious
   reviewer request is a high-reversion counter-scenario to bracket it — cheap to argue, moderately
   expensive to run.
3. **One Montréal Zone-6 envelope across all six cities**, Atlantic households mapped onto the Montréal
   EPW. The paired design cancels this within-panel, which is the defence; it does bound absolute EUI.
   A Zone-7A sensitivity is the named natural check.
4. **The metabolic channel is not independently calibrated** — unlike equipment and lighting.
5. **The 2015→2022 panel break** makes Fig. S8 a cross-sectional trend, not a matched series.
6. **TMY, not future weather**, for a 2030 projection.
7. **Conditional independence** in the Census–GSS statistical match.
8. **Weekend pooled to one day-type; hourly reporting interval.**
9. **The §4 phase-error narrative was kept deliberately.** The four-hour schedule-injection error is
   reported as a validation lesson, not hidden. If a reviewer reads it as a red flag, the answer is
   that annual energy is phase-invariant, the campaign was fully re-simulated, and the corrected timing
   is what the results report. **Do not remove this passage to make the paper look cleaner.**

🔴 **And one weakness the paper does *not* declare:** the novelty gap matrix in Table 1 — the six-
dimension claim that only this study hits all six — **was never tested against a systematic search.**
No literature search was ever run to falsify it. If a reviewer names a competing study that closes one
of those cells, **the matrix has no defence prepared** and the honest move is to concede the cell and
narrow the claim. Treat any novelty challenge as Class D until proven otherwise.

---

## §6 The two items carried into review

Neither blocked submission. Both must be closed in the revision.

1. 🟠 **13 of 16 figures are below 600 dpi** at the 5.83-inch text width (need **≥ 3,498 px** wide).
   Worst: `Figure_S05/S06/S07` at 2,100 px (360 dpi). Passing: `Figure_06` (6,836), `Figure_S09`
   (4,691), `Figure_07` (3,964). Fixed by re-exporting from the plotting scripts with
   `savefig(..., dpi=600)` or a wider `figsize`. **The 600 dpi rule bites on the separate figure files
   requested at acceptance** — if the decision is positive, this becomes due immediately. Full table in
   `submissionDocs/00_README_upload_package.md`.
2. 🟠 **The activity-crosswalk leaf-code counts do not reconcile.**
   `references_activityCodes/Data Harmonization_activityCategories - execution.xlsx` counts
   **182 / 265 / 64 / 123** (2005/2010/2015/2022, excluding the one `Work-related` header row).
   **§3.1 and SI Table B2 both state 182 / 264 / 64 / 121.** 2005 and 2015 agree; 2010 is +1, 2022 +2.
   The extras sit out of numeric order at the sheet tails (`712.0`, `713.0` in 2010, duplicating the
   labels of `720.0`/`741.0`; `1105`, `1303`, `1304` in 2022), which *reads* like post-hoc additions —
   **but that is an inference and it was never verified which mapping the pipeline actually consumed.
   That verification is the task.** The crosswalk was deliberately held out of the SI, so nothing
   submitted contradicts anything submitted; once settled it ships as
   `Supplementary_Material/data/S0_activity_harmonization_crosswalk.csv` and is a genuinely useful
   thing to offer reviewers.
   Related: SI Table B2's *"Raw-code magnitudes"* column was **14 cells of `⚠ check source`** and was
   **removed, not filled**, because filling it commits to the disputed totals.

**Also standing:** the companion paper (1J, JBPS) was **under review** at submission and is therefore
cited in the text but **absent from the reference list**, per the journal's published-or-accepted-only
rule. 🟢 **If it is accepted before the revision goes back, it must be added to the reference list**
and the in-text description updated. Check its status at revision time — this is easy to forget and
trivially fixed.

---

## §7 Rules that outrank convenience

These are project-standing and are not negotiable inside a revision:

- 🔴 **Deep research is EXTERNAL.** You do not run literature searches or verify citations yourself.
  You **author the prompt**; the user runs it. This is not a preference — on the last round **roughly
  half the citations in the returned reports were fabricated**, caught offline by arithmetic. If the
  revision needs new literature, write the prompt and hand it over.
- 🔴 **Never add a citation from an LLM research report without the user opening it.** Every prior
  round contained invented DOIs, invented author lists, and invented journal categories.
- 🔴 **No computation on the Speed login node.** `sbatch` only, minimum walltime `-t 7-00:00:00`. No
  bare `python`, no blocking `srun`. **Retrieval over `ssh`/`scp` is allowed** — "blocked because the
  file is on Speed" is not a valid status. One `scp` stream at a time; parallel fetches get the
  connection refused and the failure is silent.
- 🔴 **Verify on the installed file, not the build output.** A shipped `.docx` once lost an entire
  table column while the freshly built one was correct. Run the gate against what will actually be
  uploaded.
- **Re-derive before you quote.** Including from this document — if the two disagree, the artifact wins
  and this document gets corrected.
- On Windows the Python launcher is `py`. Never count lines with PowerShell `Measure-Object -Line`;
  use `wc -l`. Verify a backup is non-empty before truncating anything.

---

## §8 Rebuilding the documents

Chain, in order — all four scripts live in `submission/extra/build_scripts/`:

```
py ref_submit.py                  # writes ref_submit.docx: 12 pt Times, double spacing,
                                  # black headings, justified body, 10 pt centred captions,
                                  # centred PAGE-field footer
pandoc <in>.md -o raw.docx --reference-doc=ref_submit.docx --resource-path=.
py post.py raw.docx <out>.docx    # table text to 10 pt, single spaced; validates the XML
py submit_check.py <master>.docx <blinded>.docx      # the gate — run on the INSTALLED files
py build_si.py                    # rebuilds the Supplementary Material + its 8 CSVs
```

`submit_check.py` checks: paragraph/table/caption counts, `Fig. N` and `Table N` caption forms, no
stray "Figure N" in text, no `(Author, year)` commas, no duplicate alt-text captions, default font and
size, double spacing, footer present, no line numbers, table text size, zero inline colours, and the
nine blinding probes. **A single expected false positive:** the comma gate reports one hit on
`(Time Use, 2022)`, which is a dataset name inside a reference entry, not a citation.

Journal form already applied and to be preserved: `Fig. N` / `Table N` with no bold and no period ·
author–year citations **without a comma** — "(Thompson 1990)" · figure captions below, table captions
above · no line numbers (Editorial Manager adds them) · automatic page numbering.

---

## §9 The response letter

Build it as you go, not at the end. One block per reviewer point:

> **Reviewer 2, Comment 4.** *[verbatim quote]*
> **Response.** [what you did, or the evidenced reason you did not]
> **Change.** §5.3, paragraph 2 — [the new sentence, quoted exactly as it now reads]
> **Location.** page N, line N of the revised manuscript.

Rules that keep this credible: quote the reviewer verbatim, never paraphrase them into something easier
to answer. Point at the changed text, don't describe it. Where you disagree, say so courteously and
show evidence — a rebuttal that concedes nothing across an entire report reads as defensive, and a
revision that concedes everything reads as unprincipled. **Never write "we have revised X" for a change
that was not made**; that is the single fastest way to lose an editor's trust, and it is checkable.

---

## §10 What closes this round

- [ ] Triage table delivered (§3) and answered by the user
- [ ] Every Class-B number re-derived from its own artifact, disagreements reported
- [ ] Class-C work costed, approved by the user, and run under §7's cluster rules
- [ ] Both §6 items closed — figures at 600 dpi, crosswalk count reconciled
- [ ] 1J status re-checked; added to the reference list if accepted
- [ ] Master and blinded copies edited **together**, line diff still exactly 16 master-only / 6 blinded-only
- [ ] `submit_check.py` green on the **installed** revised files
- [ ] Response letter complete, every "we revised" verified against a diff of the frozen submission
- [ ] `00_README_submission.md`, `submissionDocs/00_README_upload_package.md`, and the memory file
      `project_2j_paper_writing.md` all updated in the same pass
