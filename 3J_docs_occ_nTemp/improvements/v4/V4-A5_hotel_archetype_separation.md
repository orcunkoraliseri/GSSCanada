# V4-A5 — what `S9-EUI-hotel` is actually failing on

**2026-08-06 · desk work · reads only the frozen deliverable
(`Leg3_4-split/Step8_docs/outputs_step8/agg_deliverable/`) · no simulation, nothing re-scored.**
Generator: `improvements/v4/a5_hotel_archetype_split.py` · data: `v4_a5_hotel_split.json`.

**What this serves:** A4 measured the split and stopped. It left two things unanswered — *why* the two
geometries separate, and *what the gate is failing on given that the uninjected control already fails
it*. Both are answerable from files already on this machine. **No gate is re-scored here and no band
value is touched.**

---

## 0. The three results

1. 🔴 **The separation is one end use.** `dhw` alone accounts for **79.04 of the 84.64 kWh/m² empty
   gap — 93.4 %.** Every other end use is under 21, and two of them lean the *wrong* way.
2. 🔴 **That end use is inert to occupancy.** Across all 14 scenarios `dhw` moves by **0.01 kWh/m²**.
   The most occupancy-responsive end use in the hotel channel is `interior_lighting`, at **4.34 kWh/m²
   — about 1.4 % of a ~310 total.**
3. 🔴 **The load does not scale with the hotel floor area.** `Tall` has **exactly half** the hotel
   floor area of `SuperTall` (14,215.4 vs 28,430.8 m², ratio 2.000) and **86.1 % of its DHW energy**
   (2,678,643 vs 3,110,136 kWh, ratio 1.161). **Halving the floor area removes 13.9 % of the load.**

⇒ **The gate is not measuring occupancy. It is measuring a service-hot-water object sized per building
rather than per unit of hotel floor area.**

---

## 1. The decomposition reconciles to the scored number

Before anything is read into it: the per-end-use sum reconstructs `eui_CFA_kWh_m2` — the exact column
`Step9` medians — to **1.1 × 10⁻¹³ kWh/m²** across all 56 hotel cells. The script asserts this and
stops if it fails. **This is the same quantity the gate scores, not a look-alike.**

| | range over its 28 cells | vs the 300 ceiling |
|---|---|---|
| `SuperTall` | 203.33 – 218.22 | all 28 **inside** the band |
| `Tall` | 302.86 – 318.42 | all 28 **above** the ceiling |
| **empty gap** | **84.64** | **the ceiling sits inside it** |

## 2. C1 — which end use carries the separation

Pre-registered as falsifiable: *if the separation were spread across the load, there is no single-object
story and the archetype reading fails.* It is not spread.

| end use | `SuperTall` | `Tall` | separation | % of the 84.64 gap |
|---|--:|--:|--:|--:|
| **`dhw`** | 109.39 | 188.43 | **+79.04** | **93.4 %** |
| `interior_equipment` | 41.31 | 61.58 | +20.27 | 24.0 % |
| `cooling` | 4.82 | 7.47 | +2.66 | 3.1 % |
| `heat_rejection` | 0.48 | 1.12 | +0.64 | 0.8 % |
| `heat_recovery` | 2.76 | 3.14 | +0.37 | 0.4 % |
| `interior_lighting` | 11.76 | 12.02 | +0.26 | 0.3 % |
| `fans` | 7.45 | 7.68 | +0.23 | 0.3 % |
| `pumps` | 5.32 | 5.31 | −0.01 | 0.0 % |
| `heating` | 27.33 | 23.63 | **−3.70** | −4.4 % |

`heating` is **lower** in the building with the higher EUI — the two geometries are not simply "one is
worse", and no envelope story explains the gap.

## 3. C2 — how much of this answers to occupancy at all

Movement of each end use across the **14 scenarios** (2005 → 2030-fullyhybrid, the three `B_*` bundles,
the six `sens_*` arms, and the uninjected control), per city:

