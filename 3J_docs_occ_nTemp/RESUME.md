# RESUME PROMPT — 3J Leg-2 occupancy pipeline (paste into a fresh Opus manager session)

You are the **manager (Opus)** in the two-agent workflow for the GSSCanada / eSim occupancy project
(repo root: `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main`). Read `CLAUDE.md` and your auto-memory
(`MEMORY.md`) first — they hold all operating rules. Below is exactly where we left off so you can
continue without re-deriving anything.

---

## Project in one line
3rd Journal ("3J"), **Leg-2 two-channel split** (residential + office) synthetic time-use diaries from
GSS/Census, feeding EnergyPlus BEM. Pipeline: Step 4 (augmentation/ML) → Step 5 (census linkage) →
Step 6 (forecasting) → Step 7 (BEM wiring) → Step 8/9 (simulation). 2J (single residential channel) is
fully done and in paper-writing; 3J reuses the proven 2J downstream but adds the office channel.

## ✅ STATE: Step 4 is LOCKED (2026-06-22)
**Final augmentation chain:** `R10_fast` (J3-topology MDLM) → `04L` floataware joint rake →
`04M` min-dwell smoother. **04N (bidirectional peak-shaver/filler) was tested and DROPPED.**

- 04N production sweep (job 981749, COMPLETED exit 0:0) moved G4 only 0.1 pp against a 10.33 pp gap →
  cannot close it. Window size barely matters. Dropped.
- Final scorecard: **68 PASS / 1 WARN / 2 FAIL.**
- The 2 FAILs are proven-unfixable, honestly documented limitations:
  - **G4 ≈ 10.2 pp** — structural work-mass under-fill (obs work-peak 28.72% vs syn 18.39%); the rake
    forces marginals exact, so it can't add work mass; the constrained intra-day swap can't either.
  - **OW5 ≈ 63%** — day-type ordering (WD≥Sat≥Sun) is **unobservable** (GSS = 1 diary/person), and the
    rake destroys per-respondent ordering by forcing observed marginals. No ground truth exists.
- 2J-vs-3J comparison + the LOCK decision are written into the Progress Log of
  `3J_docs_occ_nTemp\Leg2_2-split\Step4_docs\3rdJ_04_augmentationGSS_val.md` (two dated 2026-06-22 entries).
  Net finding: **3J Step 4 is strictly more capable than 2J — full second (office) channel at parity
  with 2J's residential channel, with two honestly-reported, provably-unfixable work-shape gaps.**

## ▶️ IN PROGRESS: Step 5 (downstream census linkage) for 3J Leg-2
**Build + smoke + FULL RUN DONE (2026-06-22, Sonnet employees).** New 3J-specific files under
`Leg2_2-split/Step5_docs/`: `3rdJ_05_censusLinkage_2split.py` (+ `_val.py`, `_val.md`),
plus `0_Occupancy/processed/office_archetype_lookup.csv`. Uses NEW census `0_Occupancy/Outputs_Aligned/
Aligned_Census_2025.csv` (30,274 agents; PID/SIM_HH_ID, has NOCS, no NAICS, build cols
DTYPE/BEDRM/ROOM/CONDO/REPAIR). Office archetype bundled INTO Step 5 (NOCS-keyed buckets:
1,2=Knowledge / 3,4,5=Public / 6=Sales / 7,8,9=NonOffice / 10,99=Unknown). wrk30 + colleagues30
+ office cols carry through; Census authoritative on shared cols; NAICS_donor from pool.
**NOCS 5 → Office_Public** (manager-confirmed 2026-06-22; archetype dist healthy so kept).

**FULL RUN (192,183-row pool downloaded, 381 MiB → 30,273 agents linked):** all 5 stages
(`--full/--aggregate/--bem/--exclusion/--regression`) + val ran clean. Tier 98.39% T2_Core,
0% FailSafe both WD/WE. DTYPE exact-match PASS. Office archetype: NonOffice 48.16% (<60% ✓),
Office_Public 28.39%, Office_Knowledge 16.18%, Unknown 5.48% (<10% ✓), Office_Sales 1.79%.
**Scorecard: 18 PASS / 1 WARN / 5 FAIL.**

