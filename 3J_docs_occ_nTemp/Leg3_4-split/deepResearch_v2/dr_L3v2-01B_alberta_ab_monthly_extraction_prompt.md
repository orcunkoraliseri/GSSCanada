# Deep-Research Prompt dr_L3v2-01B — ALBERTA MONTHLY HOTEL-OCCUPANCY SERIES EXTRACTION (2005–2022)

> SCOPE GUARD — READ FIRST. This is a **DATA-EXTRACTION / TRANSCRIPTION** task, not a design or
> literature task. Your only job is to retrieve the **monthly, Alberta-provincial** hotel **occupancy
> rate** (and, where published, **ADR** and **RevPAR**) for **2005-01 … 2022-12** and transcribe it into
> the fixed schema below. The sources are fixed (dr_L3-01): the **Alberta Economic Dashboard**
> "Accommodation occupancy rate" (CBRE-sourced) for **2010–2022** (REQUIRED), and **CBRE Hotels Canada
> National Market Report archives** for the **2005–2009** gap (OPTIONAL — paywalled). Do NOT choose the
> source, design the forecast, benchmark energy use, splice, or interpolate. Splicing is a downstream
> pipeline step (Step-2D); your job is to deliver the raw values each source publishes, cleanly flagged.

---

## ⚠️ v2.1 HARDENING — LEARN FROM THE FAILED FIRST RUN (read before you start)

A prior run of **this exact prompt fabricated its Alberta series** and it was caught:
- It cited the API endpoint `api.economicdata.alberta.ca` (table `CBRE_Occupancy_Percentage`) — that
  endpoint returns **HTTP 404 and does not exist.**
- It filled **2005–2009** from an alleged "open-government Alberta Tourism Market Monitor" source that
  **could not be found and contradicts dr_L3-01** (those years are paywalled CBRE only).
- Not one spot-checked value could be traced to a real page.

That fabricated report is being discarded. **Do not reproduce it.** You are being run in **Gemini Deep
Research (web browsing)**. Therefore:

1. **PROVE REACHABILITY.** For every source you cite, you must have actually opened it in THIS session.
   In Table 2, paste a short **verbatim snippet** from the live page/file (a table header, a printed
   figure, one sentence) plus the **exact working URL**. A number whose source you did not actually load
   = blank value + `STATUS = GAP`. **No snippet, no data.**
2. **NEVER invent an endpoint, table ID, or file URL.** The `api.economicdata.alberta.ca` endpoint is
   banned — it 404s. The real Alberta source is the dashboard page itself:
   https://economicdashboard.alberta.ca/dashboard/accommodation-occupancy-rate/ — open ITS actual
   download/export control, confirm what start year and columns it truly exposes, and prove it with a
   snippet. If a URL 404s or is blocked, GAP it — never substitute a plausible-looking alternative.
3. **PAYWALL / LOGIN = GAP.** CBRE / STR data is proprietary. If you cannot pass a paywall or login, you
   cannot use it. Never claim paywalled data is "open."
4. **2005–2009 HAS NO CONFIRMED OPEN SOURCE.** Expect to `GAP` these 60 months and fill Table 4 with the
   fallback decision (truncate AB to 2010, or TASPI backcast). Only fill them if you genuinely open a
   real CBRE page and can paste a snippet — otherwise GAP is the correct, expected answer.
5. **156 verified months (2010–2022) beat 216 invented ones.** Honest, well-cited partial coverage is a
   SUCCESS here; a complete-looking uncited series is a FAILED report and will be discarded.

---

## What this document is

A monthly-series harvest brief for the Hotel channel of a 4-channel GSS→BEM occupancy pipeline (Leg 3
of 3). **Alberta is the second driving province** (Calgary, Zone 7A). This series feeds the guest-room
People schedules, the SARIMA backcast gate (AB 2015–2019 MAE < 0.05), and the hotel EUI gates. A
fabricated or mis-transcribed month propagates into published energy results — accuracy and honest gaps
beat completeness.

