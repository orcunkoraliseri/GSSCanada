# What the SoftwareX review is worth to 4J

Written 2026-08-21, alongside `REVIEW_SOFTX-D-26-00798R1.md`.

> 🔴 **Confidentiality boundary, stated once and enforced throughout this file.** The manuscript is
> under confidential peer review. **Nothing unpublished from it is reused here.** Two things are
> legitimately ours to take:
>
> 1. **Its reference list**, which is public bibliography. Following a citation to a published paper
>    and reading that paper is normal scholarship.
> 2. **Methodological conclusions we reach ourselves.** Where reading someone's work made us look at
>    our own and find something, the finding is ours; the trigger is not a quotable source.
>
> What we may **not** do: cite it, paraphrase its unpublished text, adopt its design, or let its
> existence appear in any deep-research prompt. `deepResearch/README.md` states the same rule, and
> the six `P` prompts are all written as standalone questions for that reason. This file stays inside
> the repository until the paper is published, at which point everything here can be cited normally.

---

## 1. The one that lands hardest on us

🔴 **The circularity trap is not somebody else's problem — we should check our own gates for it.**

The pattern: fit a distribution `P` from microdata, sample from `P`, then validate by measuring the
divergence between `P` and the samples. That test cannot fail. Its expected value is set by the
number of draws, not by the quality of the grounding.

We have a standing rule about exactly this — `feedback_gates_must_be_seen_failing`, and the coverage
clause in every battery. But the rule catches a gate that *never failed*; it does not by itself catch
a gate that **cannot** fail because its reference and its subject are the same object. Those are
different defects and the second is harder to see.

**Action, and it is cheap:** walk the Step 5 and Step 6 gate lists and ask of each one — *what
exactly is the reference, and is it derived from the thing being scored?* Two candidates to look at
first:

* `G5.1` (IPF convergence, 0.0120 / 0.0112 / 0.0099 pp). The fitted population is checked against the
  marginals it was fitted to. That is a **solver-correctness** check, and a legitimate one, but it
  is not evidence the population is right. It should be named as convergence, never as fidelity. I
  believe our documents already do this; worth confirming rather than assuming.
* `G5.5` (100,000 prefixes byte-identical to the encoder). Same class — an encoder checked against
  itself. Correctly framed as a consistency check, and that is what it is called. Fine.

The one that would genuinely matter is `G6.1`. Its raked-donor null is built by raking the **real
N-1 diary pool onto the fitted population**, and the model is prompted from that same fitted
population. That was a deliberate choice (`score_margin` Guard 1) and it is the right one — but it
means the null and the model share a reference, and the paper needs to say why that does not make
the comparison circular. **Owed: one paragraph in the Step 6 write-up.**

## 2. The duration problem, and why it is a warning for us

A generator that samples each timestep independently from the correct hour-marginal will match every
marginal and produce completely wrong episode lengths. A divergence computed on marginals is blind
to it by construction, because any temporal reordering leaves marginals untouched.

We do not have this defect — we generate whole diaries autoregressively, and our episodes carry
explicit durations. **But we have not proved we do not have it**, and the statistic that would prove
it is not currently in any gate:

* `G4.7` counts terminated generations. `G4.15` is new. Neither looks at **episode length**.
* We know from the item 5.4 sweep that only **5–13 %** of generated diaries sum to exactly 1440
  minutes, which is a budget failure, not a duration-distribution failure — a different thing, and
  the fact that we can distinguish them is the point.
* 🔴 **Nothing we run compares the generated episode-duration distribution to the real one.** The
  corpus measurement is on disk (2,024,068 episodes, all summing to 1440), so the reference exists
  and costs nothing to compute.

**Proposal, not applied:** add a duration statistic to the Step 6 battery — mean episodes per diary,
and a KS or Wasserstein distance on the episode-length distribution, generated versus real, per fold.
It is additive, it needs no re-run of anything upstream, and it is the single most likely place a
reviewer will push. `P02` Item 3 is written to find out what the standard statistic is before we
invent one.

