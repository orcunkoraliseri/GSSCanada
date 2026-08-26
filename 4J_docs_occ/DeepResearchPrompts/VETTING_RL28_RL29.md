# Vetting record — `RL28` and `RL29`

#### Vetted 2026-08-26, before any value entered a Step 10 or Step 11 document.
#### Procedure: `README.md` § *Vetting a returned report, BEFORE any value enters a document* (7 steps).
#### Prompts: `L28_interdwelling_diversity_and_peak.md`, `L29_nonconvex_courtyard_dwelling_subdivision.md`

---

## VERDICT

| Round | Verdict | Carried into our documents | Rejected |
|---|---|---|---|
| `RL28` | **ACCEPTED on its design advice, REJECTED on its arithmetic** | the paired within-building design; the coincidence factor as the target metric; the `1/sqrt(N)` functional form | its saturation percentages; its heating-peak magnitude; its citation of our own paper as evidence |
| `RL29` | **ACCEPTED on one root cause, REJECTED on its headline remedy** | Arm D / Arm F never pooled, now with a **direction** to the bias; centroid-translate before rotating | the 120-vertex `BuildingSurface:Detailed` limit (**does not exist**); the RDP remedy (**answers a defect that is already gone**); every number resting on `[R2]` |

🔴 **The most valuable output of this round is not the literature.** Vetting it forced a re-measurement of
two blockers this project had written down, and **both were wrong**: one is dead, one does not close
arithmetically. That is the `feedback_recheck_recorded_blockers` rule paying for itself.

---

## 1. Checks run, and what each returned

Every check below is offline, cheap, and does not depend on trusting either dossier.

### 1.1 An identity the report cannot fake — `RL28`'s own scaling law

`RL28` B1 pre-commits to Rusck's form. That fixes the saturation curve completely, with no free
parameter:

```
gamma(N) = g_inf + (1 - g_inf)/sqrt(N)
=>  fraction of the asymptotic reduction reached at N  =  (1 - gamma(N))/(1 - g_inf)  =  1 - 1/sqrt(N)
```

`g_inf` **cancels**. So the saturation claim is arithmetic, not a literature finding:

| `N` | 2 | 4 | 6 | 10 | 20 | 30 | 50 | 100 |
|---|---|---|---|---|---|---|---|---|
| fraction of the asymptotic reduction reached | 29.3 % | **50.0 %** | 59.2 % | 68.4 % | 77.6 % | 81.7 % | 85.9 % | 90.0 % |

* `RL28` Section A: *"over 70 % of total peak reduction achieved by `N = 10`"* — actually **68.4 %**. Marginal.
* `RL28` Section A: *"over 90 % by `N = 20` to `30`"* — actually **77.6 %** and **81.7 %**. **90 % needs `N = 100`.** 🔴 **FALSE.**
* `RL28` Section A: *"asymptotic plateau beyond `N ~ 50`"* — 14 % of the effect is still unrealised at `N = 50`.

🔴 **The correction runs in our favour, which is why it must be stated rather than quietly used.** The
steepest part of the curve is the low end: going from `N = 1` to `N = 2` buys 29.3 percentage points, and
`N = 4` already buys **half of the entire asymptotic effect**. Our one emitted `S1` layout carries
`units_per_floor = 5` (measured, `s1_smoke_manifest.csv`). So the regime real European dwelling plates
occupy is the **informative** part of the curve, not the saturated tail. The objection *"your buildings
are too small for inter-dwelling diversity to matter"* is refuted by the dossier's own formula, and
`RL28`'s recommendation to sample for `N = 20` to `50` is aiming at the flat part.

### 1.2 Internal contradiction — `RL28` states the heating peak effect twice, differently

| Where | Claim |
|---|---|
| Section A | *"only a 2 % to 6 % peak reduction in space heating demand"* |
| B3 | *"`g_inf` approx 0.85 - 0.95, **5-15 %** peak reduction"* |
| Section E | *"modest peak reductions of **2-6 %**"* |

B3's own `g_inf` range implies a 5 to 15 % asymptotic reduction, contradicting Sections A and E.
**Consequence:** no pre-registered effect magnitude is taken from `RL28`. `H10` pre-registers the
**shape** of the curve, which the dossier states consistently, and lets Step 10 measure the magnitude.

### 1.3 Physics check — the low-pass attenuation

`|H(jw)| = 1/sqrt(1 + (w*tau)^2)`, `w = 2*pi/24 h`:

| `tau` | 50 h | 100 h | 150 h |
|---|---|---|---|
| attenuation of the diurnal component | **92.4 %** | 96.2 % | 97.5 % |

