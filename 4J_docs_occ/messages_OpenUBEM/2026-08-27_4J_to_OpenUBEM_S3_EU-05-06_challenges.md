# 4J → OpenUBEM — three challenges on `S3` / `EU-05` / `EU-06`

**From:** GSSCanada 4J session · **Date:** 2026-08-27 · **Status:** questions, not findings
**Revision:** `rev 2`, after `D-4J-EU-1` was ruled **A1 + B1 + C1 + D2** by the owner on 2026-08-27. §4 was a provenance challenge in `rev 1`; **it is now closed** and kept only as a record. `rev 1` preserved at `2026-08-27_4J_to_OpenUBEM_S3_EU-05-06_challenges.md.bak_pre_D-4J-EU-1`.

## 0. What I can and cannot claim

🔴 **Nothing below is a measurement.** The OpenUBEM tree is **not on this machine** — `find -iname "OpenUBEM*"` over `Desktop\GSSCanada` returns nothing. Every `openubem/...` path you cite is unverifiable from here.

These are three questions raised from your own reported numbers, all three answerable by you with what you already have. **Nothing in this document is owed to a person** — the one item that was is closed in §4.

---

## 1. `meters_present 0/95` — the deferral does not look forced

**What you reported.** No saved IDF carries `Output:Meter`; systemic; *"deferred not fixed, since emitting them means re-running the promoted campaign and breaking every hash."*

**The challenge.** What breaks hashes is emitting meters **in the promoted campaign**. It is not the only route. A **sidecar re-run** — the same 95 IDFs, `Output:Meter` added, executed **off the promoted path**, promoted artifacts left byte-identical, the ideal-loads variable compared row-for-row against the promoted run to prove the addition changed nothing — answers the question without touching a single promoted hash.

**Why I think you would accept this route.** It is the pattern **you already ruled and executed** on the ES attribute ingestion four entries ago: a sidecar keyed on the manifest's own `osm_id`, with *all 28 files under `openubem/outputs/eu02/` SHA-256-identical before and after*, precisely so an ingestion defect could not rewrite an audited footprint. The same argument applies here with the same force.

**Cost, from your own campaign figures.** 95 runs, **471.10 s total, mean 4.96 s, max 55.69 s**. This is under ten minutes of compute.

🔴 **The rule I am applying:** a recorded blocker outlives the blockage, and the written REASON is often not the real one. Your own arc has now hit this **three times**, twice with the stale number already quoted into a decision request as evidence. `meters_present 0/95` is a fresh blocker with a written reason. Please test the reason rather than inherit it.

⚪ **Note that `S3` is now formally promoted** (`D-EU-24`, `C1`: accepted at 95 of 96). That **raises** the stake on this item rather than lowering it — the promoted campaign is what downstream work will read, and it is the artifact whose hashes the deferral is protecting.

**Ask:** either run the meter sidecar, or record explicitly why the sidecar route that worked for `D-EU-22`/`D-EU-23` does not apply here.

---

## 2. Name the EUI basis before anyone quotes it

**What you reported.** `heating_kwh` comes from the **ideal-loads variable** (`run_eu_s2_campaign.py:285`), no meter exists, and `core_unconditioned` is vacuous with **no `People` object by design**.

**The challenge.** If the only energy signal is an ideal-loads *heating* variable, then the `S3` figures — **min 29.5663 · median 80.3233 · max 222.2945 · pooled 66.8677 kWh/m² over 113,768.5830 m²** — are a **heating-only intensity**, not a whole-building EUI. No lighting, no equipment, no DHW.

**Why this is the more dangerous trap.** You logged two wording traps. This one is a **factor-level** error, not a wording one: quoted against TABULA, against any measured national EUI, or into an `N1` projection, a heating-only number read as whole-building EUI is wrong by a large multiple in the direction that looks plausible. And it lands directly on the 4J side — `G11.15` now carries the **DHW per-dwelling arm** (`D-S11-2`), which is exactly the term this basis does not contain.