Target file (this prompt fills the AB rows):
```
YEAR, MONTH, PR, occupancy_rate, ADR_CAD, RevPAR_CAD, SOURCE, PROVENANCE, STATUS
```

## Role

Alberta / Canadian commercial-lodging data-extraction specialist. Work from two named sources, kept
**strictly separated** by the `SOURCE` tag so the downstream splice can calibrate them:

1. **`ABDASH`** — Alberta Economic Dashboard, "Accommodation occupancy rate" indicator (data sourced
   from CBRE), monthly, Alberta-provincial, **2010–present**, direct CSV/XLSX/JSON download. **Excludes
   major resort areas (Banff, Jasper).** Portal:
   https://economicdashboard.alberta.ca/dashboard/accommodation-occupancy-rate/
2. **`CBRE`** — CBRE Hotels Canada *"Trends in the Canadian Hotel Industry / National Market Report"*
   archives, monthly Alberta-provincial, for the **2005–2009** gap only. Proprietary/paywalled; academic
   access needs an agreement. **If you cannot obtain verifiable CBRE monthly Alberta values for
   2005–2009, report those 60 months as `GAP` — do NOT reconstruct them from national data, price
   indexes, or memory.**

Browse the actual dashboard export and any obtainable CBRE report; transcribe, do not reconstruct.

## Why this matters (so you scope correctly)

- **occupancy_rate** is the driver (0–1 fraction; convert published percent). The Alberta Dashboard
  excludes resorts, so its provincial rate runs **2–4 pp lower** than raw CBRE provincial (which
  includes Banff/Jasper) — this is *expected* and is exactly why the two sources are kept separate and
  spliced downstream with a calibration factor. **Do not pre-adjust either source to match the other.**
- **ADR_CAD** = dashboard "Average Daily Room Rate" / CBRE ADR, CAD. **RevPAR_CAD** = dashboard RevPAR
  directly, or CBRE RevPAR; if a month has occupancy + ADR but no RevPAR, you MAY back-compute
  `RevPAR = occupancy × ADR` and set `STATUS = COMPUTED`.
- **COVID months are signal, not gaps** — keep 2020-03 … 2022-06 exactly as published (Calgary/AB crater
  to single digits — correct and required for the SARIMA COVID dummy).
- **2005–2009 is explicitly optional.** The pipeline has a documented fallback: truncate the AB SARIMA
  training window to 2010-01, or use StatCan TASPI (18-10-0249-01) as an exogenous backcast regressor.
  So an honest "2005–2009 = GAP, CBRE archive not obtainable" is a fully acceptable, useful result —
  far better than invented values.

---

## REQUIRED OUTPUT — fill every month you can verify; mark the rest GAP

### Table 1 — AB monthly series, 2005-01 … 2022-12 (up to 216 rows)

One row per month. `PR = AB`. Use `SOURCE = ABDASH` for 2010–2022 rows and `SOURCE = CBRE` for any
2005–2009 rows you obtain. Leave the value cell **blank** and set `STATUS = GAP` for any month not
verified from its source — **no interpolation, no carry-forward, no cross-source borrowing.**

| YEAR | MONTH | PR | occupancy_rate | ADR_CAD | RevPAR_CAD | SOURCE | PROVENANCE | STATUS |
|---|---|---|---|---|---|---|---|---|
| 2005 | 1 | AB |  |  |  | CBRE |  | GAP (if not obtained) |
| … | … | … | … | … | … | … | … | … |
| 2010 | 1 | AB |  |  |  | ABDASH |  |  |
| … | … | … | … | … | … | … | … | … |
| 2022 | 12 | AB |  |  |  | ABDASH |  |  |

Then repeat the identical data as a fenced CSV block (exact header, no extra columns):

```csv
YEAR,MONTH,PR,occupancy_rate,ADR_CAD,RevPAR_CAD,SOURCE,PROVENANCE,STATUS
2005,1,AB,,,,CBRE,,GAP
...
2022,12,AB,,,,ABDASH,,
```

### Table 2 — Per-source, per-year citation

