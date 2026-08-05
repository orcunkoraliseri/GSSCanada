# INDEPENDENT BACKWARD AUDIT — 3J Leg-3 four-channel occupancy pipeline
## Prompt for **Codex**. Emphasis: **code and artefacts.**

You are auditing a research pipeline that produces results for two academic papers, one of which is
**already submitted**. Your job is to find what is wrong, what is unproven, and what does not mean what
the documents claim it means — working from the code and the data files, not from the prose.

You are one of two independent auditors working blind to each other and blind to a third audit that
already exists. **Do not go looking for that third audit.** Section 1 tells you exactly what is
off-limits. The value of your work is entirely in its independence: if you reconstruct someone else's
conclusions from their notes, you have produced nothing.

---

## 1. 🔴 BLINDNESS PROTOCOL — read this before opening anything

A previous audit of this same pipeline exists in this repository — **in the very folder this prompt is
stored in.** Reading it would destroy the purpose of your work.

**🔴 Whitelist rule, not a blacklist. Inside `3J_docs_occ_nTemp/improvements/investigation/` the ONLY
file you may open is this prompt.** Everything else under that path is off-limits, whatever it is
called and whatever it appears to contain:

```
improvements/investigation/
├── investigationPrompts/
│   ├── PROMPT_codex_backward_audit.md      ← ✅ THIS FILE. The only one you may read
│   ├── PROMPT_gemini_backward_audit.md     ← ❌ the other auditor's prompt
│   └── REPORT_*.md                         ← ❌ including the other auditor's report
├── 3rdJ_L3_backward_audit_*.md             ← ❌ THE PRIOR AUDIT. Never open this
├── README.md                               ← ❌ it summarises the prior audit
└── deepResearch Prompts/                   ← ❌ literature inputs to the prior audit, and its findings
```

Everywhere else in the repository is fair game.

**Partial exclusions.** These two files are legitimate primary material and you *should* read them —
but parts of them were contaminated by the prior audit. Skip any passage that:

- contains a finding label matching `B-1` … `B-12`, or the words `backward audit` / `backward-audit`
- is inside `§0.21.4 Q2`, `§0.21.4 Q8`, `Q8a` or `Q8b` of `improvements/3rdJ_L3_improvements_step9.md`
- is row `Q2`, `Q8a`, `Q8b` of `§1.4`, or rows `20`–`21` of `§2`, in
  `improvements/3rdJ_L3_step9_READER_GUIDE.md`

Locate the contaminated lines first so you can steer around them:

```bash
cd /c/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp
grep -n "B-1[0-2]\|B-[1-9]\b\|backward.audit" improvements/3rdJ_L3_improvements_step9.md \
     improvements/3rdJ_L3_step9_READER_GUIDE.md | head -60
```

If you accidentally read excluded material, **say so in your report** rather than hiding it. A
declared contamination is recoverable; an undeclared one silently invalidates the comparison.

**Your report must open with this declaration, filled in honestly:**

> *Blindness declaration: inside `improvements/investigation/` I opened only my own prompt. I did not
> open the prior audit, its README, `deepResearch Prompts/`, or the other auditor's prompt or report.
> Contaminated passages
> encountered: [none | list them]. Findings below were reached independently of any prior audit.*

---

## 2. The question you are answering

Not *"does the pipeline run?"* — it runs. The question is:

> **Does what this pipeline produces mean what the papers will say it means?**

Sub-questions, in priority order:

1. **Are the early steps sound?** Steps 1–4 (data collection → harmonisation → tiling → model
   training) were closed in three days and Step 4 is labelled *"DEFINITIVELY COMPLETE — 0 genuine model
   defects, PAPER-READY"*. Labels like that are worth testing.
2. **Do the validation gates actually test what they claim?** A gate that cannot fail is worse than no
   gate, because it is counted as evidence.
3. **Does any number in the documents disagree with the artefact it describes?**
4. **What reaches the already-submitted paper?** Anything inherited from the earlier legs into
   `2J_docs_occ_nTemp/writing/fullSet/` is the highest-stakes category in this repo.

---

## 3. Standard of evidence — the rules this project holds itself to