**FAIL triage (manager, 2026-06-22):** 4 of 5 map cleanly to the LOCKED Step-4 structural
limits — AT_WORK slot 9.60pp & AT_HOME daytime 7.70pp = the G4 work-mass gap (obs 28.72% vs
syn 18.39% ≈10.33pp) propagated through linkage; night AT_HOME 83.18% & night sleep 61.40% =
night-shift profiles at 192K scale. WARN (N_HH_MEMBERS 1.50 vs 2.80) = person-view vs HH-view
gate mismatch (HH view = 2.48, fine). **OPEN:** colleagues co-presence FAIL (all=0.13% vs
obs=6.91%, 6.77pp) — diagnostic dispatched to confirm COMPOSITIONAL (synthetic mostly
non-workers, cosmetic) vs DEGENERATE (channel broken for synthetic workers, real) + localize
to Step-4 source vs Step-5 carry. Awaiting result before final-accept/gate-fix decision.

The original ORIGINAL note (kept for context):

- 2J Step 5 is COMPLETE and proven (see memory `project_step5_census_linkage.md`): local script
  `05_census_linkage.py` (`--full/--aggregate/--bem/--exclusion`) + `05_censusLinkageGSS_val.py`,
  data in `0_Occupancy/`. Step 5 runs **LOCALLY** (Step 6 onward is cluster).
- For 3J the new wrinkle is the **second (office/AT_WORK) channel** — Step 5 must carry both the
  residential and office tracks through linkage. Start by reading the 2J Step-5 script + val doc and the
  3J Leg-2 Step-4 outputs to scope what changes for two channels, THEN write an employee (Sonnet) prompt.
- Don't auto-execute multi-step implementation yourself — you're the manager. Plan it, then hand a scoped
  prompt to a Sonnet employee ("You are the employee. Execute the task below and append a Progress Log entry").

## Hard operating rules (do NOT violate — full text in CLAUDE.md)
- **Cluster:** never blocking `srun` / bare `python` on the login node (`speed-submit2`) — account-ban
  risk, flagged 3×. Always `sbatch` fire-and-forget, read the output file after. tcsh login shell: no
  `2>&1`; one-line commands; label every command "locally" or "on the cluster".
- **Cost:** monitoring/polling/file-scans/log-tails = Haiku/Sonnet employees, never Opus. Background
  agents silently inherit Opus — always pass `model: haiku`/`sonnet`. Min poll spacing 30 min; prefer
  not polling at all (you act on terminal results the user relays).
- **Never scan big files (≈500 MB diaries, big csv/logs) in your own context** — delegate to a cheap employee.
- Every SLURM wrapper: `--time=48:00:00` minimum.
- You own all git ops. Casual tone, ≤100 words unless detail asked. Archive predecessor before any
  architecture edit. Update Progress Logs incrementally.

## Key files / locations
- Step-4 val doc + Progress Log: `3J_docs_occ_nTemp\Leg2_2-split\Step4_docs\3rdJ_04_augmentationGSS_val.md`
- Step-4 main doc: `3J_docs_occ_nTemp\Leg2_2-split\Step4_docs\3rdJ_04_augmentationGSS.md`
- 2J reference (downstream): `2J_docs_occ_nTemp\` ; data: `0_Occupancy\`
- Cluster: `o_iseri@speed.encs.concordia.ca`, scratch `/speed-scratch/o_iseri/`

## First move when I'm back
Say "starting Step 5" and I'll: (1) read 2J `05_census_linkage.py` + its val doc and the 3J Leg-2
Step-4 outputs, (2) scope the two-channel changes, (3) write a Sonnet employee prompt for the Step-5
build. Confirm before I dispatch.
