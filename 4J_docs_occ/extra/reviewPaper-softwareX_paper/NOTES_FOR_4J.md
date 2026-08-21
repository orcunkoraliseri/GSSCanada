# What the SoftwareX review is worth to our pipeline

Rewritten 2026-08-21 after `RP01`…`RP06` came back and were vetted.
Vetting record: `deepResearch/VETTING_RP01-RP06.md` · Long form: `NOTES_FOR_4J_longform.md`, `REVIEW_annex_detailed_evidence.md`

Targets: `4thJ_00_HETUS_LLM_Pipeline.md` and `4thJ_00_HETUS_LLM_Pipeline_Overview.md`.

> 🔴 **Confidentiality.** The manuscript is under review. Nothing unpublished from it is reused
> here. Legitimately ours: its **public reference list**, and **methodological conclusions we
> reached ourselves**. We may not cite it, paraphrase it, or let it appear in any deep-research
> prompt. This file stays in the repo until the paper is published.

---

## 1. Headline: we are in better shape than I assumed

My first draft of this file said "nothing we run compares generated episode durations to real
ones". **That was wrong, and the correction matters.** The Overview's Tier 1 gate table already
specifies all of it:

- Dwell-time distribution, **Wasserstein-1 per activity, ≤ 10.0 min** (= one slot width)
- **Transitions per day ≤ 1.50** absolute error; transition-matrix **TVD ≤ 0.050**
- Diurnal marginal divergence as **JSD in bits**, not KL — so no `epsilon`, no unbounded values
- The shuffled-diary negative control, which **must PASS marginals and FAIL transitions and dwell**
- "each is additionally reported as a **sample-size-matched bootstrap**, where the synthetic-to-real
  divergence must not exceed the **real-to-real split-half divergence**"

That last line is the null-comparison discipline the external literature (`RP02`, Snoke et al.
2018) says is mandatory, and we pre-registered it before I went looking. The shuffled-diary control
is the independent-sampler test.

🔴 **So the action is not to add gates. It is to make sure the Step 6 battery, when built,
implements the Tier 1 table it inherits.** A grep of `tools/` shows no dwell-time or
transition-count checker exists yet — Steps 2/3/5 do not need one. Step 6 does, and it is the step
that will be read.

## 2. The one genuinely new check — hour-support constancy

The reviewed paper's real defect was a **diary-day boundary error**: a 04:00–04:00 diary binned on
a 00:00–24:00 wall clock, so four hours had zero data and the evening degraded to 6% coverage as
respondents entered their overnight episode. I found it by summing a column that had to total 100.

- 🔴 **We already ruled this correctly** — `D-S2-5` set origin 04:00 cyclic. Not our bug.
- 🔴 **But no gate of ours would have caught it if we had got it wrong.** Our checks are
  episode-based (durations sum to 1440, round-trip exact, code legality). A wall-clock-binned table
  passes every one of them, because the error is in *support per hour*, not in totals.

**Proposal — small, additive, one function.** Wherever we bin episodes into a time-of-day profile
(Step 6 scoring against Eurostat; Step 8/9 schedule assembly), assert that the **number of
contributing diaries is constant across all 24 hours** within a cell. Support that shrinks with the
clock is a boundary bug.

- Perturbation that must fell it: bin one fold on a 00:00 origin instead of 04:00.
- Cost: near zero — it runs on a table we already compute.
- **This is the item I would actually implement.**

## 3. Baselines — one gap, and it is small

`RP01` is unambiguous: the accepted comparator for a generative occupancy model is a **first-order
inhomogeneous Markov chain fitted to the same microdata**, not a deterministic schedule.

- Our Tier 4 nulls are the **raked-donor null** (built, 34 selftests green) and the pooled-average
  diary. Both are strong; the raked-donor null is stronger than the literature asks for.
- "Markov" appears in our pipeline docs only as the **Step 8 day-chaining** rule, never as a
  generation baseline.
- **Small addition worth considering:** a first-order inhomogeneous Markov chain fitted per fold on
  the N−1 training countries, reported alongside the raked-donor null. Cheap, it is the comparator
  a reviewer will name, and it makes the raked-donor null look deliberate rather than idiosyncratic.
- Paper-1 framing: our high-order Markov baseline at 0.691 vs 0.98 is the right *family*, but we
  never said which family. **Add a short "classical TUS lineage" paragraph to Related Work.**
  Write-up gap, not a method gap.

## 4. Corrections to claims we might otherwise have made

- **Secondary activities — already ruled, do not re-open.** I had filed this as an unclaimed HETUS
  advantage. It is not: §3B-bis records Spain at **12.2% of slots**, `act2_raw` carried through
  Steps 1–2 but deliberately **not serialised** (a field only one country can emit leaks country
  identity into LOCO), and `D-S9-1` then dropped `act2`. One sentence in the limitations, phrased
  as a design choice.
- **Reproducibility.** `RP05`: bit-exact local reproducibility needs `batch_size=1`,
  `torch.use_deterministic_algorithms(True)`, `CUBLAS_WORKSPACE_CONFIG=:4096:8` **and a fixed GPU
  architecture**. 🔴 Speed jobs can land on different nodes, so we cannot claim bit-reproducibility.
  The honest claim is "pinned base revision + pinned adapter + recorded seeds" — **and not even that
  until `FINDING 66` is fixed.** Do not write the reproducibility sentence first.