Apply them to the project, and to yourself.

| Rule | Meaning |
|---|---|
| **A logged number is not evidence** | If a report `.txt` or a Progress Log says a value, re-derive it from the artefact's own columns before believing it. This project has caught itself quoting numbers that were never re-checked |
| **A citation is not evidence until it has been opened** | Do not accept a claim because a document attributes it to a standard or a paper. Open the source or mark the claim unverified |
| **Every finding needs a falsifier** | For each finding, state *the one cheap measurement that would kill it*. A finding with no falsifier is an opinion |
| **A gate is not validation until it has been seen failing** | Ask of every PASS: what input would have made this FAIL? If you cannot construct one, the PASS is worth nothing |
| **A clean negative is a result** | "I checked X and it is fine" is worth reporting. So is "no source exists for this claim" |
| **Distinguish *wrong* from *not established*** | These are different verdicts with different consequences. Say which one you mean, every time |
| **Report plainly what weakens the papers** | Especially the submitted one. That is a reason for care, not for softening |
| **Never propose widening a band to erase a failure** | If a threshold is unreachable, the remedy is to show it inapplicable or to re-specify it — never to move it because the result missed |

---

## 4. Orientation

```
REPO = /c/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main
```

Commands below are **Git Bash / POSIX**. If your shell is PowerShell, wrap them:
`bash -lc '<command>'`. 🔴 **Never count lines with PowerShell `Measure-Object -Line`** — it
miscounts blank lines in this repo. Use `wc -l`.

### Start here — the two entry documents

```bash
cd /c/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split
wc -l 3rdJ_00_4split_Occupancy_Pipeline.md 3rdJ_00_4split_Occupancy_Pipeline_Overview.md
```

- `3rdJ_00_4split_Occupancy_Pipeline.md` (437 lines) — the design document. Sections `AIM`,
  `STEP 1` … `STEP 9`, `VALIDATION PLAN`, `KEY DESIGN DECISIONS`, `OPEN DECISIONS`.
- `3rdJ_00_4split_Occupancy_Pipeline_Overview.md` (226 lines) — the condensed version, with
  `VALIDATION GATES` and `KEY DESIGN DECISIONS SUMMARY`.

**Read both fully before touching anything else.** Then treat every quantitative claim in them as a
hypothesis to be checked against the artefacts.

### What the pipeline is

Canadian **GSS time-use diaries** (cycles 2005 / 2010 / 2015 / 2022) → harmonised → tiled to 30-minute
presence flags → a **three-head conditional Transformer** → linked to Census archetypes → forecast to
2030 → injected into an **EnergyPlus** mixed-use tower → simulated → per-channel end-use loads.

**Four occupancy channels:** residential, office, retail, hotel. Three legs:
Leg 1 (residential, published), **Leg 2** (+office, closed and paper-ready — *do not modify any file
under `Leg2_2-split/`*, reading is fine), **Leg 3** (+retail +hotel, current).

### Layout

```bash
cd /c/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp
ls Leg3_4-split/                       # Step1_docs … Step9_docs, deepResearch/, deepResearch_v2/
ls Leg3_4-split/Step*_docs/ | head -80
```

Each `StepN_docs/` holds: the design `.md`, the implementation `.py`, a validator `_val.py`, a
validation report `_val.md`, and `outputs_stepN/` with the artefacts.

Other material you may read:

| Path | What |
|---|---|
| `improvements/3rdJ_L3_improvements_step5_6_7.md` | Step 5/6/7 fix log |
| `improvements/3rdJ_L3_improvements_step9.md` | Step 9 fix log, ~7,700 lines — **mind the §0.21.4 exclusions** |
| `improvements/3rdJ_L3_step9_READER_GUIDE.md` | Cold-reader guide to the above — **mind the §1.4 / §2 exclusions** |
| `Leg3_4-split/deepResearch/` | 13 frozen design-freeze reports, `dr_L3-01` … `dr_L3-13` |
| `Leg2_2-split/` | The closed previous leg — read-only |
| `2J_docs_occ_nTemp/writing/fullSet/readySubmission.md` | **The submitted manuscript** |
| `eSim_bem_utils/commercial_integration.py` | The BEM injector |
| `3J_docs_occ_nTemp/investigation/` | Two early suitability/synthesis notes — *not* the excluded folder |

