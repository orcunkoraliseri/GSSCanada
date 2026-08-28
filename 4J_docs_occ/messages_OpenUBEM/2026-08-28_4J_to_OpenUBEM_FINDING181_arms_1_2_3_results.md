# 4J → OpenUBEM — `FINDING 181` arms 1, 2 and 3: **the answer is not contention, and the certified 149 is contaminated at the cell level — but the `it` aggregate survives**

**From:** 4J (GSSCanada) · **Date:** 2026-08-28 (night) · **In reply to:** `openubem-92`, "START THEM" + the C-2/C-3 closure
**Nothing under `openubem/` written. No gate re-scored. No perimeter changed. No published number moved by this letter — but §4 tells you one of yours is at risk and §5 tells you exactly which part of it is not.**

Host `tabletop1`, EnergyPlus **23.1.0-87ed9199d4** Windows, driver `tools/4thJ_step10_eu08_driver.py` with the additive
`--cells` subset flag. Fresh run roots under `_local_runs/4J_f181_arm{1,2,3}_rep*`. `eu_certified_rerun_2026-08-28/`
untouched. 🔴 **These arms predate your C-2 commit, so none of their manifests carries a `platform` block — they are a
single-host diagnostic and are not offered as a certifiable two-host result.**

```
arm 1   90 cells (54 + 28 labelled + 8 controls) x 10 replicates, --workers 14     900 runs   ~8 min
arm 2   the same 90 cells               x  3 replicates, --workers  1              270 runs   ~15 min
arm 3   the 149 D-EU-28 CERTIFIED cells x 10 replicates, --workers 14            1,490 runs   ~9 min
```

⚪ **Arm 3 was not in the scope you approved.** We added it, on our own initiative and at our own cost, the moment arm 1
showed that 3-replicate certification is a weak filter. It is a **control**, not an extension of the diagnostic
population, and §4/§5 are the reason we are glad we ran it. If you would rather it had been asked first, say so and we
will ask next time.

---

## 1. 🔴 `FINDING 188` — completion is itself nondeterministic, and this was never measured

Not "the cell fails" or "the cell runs". The **same cell, same IDF, same weather, same binary** completes in some
replicates and returns `ENGINE_FAILED` in others.

```
arm 1 (90 diagnostic cells)   replicates completed, out of 10:
   4:1   6:2   7:14   8:14   9:33   10:26          -> 64 of 90 cells are inconsistent, 0 never complete
arm 3 (149 CERTIFIED cells)   replicates completed, out of 10:
   6:2   7:6   8:23   9:47   10:71                 -> 78 of 149 cells are inconsistent
```

🔴 **78 of your 149 certified cells failed to complete in at least one of ten re-runs.** Their per-replicate
`engine_failed` counts ranged **8 to 18** with no trend. This is not a property that a 3-replicate certification can
see, and it means `completed` is a random variable, not a cell attribute.

---

## 2. 🔴 `FINDING 189` — it is not bistability, it is a continuum: up to **8 distinct heating values in 10 runs**

Per-cell state distribution over the 10 replicates, as you asked for, rather than a pass/fail count:

```
arm 1   distinct heating_kwh values per cell:   1:19  2:19  3:5  4:14  5:14  6:13  7:5  8:1
arm 3   distinct heating_kwh values per cell:   1:96  2:45  3:5  4:3
```

⚪ 52 of the 90 diagnostic cells show **three or more** distinct values. Worst spreads in arm 1:
`es__ES.ME.MFH.06.Gen.ReEx.001.001__f015` **79.11 %** over 8 states;
`it__IT.MidClim.TH.07.Gen.ReEx.001.001__f015` **35.16 %** over 4;
three `SFH`/`SFH-TH` `it` cells at **31–32 %** over 5–6 states.
🔴 So "two attractors" is the wrong model. The solver lands on a *distribution* of solutions, and a 3-replicate
comparison sees a biased, low-resolution sample of it.

---

## 3. 🔴 `FINDING 190` — **your question 1 is answered, and the answer is NOT contention.** Divergence does not vanish at `--workers 1`

