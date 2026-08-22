# `D-S6-11` — three design choices `G6.7` cannot be built without, and the one that failed first

**Date:** 2026-08-22 (night)
**Raised by:** building the fictional-country control — `tools/4thJ_step6_g67_prefixes.py` and
`tools/4thJ_step6_g67_score.py`.
**Status:** OPEN. Built, prefixes generated for `es`, **nothing generated on the GPU yet**.
`prereg.md` untouched, md5 `e4243e07cdd80c9c846b91f40e3e8c45`.

`G6.7` answers *"it read about the country on the web"*. The spec gives the quantity — generate under
a fictional country token with perturbed marginals, require **slope ≥ 0.8** and no national-stereotype
residual — and gives none of the arithmetic. Three choices had to be made to compute it at all.

🟢 The token guard works and is asserted at start-up: `enc_country("x_zz")` **raises** without the
keyword and returns the token with it, so a synthetic prefix leaking into any production path is a
hard error, not a silent row.

---

## Item 1 — what is perturbed. 🔴 `FINDING 90`: the first design had no amplitude.

**First build:** interpolate the age mix between the fold's own distribution and that distribution
**reversed** across the age ordering. It looked like the largest move available. Spain's age mix is
very nearly symmetric, so it was not:

| | `t = 0` | `t = 1` | movement |
|---|---|---|---|
| expected `AC0` | 683.6 | 682.8 | **0.8 min/day** |
| expected `AC1_TR` | 180.4 | 179.8 | 0.6 min/day |
| expected `AC2` | 23.2 | 22.7 | 0.5 min/day |

A slope fitted across 0.8 min/day of predictor movement is noise wearing a threshold's clothes. **It
would have passed or failed at random and neither verdict would have meant anything.**

**Implemented instead:** an exponential tilt, `share(b) ∝ base(b) · exp(λ · rank(b))`, λ swept from
**−0.6 to +0.6** over five levels. Monotone in λ, every observed band keeps non-zero mass, nothing is
extrapolated outside the support, and the amplitude is a parameter rather than an accident:

| λ | mean age rank | expected `AC0` | expected `AC2` | expected `AC1_TR` |
|---|---|---|---|---|
| −0.60 | 1.77 | 693.2 | **84.8** | 153.3 |
| −0.30 | 2.53 | 689.9 | 51.0 | 173.8 |
| +0.00 | 3.57 | 690.6 | 26.2 | 167.8 |
| +0.30 | 4.69 | 698.0 | 10.4 | 141.4 |
| +0.60 | 5.59 | **714.1** | **5.5** | 122.7 |

🟢 **A `V6.g`-style AMPLITUDE GUARD is now in the builder and it is not advisory:** `G6.7` **refuses
to be scored** unless the widest expected range across aggregates is ≥ 30 min/day. The `es` build
measures **79.3**. The first design would have been refused.

**Confirm the axis or name another.** Age was chosen because its effect on the level-1 budget is the
largest and least ambiguous — employment collapses and `AC0` rises as the mix ages — and a
perturbation a model could follow by accident is not a test.

---

## Item 2 — how a drawn prefix is PRICED, when the donors have never seen its stratum

The expected budget at each level is `Σ share(s) · budget_donor(s)`, over the **two donor countries
only**; using the held-out country's own diaries would leak the answer into the yardstick.

**First build dropped any prefix the donors could not price at its full six-field stratum — 24,624 of
100,000, 24.6 %.** That is not a dropped row, it is a silently changed marginal, and it is
country-correlated by construction.

**Implemented instead:** a fixed backoff ladder, and every level records how many draws were priced at
which rung.

| rung | key | cells (fold `es`) |
|---|---|---|
| `full` | age, sex, hh_type, econ, day_type | 774 |
| `no_econ` | age, sex, hh_type, day_type | 259 |
| `no_econ_no_hh` | age, sex, day_type | 48 |
| `age_day` | age, day_type | 24 |
| `age` | age | 8 |

At λ = 0 **76 %** of draws price at the full key; at λ = +0.60, 65 %. Nothing is dropped.

| | option | consequence |
|---|---|---|
| **(a)** | 🟢 **Recommended. The ladder, with the rung mix reported per level.** | No prefix leaves the population, the marginal the model is conditioned on is the marginal the expectation is computed from, and the coarsening is visible |
| **(b)** | Drop unpriced prefixes. | 24.6 % of Spain, and the drop rate itself moves with λ (it would be a confound with the perturbation) |
| **(c)** | Price everything at a coarse key from the start. | Throws away the 76 % that *are* fully observed |

---

## Item 3 — what clause 2 means when NO real country's token was used

The spec: *"the residual against any real country's profile must not be the smallest for a country
whose token was not used."* Under a fictional token, **no** real country's token was used, so the
literal sentence has no referent.