`RL28` B4 claims *"93-98 %"*. The lower edge is **92.4 %**, not 93 %. Minor, and the direction holds: a
heavy-mass envelope is a low-pass filter that removes almost all of a conserved-mean redistribution.
🟢 **This is the physical explanation of the Step 8 annual null, and it is the one genuinely useful thing
`RL28` contributes to the write-up.**

### 1.4 🔴 `RL29` B15 — the EnergyPlus 120-vertex limit does not exist

`RL29` rates this **Tier 1, confidence H, "read full text"**. Checked against two installed IDDs:

```
$ awk '/^BuildingSurface:Detailed,/,/^$/' /c/EnergyPlusV22-1-0/Energy+.idd | grep -i "extensible|max-fields"
$ awk '/^BuildingSurface:Detailed,/,/^$/' /c/EnergyPlusV24-2-0/Energy+.idd | grep -i "extensible|max-fields"
  \extensible:3 -- duplicate last set of x,y,z coordinates (last 3 fields) ...
       \note shown with 120 vertex coordinates -- extensible object
       \begin-extensible
```

`BuildingSurface:Detailed` carries `\extensible:3`, `\min-fields 20`, and **no `\max-fields`**. The IDD
says in its own note that 120 is what is **shown**, and that the object is **extensible**. There is no
120-vertex ceiling in either version.

🔴 **This is `README` vetting step 6 in its purest form.** The `~120-vertex` figure was in our own prompt,
because it is in `OpenUBEM_debug_References.md` ch.1. The dossier handed it back rated Tier 1 with a
claim to have read the IDD. **Laundered, not verified.**

### 1.5 🔴 And the defect it explains is already gone

`RL29`'s `D-S10-4` proposes a design change (RDP simplification, `epsilon = 0.15 m`, on every cadastral
polygon) to fix the 173-vertex `EPLUS_FATAL`. Measured on disk, 2026-08-26:

```
$ grep -rl "EPLUS_FATAL" openubem/outputs/eu_evidence/EU-04/          -> no matches
$ eplus_status counts, s1_smoke_manifest.csv (regenerated 2026-08-26 12:10)
  Counter({'EPLUS_COMPLETED': 12})
$ tail -1 s1_smoke/BATIMENT0000000240877527_part0.err
  EnergyPlus Completed Successfully-- 26 Warning; 0 Severe Errors
$ tail -1 s2_campaign/BATIMENT0000000240877527_part0/eplusout.err
  EnergyPlus Completed Successfully-- 24 Warning; 0 Severe Errors
$ tail -1 s2_campaign_v2/BATIMENT0000000240877527_part0/eplusout.err
  EnergyPlus Completed Successfully-- 19 Warning; 0 Severe Errors
```

The named building runs to completion in **all three** campaigns, with **0 Severe Errors** in each, and
`EPLUS_FATAL` occurs **nowhere** in the EU-04 evidence tree. The layout axis is unchanged (8 refused /
3 fallback / 1 emitted), so this is not a different sample — it is the same 12 buildings, re-run.

🔴 **Adopting `RL29`'s remedy would have changed the geometry of every footprint in the corpus to fix a
defect that no longer reproduces.** The stale record lives in three places and all three need the
correction: `OpenUBEM_debug_References.md` ch.1, `MVP_european_locations.md` §EU-04, and our own
`4thJ_10_ubemRealStock.md` §6.5 (corrected 2026-08-26).

### 1.6 🔴 `RL29` B19 — the CRS story does not close on our own numbers

`RL29` argues the `AREA_GAP` failure is caused by an absolute `1e-8 m2` tolerance being finer than
double precision at `1e6 m` coordinates. Our recorded `area_error_fraction` is **5.09e-12**, and the
building is `BATIMENT0000000240879449_part0`, footprint **544.206 m2** (`s1_smoke_manifest.csv`):

| quantity | value |
|---|---|
| recorded error fraction | 5.09e-12 |
| footprint area | 544.206 m2 |
| implied absolute gap | **2.77e-9 m2** |
| tolerance | 1e-8 m2 |
| verdict | **inside tolerance — this should have passed** |
| area at which the absolute tolerance would be crossed at that fraction | **~1 965 m2** |

So the failure is **not** explained by "the absolute tolerance is too tight for the plate size". Either
`area_error_fraction` is not `|dA|/A`, or the binding refusal is `OUTSIDE_FOOTPRINT` — a containment
test, not an area test — with `AREA_GAP` reported alongside it.