## 3. Literature we are under-citing, and it is our own field

The searches behind review Point 3 turned up a lineage we barely cite: **twenty years of stochastic
occupancy and activity models built from national time-use surveys** — Richardson (UK), Widén and
Wäckelgård (Sweden), Wilke (France), Aerts (Belgium), Flett and Kelly (UK), and on the US side a
distinct ATUS branch including Mitra's multi-year typical schedules, LBNL's typical US residential
occupancy profiles, and ATUS-based inhomogeneous-Markov stochastic schedules.

Two review articles appear to exist and are the highest-value single citations if confirmed:

* a **comprehensive review of time-use surveys in modelling occupant presence and behaviour**
  (~2021), and
* a **review of ATUS applications in modelling energy-related occupant–building interactions**
  (*Energy and Buildings*, ~2023).

🔴 **Why this matters to us specifically.** Our own baseline in Paper 1 was a high-order Markov chain
at 0.691 accuracy against 0.98 for the deep models. If first-order Markov TUS-occupancy models are
the field's accepted comparator, then our baseline is the right family — good. But we have never
said so, never cited the lineage it comes from, and never explained why our Markov baseline is a
fair implementation of it rather than a weak one. A reviewer who knows this literature will ask, and
"0.691 versus 0.98" invites the question. `P01` Item 3 asks precisely what the accepted baseline is.

This is a **write-up gap, not a method gap**, which is the good kind.

## 4. Silicon sampling — our reviewers are going to raise it

The standard validation move in persona-conditioned LLM work is *different personas behave
differently, in the expected direction, therefore the demographic conditioning works.* That
inference is weaker than it looks: a language model already holds a strong prior about what a
68-year-old retiree does, so the between-persona difference may show only that the stereotype is
intact, not that the pipeline is wired to real microdata.

**Our exposure.** We fine-tune on real diaries, which is a materially stronger position than
prompting a hosted model with a persona description — but we have never tested whether our
conditioning tracks the **grounding data** or the **model's prior**. And we already have a finding
that sharpens the worry: `FINDING 63`, where a repair fixed a marginal and left the joint
distribution wrong (1,512 employed Italian 13-year-olds off one donor diary). That is exactly the
marginal-versus-joint failure mode the silicon-sampling critique describes, arrived at
independently, in our own pipeline, by reading an output rather than by running a check.

**The decisive experiment, and we could actually run it:** condition on a stratum whose real
behaviour is **counter-stereotypical** and see whether the generator follows the data or the prior.
We have three countries whose conventions differ deterministically (`FINDING 48`, `FINDING 61`) —
Italy labels every 11–14-year-old `unknown`, the UK labels them `other_inactive`, Spain `student`.
That is a ready-made probe: the model must produce a country's convention it was never trained on
under LOCO, and the failure direction tells us whether it is following the prefix or its prior.

Not proposed as work yet. Recorded because it is the strongest experiment available to us and it
costs one generation pass. `P03` Item 2 asks whether anyone has already framed this test.

## 5. Reproducibility — a claim we can make and currently do not

Greedy decoding at `T = 0` on a **hosted API** is not reproducible. The dominant cause is
batch-size-dependent reduction kernels — a request served under a different dynamic batch takes a
different reduction order — compounded by floating-point non-associativity and shape-dependent
kernel selection. Provider-side model updates behind a stable alias make it worse over time.

**We are in the other position and have not said so.** We fine-tune an open-weight base
(`allenai/OLMo-2-0425-1B` at a pinned revision `a1847dff3500`) plus a LoRA adapter, serve it
ourselves, and can pin the whole stack. That is a real methodological advantage over the
hosted-agent pattern, and it belongs in the paper as one sentence in the reproducibility statement.

