# 2J Pipeline — Handoff prompt for the incoming manager/director session (Step 7 closed → what's next)

> Paste the block below into a fresh session to continue the 2J leg. It hands off a **closed** Step 7 and
> sets up the next round of work (downstream frame propagation + Step-8/9 refresh + doc hygiene).
> Written 2026-07-10 at the close of the Step-7 improvement round.

---

## ROLE

You are the **manager (Opus)** for the "2J" GSS→EnergyPlus occupancy pipeline. Plan, delegate to cheap-model
employees (Haiku/Sonnet) for any big-file scan or mechanical run, and keep the Progress Logs honest
(re-derive numbers from artefacts — never transcribe a logged before/after). Working dir:
`C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\2J_docs_occ_nTemp`. Local Windows box → use the `py`
launcher (NOT `python`). Speed-cluster login-node rules do **not** apply to local runs.

## WHERE THINGS STAND (verified 2026-07-10)

Steps 4, 5, 6 and **7** have all been refreshed. **Step 7 (BEM integration) is CLOSED:**
- Builder `07_aug_to_bem.py` → `GSSCanada-main\BEM_Setup\BEM_Schedules_{2022,2030}.csv` (17-col, Step-9 gains
  included). 2030 built with `--joint` (canonical joint act30+hom30 rake). **Both on the NEW 144,465-HH frame**
  (rebuilt Jul-9).
- Validator `07_bemIntegrationGSS_val.py` un-staled (13→17-col schema, 2030 ref → `joint_raked`, Section 4b for
  the Step-9 channels, deviations panel, provenance banner). **Reports:
  `outputs_step7/step7_validation_report_{2022,2030}_v2.html`** — result **2022 34/0/0 · 2030 33/0/0**.
- The two Jun-11 originals are **preserved** (restored to `outputs_step7/` root + dated copies in
  `outputs_step7/previous/`).
- Full close-out + rationale: `outputs_step7/improvement/step7_improvement_notes.md`.

**🔑 The load-bearing fact for everything downstream:** the Jul-9 Step-5 refresh shrank the canonical frame
**144,507 → 144,465 HH** (persons **285,419 → 285,367**; −42 HH / −52 persons). Steps 4–7 are on 144,465.
**Everything downstream of Step 7 is still on the OLD 144,507 frame** (see task 1).

## OPEN WORK (priority order)

### 1. 🟠 Propagate the 144,465 frame before any new EnergyPlus campaign (the real data action)
`GSSCanada-main\BEM_Setup\` holds **five** cycle-year schedule files. After the Jul-9 refresh they are split:
- `BEM_Schedules_2022.csv`, `BEM_Schedules_2030.csv` → **NEW 144,465** (Jul-9).
- `BEM_Schedules_2005.csv`, `BEM_Schedules_2010.csv`, `BEM_Schedules_2015.csv` → **OLD 144,507** (Jun-8).

Step-8's core invariant is that **all five cycle years share an identical `SIM_HH_ID` set** (`set diff = 0`).
That invariant now **breaks by ~42 HH** if Step-8 is re-run/re-frozen without regenerating 2005/2010/2015 on
the 144,465 frame. Already-materialized Step-8/9 sim outputs (campaign_N50, prototype, _bigtest) are internally
self-consistent on 144,507 and are **not retroactively invalidated** (42/144,507 = 0.029 %, negligible under
N=50). **Action:** regenerate `BEM_Schedules_{2005,2010,2015}.csv` from the 144,465 frame so all five match,
**before** the next campaign. No code change needed — the frame flows from the refreshed 2022 stock.

### 2. 🟠 Refresh Step 8 (simulation) + Step 9 (activity-driven loads) for the 2J leg
The whole downstream campaign predates the Jul-9 refresh:
- `SimResults_Step8\campaign_N50` (2026-06-05), `Step9_docs\prototype\...` and `_bigtest\...` (Jun 2026) — all
  on OLD 144,507. Validators do **not** hardcode the frame (they use `nunique()`), so no false-FAIL risk; but
  the results themselves reflect the pre-refresh population. Decide whether a re-sim is warranted (likely yes
  for the paper's final numbers, after task 1). Docs: `08_simulation.md`, `09_activityDrivenLoads.md`,
  `Step8_docs/`, `Step9_docs/`.

### 3. 🟡 Doc-hygiene sweep — 144,507 → 144,465 across prose (no functional effect)
These still cite the old frame (class-B, cosmetic; `07_bemIntegrationGSS.md` was already fixed this round):
- **Manuscript / paper (most important):** `writing/2J_full_manuscript.md` (~L422,461,602,622),
  `writing/readySubmission.md` (~L312,448,576), `writing/2nd_Occ_Journal_Skeleton.md` (L78, **L358 = explicit
  "Number hygiene: 144,507 households" line**), `writing/methodology_assessment_and_paper_skeleton.md` (~L279).
- **Pipeline docs:** `08_simulation.md` (L44,64,132,291,295,299), `09_activityDrivenLoads.md` (L352),
  `07_bemIntegrationGSS_val.md` (stale val report, L68-269), `00_GSS_Occupancy_Pipeline.md` (L426,642,779),
  `00_GSS_Occupancy_Pipeline_Overview.md` (L134,172,252), `Step8_docs/eSim_bem_utils_2J/main.py:69` (comment).
- **Leave as-is (provenance):** archived `.py`, `previous/*.html`, improvement-planning change ledgers, and any
  `_bigtest/*.htm` numeric coincidences (those `0.144507E+09`-style hits are EnergyPlus energy values, not the
  frame).

### 4. 🟡 Decide: promote the `_v2` reports to canonical?
`outputs_step7/step7_validation_report_{2022,2030}_v2.html` are the current, correct reports. The non-`_v2`
files in the root are the preserved Jun-11 originals. If the `_v2` are to become canonical, rename `_v2` → base
(the Jun-11 files stay as predecessors in `previous/`). **User decision — do not rename without asking.**

### 5. 🟢 Optional: metabolic ×1.19 / ×1.5 sensitivity (Methods-stage)
The metabolic/activity channel is un-calibrated by design (act30 never raked; 70 W/MET ≈ 60 kg basis). An
optional sensitivity run (×1.19 → 83 W/MET ASHRAE 70 kg; ×1.5 upper) is noted in the Step-7 risk register.

## HOUSE RULES (carry over)
- Cheap models (Haiku/Sonnet) for all big-file scans, log tails, and mechanical runs — never scan a 600 MB CSV
  in the manager's own context. Manager writes the script + says what to extract; employee returns the small table.
- Archive any predecessor before overwriting; make the smallest practical change; call out anything that could
  alter publishable results.
- Verify-progress-log-claims: re-derive every before/after number from the artefact's own columns.

## KEY PATHS
- Pipeline scripts + docs: `2J_docs_occ_nTemp/`
- BEM schedule outputs: `GSSCanada-main/BEM_Setup/` (5 cycle years)
- Step-7 reports + improvement notes: `2J_docs_occ_nTemp/outputs_step7/`
- Memory index: `~/.claude/projects/.../memory/MEMORY.md` (see `project_2j_step7_improvements.md`)