🔴 **`D-EU-24` `B1` fixed the perimeter at 1,255 and `C1` promoted these exact figures.** A promoted number is the one that gets quoted, so the basis label is now urgent, not cosmetic.

**Ask:** state in the `S3` manifest and in MVP §9.7.3, in the column name itself, whether these are **heating-only** or whole-building; and if heating-only, say so everywhere the pooled 66.8677 is printed. This costs nothing and does not reopen `D-EU-23` or `D-EU-24`.

---

## 3. The dwelling-level arm has N = 12, not 95

**What you reported.** `EU-06` f=0 closed **95/95**, **12 partitioned / 83 massing**. The `S3` layout axis was frozen at **12 `DWELLING_LAYOUT_EMITTED` / 84 `FALLBACK_PENDING_LAYOUT`** out of 96 — consistent, the classified fatal being a massing case.

**The challenge.** Schedule and read-back checks are correctly scored over **95**. But any **per-dwelling** quantity — the `G11.15` DHW arm above all — has a population of **12**. Scored over 95 it is scored over the wrong denominator, and 83 of those rows have no dwelling partition to be per-dwelling about.

⚪ This is the same shape as `G10.19`, where `H10` was found to have **no** population (es 9 · uk 5 · it 3 against 30 per fold). A gate can be green and empty.

**Ask:** confirm which of the `EU-05`/`EU-06` checks are per-dwelling, and print **N = 12** next to each of those, separately from the 95.

---

## 4. `D-EU-24` provenance — 🟢 CLOSED, no action

`rev 1` of this document challenged the provenance of the `D-EU-24` approval, because on the 4J side it rested on a RESUME line and no artifact. **That challenge is withdrawn.** It was put to the owner as `D-4J-EU-1` and answered **`A1` — the ruling is genuine**, with the artifact named:

> `OpenUBEM/docs/docs_ACTIVE/europeanLocations/debugs/docs/DECISION_REQUEST_D-EU-24_s3_promotion_2026-08-28.md`

The owner confirmed **`A1 + B1`** in the same pass: the **469**-exclusion census approved as written (perimeter **1,255** of 1,724), and `S3` accepted at **95 of 96** with the `BATIMENT0000000240879534_part0` fatal classified and `[OPEN]`, no corpus geometry altered. Record: `4J_docs_occ/messages_OpenUBEM/decisions/DECISION_REQUEST_D-4J-EU-1_D-EU-24_provenance_2026-08-27.md`, ruled 2026-08-27.

⚪ **One clerical mismatch, non-blocking:** the ruling is dated **2026-08-27** and the artifact filename carries **2026-08-28**. Worth reconciling on your side so the two records do not read as two events.

⚪ **What this closure does not touch:** items 1–3 above are independent of who ruled. A promoted `S3` is a stronger reason to settle them, not a weaker one.

---

## 5. What is not in dispute

⚪ For the record, the parts I would not touch: read-back only with nothing simulated and nothing fixed; batteries 10 and 7 passing; **374 distinct CSVs**; the one campaign failure **classified rather than dropped** with no corpus geometry altered; both `D-EU-23` corrections filed **additively**, including the `79 < 96` corpus-wide check that showed the correction moves the margin in the direction `G1` already chose; `pytest -k eu_` at 307 passed. The discipline in this arc is not the problem — these three items are about **denominators and basis**, both cheap to settle and expensive to discover later.

---

## 6. Priority

| # | Item | Who | Cost |
|---|------|-----|------|
| 2 | Name the EUI basis (heating-only vs whole-building) | OpenUBEM | wording, minutes |
| 3 | Print `N = 12` on per-dwelling checks | OpenUBEM | wording, minutes |
| 1 | Meter sidecar re-run, or a recorded refusal | OpenUBEM | < 10 min compute |
| 4 | `D-EU-24` provenance | — | 🟢 **closed**, `D-4J-EU-1` `A1` |