🔴 **But we must not overclaim it, and right now we would.** `FINDING 66`, found today: the item 5.4
sweep never calls `torch.manual_seed` anywhere, so its sampled generations are not reproducible
either — and the artefact writes `seed: 42` beside the curve, which scopes only the prompt draw. We
would be claiming an advantage we have not yet earned in our own code. Fix `FINDING 66` first, then
claim it. `P05` Item 4 asks how strong the claim can legitimately be.

## 6. Smaller things worth keeping

* **Day bases again.** ATUS deliberately oversamples weekend diary days and corrects it in the person
  weight. HETUS may leave that to the analyst. This is `FINDING 53` in another survey's clothes — our
  three countries sit on three different day bases (uk 71.45/14.32/14.24, es 50/25/25, it 33/33/33)
  and only the UK is calendar-representative. If ATUS solves in the weight what HETUS leaves open,
  that is worth knowing and worth stating as a limitation. `P06` Item 4 asks it directly.
* **Multi-year pooling.** Pooling two survey years without rescaling the annual weights double-counts
  the population. We should check whether anything in our own pipeline pools waves. `P06` Item 3.
* **Secondary activities.** ATUS records one primary activity per episode; HETUS may record
  secondary activity more completely. If it does, that is an advantage of our corpus we currently do
  not claim. `P06` Item 5.
* **Naming a validation tier honestly.** Calling a tier "fidelity" when it demonstrates "sampler
  correctness" is the kind of drift that costs a paper credibility for no gain. Worth a pass over our
  own gate names before submission — several of ours are named for what we hope they show rather
  than what they measure.
* **Artefact hygiene as a reviewable property.** All three of the reviewed paper's artefact links
  resolved, versions agreed across GitHub / PyPI / Zenodo, and the tests ran offline against a mock
  provider. That took ten minutes to verify and materially raised my assessment. When 4J ships, the
  same ten minutes should return the same answer for us.

## 7. Bibliography to chase

Public, from the reviewed paper's reference list plus the searches around it. To be resolved and read
independently; **none of these is cited to the manuscript.**

* Hong, Taylor-Lange, D'Oca, Yan, Corgnati (2016), *Advances in research and applications of
  energy-related occupant behavior in buildings*, Energy and Buildings 116, 694–702.
* Yan, O'Brien, Hong, Feng, Gunay, Tahmasebi, Mahdavi (2015), *Occupant behavior modeling for building
  performance simulation*, Energy and Buildings 107, 264–278.
* Park et al. (2023), *Generative agents: interactive simulacra of human behavior*, UIST.
  `10.1145/3586183.3606763` — the memory/reflection architecture, and the origin of the self-assigned
  importance score whose circularity is a known weakness.
* Arslan and Munawar (2026), *Large language models in building energy applications: a survey*,
  Energy & Buildings 352, 116800. The obvious entry point to the LLM-in-BEM literature.
* Fisher, Gershuny, Altintas, Gauthier — Multinational Time Use Study user's guide. Relevant to our
  HETUS-versus-MTUS positioning.
* Eurostat (2019), *Harmonised European Time Use Surveys — 2018 guidelines*, `10.2785/926903`. We
  should be citing the guidelines document by DOI and may not be.
* The TUS-occupancy lineage in §3 above — Richardson, Widén and Wäckelgård, Wilke, Aerts, Flett and
  Kelly, Mitra — plus the two review articles. **`P01` exists to confirm every one of these; do not
  cite any of them until it comes back and is vetted.**
* Allcott (2011), *Social norms and energy conservation*, Journal of Public Economics 95(9–10),
  1082–1095. The peer-comparison field evidence. `P04` confirms the numbers.

---
---

# Round 2 — after RP01…RP06 came back and were vetted

Added 2026-08-21. Vetting record: `deepResearch/VETTING_RP01-RP06.md`. All six responses
returned; no fabricated reference; four defects recorded there. **Nothing below rests on a
response alone** — each item names what was independently verified.

The confidentiality boundary at the top of this file still governs everything here.