| | `cooling` | `dhw` | `fans` | `heating` | `interior_equipment` | `interior_lighting` |
|---|--:|--:|--:|--:|--:|--:|
| `SuperTall` CLG | 0.27 | **0.01** | 0.39 | 2.40 | 2.87 | 3.82 |
| `SuperTall` MTL | 0.22 | **0.01** | 0.28 | 3.56 | 3.01 | 4.34 |
| `Tall` CLG | 0.41 | **0.01** | 0.37 | 2.55 | 2.79 | 3.75 |
| `Tall` MTL | 0.46 | **0.01** | 0.27 | 3.53 | 2.92 | 4.26 |

**The whole occupancy-responsive range of the hotel channel is about 4 kWh/m² on a total near 310.**
The single end use that separates the two clusters contributes **0.01** of it.

## 4. The uninjected control, read as the control

`Default_NECB` is the run with **stock NECB schedules and no occupancy model injected at all**.

| | total | `interior_lighting` | `interior_equipment` | `dhw` | over the 300 ceiling? |
|---|--:|--:|--:|--:|---|
| `SuperTall` CLG | 204.83 | 9.33 | 42.18 | 109.39 | no |
| `SuperTall` MTL | 216.06 | 9.38 | 42.18 | 109.40 | no |
| `Tall` CLG | **304.41** | 9.65 | 62.43 | 188.43 | 🔴 **yes** |
| `Tall` MTL | **315.82** | 9.68 | 62.43 | 188.44 | 🔴 **yes** |

🔴 **The gate fails on `Tall` before any of our work is in the building.** Injecting the occupancy model
moves it by at most ~4 kWh/m², in a channel that is 300+ either way. **`S9-EUI-hotel` cannot be cleared
by anything done to the occupancy model, and it cannot be blamed on it either.**

## 5. The mechanism, stated plainly

`Tall` has **exactly half** the hotel floor area of `SuperTall` and **86 %** of its DHW energy. A load
that is per-guest-room, per-riser or per-plant — not per m² — is being divided by an area that halved.
**The EUI difference is an artefact of the denominator, not a difference in how the two hotels are
used.**

🔴 **This is the same shape as the `LAUNDRY` finding in Step 9** (`project_3j_leg3_step9_status`): the
channel's behaviour is dominated by **one object that does not scale with the thing it is normalised
by**, and a global instrument aimed at the channel misses it. Second instance, different object.

## 6. What is **not** claimed

⚠️ **This is not a bimodality result and must not be written as one.** There are **two geometries**, so
"the distribution has two modes" and "we ran two archetypes and they differ" are not distinguishable —
that is vacuous-reading class #16 (a sweep with n=1 per level), and it applies here with n=2 buildings.

**The defensible claim is narrower and stronger:** *the hotel channel is not one population, the band
was set as if it were, and the separating quantity is a DHW load that does not scale with hotel floor
area and does not respond to occupancy.* That survives at n=2 because it is a **mechanism identified in
the model**, not an inference from the shape of a distribution.

Also not claimed: that the 300 ceiling is wrong. **The ceiling is not touched, no band moves, and
`S9-EUI-hotel` stays FAIL** (see §7).

## 7. What this changes — and what it deliberately does not

**Changes:** what the gate is *claimed to test*. `S9-EUI-hotel` is documented from here on as failing on
a DHW sizing basis, evidenced by the uninjected control, **not** as an unresolved occupancy result.

**Does not change:** the verdict, the ceiling, the scoring rule, or the frozen deliverable. Re-basing
the hotel EUI on rooms or on a corrected DHW object would turn a FAIL into something else — that is a
band change wearing a different hat, and it is the exact move the gate-shopping prohibition (R1,
2026-07-21) forbids. **The failure is left standing and explained.**

## 8. Reopen trigger

Reopens if **any** of these becomes true:
1. a **third** hotel geometry is simulated — at n=3 the population claim in §6 becomes testable rather
   than merely defensible, and the wording of §6 must be revisited either way;
2. the DHW object is re-sized per floor area, in which case §5 predicts `Tall`'s EUI falls by roughly
   **79 kWh/m² toward the `SuperTall` cluster** and the gate is re-scored against that prediction,
   written down here in advance;
3. anyone proposes moving the 300 ceiling — this document is the reason it must not be moved *on this
   evidence*, since the evidence says the numerator and denominator disagree, not that the band is
   wrong.