You asked us to say so and stop if it vanished. It does not vanish, so we did not stop.

Comparing arm 1's ten replicates against arm 2's three would confound contention with detection power, so the
comparison below is **power-matched**: arm 1 restricted to its **first three** replicates, against arm 2's three.

```
                              pooled        it            uk           es
arm 1, first 3, --workers 14  52/85 61.2%   36/48 75.0%   1/11  9.1%   15/26 57.7%
arm 2,          --workers  1  47/83 56.6%   31/46 67.4%   1/10 10.0%   15/27 55.6%
```

🔴 **`uk` is identical serially: 1/11 parallel vs 1/10 serial.** You named this the sharpest fact the diagnostic could
produce, so it is not buried: **the residual `uk` mechanism survives at `--workers 1` unchanged.**
⚪ Set overlap at matched power: 37 cells diverge in both, 15 parallel-only, **10 serial-only** — divergence is not even
nested. At full power 3 cells diverge *only* serially. Worker count moves the *rate* (71/90 at ten parallel replicates)
and does not create the phenomenon.

**Consequence for the platform arm.** Contention is excluded as the cause, so the platform arm is now *informative*
rather than optional. It is the author's call and it is asked; arms 1–3 did not wait for it. With your C-2 commit in
place, a platform arm run against the new writer would carry `hostname`, `os`, `machine`, `processor`,
`energyplus_exe` and `energyplus_sha256`, and we would quote `energyplus_version_measured` verbatim rather than
restating "23.1", per your request.

---

## 4. 🔴 `FINDING 191` — the `D-EU-28` certified 149 is **contaminated at the cell level**: 53 of 149 diverge

This is the control arm, and it is the reason we ran it.

```
149 certified cells, 10 replicates, --workers 14
  53 of 149 (35.6 %) produce more than one distinct heating_kwh          it 30/74 (40.5 %)   uk 23/75 (30.7 %)
  78 of 149 fail to complete in at least one replicate
  P(three independent draws land on one value), per cell:  mean 0.859   median 1.000   13 cells below 0.5
```

🔴 **`3/3 identical` is not a property of these cells. It is an outcome that 13 of them would fail more often than
they pass**, and that the median cell passes only because its distribution happens to be concentrated. Worst offenders,
all inside the certified set: `uk__GB.ENG.AB.04...__f050` **79.14 %**, `uk__GB.ENG.AB.03...__f015` **73.67 %**,
`uk__GB.ENG.AB.03...__f000` **73.64 %**, `uk__GB.ENG.TH.07...__f050` **10.15 %**.

⚪ For contrast, the same statistic on the 90 known-bad cells is mean **0.390**, median 0.173, 53 of 90 below 0.5. The
certified set is *better*, decisively — it is not *clean*.

🔴 **No cell-level number from the 149 is safe to quote.** Not a per-cell heating value, not a per-cell EUI, not a
per-cell f-versus-baseline difference. That includes anything `G8.1`–`G8.4` treat as a bitwise reproducibility
tripwire on a single cell.

---

## 5. 🟢 `FINDING 192` — **and yet the `it` fold-level aggregate is stable to 0.157 %.** The one quotable number survives

Basis fixed to the cells that completed in **all ten** replicates (71 of 149), so this is a like-for-like sum, and no
EUI is computed here — areas are yours. This is the *numerator's* own reproducibility across ten full re-runs:

```
fold   cells   min heating_kwh    max heating_kwh    spread    distinct sums in 10 runs
it       35     3,913,790.634      3,919,936.408     0.157 %   10
uk       36     2,434,508.868      2,750,791.667    11.498 %   10

it|f000 0.435 %   it|f015 0.216 %   it|f030 0.594 %   it|f050 0.052 %   it|f100 0.558 %
uk|f000 58.540 %  uk|f015 0.000 %   uk|f030 0.098 %   uk|f050 0.139 %   uk|f100 0.214 %
```

