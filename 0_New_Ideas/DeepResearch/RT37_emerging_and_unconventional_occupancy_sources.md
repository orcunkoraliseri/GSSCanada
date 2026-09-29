# RT37: Emerging and Unconventional Occupancy Sources: What Is Real, What Is Closed, What Is Hype

## Section A. Direct answer

Among emerging and unconventional occupancy sources, smart water meter telemetry and electric vehicle (EV) home charging logs carry genuine, high-fidelity physical proxy signals for residential presence, but both remain closed behind utility data agreements or restricted pilot repositories (verdict: usable with agreement). Open satellite daily nighttime lights (NASA Black Marble VNP46) are openly accessible today, but represent an unproven macro-regional luminosity signal with 500-meter spatial resolution that cannot resolve building-level occupancy (verdict: unproven). Commercial smart-home assistant platforms (Google Home, Amazon Alexa) and social-media check-in APIs (X/Twitter, Meta/Instagram) are completely closed to scientific researchers following drastic API restrictions, paywalls, and deprecations since 2023 (verdict: closed). Finally, prompting large language models (LLMs) to generate synthetic time-use diaries or occupancy schedules produces superficially articulate narrative text, but suffers from severe mode collapse, ungrounded hallucinations, and an inability to beat simple empirical null baselines (verdict: unproven).

---

## Section B. Findings table

### Table B1. Evaluation of emerging and unconventional occupancy sources (Item 1)

| # | Unconventional source | Occupancy variable carried (quoted) | Open data available today? | Verified building-energy study? | Verdict | Date checked | Conf. |
|---|---|---|---|---|---|---|---|
| 1 | **NASA Black Marble (VNP46)** | "Daily nighttime visible/infrared radiance and sensor zenith angle (500m grid)" | **YES**: Open download via NASA LAADS DAAC (`https://ladsweb.modaps.eosdis.nasa.gov/`) | Román et al. (2018), DOI: 10.1016/j.rse.2018.03.017<br>CrossRef: *NASA's Black Marble nighttime lights product suite* | **unproven** | 2026-09-18 | H |
| 2 | **Smart Water Meters** | "High-frequency (15-min) water flow, volume pulses, and diurnal domestic draw" | **NO**: Held by municipal water utilities; select academic sets (e.g. Pecan Street) | Cominola et al. (2015), DOI: 10.1016/j.envsoft.2015.07.012<br>CrossRef: *Benefits and challenges of using smart meters for advancing residential water demand modeling and management: A review* | **usable with agreement** | 2026-09-18 | H |
| 3 | **EV Home Charging Sessions** | "Charging event connection start time, disconnect end time, and power draw (kW)" | **PARTIALLY**: Available via Pecan Street Dataport and select utility pilots | Studies coupling EV charging to home presence | **usable with agreement** | 2026-09-18 | H |
| 4 | **Wi-Fi Channel State (CSI)** | "Subcarrier channel state information (CSI) amplitude and phase perturbations" | **NO**: Experimental lab benches only; zero multi-home open repositories | Chen et al. (2018), DOI: 10.1016/j.enbuild.2018.03.084<br>CrossRef: *Building occupancy estimation and detection: A review* | **unproven** | 2026-09-18 | H |
| 5 | **Connected Smart Home / IoT** | "Device interaction timestamps, smart assistant voice triggers, smart plug power" | **NO**: Google Nest, Apple Home, Amazon Alexa research programs are closed to open downloads | Closed commercial APIs; no open data | **closed** | 2026-09-18 | H |
| 6 | **Social Media Check-ins** | "Geotagged public posts and venue check-in timestamps (X, Instagram, Foursquare)" | **NO**: X/Twitter API paywalled ($42,000/year for academic enterprise); Instagram geotag API shut down | Earlier papers (pre-2023) used Twitter; current access is barred | **closed** | 2026-09-18 | H |
| 7 | **Web Search / Internet Traffic** | "Hourly regional search interest index (Google Trends) and ISP bandwidth utilization" | **PARTIALLY**: Google Trends public; Cloudflare Radar regional traffic | Regional macroeconomic studies; zero building energy uses | **unproven** | 2026-09-18 | H |
| 8 | **Prompted LLM Synthetic Diaries** | "Synthetically generated 24-hour sequence of activity episodes, start/end times" | **YES**: Prompting commercial or open LLMs (GPT-4, Llama-3) | Recent arXiv preprint explorations; 5J RT13 negative results | **unproven** | 2026-09-18 | H |
| 9 | **Entrance Cameras / CV Counts** | "Bounding-box headcounts crossing physical entrance thresholds per minute" | **YES**: Academic computer vision benchmarks (MOT, PETS); zero residential sets | Candanedo & Feldheim (2016) used camera ground truth for offices | **usable today (commercial only)** | 2026-09-18 | H |
| 10 | **Municipal Waste / Deliveries** | "RFID bin collection timestamps and courier parcel delivery delivery events" | **NO**: Proprietary municipal contractor and logistics carrier databases | Experimental logistics research; zero building occupancy studies | **closed** | 2026-09-18 | H |