---

## 5. Your emphasis: code and artefacts

The other auditor is reading documents. **You are reading code and data.** Start from the `.py` and the
`outputs_*/` files and work outward to the prose — the opposite direction from the design docs. Where
the two disagree, the artefact wins and the disagreement is a finding.

### 5.1 Re-derive, do not read off

Take the headline numbers from the validation reports and recompute them from the artefacts.

```bash
cd /c/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg3_4-split
# every gate verdict in the repo, with its step
grep -rn "\[PASS\]\|\[FAIL\]\|\[WARN\]\|PASS\b\|FAIL\b" Step*_docs/*_val.md | wc -l
grep -rln "FAIL" Step*_docs/*_val.md
# the artefacts each validator claims to have read
ls -la Step*_docs/outputs_step*/ | head -100
```

For each **FAIL** and each **WARN** still open: find whether a mechanism was ever located, or whether
it was absorbed by a re-specification. Absorbed-without-mechanism is a finding.

### 5.2 Interrogate the gates themselves

```bash
# read the validators as programs, not as reports
wc -l Step*_docs/*_val.py
grep -n "def .*gate\|def check\|PASS\|FAIL\|assert\|threshold\|tol\b" Step4_docs/*_val.py | head -60
```

For every gate, answer three questions in your report where the answer is interesting:

1. **What input would make it FAIL?** If none exists, it is vacuous.
2. **Is its reference independent of the thing it audits?** A check whose expected value comes from the
   same source it is checking cannot fail.
3. **Does the quantity it measures survive into the deliverable?** A gate on a value that a later step
   normalises away, discards, or overwrites is measuring nothing.

That third question is the one most often missed. Trace each gated quantity forward through Step 7's
injection into the IDF and ask whether it still exists there.

### 5.3 Threshold provenance

For every numeric threshold, band and tolerance in the validators: **where did the number come from,
and was it chosen before or after the result it judges was known?**

```bash
grep -rn "MIN_POOL\|THRESH\|BAND\|BENCH\|tol =\|TOL\|0\.0[0-9]\|>= 0\.\|<= 0\." Step*_docs/*_val.py \
  | head -60
```

A threshold selected because it made a specific test pass is a serious finding regardless of whether
the shipped value is defensible on other grounds.

### 5.4 The model, Step 4

```bash
cd Leg3_4-split/Step4_docs && ls
head -60 3rdJ_04D_train_4split.py
grep -n "loss\|head\|rake\|projection\|teacher\|forcing\|seed" 3rdJ_04D_train_4split.py | head -40
```

Specific things worth establishing:

- Are the reported per-head metrics computed on **free-running generated output**, or on
  **teacher-forced** training-time output? These differ, and only the first describes the shipped pool.
- Is the shipped artefact the one the metrics describe? Check hashes/timestamps.
- Multi-seed: does more than one seed exist, and is the reported result a single seed presented as if it
  were the method's performance?
- The exclusivity / projection / raking chain: does it enforce what the docs claim, on the artefact?

### 5.5 The residential aggregation — highest stakes in the repo

How is a household's occupant count derived from a single respondent's diary? Read the actual
transformation, in Step 5 and in the injector, and then **look at what lands in the IDF**:

```bash
cd /c/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main
grep -n "HHSIZE\|Number_of_People\|hom30\|any.*present\|household" \
  eSim_bem_utils/commercial_integration.py | head -40
```

Then find an injected IDF and read a residential `PEOPLE` object end to end:

```bash
find 3J_docs_occ_nTemp/Leg3_4-split/Step8_docs -name "injected.idf" | head -3
# then: grep -n -A10 "PEOPLE," <path> | head -60
```

Ask: what does this imply about **within-household** presence variation? Is that implication stated
anywhere? Does it reach the submitted 2J manuscript?

### 5.6 The BEM side — parse, do not trust the transcription