- **Fine-tuning does not settle the joint.** `RP03` is explicit that fine-tuning shifts conditional
  probabilities toward the empirical distribution but does not certify **joint** fidelity, and adds
  tail truncation. So "we fine-tune on real diaries, therefore this is not silicon sampling" is
  half true. Our own `FINDING 63` (1,512 employed Italian 13-year-olds off one donor diary) is that
  exact failure mode, caught in our own pipeline — worth saying, as evidence we look at joints.
- **`epsilon`-smoothed KL ratios are not effect sizes.** Moving `epsilon` from 1e-4 to 1e-15 takes a
  "superiority multiplier" from 461× to 1727×. Our Tier 1 uses JSD in bits, so we are clean —
  **but check we never divide two divergences anywhere in the write-up.**

## 5. Two things worth measuring, both cheap

- **`FINDING 65` / `D-S5-13` has external backing.** `RP05` B17: a decoding temperature chosen from
  a single-realisation sweep is not defensible; multiple seeds per grid point are needed before the
  curve separates from noise. Independent agreement with `G5.8`'s own registered clause. **Option
  (a) — finish the three folds, then replicate at a narrow window around the chosen T — is right.**
- **The counter-stereotypical probe has a name.** `RP03` calls it the *counter-stereotypical
  grounding test* and names the fallacy it defeats (*Face Validity Trap* / *Nominal Steering
  Fallacy*). We have a ready-made instance: `FINDING 48`/`FINDING 61` — Italy labels every
  11–14-year-old `unknown`, the UK `other_inactive`, Spain `student`. Under LOCO the model must
  produce a convention it never trained on. **One generation pass, and the strongest single
  experiment available to us.** Recorded, not proposed as work yet.

## 6. Day bases — `FINDING 53` is now a stronger statement

Verified directly from the BLS ATUS User's Guide (downloaded and quoted):

- Design: *"10 percent of the sample is allocated to each weekday, and 25 percent … to each weekend
  day"* (p. 13) — a deliberate 50/50 split.
- Correction: *"the weights (variable `TUFINLWGT`) were constructed so that each day of the week is
  correctly represented"* (p. 37).

ATUS oversamples weekends **on purpose** and repairs it **inside the person weight**. Our three
folds sit on three different day bases (uk 71.45/14.32/14.24, es 50/25/25, it 33/33/33), and only
the UK is calendar-representative.

🔴 So the framing improves: not "HETUS leaves this open" but **"ATUS repairs this in the weight;
our files do not, and we repaired it ourselves in `weight_dia_cal`."** That turns a limitation into
a methods contribution. Needs one verification pass against the Eurostat 2018 guidelines first.

## 7. Bibliography — verified, safe to cite

Every DOI resolved through CrossRef with matching **title, journal, volume, issue, pages and first
author** on 2026-08-21.

- Richardson et al. 2008 `10.1016/j.enbuild.2008.02.006`
- Widén & Wäckelgård 2010 `10.1016/j.apenergy.2009.11.006` — 🔴 ***Applied Energy*, not *Energy and
  Buildings*; a widely propagated wrong DOI points at an unrelated paper**
- Page et al. 2008 `10.1016/j.enbuild.2007.01.018` · Wilke et al. 2013 `10.1016/j.buildenv.2012.10.021`
- Aerts et al. 2014 `10.1016/j.buildenv.2014.01.021` · Flett & Kelly 2016 `10.1016/j.enbuild.2016.05.015`
- Mitra et al. 2020 `10.1016/j.enbuild.2019.109713` · Mitra et al. 2021 `10.1016/j.enbuild.2021.110791`
- Malekpour Koupaei et al. 2022 `10.1080/23744731.2022.2087536` — 🔴 **pp. 776–790, first author
  "Malekpour Koupaei"** (the response had both wrong)
- Chen et al. 2022 `10.1016/j.apenergy.2022.119890`
- **Reviews, the efficient entry points:** Osman & Ouf 2021 `10.1016/j.buildenv.2021.107785`;
  Vosoughkhosravi et al. 2023 `10.1016/j.enbuild.2023.113245`
- Snoke et al. 2018 `10.1111/rssa.12358` · Paninski 2003 `10.1162/089976603321780272`
- Argyle et al. 2023 `10.1017/pan.2023.2` · Bisbee et al. 2024 `10.1017/pan.2024.5`
- Our Paper 1, confirmed: Iseri et al. 2026, *Energy and Buildings* 357, 117155,
  `10.1016/j.enbuild.2026.117155`

**Do not cite:** Buttitta 2020 as `RP01` gave it — that DOI 404s and the title does not exist. The
real paper is `10.1016/j.enbuild.2019.109577`, *Energy and Buildings* 206, 109577.

**Do not repeat as fact:** `RP03`'s claim that *zero* BEM LLM-agent papers validate against measured
occupant data. Plausible and useful, but it is one search's absence — `FINDING 47` is the precedent.

---

## In order, if we act on this

1. **Hour-support constancy check** for Step 6 / Step 8 binning (§2). Small, new, nothing else covers it.
2. **Implement the Tier 1 dwell-time and transition gates** the Overview already specifies (§1).
3. **Fix `FINDING 66`** (seed the generation) before any reproducibility sentence is written (§4).
4. Add the **first-order Markov comparator** and the **lineage paragraph** (§3).
5. Everything else is write-up.