## 8. The finding that should change how we build gates

The reviewed manuscript's central defect turned out to be a **diary-day boundary error**: its
ATUS extraction binned a 04:00–04:00 diary onto a 00:00–24:00 wall clock, so four hours of the
day had zero data and the evening hours degraded to single-digit coverage as respondents entered
their overnight sleep episode. I found it by summing a column that had to total 100 and did not.

🔴 **We ruled the same hazard correctly and for the same reason** — `D-S2-5` set origin 04:00
cyclic — so this is not a defect we share. The uncomfortable question is the other one:

> **If we had got it wrong, which of our gates would have failed?**

I do not think any of them would have. Our batteries check that episodes sum to 1440 and that
round-trips are exact — both of which a wall-clock-binned table would pass, because the error is
in *coverage per hour*, not in the totals. What catches it is a **marginal-completeness check**:
for every (fold, day type, hour), does the activity distribution sum to 1 over a *constant*
denominator, and is that denominator the full stratum?

**Proposal, additive, cheap:** a gate that asserts, for every conditioning cell we ever build a
table on, that the number of contributing diaries is equal across hours. A cell whose support
shrinks with the clock is a boundary bug. This would have caught the reviewed paper's defect in
one line, and it is the kind of check `feedback_gates_must_be_seen_failing` is about — it fails
loudly under a deliberately mis-wrapped day.

This is the highest-value item in this file.

## 9. The duration gate is now mandatory, and I know what to compute

Section 2 above said we had no episode-length gate and that `P02` would tell us the standard
statistic. It came back. **Verified: every DOI below resolved through CrossRef with matching
title, journal, volume, issue, pages and first author.**

The field's accepted duration battery is:

* **Episode-length distribution distance** — 1-D Wasserstein `W1` on bout lengths per activity
  (physical units: minutes, so the result reads as "our sleep bouts are X minutes short").
* **Mean daily transition count** `N_trans`, generated vs real.
* **Transition-matrix TVD**, generated vs real first-order kernel.
* Optionally Kaplan–Meier survival curves per state.

Prior art for each: Wilke et al. (2013) reported duration survival curves and hazard functions;
Flett & Kelly (2016) reported dwell-time distributions and daily transition counts; Page et al.
(2008) introduced the mobility parameter precisely because marginal presence cannot constrain
persistence.

🔴 **The reference already exists on disk**: 2,024,068 episodes, all summing to 1440. Computing
`W1` on bout lengths and `N_trans` costs nothing. **Add to the Step 6 battery.** This is now the
single most likely thing a reviewer will ask us for, and we would currently have no answer.

Bounded metrics, while we are here: `P02` is emphatic that epsilon-smoothed KL ratios are not
effect sizes (changing epsilon from 1e-4 to 1e-15 moves a "superiority multiplier" from 461x to
1727x with no change in model behaviour). Use JSD or TVD for nominal distributions. **Check
whether any of our own reported divergences carry an epsilon and, if so, whether we ever divide
two of them.**

## 10. The baseline question is settled, and it is not in our favour by default

`P01` answers Item 3 without hedging: comparing a 2026 generative occupancy model only against a
deterministic schedule is **not acceptable**; the mandatory comparator is a **first-order
inhomogeneous Markov chain fitted to the same survey microdata**, evaluated on duration
distributions and transition frequencies as well as marginals.

Our Paper-1 baseline was a high-order Markov chain at 0.691 accuracy against 0.98 — so we are in
the right family. What we have never done is **say so**, or cite the lineage it comes from, or
explain why our implementation is a fair one rather than a weak one. `0.691 vs 0.98` invites
exactly that question.

**Write-up gap, not a method gap.** Add a "classical TUS lineage" paragraph to Related Work.

## 11. Silicon sampling — the probe I proposed has a name and a literature