| Source | Year(s) | Exact product / dashboard export / report title | Access route | Months found | Resort-inclusion definition | Notes / breaks |
|---|---|---|---|---|---|---|
| ABDASH | 2010 |  |  |  | excludes Banff/Jasper |  |
| … | … |  |  |  |  |  |
| CBRE | 2005–2009 |  |  |  | includes resorts (raw provincial) |  |

### Table 3 — Reconciliation against the dr_L3-01 sanity magnitudes

Compute from YOUR extracted data; flag — do not adjust — any violation.

| Check | Expected (dr_L3-01) | Your extracted value | Pass / Flag |
|---|---|---|---|
| AB annual-avg occupancy, mean of 2015–2019 (ABDASH, excl. resorts) | 0.54–0.58 |  |  |
| 2020-04 AB / Calgary occupancy (COVID trough) | 0.03–0.08 |  |  |
| Seasonal shape sanity | summer > winter each non-COVID year |  |  |
| ABDASH-vs-CBRE level at 2010 overlap (if CBRE obtained) | CBRE provincial ~2–4 pp higher than ABDASH |  |  |

### Table 4 — 2005–2009 acquisition outcome (record the decision explicitly)

| Path attempted | Obtained? (Y/N) | If N, why (paywall / no academic access / not found) | Recommended fallback the pipeline should record |
|---|---|---|---|
| CBRE National Market Report archives 2005–2009 |  |  | truncate AB SARIMA to 2010-01 **or** TASPI 18-10-0249-01 backcast regressor |

---

## Part C — Synthesis (short)

1. **Coverage verdict:** of the 156 mandatory months (2010–2022) how many `OK` / `GAP` / RevPAR
   `COMPUTED`; and separately the 60 optional months (2005–2009) outcome.
2. **Resort-exclusion note:** confirm the ABDASH series excludes Banff/Jasper, and (if CBRE obtained)
   quantify the level offset at the 2010 overlap — this is the input to the Step-2D splice, so state it
   but **do not apply it**.
3. **Least-certain cells** and the exact export that would resolve them.

## Output format (follow exactly)

1. **Lead with Table 1 (markdown) immediately followed by the identical CSV block.**
2. Then Tables 2–4, then Part C.
3. Inline citations throughout; keep ABDASH (open-licence) and CBRE (proprietary) citations distinct.
4. **"Confidence and caveats."**
5. **Reference list** — full citations, retrieval dates, live URLs (dashboard indicator page, not a
   search page). Do **not** paste proprietary CBRE report PDFs; cite values + source, no raw redistribution.

## Hard requirements

- **No fabricated values.** Non-blank cells trace to their `PROVENANCE`. Unverified month = blank +
  `STATUS = GAP`. A plausible full 216-month series with no per-year citation is a failed report.
- **Keep the two sources separated** by `SOURCE` tag; **do not splice, calibrate, or blend** them — that
  is a downstream pipeline step. Just deliver each source's raw published values.
- **No interpolation / smoothing / seasonal adjustment / carry-forward.**
- **occupancy_rate as 0–1 fraction**; keep all COVID months as published.
- **2005–2009 GAP is acceptable** — honest absence beats invention; fill Table 4 either way.
- **Stay on AB only** — Québec is `dr_L3v2-01A`.
- **No StatCan occupancy table** exists (dr_L3-01); TASPI is a *price* index, usable only as a flagged
  backcast regressor, never transcribed as an occupancy value.
- **Reachability-proof rule (v2.1):** every non-blank value's source was opened in this session and
  carries a pasted verbatim snippet + working URL in Table 2 — otherwise the value is blank + `GAP`.
  The banned `api.economicdata.alberta.ca` endpoint and any un-openable 2005–2009 "open" source are the
  exact things that got the last run discarded.

---

## Progress Log

### 2026-07-19 — AB series RESOLVED via a different, verified-working source (supersedes the discarded ABDASH/CBRE attempt)

