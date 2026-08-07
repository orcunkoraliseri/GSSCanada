# V07. An open, machine-readable Quebec hotel-occupancy series covering 2011–2018

Read `00_MASTER_BRIEF_V2.md` first for shared context, and answer in the schema of
`_RESPONSE_TEMPLATE.md` (Sections A to H).

---

## Why we are asking

The hotel channel of our four-split occupancy model is injected with measured monthly occupancy
rates. **Alberta is solved**: the *Alberta Tourism Market Monitor* is published as open PDFs on
`open.alberta.ca` under the Open Government Licence, and we extracted a continuous monthly series
for **2011–2022** from it (source tag `ABMKTMONITOR`).

**Quebec is not.** The Institut de la statistique du Québec publishes the equivalent
hotel-establishment occupancy statistics through a **Power BI front end** with no download endpoint
we have been able to reach, and every open equivalent we have looked at starts at **2019**.

The consequence is concrete and currently written into our results as a limitation: the hotel channel
is **uninjected before 2019**, which makes one of our longitudinal gates (`S9-LONG-hotel`) pass for
the wrong reason — it passes because there is nothing to compare, not because the model agrees with
anything. **We would rather fix the data than keep explaining the hole.**

We are not asking whether Quebec hotel occupancy data exists. We know it does. We are asking for a
**retrievable, citable, pre-2019 monthly series**, or a defensible statement that none is public.

---

## What we need

1. **A monthly (or at minimum quarterly) hotel/tourist-accommodation occupancy-rate series for
   Quebec covering some or all of 2011–2018**, in a form that can be downloaded without a login: CSV,
   XLSX, PDF table, or a documented API/CKAN endpoint. State the **exact URL** and the **file format**.
2. **The geographic and establishment scope of whatever you find** — province-wide, or by tourism
   region (Montreal, Quebec City, and the rest), and whether it covers hotels only or all
   tourist-accommodation establishments. Our Alberta series is province-wide monthly; say plainly
   whether the Quebec series is comparable or not.
3. **The definition of the occupancy rate used** — rooms occupied over rooms available, over the
   whole month, and whether seasonally closed establishments are in the denominator. Two series with
   the same name and different denominators are not interchangeable, and we need to know which we
   would be splicing.
4. **Whether the ISQ Power BI dashboard has a documented data endpoint.** Power BI reports frequently
   expose an underlying dataset. If a stable query or export URL exists, give it; if the only access
   is interactive, **say so explicitly** — that is a usable answer and it closes the question.
5. **Any published archive of the pre-Power-BI product.** ISQ and Tourisme Québec circulated bulletins
   in PDF for years before the dashboard existed. A discontinued bulletin series with monthly tables
   would fully solve this.
6. **If nothing open exists, the terms of the closed route** — who licenses the historical series,
   whether it is available to academic researchers, at what cost, and with what redistribution
   restriction. We need to know whether a number obtained this way could be **published** in a paper.

---

## Named leads

- **Institut de la statistique du Québec (ISQ)** — `statistique.quebec.ca`; the *hébergement
  touristique* / occupancy statistics; look specifically for discontinued bulletin series and for
  `.csv`/`.xlsx` under any "données détaillées" or "tableaux statistiques" heading.
- **Données Québec** (`donneesquebec.ca`) — the province's **CKAN** open-data portal. CKAN exposes a
  package-search API; Alberta's equivalent is exactly how the AB series was found, so this is the
  single most likely place for a machine-readable answer.
- **Tourisme Québec / Ministère du Tourisme** — *Le tourisme en bref*, *Bulletin touristique*, and
  any monthly performance bulletin; check for a PDF archive of superseded issues.
- **Statistics Canada** — the *Traveller Accommodation Services* survey and the monthly
  accommodation series; provincial tables may carry Quebec occupancy on a **different definition**,
  which is still useful if item 3 is answered. Give the exact table number.
- **CBRE Hotels / STR (Smith Travel Research)** — commercial, and named here only for item 6. **We do
  not have and have never obtained CBRE data**; do not report a CBRE figure as if retrievable.
- **Association Hôtellerie Québec**, and university tourism-research chairs (UQAM, Université Laval)
  that may have archived the historical series in published work.

---

## Deliverable

Section A must contain a **direct verdict on one question**: *is there an open, downloadable Quebec
hotel-occupancy series covering any part of 2011–2018?* Answer **YES with a URL**, or **NO with the
set of places checked**. A list of promising-looking links is not an answer to this.

If YES, include a **table of the actual monthly values** for at least one full year, transcribed from
the source you opened, plus the URL and the retrieval date, so we can verify the extraction before we
build anything on it.

If NO, Section A must say so in one sentence, and Section B must list **what was checked and how** —
portal, search terms, and what came back — so the negative result is reusable and we do not pay to
discover the same nothing twice.

**Rules that apply to this prompt, restated:**

- **A citation is not evidence until you have opened it.** Do not report a table's contents from a
  search-result snippet.
- **Verify any DOI via `https://api.crossref.org/works/<DOI>`**, and verify report numbers by opening
  the PDF and reading the table.
- **`NOT FOUND` beats an invented number.** Every previous round of this project's deep research
  contained at least one fabricated figure, and all of them were caught by arithmetic afterwards. A
  plausible-looking occupancy rate that does not exist in any document costs us more than an empty
  cell.
- **Never propose relaxing a threshold or band because our model fails it.** That is not what this
  question is for.
- **Keep as-modelled and empirical figures strictly separate**, and label every number as one or the
  other.
- **No em dashes or en dashes in the returned text.**