Section 4 above proposed conditioning on a counter-stereotypical stratum to see whether the
generator follows the data or the model's prior. `P03` confirms this is a recognised design — the
**"counter-stereotypical grounding test"** — and that the inference we were worried about has
names: the **Face Validity Trap** / **Nominal Steering Fallacy**. So we are not inventing an
evaluation; we would be applying one.

Verified anchors (DOIs re-resolved): Argyle et al. (2023) `10.1017/pan.2023.2` for the original
positive result; Bisbee et al. (2024) `10.1017/pan.2024.5` for variance collapse and the failure
to reproduce **joint** distributions and regression coefficients; Cheng, Piccardi & Yang (2023)
`10.18653/v1/2023.emnlp-main.669` for caricature.

Two things land on us directly:

* **Bisbee's joint-distribution failure is `FINDING 63` in someone else's vocabulary** — we fixed
  a marginal and left the joint wrong (1,512 employed Italian 13-year-olds off one donor diary).
  We found it independently, in our own pipeline, by reading an output. That is worth one
  sentence in the paper: it is evidence we look at joints, not just marginals.
* `P03` is explicit that fine-tuning **shifts** conditional transition probabilities toward the
  empirical distribution but does **not** automatically fix higher-order joint fidelity, and adds
  tail truncation and memorisation risk. 🔴 So our "we fine-tune on real diaries, therefore we are
  not doing silicon sampling" line is **half true and must not be written as if it were whole**.
  The honest version: fine-tuning removes prior dominance on the conditioned attributes; it does
  not certify the joint. Our LOCO design plus `FINDING 48` / `FINDING 61` gives us the
  counter-stereotypical probe to test it — one generation pass.

Memorisation: a 144-slot daily sequence is a quasi-identifier. We already know weights cannot be
released; a prefix-probing memorisation check would let us say *why* in measurable terms.

## 12. `FINDING 65` / `D-S5-13` has external support

`P05` Item 5 (B17): sweeping a decoding temperature requires **multiple seeds per grid point**
before the curve is separable from noise, and a temperature chosen from a single-realisation
sweep is not a defensible choice.

That is independent agreement with `G5.8`'s own registered sensitivity clause and with
`FINDING 65`. **`D-S5-13` option (a) — finish the three folds, then replicate at a narrow window
around the chosen T — is the right call and now has a citation behind it.**

`P05` also confirms `FINDING 66` matters and gives the fix precisely: bit-exact local
reproducibility needs `batch_size=1`, `torch.use_deterministic_algorithms(True)`,
`CUBLAS_WORKSPACE_CONFIG=:4096:8`, **and a fixed GPU architecture**. 🔴 That last one is a problem
for us: Speed jobs can land on different physical nodes between runs. So the honest claim for our
paper is *"pinned base revision + pinned adapter + recorded seeds"*, **not** "bit-reproducible" —
and we cannot claim even that until `FINDING 66` is fixed. Do not write the reproducibility
sentence before the seeding is in.

## 13. Day bases — ATUS solves in the weight what our HETUS files do not

Verified against the BLS ATUS User's Guide directly (downloaded, searched, quoted):

* Design: *"10 percent of the sample is allocated to each weekday, and 25 percent … to each
  weekend day"* (p. 13) — a deliberate 50/50 weekday/weekend split.
* Correction: *"the weights (variable `TUFINLWGT`) were constructed so that each day of the week
  is correctly represented"* (p. 37).

So ATUS oversamples weekends **on purpose** and repairs it **inside the person weight**. Our three
HETUS folds sit on three different day bases (uk 71.45/14.32/14.24, es 50/25/25, it 33/33/33) and
only the UK is calendar-representative — `FINDING 53`.