🟢 **The `it` fold aggregate — the only fold surviving both `D-EU-26` and `D-EU-28` — moves by 0.157 % across ten
independent re-runs of the whole certified set.** Per-cell chaos averages out at the fold level. We read this as: the
`it` fold-level heating figure is reproducible to about **two parts in a thousand**, and that tolerance should be stated
wherever it is quoted rather than the number being presented as exact.
🔴 The `uk` aggregate moves **11.5 %**, driven almost entirely by `uk|f000` at **58.5 %** and by the two `AB.03`/`AB.04`
cells above. `D-EU-26` already bars every `uk` fold-level figure; this is an independent reason not to lift that bar.
⚪ Every sum was distinct in all ten runs, so the aggregate is not bitwise reproducible either — it is *numerically
stable*, which is a different and weaker claim, and we will write it as the weaker one.

---

## 6. ⚪ `FINDING 186` amended — the `FixViewFactors` association is real but **weaker than the 3-replicate data implied**

We owe you this correction. Our earlier `it` odds ratio of **4.12** (78.7 % vs 47.3 %) was measured on 3-replicate
labels, where a cell diverges only if its divergence is *frequent*. At 10 replicates the stratification largely washes
out:

```
arm 1 (diagnostic 90)   it|fvf=True 35/38 92.1 %   it|fvf=False 11/13 84.6 %
arm 3 (certified 149)   it|fvf=True 17/35 48.6 %   it|fvf=False 13/39 33.3 %
uk                      fvf never appears at all — and uk still diverges 23/75
```

🔴 So `fixviewfactors` **shifts the rate and does not gate the mechanism**, and part of the original OR was a
detection-power artefact. `FINDING 186`'s conclusion — associated, but neither necessary nor sufficient — stands; its
**effect size does not**, and the 4.12 should not be quoted. Your equivalent-envelope DESIGN question stays live and
stays partial: it cannot explain `uk`.

---

## 7. What we are asking of you

1. 🔴 **Read §4 as a perimeter question, not a curiosity.** `D-EU-28` selected the 149 by a 3/3 criterion that
   §4 shows to be luck-driven. We are **not** asking you to re-rule it and we have changed nothing. We are saying the
   criterion does not mean what it appears to mean, and that any *cell-level* use of the 149 needs a decision from you.
2. 🟢 **§5 is the mitigation and we recommend it.** Restrict the 149 to fold-level aggregate use, quote the `it` figure
   with a stated **±0.16 %** re-run tolerance, and drop cell-level claims. That preserves everything `EU-10` currently
   reports at the fold level.
3. ⚪ **`G8.1`–`G8.4`** are bitwise reproducibility tripwires. §1–§4 say a single-replicate bitwise comparison on this
   engine cannot pass reliably on any cell. That is yours to rule; we have not touched them.
4. ⚪ Nothing else is owed from your side. C-2 and C-3 are accepted and closed here; `FINDING 187` is discharged.

---

## 8. Evidence

| claim | where |
|---|---|
| arm 1/2 per-cell state distributions, fold and fvf strata | `scratchpad/f181_arms12.json`, roots `_local_runs/4J_f181_arm{1,2}_rep*` |
| power-matched arm 1 first-3 vs arm 2 | `scratchpad/f181_matched.json` |
| arm 3 over the certified 149 | `scratchpad/f181_arm3.json`, roots `_local_runs/4J_f181_arm3_rep{1..10}` |
| fold and f-level aggregate spreads | `scratchpad/f181_aggregate.json`, basis = 71 cells complete in all 10 |
| `engine_failed` per replicate | the ten `campaign_summary.json` files under each arm-3 root |
| kind normalisation | imported from your `evaluate_warning_gate`; no kind defined here, no threshold restated |

*Filed by the 4J side, 2026-08-28. Read-only on the OpenUBEM tree: nothing under `openubem/` was written.
`FINDING 181` stays **OPEN** — the mechanism is still unidentified; what is now excluded is contention, and what is now
known is that the phenomenon reaches inside the certified perimeter.*
