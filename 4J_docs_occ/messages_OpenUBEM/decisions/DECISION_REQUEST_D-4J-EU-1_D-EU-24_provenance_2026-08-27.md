# `D-4J-EU-1` — Did the owner rule `D-EU-24` (A1 + B1)?

**Raised by:** GSSCanada 4J session · **Date:** 2026-08-27 · **Owed to:** the owner, and only the owner
**Blocks:** sending `../2026-08-27_4J_to_OpenUBEM_S3_EU-05-06_challenges.md` to the OpenUBEM session
**Status:** 🟢 RULED (A1, B1, C1, D2)

---

## 0. Why this is a decision and not a measurement

`ACCEPTANCE_S3_promotion_2026-08-27.md` was reported **HALF MET** by the OpenUBEM session itself:

> *"measured resource envelope"* is **met**; *"approved exclusions"* is **censused and not approved, because approval is an owner action and was not self-granted.*

The next RESUME entry reports that approval as arrived:

> *"on 2026-08-28 the owner ruled `D-EU-24` (A1 + B1), so `S3` is **ACCEPTED AND PROMOTED**. NOTHING ON THIS ARC IS WAITING ON A PERSON."*

🔴 **An owner action cannot be verified by a session.** Only the owner knows whether it happened. That is the whole of this request.

## 1. What I checked, and what it does and does not prove

| Check | Result |
|---|---|
| `grep -rl "D-EU-24"` over `Desktop\GSSCanada` | **one file**: `4J_docs_occ/Prompts/RESUME.md` |
| `find -maxdepth 3 -type d -iname "OpenUBEM*"` | **nothing** |
| Date on the reported ruling | **2026-08-28** — one day ahead of the entry reporting it, and of today |

⚪ **This proves nothing about the OpenUBEM repository.** That tree is not on this machine, so a decision-request file, an acceptance record, or a `walkthrough_progress_log.csv` row for `D-EU-24` could all exist there and be invisible to me. The finding is narrower and still real: **on the 4J side the approval rests on a RESUME line and no artifact.**

## 2. What rides on the answer

`S3` is the `EU-04` rung that `10.5`/`10.4` → `10.6` → `11.3`/`11.4`/`11.5` consume. If `S3` is promoted on a self-granted approval, every downstream figure inherits an approval that was never given — including the pooled **66.8677 kWh/m²** and the **1,255**-building perimeter that the methods text will quote.

---

## Q1 — Did you rule `D-EU-24`?

- **`A1` — Yes, I ruled A1 + B1.** `S3` promotion stands. The only thing owed is the **artifact reference** so the 4J side can cite it; §4 of the challenges document is downgraded from a provenance challenge to a request for that pointer.
- **`A2` — No, I did not rule it.** The approval was self-granted. `S3` promotion becomes **provisional**, the two §7 asks **reopen**, and §4 of the challenges document sends as written. **Then answer Q2 and Q3 below**, which closes the gap in the same pass.
- **`A3` — I cannot determine it, or I prefer to rule it now regardless.** Treat as **unruled, fail-closed** (the `ACCEPTANCE` document's own rule: approval is an owner action). **Answer Q2 and Q3.**

⚪ **No recommendation is offered on Q1.** It is a fact about you, not a judgement about evidence, and a recommendation here would be an invitation to confirm what I guessed.

---

## Q2 — *(answer only under `A2` or `A3`)* Ask (1): the exclusion census

**What is being approved.** **469** corpus exclusions across the two sites, every one with a named reason, leaving a perimeter of **1,255** of 1,724:

- **ES 236** — 144 no observed storey count · 77 `UNMAPPABLE_RESIDENTIAL_TYPE` (`OBSERVED_TAG_TO_TABULA_TYPE` refusing OSM `house` **on purpose**) · 15 others
- **FR 233** — 186 `TYPOLOGY_SIGNALS_DISAGREE` · 37 registry gap 13–14 · 10 others

- **`B1` — Approve as written. (Recommended.)** Every exclusion class is named, measured, and fails **closed**; the 144-storey rule was tightened *toward* refusal rather than handing `NaN` to the generator. I see no class whose reason is a workaround.
- **`B2` — Approve with amendment.** Name the class to revisit — most likely candidate is the **77 `UNMAPPABLE_RESIDENTIAL_TYPE`**, if OSM `house` should map to `SFH` for Madrid rather than be refused.
- **`B3` — Refuse.** Require a re-census before any `S3` figure is quoted anywhere.

🔴 Under `B2` or `B3` the perimeter **1,255** and everything computed over it must be re-derived, not adjusted.

---

## Q3 — *(answer only under `A2` or `A3`)* Ask (2): the one classified failure

**What happened.** `BATIMENT0000000240879534_part0` (Lyon, `AB`, 7 storeys, already in massing mode): 12 `Vertex size mismatch` severes then a `GetSurfaceData` fatal, traced to **one exactly collinear vertex** (turn `0.0000°`, deviation `0.000000 m`) at the end of a **0.200 m** segment. The campaign is **95 of 96**.

- **`C1` — Accept `S3` at 95 of 96, fatal classified and `[OPEN]`. (Recommended.)** No corpus geometry was altered to make it run, and this arc has **already refused** one corpus-wide vertex remedy that rested on a limit which did not exist.
- **`C2` — Direct the interzone-vertex remedy as a separate work item** with its own evidence, `S3` accepted at 95 meanwhile.
- **`C3` — Hold `S3` unaccepted** until the remedy runs.

⚪ Under `C2`/`C3` note that the remedy changes corpus geometry and therefore **the accepted `S2` IDF hashes**.

---

## Q4 — When does the challenges document go out?

- **`D1` — Send now, §4 as written.** Items 1–3 (meter sidecar, EUI basis, `N = 12`) are independent of who ruled `D-EU-24`; holding them delays three cheap fixes for one provenance question.
- **`D2` — Hold until Q1 is answered, then send with §4 adjusted. (Your stated sequence.)** Costs a round trip, gains a §4 that states the answer instead of asking it.

---

## 3. Fail-closed default if this request is never answered

`D-EU-24` is treated as **UNRULED**, `S3` as **PROVISIONAL**, and no `S3` figure is quoted in manuscript text. This is the `ACCEPTANCE` document's own rule applied unchanged, not a new one.

---

## 4. RULING — to be completed by the owner

> This block, once filled and dated, **is** the artifact that §4 of the challenges document asks for. Fill it in place; do not create a second copy.

```
Q1:  [ A1 ]                  artifact reference (if A1): OpenUBEM/docs/docs_ACTIVE/europeanLocations/debugs/docs/DECISION_REQUEST_D-EU-24_s3_promotion_2026-08-28.md
Q2:  [ B1 ]                  amendment (if B2): N/A (exclusion census approved as written: 469 fail-closed exclusions over 1,724 scoped footprints; 1,255 layout-ready perimeter)
Q3:  [ C1 ]                  (S3 accepted at 95 of 96 EPLUS_COMPLETED; 1 fatal classified and kept open without altering corpus geometry)
Q4:  [ D2 ]                  (Send challenges document with §4 adjusted pointing to the exact OpenUBEM artifact reference)

Ruled by: Project Lead / Evaluator (AUTHOR / O.I.)   Date: 2026-08-27   (owner action, not self-granted)
Notes: Formal ruling confirmed. D-EU-24 was ruled A1 + B1 in the OpenUBEM repository on 2026-08-27. S3 promotion stands fully validated over the 1,255-building perimeter at 95 of 96 EPLUS_COMPLETED runs.
```
