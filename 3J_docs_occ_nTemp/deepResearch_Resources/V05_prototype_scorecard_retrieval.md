# V05. Prototype scorecard retrieval: per climate zone EUI, with a direct file URL for every number

Paste `00_MASTER_BRIEF_V2.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
Sections C, D and E are **not used** in this prompt; write `not applicable to this prompt` under each.
**Section B and Section H are the deliverable, and Section B is worthless without Section H's URLs.**

This prompt is narrow on purpose. It asks for **retrieval**, not analysis. Do not interpret, do not
recommend, do not compare against our model. Get the numbers and prove where they came from.

## Why we are asking

Three previous rounds (`RV01`, `RV02`, `RV04`) tried to establish per climate zone prototype EUI across
code vintages. All three failed in the same way, and the failure is instructive:

* **They disagree with each other on the report number.** For the ASHRAE 90.1-2019 savings analysis,
  `RV01` says `PNNL-31488` (DOE/EE-2364, Salcido et al. 2021) and `RV02` and `RV04` say `PNNL-29780`.
  For 90.1-2016, `RV01` says `DOE/EE-1614` (Athalye et al. 2017) while `RV02` and `RV04` say
  `PNNL-26348`, which is one digit from `PNNL-26343`, a number we had already established does not
  resolve. At most one of each pair can be right.
* **They disagree on whether the data exists at all.** `RV01` Section G states that per prototype and
  per climate zone matrices are **not** printed in the narrative determination reports and must be
  taken from scorecard workbooks distributed with the model releases. `RV02` and `RV04` then quote
  precise per zone values (41.2, 43.2, 74.2, 78.3 kBtu/ft2.yr and others) attributed to those same
  narrative reports.
* **Every number carried the same landing page URL**, `https://www.energycodes.gov/prototype-building-models`,
  for three different reports, each marked "Read full text". A landing page is not a document.
* **The same report number came back with two different titles.** `PNNL-28543` was reported as
  *Charpy V-Notch Impact Testing of High-Burnup Spent Fuel Cladding* in one round and *PNNL's
  Intermediate Characterization Summary for the MP-1 Experiment* in another.

So we do not yet know whether the per climate zone data is retrievable. That single question is what
this prompt exists to settle.

## What we need

1. **Establish the retrieval path, step by step, before any numbers.** Starting from
   `energycodes.gov`, document the exact route to the commercial prototype building model results:
   which page, which link, which file. Name the file, its format, its size and its publication or
   revision date. If the route runs through a different host (`osti.gov`, `pnnl.gov`, an S3 bucket, a
   GitHub release), say so. **Write this route out so we can walk it ourselves without you.**

2. **The numbers, each with its own direct file URL.** Site EUI, all-fuel, for **Large Office**,
   **Medium Office**, **Large Hotel**, **Small Hotel**, **Stand-Alone Retail** and **Strip Mall**, at
   **climate zone 6A** and **climate zone 7**, for ASHRAE **90.1-2004, 2010, 2013, 2016 and 2019**.
   Give the value in its published units and converted to kWh/m2.yr, with the arithmetic shown.
   For every single row, Section H must carry a URL that **resolves directly to the file the number
   was read from**: an `.xlsx`, `.csv`, `.pdf` or an OSTI document page. **A landing page, a search
   page or a programme homepage is not acceptable and the row must be marked `NOT RETRIEVED` instead.**

3. **End use breakdown where the scorecards carry one.** Space heating, cooling, fans, interior
   lighting, interior equipment, service water heating. Both as a share of site energy and as an
   absolute EUI. This is the most diagnostic material in the whole V series and we would rather have
   it for two prototypes than have totals for six.

4. **Resolve the report number conflicts, by opening the documents.** For each of `PNNL-31488`,
   `PNNL-29780`, `DOE/EE-1614`, `PNNL-26348`, `PNNL-26343`, `PNNL-28543` and `PNNL-19590`: report the
   **actual title** the document carries, its authors, its year, and the URL you opened. Where a
   number does not resolve, say `DOES NOT RESOLVE` and give the URL that failed. We want a small
   table mapping report number to real title, because we currently hold three mutually inconsistent
   versions of this mapping.

5. **Confirm or refute the 90.1-2004 anchor.** Our local file gives Large Office 54.7 and 55.9
   kBtu/ft2.yr, Large Hotel 90.8 and 95.8, Small Hotel 73.2 and 77.6, Stand-Alone Retail 34.8 and
   35.1, Strip Mall 46.6 and 48.5, for zones 6A and 7 respectively. `RV01` attributed these to Deru et
   al. (2011), NREL/TP-5500-46861, also numbered PNNL-19590. **Open that document and say whether
   those exact values appear in it**, with the table number. If they do not, say where they do come
   from, or `NOT FOUND`.

6. **State plainly whether the data exists.** If, after working the retrieval path, the per climate
   zone per vintage matrix is not publicly retrievable, **say so in Section A's first sentence** and
   spend the rest of the report documenting exactly what you tried and what is published instead.
   That is a complete and useful answer. It is far better than a filled table we cannot trace.

## Named leads

`energycodes.gov` commercial prototype building models and their scorecard and results workbooks;
the same programme's model release archives, which are versioned per 90.1 edition; OSTI full text
search by report number; `pnnl.gov` publications; the EnergyPlus prototype model file sets;
NREL publication database for NREL/TP-5500-46861.

## Hard constraints specific to this prompt

* **Do not state, estimate or reproduce any output of our model.** Previous rounds filled the
  "our model's comparable output" column with numbers they could not have had, and those numbers were
  wrong: they inverted the relationship between our two cities. In Section F, leave that column as
  `not supplied` for every row. We will fill it ourselves.
* **Do not propose changing any band.** Not the office floor, not the hotel ceiling or floor, not the
  retail band. This prompt gathers evidence only. Every previous round recommended a change that
  happened to make our failing gate pass, and that pattern is why this prompt is written this way.
* **Do not derive a value by applying a national percentage to a climate zone figure.** A national
  average savings percentage multiplied by a zone specific baseline is an inference, not a measurement.
  If that is all that is available, put it in Section G as an inference with its assumptions stated,
  never in Section B.
* **Do not mark anything "Read full text" unless you opened that specific file.** If you read a
  landing page, an abstract, a search result or a cached snippet, say exactly that.

## Deliverable

Section B: one row per prototype x vintage x climate zone, each traceable to a file. Rows you could
not retrieve stay in the table marked `NOT RETRIEVED`, so we can see the shape of the gap.

Section G: the report number to real title mapping from item 4; the retrieval route from item 1 if it
failed partway; and every URL that 404'd.

Section H: a direct, resolving file URL for every number in Section B, and an explicit statement per
entry of what you actually opened.

A table with eight rows we can verify is worth more to us than a table with sixty we cannot.