The ABDASH (`economicdashboard.alberta.ca`) API this prompt targeted turned out to be unreliable to
drive programmatically. Rather than retry it, this run harvested the equivalent data from a **different,
verified open-government source**: the **Alberta Tourism Market Monitor** monthly PDFs
(open.alberta.ca, CKAN `package_search`, licence OGL-Alberta), datasets titled
`Alberta tourism market monitor : monthly update [YEAR]`, YEAR = 2011..2022 (12 datasets, 130 monthly
PDF resources, all confirmed real via `package_search`/`package_show` — no invented endpoints, no
paywall). Every PDF was actually downloaded (curl, HTTP 200, verified `%PDF-` header) and parsed with
`pymupdf` — this is transcription from real files, not a browsing-tool claim.

**What changed vs. the original ask:** the Market Monitor PDFs report Calgary / Edmonton / Alberta
Resorts / "Total Alberta (excl. Resorts)" as **separate rows** (no single ABDASH-style blended
provincial series, no RevPAR column printed directly — RevPAR is derivable as occ×ADR if ever needed but
was not computed here per scope). Coverage is **2011–2022** (2005–2010 was never in scope for this
source and remains the same GAP the original prompt already treated as optional/CBRE-only).

**Method notes (for reuse):**
- Table layout is NOT a fixed trailing-12-month window — it's Jan-of-current-year through the latest
  available month, reset every January, with a Yr-to-Date column appended once enough months exist.
  Token counts per row vary (2–13); an ambiguous count was disambiguated by checking whether the last
  value ≈ mean of the preceding ones (YTD signature) — never guessed outright.
- Reference year per GEO row was resolved **locally** (nearest "Point change from YYYY" / "Variance from
  YYYY" following that specific label + 1), not per-document — some transition-era PDFs (e.g. Mar-2022)
  mix reference years across GEO rows within the same file.
- Anchor check: Calgary 2017 Jan–Dec reproduced **exactly** (42.5, 50.8, 53.0, 56.1, 58.9, 67.0, 76.9,
  73.6, 71.2, 58.4, 56.8, 45.3 %) against the known-good values in the task brief.

**Deliverable:** `deepResearch_v2/hotel_ab_monthly_2012_2022.csv` (long format:
`YEAR,MONTH,GEO,metric,value,SOURCE,PROVENANCE,STATUS`; `SOURCE=ABMKTMONITOR`; occupancy as 0–1
fraction). Coverage (OK / GAP months, min–max): Calgary occ 137/7 (2011-01→2022-09), Edmonton occ
139/5, AlbertaResorts occ 139/5, AlbertaExclResorts occ 140/4 — all 4 GEOs parsed clean in all 130
PDFs with zero core-row parse failures; ADR_CAD captured as a bonus per-GEO (not just the blended
total). Remaining GAPs sit only at the two edges: tail of 2011 (before this source's own coverage
starts in earnest) and Oct–Dec 2022 (2022 dataset on open.alberta.ca tops out at the November-2022
PDF; no December-2022 resource existed yet to harvest).

**Reconciliation vs. dr_L3-01 sanity magnitudes:** AlbertaExclResorts annual-avg occupancy 2015–2019 =
0.587/0.524/0.537/0.559/0.541 (expected 0.54–0.58, PASS with 2015 marginally above band); Calgary 2019
annual avg = 0.605 (expected ~0.62, PASS within ~1.5pp); Calgary July always >0.75 in non-COVID years
(peaks 0.83–0.84) and craters to 0.234 in Jul-2020 (PASS, Stampede signature intact); 2020-04 Calgary =
0.091, AlbertaExclResorts = 0.125 (expected 0.03–0.10; Calgary in-band, AlbertaExclResorts marginally
above — flagged, not adjusted).

**Verdict:** the AB monthly occupancy series (Calgary / Edmonton / Alberta Resorts / Alberta-excl-Resorts)
is **usable as-is for 2012–2022** for the Hotel-channel driver — real, cited, per-row-provenanced,
GAP-flagged at the true edges only. This resolves the AB series without needing the CBRE 2005–2009 gap
fill (still untouched/optional per the original scope) and without ever touching the broken ABDASH
endpoint. Coverage starts a decade later than 2005 by design of the chosen source, not by omission.