**Implemented reading:** at every level,

    MAE(generated, EXPECTED at this level)  <  MAE(generated, country c's own overall profile)  ∀ c

If a national profile explains the output better than the conditioning vector the model was actually
given, the model is reciting a country. Each country's profile is built from the **corpus**, weighted
— not from Eurostat, whose only all-ages row is `TOTAL` and whose population base `D-S6-8` item 2
just ruled out of every verdict.

🔴 This is an operationalisation of a sentence, not the sentence. It is the item most worth
overruling.

---

## 🟢 The battery exists and names the two defects the gate is for

| perturbation | what it injects | should fell |
|---|---|---|
| `null` | nothing | nothing |
| `ignore_prefix` | the same mean day at every level | clause 1 — slope collapses to 0 |
| `recite_country` | a donor country's national profile at every level | clauses 1 **and** 2 |
| `flatten` | follows the vector at **half** strength | clause 1 at the band, not at the sign — the 0.8 threshold itself |

`flatten` is the one that tests the number rather than the direction: a model that tracks the
perturbation perfectly in sign but at half amplitude scores ≈ 0.5 and must fail.

🔴 **Nothing has been run on the GPU.** The five `es` level batches are not generated: the three
privacy-audit jobs are occupying `2g.20gb` slices of the same physical GPU the Leg-5 80 GB instance
needs, and adding five more generation jobs would extend that block. Leg 5 is the critical path and
`G6.7`'s rehearsal waits behind it.

---

## Answer box

> **`D-S6-11` Item 1 (Perturbation Axis & Amplitude Guard):** (confirm / name another)  → **CONFIRM — Exponential age-rank tilt $\lambda \in [-0.6, +0.6]$ across 5 levels with $\ge 30$ min/day amplitude guard.**
>
> **`D-S6-11` Item 2 (Prefix Pricing):** (a) backoff ladder / (b) drop unpriced / (c) coarse key everywhere  → **(a) Fixed backoff ladder (`full` $\to$ `no_econ` $\to$ `no_econ_no_hh` $\to$ `age_day` $\to$ `age`) with rung distribution reported per level.**
>
> **`D-S6-11` Item 3 (Clause 2 Interpretation):** (confirm / replace)  → **CONFIRM — Conditioning vector must explain output better than any donor country's weighted empirical profile at every level.**

---

## Author's Rulings & Directives (2026-08-22)

| # | Item / Decision | Ruled Option | Summary of Decision | Action Required |
|---|---|---|---|---|
| **1** | Perturbation Axis & Amplitude | 🟢 **Confirmed** | **Exponential age-rank tilt** $\text{share}(b) \propto \text{base}(b) \cdot \exp(\lambda \cdot \text{rank}(b))$ over 5 levels with **Amplitude Guard $\ge 30$ min/day** (measured Spanish spread: 79.3 min/day). | Confirmed in `tools/4thJ_step6_g67_prefixes.py`; guarantees meaningful predictor dynamic range. |
| **2** | Prefix Pricing Mechanism | 🟢 **Option (a)** | **Fixed backoff ladder** with rung mix reported per level; zero prefixes dropped ($0\%$ loss of marginal support). | Confirmed in `tools/4thJ_step6_g67_score.py`; preserves full sample support while tracking coarsening transparency. |
| **3** | Clause 2 Anti-Stereotyping Operationalisation | 🟢 **Confirmed** | $\text{MAE}(\text{gen}, \text{EXP}(\lambda)) < \text{MAE}(\text{gen}, \text{profile}_c) \; \forall c$ using **weighted corpus profiles**. | Confirmed; ensures model conditions on the synthetic vector rather than reciting a memorised national template. |

---

### Detailed Rulings and Directives

#### 1. Item 1 (Perturbation Axis & Amplitude Guard) — Confirmed
* **Choice**: Confirm the exponential age-rank tilt along $\lambda \in \{-0.6, -0.3, 0.0, +0.3, +0.6\}$ and enforce the $\ge 30$ min/day amplitude guard.
* **Scientific Rationale**:
  - The initial design of reversing the age distribution produced only $0.8$ min/day of variation due to near-symmetric population demographics in Spain, which would have rendered slope estimation meaningless.
  - The exponential tilt produces a robust $79.3$ min/day spread across aggregates while maintaining full support within legitimate age bands.
  - The non-advisory amplitude guard ($\ge 30$ min/day) ensures that test validity is enforced programmatically before scoring.

#### 2. Item 2 (Prefix Pricing Backoff Ladder) — Ruled: Option (a)
* **Choice**: Adopt the 5-rung backoff ladder (`full` $\to$ `no_econ` $\to$ `no_econ_no_hh` $\to$ `age_day` $\to$ `age`) and record the distribution of pricing rungs at each $\lambda$ level.
* **Scientific Rationale**:
  - Dropping unpriced prefixes would discard $24.6\%$ of Spanish prefixes and introduce a confounding selection bias that shifts with $\lambda$.
  - Pricing everything on a coarse key would discard the $76\%$ of strata that are fully observed in donor microdata.
  - The backoff ladder preserves $100\%$ of drawn prefixes while maintaining complete auditability of the pricing depth.

#### 3. Item 3 (Clause 2 Anti-Stereotype Operationalisation) — Confirmed
* **Choice**: Operationalise Clause 2 as requiring generated outputs to be strictly closer to the expected synthetic profile than to any donor country's baseline weighted empirical profile.
* **Scientific Rationale**:
  - Under a fictional country token (`x_zz`), no real country token is present in the prompt.
  - Comparing generated diaries against weighted national baselines directly tests the hypothesis that the model is merely reciting a memorised donor country rather than responding dynamically to the conditioned prefix vector.

---

⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` remains untouched and verified. Nothing is running on Speed.
