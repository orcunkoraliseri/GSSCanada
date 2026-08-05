# INDEPENDENT BACKWARD AUDIT — 3J Leg-3 four-channel occupancy pipeline
## Prompt for **Gemini**. Emphasis: **claims, documents and provenance.**

You are auditing a research pipeline that produces results for two academic papers, one of which is
**already submitted**. Your job is to find what is wrong, what is unproven, and what does not mean what
the documents claim it means — by tracing every load-bearing *claim* back to whatever is supposed to
support it.

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
│   ├── PROMPT_gemini_backward_audit.md     ← ✅ THIS FILE. The only one you may read
│   ├── PROMPT_codex_backward_audit.md      ← ❌ the other auditor's prompt
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

⚠️ **This exclusion matters more for you than for the other auditor.** Your strength is ingesting the
whole document corpus at once — which is exactly how the excluded folder would get swept in. Build your
file list explicitly and check it before you read:

```bash
find . -name "*.md" -not -path "*/improvements/investigation/*" | sort
```

That single exclusion is sufficient and complete — your own prompt lives under it, and you have already
been given that. **Never widen the file list to include anything under `improvements/investigation/`.**

If you accidentally read excluded material, **say so in your report** rather than hiding it. A declared
contamination is recoverable; an undeclared one silently invalidates the comparison.

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

1. **Is every load-bearing claim actually supported?** The design documents assert constants, standards
   references, external benchmarks and "CONFIRMED" bands. Trace each to its source.
2. **Do the documents agree with each other, and with the artefacts?** This project has three legs, nine
   steps, a design freeze round of 13 research reports, and several fix logs. Divergence between them is
   where meaning quietly changes.
3. **What is inherited without ever being re-examined?** An assumption that entered in Leg 1 and was
   carried forward by convention is the most dangerous kind, because no leg owns it.
4. **What reaches the already-submitted paper?** `2J_docs_occ_nTemp/writing/fullSet/readySubmission.md`
   is the highest-stakes document in this repository.

---

## 3. Standard of evidence — the rules this project holds itself to

Apply them to the project, and to yourself.

