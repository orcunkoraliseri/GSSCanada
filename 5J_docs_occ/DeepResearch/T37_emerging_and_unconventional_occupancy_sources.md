# T37. Emerging and unconventional occupancy sources: what is real, what is closed, what is hype

Paste `00_MASTER_BRIEF.md` first (read its section 9). Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Run in wave 6, after `T19`. This is the catch-all; expect most rows to be closed
doors, and say so.

## Why we are asking

`T20` to `T30` cover the established source families. Other sources are appearing or disappearing:
daily night-time light from satellites, smart water meters, electric-vehicle charging data, Wi-Fi
channel sensing, connected appliances, social-media check-ins (largely closed since 2023), search
and web traffic, and synthetic data from large language models prompted to write diaries. Some of
these may be real occupancy signals; some are closed by terms of service; some are hype. We need an
honest sorting, so that none is proposed later without this check.

## What we need

### Item 1. The candidates

For each source below, one row in Section B with: what occupancy variable it carries (quoted from a
source), whether open data exist today (with a URL you opened), whether a building-energy study used
it for occupancy (with a verified identifier), and a verdict among `usable today`, `usable with
agreement`, `closed`, `unproven`.

1. Daily night-time light (NASA Black Marble VNP46) as a presence or activity signal at district scale.
2. Smart water meters and water-use data.
3. Electric-vehicle charging sessions (home charging start and stop times).
4. Wi-Fi and Bluetooth sensing, including channel-state sensing, in dwellings.
5. Connected appliances and home-assistant platforms (research data programs).
6. Social-media check-ins and geotagged posts (state the current API terms of the major platforms).
7. Web search and web-traffic indices as presence proxies.
8. Large language models prompted to produce time-use diaries or occupancy schedules.
9. Camera and computer-vision counts at building entrances (public datasets only).
10. Waste, delivery or other municipal service data as presence proxies.
11. Any other source you find in 2023 to 2026 literature.

### Item 2. LLM-written diaries specifically

Works that generated synthetic time-use diaries or occupancy schedules by prompting a language model
(not fine-tuning on diaries), and whether any compared them with a real survey. Section C rows. This
bears on our own negative result (brief section 3, item 2); report without judging that result.

### Item 3. The honest shortlist

Of item 1, which at most three are real candidates for a researcher with our assets? Name the evidence
row for each. Zero is a valid answer.

## Named leads

NASA LAADS and Black Marble documentation; utility and city water data portals; EV charging open
datasets (for example city or utility releases); arXiv `cs.CL`, `cs.CY`, `cs.HC`; *Energy and
Buildings*, *Applied Energy*, *Remote Sensing of Environment*, *Scientific Data*; BuildSys and
e-Energy proceedings.

## Hard constraints specific to this prompt

* A verdict of `usable today` needs an opened dataset URL and a verified use. Otherwise the verdict is
  `unproven` or `closed`.
* Platform API terms quoted with the date checked; they changed often after 2023.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers first: which unconventional sources are real occupancy signals available today,
and which are closed or unproven.

**Section B** is item 1. **Section C** is item 2. **Section D** is item 3 against `A14`. **Section G**
carries your negative controls.