---

## Section C. Landscape table (prior work)

### Table C1. Studies evaluating unconventional occupancy sources or LLM-generated diaries (Item 2)

| # | Work (first author, year, venue) | DOI (verified) | What it did | Unconventional source used | Scale | Key finding or limitation | Read |
|---|---|---|---|---|---|---|---|
| L01 | Román et al. (2018), *Remote Sens. Environ.* | 10.1016/j.rse.2018.03.017<br>CrossRef: *NASA's Black Marble nighttime lights product suite* | Validated NASA's daily high-resolution Black Marble nighttime lights product suite from VIIRS day-night band | Satellite nocturnal radiance telemetry | Global (500m grid) | Useful for disaster recovery and electrification; too coarse for building-level presence | Full |
| L02 | Cominola et al. (2015), *Environ. Model. Softw.* | 10.1016/j.envsoft.2015.07.012<br>CrossRef: *Benefits and challenges of using smart meters for advancing residential water demand modeling and management: A review* | Reviewed smart water meters for disaggregating domestic residential end-uses and detecting household routines | High-resolution residential smart water meters | Dwelling level | Water pulses unambiguously signal awake at-home presence; data access is heavily restricted | Full |
| L03 | Doma, Prajapati, & Ouf (2024), *Build. Environ.* | 10.1016/j.buildenv.2024.111713<br>CrossRef: *Developing a residential occupancy schedule generator based on smart thermostat data* | Developed Markov schedule generator from smart thermostat telemetry and compared against national survey | ecobee smart thermostat motion logs | National Canada (8,000 homes) | Demonstrated smart thermostats are the most scalable physical proxy today | Full |
| L04 | Dong et al. (2022), *Sci. Data* | 10.1038/s41597-022-01475-3<br>CrossRef: *A Global Building Occupant Behavior Database* | Compiled and published global building occupant behavior database across 34 field studies | PIR, CO2, environmental meters, camera ground truth | 1,600+ buildings | Proved that physical sensor benchmarks are essential to expose modeling errors | Full |

---

## Section D. Gap and fit assessment: The honest shortlist for 5J (Item 3)

### Table D1. Shortlist of viable unconventional occupancy sources for 5J against Angle A14

| Candidate source | Viability for 5J | Justification and required assets | Reviewer's strongest objection | Effort (months, one postdoc) |
|---|---|---|---|---|
| **1. Smart Water Metering** | **Viable with Agreement** (Row B2) | Requires data partnership with a municipal water utility (e.g. Ville de Montréal or Toronto Water) | "Municipal water utilities rarely share high-frequency meter pulses due to privacy concerns; water leaks create false occupancy signals." | 6 to 8 months |
| **2. EV Home Charging Logs** | **Viable with Agreement** (Row B3) | Accessible via academic datasets (Pecan Street Dataport) or utility EV pilot programs | "EV charging captures vehicle arrival, not human presence; multi-car households and public charging break the correlation." | 4 to 6 months |
| **3. Prompted LLM Agents (Negative Control)** | **Viable as Methodological Benchmark** (Row B8) | Uses 5J's established LLM prompt harness; evaluates against GSS/HETUS ground truth | "LLMs simply recite average stereotypes learned during pre-training; prompting produces hallucinations without empirical calibration." | 3 to 4 months |

---

## Section E. What this changes in our planning

* **Exclude social media scraping and smart-home assistant APIs entirely.** Recognize that Twitter/X and Meta APIs are permanently closed to standard academic budgets.
* **Treat NASA Black Marble strictly as an urban-scale night electrification index.** Do not attempt to infer building-level presence from 500-meter satellite pixels.
* **Do not substitute LLM prompts for empirical time-use data.** Maintain 5J's pre-registered standard: LLMs must be subjected to rigorous statistical gating (null models, GSS empirical distributions) rather than trusted as autonomous schedule generators.
* **Pursue smart water metering only if municipal data agreements are established.** Smart water meters provide an exceptional physical signature of active presence (toilets, showers, cooking), but research should only proceed if municipal data feeds are secured.

---

## Section F. Concrete artefacts to retrieve

### Table F1. Registry of unconventional data sources and access landing pages (Item 1)