| Rule | Meaning |
|---|---|
| **A citation is not evidence until it has been opened** | Do not accept a claim because a document attributes it to a standard, a table or a paper. Open the source, or mark the claim unverified. **This is your central instrument** |
| **A logged number is not evidence** | If a report or a Progress Log states a value, it may never have been re-derived. Prefer the artefact |
| **Every finding needs a falsifier** | State *the one cheap measurement that would kill it*. A finding with no falsifier is an opinion |
| **A gate is not validation until it has been seen failing** | Ask of every PASS: what input would have made this FAIL? If none exists, the PASS is worth nothing |
| **A clean negative is a result** | "No source exists for this claim" is one of the most valuable things you can return |
| **Distinguish *wrong* from *not established*** | Different verdicts, different consequences. Say which you mean, every time |
| **Report plainly what weakens the papers** | Especially the submitted one. That is a reason for care, not for softening |
| **Never propose widening a band to erase a failure** | If a threshold is unreachable, show it inapplicable or re-specify it — never move it because the result missed |

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
grep -n "^#\{1,3\} " 3rdJ_00_4split_Occupancy_Pipeline.md
```

- `3rdJ_00_4split_Occupancy_Pipeline.md` (437 lines) — the design document: `AIM`, `STEP 1` … `STEP 9`,
  `VALIDATION PLAN`, `KEY DESIGN DECISIONS`, `OPEN DECISIONS`.
- `3rdJ_00_4split_Occupancy_Pipeline_Overview.md` (226 lines) — condensed, with `VALIDATION GATES` and
  `KEY DESIGN DECISIONS SUMMARY`.

**Read both fully first.** Then build a register of every quantitative or attributed claim in them, and
spend the audit discharging that register.

### What the pipeline is

Canadian **GSS time-use diaries** (2005 / 2010 / 2015 / 2022) → harmonised → tiled to 30-minute presence
flags → a **three-head conditional Transformer** → linked to Census archetypes → forecast to 2030 →
injected into an **EnergyPlus** mixed-use tower → simulated → per-channel end-use loads.

**Four occupancy channels:** residential, office, retail, hotel. Three legs: Leg 1 (residential,
published), **Leg 2** (+office, closed and paper-ready — *do not modify any file under
`Leg2_2-split/`*, reading is fine), **Leg 3** (+retail +hotel, current).

### The document corpus

```bash
cd /c/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp
find . -name "*.md" -not -path "*/improvements/investigation/*" | xargs wc -l | sort -n | tail -40
```

| Path | What |
|---|---|
| `Leg3_4-split/Step{1..9}_docs/*.md` | Per-step design doc + validation report |
| `Leg3_4-split/deepResearch/` | 13 frozen design-freeze reports, `dr_L3-01` … `dr_L3-13` — the external evidence base for most design decisions |
| `Leg3_4-split/deepResearch_v2/` | Later round |
| `improvements/3rdJ_L3_improvements_step5_6_7.md` | Step 5/6/7 fix log |
| `improvements/3rdJ_L3_improvements_step9.md` | Step 9 fix log, ~7,700 lines — **mind the §0.21.4 exclusions** |
| `improvements/3rdJ_L3_step9_READER_GUIDE.md` | Cold-reader guide — **mind the §1.4 / §2 exclusions** |
| `Leg2_2-split/` | The closed previous leg |
| `2J_docs_occ_nTemp/writing/fullSet/readySubmission.md` | **The submitted manuscript** |
| `3J_docs_occ_nTemp/investigation/` | Two early suitability/synthesis notes — *not* the excluded folder |
| `RESUME.md`, `Leg3_4-split/4-channel_split.md` | Summaries |

---

## 5. Your emphasis: claims, provenance and cross-document consistency

The other auditor is executing code. **You are tracing claims.** Your advantage is holding the entire
corpus at once and seeing where two documents cannot both be true.

### 5.1 Build the claim register first

Go through both entry documents and extract every claim of these kinds:

- **A constant with a unit** — a density, a peak fraction, a power density, an area, a count
- **An attribution** — "NECB Table X says…", "per ASHRAE 90.1…", "Richardson et al. found…", "dr_L3-06
  CONFIRMED this band"
- **An external benchmark or band** — any `[lo, hi]` a result is compared against
- **A frame count** — any N of households, respondents, diary-days, cells, zones
- **A design property stated as implemented** — "we do X", "the model uses Y", "Z is never scaled"

For each, record: the claim, `path:line`, what is supposed to support it, and whether you could open
that support. **The last column is the audit.** Claims where support could not be opened are findings,
even when the claim turns out to be true.

### 5.2 Cross-document contradiction sweep

Constants and counts repeat across the corpus. Where the same quantity appears twice with different
values, one of them is wrong and something downstream inherited it.

```bash
cd /c/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp
# frame counts
grep -rn "[0-9]\{2,3\},[0-9]\{3\}" --include=*.md . | grep -iv "investigation/" | head -60
# densities, peaks, m2/person
grep -rni "m²/person\|m2/person\|person/m\|peak fraction\|W/m²\|W/m2" --include=*.md . | head -60
# bands
grep -rn "\[[0-9]\+ *, *[0-9]\+\]" --include=*.md . | head -40
```

Then check the ones that matter against the artefact rather than against the other document — two
documents agreeing tells you nothing if one copied the other.

### 5.3 The design-freeze reports are secondary sources — treat them as such

`Leg3_4-split/deepResearch/dr_L3-01` … `13` supply the external justification for many decisions and
several are described as "CONFIRMED". For the ones that carry weight:

- Does the report actually contain the number the design document attributes to it?
- Does the report cite a primary source, or does it assert?
- Is the quantity in the report **the same quantity** as the one it is used to justify? A band derived
  on one denominator being used to judge a rate computed on a different denominator is a silent
  category error and is very hard to see from either document alone.
- Is any of them *circular* — a check whose expected value comes from the same source it is checking?

```bash
ls Leg3_4-split/deepResearch/
grep -rn "CONFIRMED\|confirmed" Leg3_4-split/deepResearch/*.md | head -40
```

### 5.4 Inheritance across the three legs

Trace what Leg 3 carries from Leg 2 and from Leg 1 — and find what was never re-derived.

```bash
grep -rn "Leg.2\|Leg 2\|inherit\|unchanged from\|same as Leg\|reuse" --include=*.md \
  Leg3_4-split/ | head -60
```

For each inherited item: was it re-verified in Leg 3, or assumed? An assumption inherited twice has
usually stopped being visible to anyone. Pay particular attention to anything inherited into
`readySubmission.md`.

### 5.5 The validation plan versus what was actually validated

Compare the `VALIDATION PLAN` / `VALIDATION GATES` sections of the entry documents against the gates
that actually exist and actually ran:

```bash
grep -rn "PASS\|FAIL\|WARN" Leg3_4-split/Step*_docs/*_val.md | wc -l
grep -rln "FAIL" Leg3_4-split/Step*_docs/*_val.md
```

Three questions per gate, answered where interesting:

1. **Was it ever implemented?** A gate promised in the plan and absent from the code is a specific,
   common and serious defect.
2. **What input would make it FAIL?** If none, it is vacuous.
3. **Does the quantity it measures survive into the deliverable?** If a later step normalises it away,
   discards it or overwrites it, the gate measures nothing — no matter how carefully it was computed.

Also look for gates that were **re-specified after their result was known**, and for thresholds whose
justification appears in a document dated after the run.

### 5.6 The `OPEN DECISIONS` sections

Both entry documents end with open decisions. For each: was it resolved? Where is the resolution
recorded? Does the resolution match what the code does? Silently-closed decisions are a rich seam.

### 5.7 The submitted manuscript

```bash
wc -l ../2J_docs_occ_nTemp/writing/fullSet/readySubmission.md
```

Read it as an auditor, not as a reader. Which of its claims depend on the machinery you have just
examined? Which of its stated limitations are complete, and which limitation is missing? If anything in
Leg 3 casts doubt on a 2J claim, that is the single most important thing you can report.

---

## 6. Constraints

- **Read-only.** Change no pipeline file, no artefact, no gate. The only file you create is your report.
- **No cluster, no simulation.** Do not submit SLURM jobs, do not connect to
  `speed.encs.concordia.ca`, do not run EnergyPlus or retrain anything. If a check needs compute,
  describe it as a falsifier instead.
- **`Leg2_2-split/` is frozen** — read freely, modify nothing.
- **Big files:** `augmented_diaries.csv` is ~418 MB and `.sql` outputs are large. Stream with
  `head`/`awk`/`wc -l`; never load them whole.
- **Cite everything as `path:line`.** A finding without a file-and-line reference will not be actionable.
- If you cannot verify something, **say it is unverified** rather than inferring it.

---

## 7. Deliverable

Write **one markdown file**:

```
3J_docs_occ_nTemp/improvements/investigation/investigationPrompts/REPORT_gemini_backward_audit.md
```

### Required structure

```markdown
# Independent backward audit — 3J Leg-3 — GEMINI
**Date:** <date> · **Auditor:** Gemini · **Basis:** claims, documents and provenance
**Blindness declaration:** <the declaration from §1, filled in>

## Method, and its limits
What you read, what you traced, what you did NOT check and what that costs.
Be explicit about coverage: a reader must know where your eyes never went.

## Verdict, up front
One paragraph, then a severity table:

| | Finding | Severity | Step | Reaches the submitted 2J paper? |
|---|---|---|---|---|
| G-1 | … | High / Med / Low | … | yes / no |

Number your findings **G-1, G-2, …** (G for Gemini) so they can be cross-referenced later.

## The claim register
The full table from §5.1 — claim, `path:line`, supporting source, could it be opened, verdict.
Include the claims that checked out. This table is a deliverable in its own right.

## Findings
One section per finding. Each MUST contain:
- **The evidence** — `path:line`, the actual text or values
- **Why it matters** — what conclusion it changes; name the paper claim if any
- **Magnitude, honestly** — how big is it, and the honest upper bound if unknown
- **Falsifier** — the single cheapest measurement that would kill this finding
- **Recommended action** — and its cost

## Contradictions between documents
Every place two documents state incompatible things about the same quantity, with both references and
a judgement on which is likely correct and what inherited the wrong one.

## What is NOT wrong
Things you checked that are sound, so nobody re-audits them. Include the ones you expected to be broken
and were not.

## Unsupported or unopenable citations
Every attributed claim whose source you could not open, could not find, or which does not say what it
is cited for. This is a primary deliverable, not an appendix.

## Open questions I could not settle
What you would need — data, access, a source, compute — and why it blocks.

## Recommended order of work
Ordered by (evidence gained) / (cost), not by severity. State the cost of each item.
```

### On tone

Write findings plainly. If an area is sound, say so without hedging — an audit that finds problems
everywhere is as useless as one that finds none. If something weakens the submitted paper, state it
directly and completely; that is the most valuable thing you can produce here.

**A finding you are unsure about is still worth reporting** — mark it low-confidence and give the
falsifier. Do not filter to only what you can prove; that is what the falsifier column is for.