🔴 **This makes `FINDING 53` a stronger statement than we had it.** `P06` reports that HETUS is
*supposed* to supply a diary weight handling the 5:2 adjustment. Our own measurement says two of
our three countries do not come out calendar-representative. Either the harmonised files deviate
from the Eurostat guideline, or the guideline leaves it to the analyst. Either way the correct
framing is no longer "HETUS leaves this open" — it is **"ATUS repairs this in the weight; our
files do not, and we repaired it ourselves in `weight_dia_cal`."** That is a defensible, citable
methods sentence and it turns a limitation into a contribution. It needs one verification pass
against the Eurostat 2018 guidelines before we write it.

Weight pooling, corrected (the response got this wrong — see the vetting record): the real BLS
rule is about **weight-variable comparability across years**, not a divide-by-K. Applies to us
only if we ever pool HETUS waves; worth checking that we do not.

## 14. Secondary activities — a claim we may be able to make, unverified

`P06` claims HETUS carries a full second activity column across all 3-digit codes while ATUS
records secondary activity only for care of children under 13 (the ATUS half is **verified
verbatim** from the User's Guide p. 57: *"With the exception of the care of children under age 13,
information on secondary activities is not collected in ATUS."* The HETUS half is **not
verified**).

If true, that is an advantage of our corpus we currently do not claim. 🔴 Check our own
`harmonised.parquet` for a secondary-activity column before writing anything. If we dropped it in
harmonisation, that is a limitation to declare, not an advantage to claim.

## 15. Honest tier naming — a worked example

The reviewed paper calls a tier "fidelity" when it demonstrates sampler correctness, and I could
show with a bootstrap that the tier cannot fail. **Do a naming pass over our own gate list before
submission.** The specific question for each: *what is the reference, and is it derived from the
thing being scored?* Section 1 above lists the candidates; `G6.1` is the one that needs a written
justification rather than a rename.

## 16. Bibliography — status after vetting

Everything in Section 7 above stands, with these changes:

**Now verified and safe to cite** (CrossRef exact on title / journal / volume / issue / pages /
first author):
Richardson et al. 2008 `10.1016/j.enbuild.2008.02.006` · Widén & Wäckelgård 2010
`10.1016/j.apenergy.2009.11.006` (**note: *Applied Energy*, not *Energy and Buildings* — a widely
propagated wrong DOI points at an unrelated paper**) · Page et al. 2008
`10.1016/j.enbuild.2007.01.018` · Wilke et al. 2013 `10.1016/j.buildenv.2012.10.021` · Aerts et
al. 2014 `10.1016/j.buildenv.2014.01.021` · Flett & Kelly 2016 `10.1016/j.enbuild.2016.05.015` ·
Mitra et al. 2020 `10.1016/j.enbuild.2019.109713` · Mitra et al. 2021
`10.1016/j.enbuild.2021.110791` · Malekpour Koupaei et al. 2022 `10.1080/23744731.2022.2087536`
(**pp. 776–790, first author Malekpour Koupaei**) · Chen et al. 2022
`10.1016/j.apenergy.2022.119890` · Snoke et al. 2018 `10.1111/rssa.12358` · Paninski 2003
`10.1162/089976603321780272` · Allcott 2011 `10.1016/j.jpubeco.2011.03.003`.

**The two review articles exist and are the efficient entry points**: Osman & Ouf 2021,
*Building and Environment* 196, 107785, `10.1016/j.buildenv.2021.107785`; Vosoughkhosravi, Jafari
& Zhu 2023, *Energy and Buildings* 294, 113245, `10.1016/j.enbuild.2023.113245`.

**Do not cite**: Buttitta 2020 as given in RP01 — that DOI 404s and the title does not exist. The
real paper is `10.1016/j.enbuild.2019.109577`, *Energy and Buildings* 206, 109577.

**Our own Paper 1 confirmed**: Iseri et al. 2026, *Energy and Buildings* 357, 117155,
`10.1016/j.enbuild.2026.117155`.

**Do not cite until we check it ourselves**: any claim that no BEM LLM-agent paper validates
against measured occupant data (`P03` B12). Plausible, useful, unproven — `FINDING 47` is the
precedent for what happens when we trust a confident absence.
