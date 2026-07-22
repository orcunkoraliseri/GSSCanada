# Deep-Research Prompt dr_L3v2-01A (GEMINI ANTIGRAVITY / agentic edition) — QUÉBEC (ISQ) MONTHLY HOTEL-OCCUPANCY SERIES EXTRACTION (2005–2022)

> **Which edition is this?** This is the **Gemini Antigravity (agentic IDE)** edition. Unlike the plain
> web Deep-Research edition, you can run a **multi-step agent pipeline** and **write output files**.
> Execute the AGENT PIPELINE below **in order**, and at the end **write the finished report to a file**
> in this folder: `dr_L3v2-01A_isq_qc_monthly_extraction_REPORT.md`. The extraction spec (schema,
> routes, anti-fabrication rules) is identical to the web edition; the pipeline is the added part.

> SCOPE GUARD — READ FIRST. This is a **DATA-EXTRACTION / TRANSCRIPTION** task. Retrieve, from the
> **Institut de la statistique du Québec (ISQ)** accommodation-frequentation program, the **monthly,
> Québec-provincial** hotel **occupancy rate** (+ ADR, RevPAR where published) for **2005-01 → 2022-12**
> (216 months) and transcribe it faithfully. Do NOT design the forecast, benchmark energy, or interpolate.

---

## ⚠️ v2.2 HARDENING + ROUTING — READ BEFORE YOU START (updated 2026-07-19)

Two prior runs failed identically: they hit the ISQ **Power-BI dashboard** (export disabled), gave up,
and returned ~100 % GAP (one recovered only 20 summer months from a blog). The sibling Alberta task was
rescued by abandoning the live dashboard for an **open-data / static / archived** source. Apply that
lesson to Québec.

### CONFIRMED DEAD ENDS — do NOT spend budget re-checking these
1. **ISQ Power-BI dashboard** (`statistique.quebec.ca`) — export disabled, not scriptable. Skip.
2. **Données Québec** (`donneesquebec.ca`, CKAN) — verified 2026-07-19: hosts only **SIT Québec
   establishment registries** (Hôtels/Gîtes/Campings coordinates & types, CSV/JSON/XML), **NOT** the
   monthly taux-d'occupation series. Do not re-probe it for occupancy.

### PRIORITY ROUTES (try in this order) — the actual opportunity
1. **Internet Archive / Wayback Machine (`web.archive.org`)** — pre-migration ISQ **static Excel/PDF
   tables** of « taux d'occupation des établissements hôteliers ». Search archived snapshots (~2010–2019)
   of `statistique.quebec.ca`, legacy `stat.gouv.qc.ca`, and `bdso.gouv.qc.ca`. **Most promising untried route.**
2. **BDSO** (`bdso.gouv.qc.ca`) — official statistics data bank; look for a downloadable frequentation /
   occupation table (HTML/XLS/CSV).
3. **AHQ** (`hotelleriequebec.com`) — sweep the WHOLE site (blog/news archive, annual « bilans ») for
   months beyond the Jul/Aug retrospective; they re-publish ISQ figures verbatim.
4. **Tourisme Montréal industry portal** (`industrie.mtl.org`) + **Institut du Québec**
   (`institutduquebec.ca`) — **Montréal-market** monthly occupancy (useful, but tag market-level in
   PROVENANCE; never pass a Montréal number as QC-provincial).
5. **Tourisme Québec legacy « performance touristique »** + ISQ « Bulletin statistique régional » /
   « Panorama des régions » — mostly **annual** → Table-3 reconciliation only, never monthly cells.

### Non-negotiable anti-fabrication rules
- **PROVE REACHABILITY** — every non-blank value's source opened this run; Table 2 carries a pasted
  **verbatim snippet + working URL**. **No snippet, no data** → blank + `GAP`.
- **NEVER invent an endpoint/table ID/file URL.** 404/blocked/login → GAP, never a substitute.
- **PAYWALL / LOGIN = GAP.**
- **20 verified months beat 216 invented ones.**

---

## Target schema (this prompt fills the QC rows)
```
YEAR, MONTH, PR, occupancy_rate, ADR_CAD, RevPAR_CAD, SOURCE, PROVENANCE, STATUS
```
- **occupancy_rate** = provincial taux d'occupation, monthly, **0–1 fraction** (65.2 % → 0.652).
- **ADR_CAD** = « prix moyen de location »; **RevPAR_CAD** = « RUD » (may be `COMPUTED` = occ × ADR, flagged).
- COVID months (2020-03 … 2022-06) kept as published — signal, not gaps.
- `STATUS` ∈ {`OK`, `GAP`, `COMPUTED`}.