🟢 **The root cause `RL29` names is still right, and it is ours, not theirs:**
`generate_european_dwelling_layout` rotates about the **literal coordinate origin**
(`openubem/geometry/european_residential.py:504`), so rotation noise scales with distance from `(0,0)` —
that is a verified code fact, and centroid-translating before rotating fixes it in every CRS.
**What changes for us:** `G10.10` must test the **rotation origin**, not the tolerance units, and the
5.09e-12 / 1e-8 pairing must not be repeated as a causal statement until it is re-measured.

### 1.7 Citation defects

| Ref | Defect | Consequence |
|---|---|---|
| `RL29` `[R2]` Vivian et al. (2020) | 🔴 **Self-refuting.** The dossier's own "Crossref verified" line returns a **different paper** — *"Analysis and application of a lumped-capacitance model for urban building energy modelling"*, Zarrella et al. — not the cited *"Evaluation of the impact of thermal zoning on building energy simulations"*. | B1, B2, B4, B5 all lean on `[R2]`. **The fallback-bias percentages and the `N_u` error ladder may not be quoted** until it is resolved. The bias *direction* survives on Chen & Hong (2018) `[R1]`, which is correctly cited. |
| `RL28` `[R15]` Gaetani et al. | Cited as **2017**; its own CrossRef line returns **Year: 2016**. | Use the DOI, not the year, when citing. |
| `RL28` `[R16]` vs `RL29` `[R17]` | Same DOI `10.1016/j.energy.2016.10.057`, dated **2016** in `RL28` and **2017** in `RL29`. *Energy* vol. 117 is **2017**. | `RL28` is wrong. Cross-dossier contradiction found by comparing the two rounds against each other. |
| `RL28` `[R1]` Rusck (1956) | Given a Semantic Scholar URL whose hash is not credible, for a 1956 in-house periodical (*ASEA Journal*), and claimed *"opened and verified"*. | Treat as a **conventional attribution** for a standard distribution-planning formula. **Do not cite it in the paper without opening it.** |
| `RL28` `[R18]` Iseri et al. (2026) | 🔴 Cites **the author's own paper** as the evidence for the within-building paired-design requirement. | `README` vetting step 1: anything a dossier says about our own work is quoted from the prompt or invented. **Not carried.** The design advice stands on its own logic, which is why it is accepted below. |
| `RL29` `[R11]` Hertel & Mehlhorn | Conflates two publications (*Information and Control* 64 and *FCT '83* LNCS 158) into one entry. | Cosmetic; the algorithm is real and standard. |
| `RL29` B13 | Selection bias about **European urban typology** sourced to two generic statistics texts (Rothman; Little & Rubin). | A sound argument, **not a sourced fact**. Write it as our reasoning, not as a citation. |

### 1.8 `README` step 7 — did either report move in the rescuing direction?

**`RL28`: partly, and it was caught.** It endorses running Step 10, then predicts the annual channel will
stay null and the peak channel will move by only a few percent — i.e. it tells us the step is worth
running *and* that its headline will be small. A pure rescue would have promised a large effect. The
endorsement is therefore weak evidence, and the design advice is accepted on its **internal logic**
(§2.1), not on the dossier's authority.

**`RL29`: no.** Its first sentence concedes the fallback is biased rather than noisy, which is the
answer that **costs** us — it forbids the pooling that would have doubled Arm D's denominator. A report
that volunteers the expensive answer to the question it was asked is the one to take more seriously.

---

## 2. What is carried into our documents

### 2.1 🟢 ACCEPTED — the paired within-building design (`RL28` Section C, row 2)

Comparing buildings that happen to have different `N_u` confounds **diversity** with **geometry, volume
and envelope area**. The fix costs one extra run per building:

* **Case A** — one diary, replicated to all `N_u` zones. Synchronised.
* **Case B** — `N_u` independently sampled diaries. Same footprint, same archetype, same weather, same `f`.
* The effect is `delta_div = Metric(Case B) - Metric(Case A)`, **within footprint**.

🔴 **This is accepted because the argument is sound, not because a dossier said it.** It is the same
control logic Step 8 already uses for `f = 0`, applied to a second axis. It also makes `H10` testable on
**Arm F** geometry as well as Arm D, which matters because Arm D is only 18 buildings of 297.

### 2.2 🟢 ACCEPTED — the coincidence factor as the target metric

`CF(N_u) = P_peak,building / sum(P_peak,zone)`, plus the 99th-percentile hourly heating power.

Why this matters more than the dossier's framing suggests: `CF` is **dimensionless and bounded in
`(0, 1]`**, and `CF = 1` exactly when every dwelling peaks in the same hour. So `H10` becomes a statement
about a bounded quantity with a known null value, instead of a statement about a difference in
`kWh/m2` whose scale depends on the archetype. **`FINDING 143` died because a peak effect was compared
against a between-diary spread it could not beat.** `CF` does not have that failure mode: the synchronised
Case A gives `CF = 1` by construction, so the comparison is against a **constant**, not a spread.

### 2.3 🟢 ACCEPTED — the functional form, as a sharper pre-registration

`H10` currently predicts only *"grows with `N_u`"*, which almost anything satisfies. It is replaced by a
**shape** prediction: `CF(N) = g_inf + (1 - g_inf)/sqrt(N)`, one free parameter `g_inf`, fitted across
the observed `N_u` range and reported with its residuals. A monotone rise that does not fit `1/sqrt(N)`
is now a **distinguishable third outcome**, and it is more interesting than either of the original two.

### 2.4 🟢 ACCEPTED — the annual channel is pre-declared as an expected null

Not as a narrowing of `H10`. `H10` stays **verbatim as pre-declared on 2026-08-26**; a prior is added
beside it: on the physics of §1.3, annual heating EUI is **expected to stay null**, and the peak/`CF`
channel is where the effect can live. Recording the expectation **before** the run is what makes a
subsequent null uninteresting-but-honest rather than a surprise to be explained away.

🔴 **The pre-declared text of `H10` is not edited.** Editing a hypothesis after commissioning literature
that predicts its outcome is indistinguishable from moving the goalposts, whatever the intent.

### 2.5 🟢 ACCEPTED — Arm F is a biased lower bound, not a noisy estimate

Direction only, magnitude quarantined behind `[R2]`. `one_zone_per_floor` spatially averages
non-coincident gains, so it **under-predicts** heating demand and peak power. This upgrades our
"never pool" rule from a purity argument to a quantified one, and it makes Arm F **usable**: a stock
total from Arm F is a **lower bound**, which is a publishable statement, where "a number with unknown
error" is not.

### 2.6 🔴 REJECTED, with the reason recorded

| Rejected | Why |
|---|---|
| RDP simplification at `epsilon = 0.15 m` as a standard pre-extrusion step | The defect it fixes does not reproduce (§1.5). Changing every footprint's geometry to fix a dead bug is a basis change wearing a fix's clothes. |
| The 120-vertex IDD limit | Measured false against two IDDs (§1.4). |
| The saturation percentages, and "sample for `N = 20` to `50`" | Arithmetically wrong, and aimed at the flat part of the curve (§1.1). |
| Any numeric fallback-bias percentage | Rests on a self-refuting citation (§1.7). |
| The 5.09e-12 / 1e-8 causal pairing | Does not close on our own areas (§1.6). |
| `Iseri et al. (2026)` as evidence for our own design | `README` vetting step 1 (§1.7). |

---

## 3. Where these landed

| Document | What changed |
|---|---|
| `Step10_docs/4thJ_10_ubemRealStock.md` | §1.1 prior and functional form; §6.4 CRS restated; **§6.5 corrected — the 173-vertex refusal is stale**; §6.6 the paired design; work items 10.9 and 10.10 |
| `Step10_docs/4thJ_10_ubemRealStock_val.md` | `G10.20` paired design, `G10.21` `CF` and the `sqrt(N)` fit, `G10.22` Arm F bias direction declared, `G10.23` rotation-origin invariance; guard `V10.i` |
| `Step11_docs/4thJ_11_stockEndUseLoads.md` | Arm F totals are a **lower bound**, not an estimate; the arm label must survive aggregation |
| `OpenUBEM_debug_References.md` ch.1 | Correction appended: the 173-vertex entry is stale and its IDD diagnosis is false |

🟢 **Closed 2026-08-26 (evening), on the author's instruction.** `MVP_european_locations.md`
§EU-04 stated *"11 of 12 `EPLUS_COMPLETED` and 1 `EPLUS_FATAL`"*; on disk it is **12 of 12**, and the
cell now carries the falsification marker and the measurement. **All three stale copies are corrected.**

🔴 **In none of the three was the original claim deleted.** Each keeps the sentence, marks it
falsified in place, and appends what falsified it. A register that quietly loses its wrong entries
cannot teach anything, and the whole value of this round was learning that a written blocker outlives
the blockage. The MVP edit was made **inside the existing table cell on one line**, and the file's line
count was asserted unchanged at **2,557** afterwards, so the table cannot have been broken.
