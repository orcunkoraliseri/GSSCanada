# Step-5 FAILs — Deep-Research Prompt Set

Deep-research briefs to understand the 3J Leg-2 **Step-5 FAILs at a deeper level** and to find
**evidenced ways to solve them**. Each `.md` here is a **standalone prompt**: paste everything below its
"paste this line" marker into a fresh deep-research session (Gemini / Claude / GPT deep research).

These FAILs are all **inherited from the LOCKED Step-4 generator**, not Step-5 linkage bugs — see the
parent investigation doc `../3rdJ_05_inherited_Step4_FAILs.md` (and the Step-4 lock record
`../../Step4_docs/3rdJ_04_augmentationGSS_val.md`). The prompts are written around that constraint:
**prioritise post-hoc / Step-5 / marginal-preserving fixes, and flag any solution that would require
re-opening (re-training) Step 4.**

## The set

| # | Prompt | Covers Step-5 gates | Step-4 root cause | Core question |
|---|--------|---------------------|-------------------|---------------|
| 01 | `01_work_mass_underfill_prompt.md` | AT_WORK max-slot (10.18 pp), AT_HOME max-slot (8.59 pp) | G4 work-peak under-fill (obs 28.72% vs syn 18.39%, −10.33 pp) | Why do generators under-produce daytime work, and how to add work mass while keeping marginals exact? |
| 02 | `02_night_occupancy_sleep_dominance_prompt.md` | Overnight AT_HOME (83.13% vs ≥85%), Night sleep dominance (61.15% vs ≥70%) | Night-shift / diverse night-activity at scale | Are the night thresholds defensible given real shift-work, or is the model off? |
| 03 | `03_colleagues_copresence_prompt.md` | Colleagues co-presence W3 (10.51% vs obs 14.88%, 4.37 pp) | Synthetic co-presence channel thinner than observed (per-worker ≈12.4% vs ≈21.2%) | Why are secondary co-presence channels under-generated, and how to correct at the linkage stage? |
| 04 | `04_marginal_vs_joint_calibration_prompt.md` | **Cross-cutting** (underpins 01–03) | The rake matches 1-D marginals exactly but never constrains the joint/temporal structure each metric needs | Why does raking leave joint structure uncorrected, and how to fix it without losing exact marginals? |

## Shared context (already embedded in each prompt)

- **Pipeline:** synthetic 48×30-min time-use diaries from Canadian **GSS-Time Use + Census** → EnergyPlus
  (residential + office). Step 4 = frozen **diffusion generator + marginal-preserving rake**; Step 5 =
  demographic-fallback **census linkage**, validated against the **observed (real-diary) subset**.
- **Why these can't be patched by raking:** the rake forces 1-D marginals exact but leaves the
  joint/temporal structure (work-peak mass, co-presence coupling) uncorrected. Each prompt asks for
  solutions that respect this.
- **Constraint to honour in any proposed fix:** Step 4 is LOCKED. Each prompt requires every solution to be
  tagged **preserves-marginals (Y/N)** and **needs-retraining (Y/N)**, and to call out fixes that would
  *game* a full-vs-observed validation.

## How to use the results

Suggested order: run **04 first** for the calibration-vs-joint-structure framework (it defines the
feasibility ladder — pure post-hoc / re-rake / re-train — used to judge every fix), then 01–03 for the
theme-specific benchmarks and solutions.

For each returned brief: (1) record the empirical benchmark + threshold verdict, (2) shortlist the
top-ranked **Step-5-compatible / marginal-preserving** solution(s), (3) bring those back as a scoped
proposal before any implementation — and only consider a Step-4 re-train if the research shows no
acceptable post-hoc path. Findings feed back into `../3rdJ_05_inherited_Step4_FAILs.md`.