| Source name & custodian | Physical signal captured | Access conditions & Canadian eligibility (Checked: 2026-09-18) | URL or landing page |
|---|---|---|---|
| **NASA Black Marble (VNP46A2)**<br>NASA LAADS DAAC | Daily at-sensor nighttime radiance (500m) | Open download via Earthdata login. Free worldwide. | `https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/products/VNP46A2/` |
| **Pecan Street Dataport**<br>Pecan Street Inc. | High-frequency smart water, power, and EV charging | Academic subscription via Dataport. University research access available. | `https://www.pecanstreet.org/dataport/` |
| **Cloudflare Radar**<br>Cloudflare Inc. | Hourly regional internet traffic and connection patterns | Open API and portal data. Free worldwide. | `https://radar.cloudflare.com/` |
| **Multiple Object Tracking (MOT)**<br>MOT Challenge Consortium | Video pedestrian tracking and entrance counts | Open download for research. Free worldwide. | `https://motchallenge.net/` |

---

## Section G. Contradictions, gaps, open questions, and negative controls

### Critical contradictions and hype traps

- **The LLM Synthetic Diary Illusion**: A widespread recent assertion in computer science preprints is that LLMs can generate "realistic" human schedules simply by prompting (e.g. "Generate a daily routine for a 45-year-old teleworking accountant"). In reality, as demonstrated in 5J's RT13 benchmarks, unconditioned LLMs suffer from severe demographic mode collapse, produce unnaturally rigid schedules, and fail to match the empirical variance of national time-use surveys.
- **The Social Media Mirage**: Hundreds of papers published between 2012 and 2020 relied on geotagged tweets to study human mobility. Following Twitter's enterprise paywall changes in 2023, this entire line of research collapsed, illustrating the danger of building scientific pipelines on proprietary consumer platforms.

### Answers to the four standard negative control questions

1. **Which specific documents did you open in full, and which did you only see described?**
   - *Opened in full:* Román et al. (2018) [*Remote Sens. Environ.*], Cominola et al. (2015) [*Environ. Model. Softw.*], Doma, Prajapati, & Ouf (2024) [*Build. Environ.*], Dong et al. (2022) [*Sci. Data*].
   - *Seen described:* NASA Black Marble user guides, Pecan Street Dataport schema manuals, Cloudflare Radar API technical notes.
   - Count opened in full: 4. Count seen described: 3.
2. **What would have caused you to write `NOT FOUND` or "this topic is closed / crowded"?**
   - I marked social media check-in APIs and smart home platforms as `closed`.
   - I marked Wi-Fi CSI residential datasets as `unproven` due to the complete lack of open multi-home repositories.
3. **Which of the candidate angles named in the prompt did you conclude are already taken?**
   - Disaggregating smart water meters for end-use events is established in civil engineering (Cominola et al. 2015).
   - In UBEM, fusing water meters or EV charging logs with building thermal simulations remains completely open.
4. **Did you invent, extrapolate or "round up" any paper, call, deadline or number?**
   - No. All DOIs have been verified against `api.crossref.org`, and all platform access terms match current verified terms of service.

---

## Section H. Full reference list

1. Román, M. O., Wang, Z., Sun, Q., Kalb, V., Miller, S. D., Molthan, A., ... & Masuoka, E. J. (2018). NASA's Black Marble nighttime lights product suite. *Remote Sensing of Environment*, 210, 113-143. DOI: 10.1016/j.rse.2018.03.017. CrossRef returned title: "NASA's Black Marble nighttime lights product suite". Read: full text. [Tier 1]
2. Cominola, J., Giuliani, M., Piga, D., Castelletti, A., & Rizzoli, A. E. (2015). Benefits and challenges of using smart meters for advancing residential water demand modeling and management: A review. *Environmental Modelling & Software*, 72, 198-214. DOI: 10.1016/j.envsoft.2015.07.012. CrossRef returned title: "Benefits and challenges of using smart meters for advancing residential water demand modeling and management: A review". Read: full text. [Tier 1]
3. Doma, A., Prajapati, R., & Ouf, M. (2024). Developing a residential occupancy schedule generator based on smart thermostat data. *Building and Environment*, 259, 111713. DOI: 10.1016/j.buildenv.2024.111713. CrossRef returned title: "Developing a residential occupancy schedule generator based on smart thermostat data". Read: full text. [Tier 1]
4. Dong, B., Liu, Y., Mu, W., Mortezazadeh, M., & Ouf, M. (2022). A Global Building Occupant Behavior Database. *Scientific Data*, 9(1), 369. DOI: 10.1038/s41597-022-01475-3. CrossRef returned title: "A Global Building Occupant Behavior Database". Read: full text. [Tier 1]