Context: Hotel channel of a 4-channel GSS→BEM pipeline (Leg 3); QC = Zone-6A / Montréal driver; feeds the
guest-room People schedules, the SARIMA backcast gate (QC 2015–2019 MAE < 0.05), and hotel EUI gates.

---

## AGENT PIPELINE — execute these stages in order (this is the Antigravity-specific part)

> Run as a sequential pipeline. Each stage consumes the previous stage's output. Do not skip ahead; do
> not fabricate to "complete" a stage — an empty/GAP result is a valid stage output. Keep a running
> scratch log of every URL you open and its HTTP result so Stage 5 can prove reachability.

**Stage 1 — RECON (enumerate routes, don't transcribe yet).**
Build a candidate-route list from the PRIORITY ROUTES above. For each: open it, record whether it is
`live / blocked / 404 / login`, and whether it plausibly carries **monthly** QC occupancy. Output a short
route table. Do **not** re-open the two CONFIRMED DEAD ENDS. Prioritise Wayback + BDSO.

**Stage 2 — FETCH + PROVE (open the live routes; capture proof).**
For every promising route from Stage 1, open the actual table/file. For each occupancy figure you intend
to use, capture: the **verbatim snippet** (the printed number in its row/label context) + the **exact
working URL** + the month(s) it covers. If a route turns out blocked/paywalled/login → mark it GAP and
move on. **A number without a captured snippet does not exist for later stages.**

**Stage 3 — TRANSCRIBE (fill the 216-row matrix).**
Populate Table 1 from Stage-2 proofs only. Every non-blank cell must map to a Stage-2 snippet. Convert
percents to 0–1. Leave unverified months blank + `GAP`. **No interpolation / carry-forward / estimation.**
Tag Montréal-market values as market-level in PROVENANCE.

**Stage 4 — RECONCILE (self-check, flag don't fix).**
Compute annual averages from your OWN transcribed data; compare to the dr_L3-01 sanity bands (Table 3
below). Flag violations — do NOT adjust values to fit.

**Stage 5 — WRITE THE REPORT FILE + SELF-AUDIT.**
Assemble the full report (Table 1 markdown + identical CSV block, Table 2 with snippets, Table 3, Part C,
Confidence & caveats, Reference list) and **save it to
`dr_L3v2-01A_isq_qc_monthly_extraction_REPORT.md`** in this folder. Then run a final self-audit pass:
for every row with `STATUS = OK`, confirm Table 2 contains a matching snippet+URL; **any OK cell lacking
proof must be downgraded to blank + `GAP`** before you finish. State the audit result at the top of the report.

---

## REQUIRED OUTPUT (the report file must contain all of this, in order)

### Table 1 — QC monthly series, 2005-01 … 2022-12 (216 rows) + identical fenced ```csv block
| YEAR | MONTH | PR | occupancy_rate | ADR_CAD | RevPAR_CAD | SOURCE | PROVENANCE | STATUS |
|---|---|---|---|---|---|---|---|---|
| 2005 | 1 | QC |  |  |  | ISQ |  | GAP |
| … | … | … | … | … | … | … | … | … |
| 2022 | 12 | QC |  |  |  | ISQ |  | GAP |

### Table 2 — Per-year citation WITH reachability proof (2005–2022)
| Year | Product / page (exact) | Access route | Months found (of 12) | Verbatim snippet + URL | Notes |
|---|---|---|---|---|---|

### Table 3 — Reconciliation vs dr_L3-01 (flag, do not adjust)
| Check | Expected | Your value | Pass / Flag |
|---|---|---|---|
| QC annual-avg occupancy, mean 2015–2019 | 0.60–0.65 |  |  |
| 2020-04 QC occupancy (COVID trough) | very low |  |  |
| Seasonal shape | summer > winter, non-COVID |  |  |
| Monotonic recovery | 2021 < 2022 < 2019 |  |  |

### Part C — Synthesis
1. Coverage verdict (OK/GAP/COMPUTED counts; dominant route).
2. Which PRIORITY ROUTES paid off vs dead.
3. Least-certain cells + the exact export that resolves them.

Then **"Confidence and caveats"** + **Reference list** (full citations, retrieval dates, live URLs).

## Hard requirements (recap)
- No fabricated values; unverified = blank + `GAP`; every non-blank cell traces to a Table-2 snippet+URL.
- No interpolation / smoothing / carry-forward. occupancy_rate 0–1; keep all COVID months.
- Stay on **QC**; no StatCan occupancy table exists. Montréal-market months tagged market-level, never as QC-provincial.
- **Finish by writing `dr_L3v2-01A_isq_qc_monthly_extraction_REPORT.md` and stating the self-audit result at its top.**