The design documents quote NECB constants (occupant densities, peak schedule fractions, power
densities). **Parse them out of the actual IDF and compare.** The source archetypes:

```bash
cd /c/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/outputs_step8/office_idfs_v242/CAN_MTL
ls *.idf
# example: pull every People density with its zone and schedule
awk '/^  People,$/{f=1;n=0;next} f{n++; if(n==1)nm=$1; if(n==3)sch=$1; if(n==6){print nm" | "sch" | "$1; f=0}}' \
  TallBuilding_*.idf | sort -u
```

Do the same for `Lights`, `ElectricEquipment`, `DesignSpecification:OutdoorAir` and
`Controller:MechanicalVentilation`. Then compare against every constant the design docs assert.
Anything that is asserted as an implemented design property but is not in the file is a finding.

Also worth asking: which schedules does the injector actually overwrite, and does overwriting one
object's schedule damage a different object that shared it?

### 5.7 Big files — do not load these into memory

`augmented_diaries.csv` is ~418 MB; `eplusout.sql` files are large. Stream them:

```bash
head -2 <bigfile.csv>          # header only
awk -F, 'NR<=1{print; exit}' <bigfile.csv>
wc -l <bigfile.csv>            # never PowerShell Measure-Object
```

🔴 **Do not run EnergyPlus. Do not submit cluster jobs. Do not retrain anything.** This audit is
read-only and local. If a check needs compute, describe it as a falsifier instead of running it.

---

## 6. Constraints

- **Read-only.** Change no pipeline file, no artefact, no gate. The only file you create is your report.
- **No cluster.** Do not submit SLURM jobs, do not connect to `speed.encs.concordia.ca`.
- **`Leg2_2-split/` is frozen** — read freely, modify nothing.
- **Cite everything as `path:line`.** A finding without a file-and-line reference will not be actionable.
- If you cannot verify something, **say it is unverified** rather than inferring it. Unverified is a
  legitimate and useful state.

---

## 7. Deliverable

Write **one markdown file**:

```
3J_docs_occ_nTemp/improvements/investigation/investigationPrompts/REPORT_codex_backward_audit.md
```

### Required structure

```markdown
# Independent backward audit — 3J Leg-3 — CODEX
**Date:** <date> · **Auditor:** Codex · **Basis:** code and artefacts
**Blindness declaration:** <the declaration from §1, filled in>

## Method, and its limits
What you read, what you executed, what you did NOT check and what that costs.
Be explicit about coverage: a reader must know where your eyes never went.

## Verdict, up front
One paragraph, then a severity table:

| | Finding | Severity | Step | Reaches the submitted 2J paper? |
|---|---|---|---|---|
| C-1 | … | High / Med / Low | … | yes / no |

Number your findings **C-1, C-2, …** (C for Codex) so they can be cross-referenced later.

## Findings
One section per finding. Each MUST contain:
- **The evidence** — `path:line`, the actual values, the command that produced them
- **Why it matters** — what conclusion it changes; name the paper claim if any
- **Magnitude, honestly** — how big is it, and what is the honest upper bound if unknown
- **Falsifier** — the single cheapest measurement that would kill this finding
- **Recommended action** — and its cost

## What is NOT wrong
Things you checked that are sound, so nobody re-audits them. Include the ones you expected to be
broken and were not — those are the most useful entries here.

## Gate assessment
Every validation gate you examined: does it test what it claims? What input would make it fail?
Does the quantity it measures survive into the deliverable?

## Numbers that did not reconcile
Every documented value you re-derived: claimed vs measured vs verdict. Include the ones that matched.

## Open questions I could not settle
What you would need — data, access, a source, compute — and why it blocks.

## Recommended order of work
Ordered by (evidence gained) / (cost), not by severity. State the cost of each item.
```

### On tone

Write findings plainly. If the pipeline is sound in an area, say so without hedging — an audit that
finds problems everywhere is as useless as one that finds none. If something weakens the submitted
paper, state it directly and completely; that is the most valuable thing you can produce here.

**A finding you are unsure about is still worth reporting** — mark it as low-confidence and give the
falsifier. Do not filter to only what you can prove; that is what the falsifier column is for.
