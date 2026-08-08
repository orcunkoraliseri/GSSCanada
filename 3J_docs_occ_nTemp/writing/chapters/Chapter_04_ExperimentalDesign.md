# 4 Experimental Design

The simulation campaign is organised as a fully-specified factorial experiment whose domain is
summarised in Table 3: two tower prototypes, two cities, and fourteen scenarios, for 56 cells in total.
Four occupancy channels drive four uses inside one stacked building at every cell; the campaign design
exists to isolate, as far as a single-building study can, which of those four uses' temporal signal is
responsible for a given change in simulated output.

---

### 4.1 The Two Towers

The building domain is two PNNL mixed-use tower prototypes, Tall and SuperTall, reused without
modification to their geometry from the two-channel construction stage. Their measured total occupiable
floor areas are 72,623.1 m2 (Tall) and 135,857.6 m2 (SuperTall) - parsed directly from the model
geometry as the sum of Space `FloorArea x Multiplier` over `IsPartOfTotalArea = 1` zones, reproducing
EnergyPlus's own Total Building Area exactly (Table 3). Both towers stack the same four occupiable uses
- residential, office, retail, hotel - inside one building envelope, plus amenity and service/MEP space
that carries no occupant-driven channel. This is the concrete meaning of "four channels driving four
uses inside one building": the campaign does not compare four separate archetype buildings, it compares
two buildings that each already contain all four uses. Figure S1 gives the measured occupiable-area
share carried by each channel in each prototype, with the service and mechanical share shown separately
because it is a share of gross floor area rather than of occupiable area; the two prototypes do not
divide their floor area between the four uses in the same proportions, which is what makes the
prototype axis a genuine experimental factor rather than a size rescaling.

---

**Figure S1.** *(insert `Figure_S01_occupiable_shares.png` here)* - Measured occupiable-area share per channel for both tower prototypes, with the service and mechanical share shown separately because it is a share of gross floor area rather than of occupiable area.

---

### 4.2 The Two Cities

Two cities anchor the climate axis: Montréal (ASHRAE climate zone 6A) and Calgary (ASHRAE climate zone
7A). Each city is assigned its own TMY EnergyPlus weather file. The Montréal and Calgary IDF for a given
tower differ from one another by a climate-tag edit only, so that any EUI delta observed between the two
cities is attributable to climate rather than to a co-varying geometry difference (Table 3, and its
footnote on the Calgary EPW's on-disk `_6B` filename versus its campaign-assigned `Z7A` climate-zone
label).

---

### 4.3 The 56-Cell Campaign and Its Scenario Levers

The full campaign crosses 2 towers x 2 cities x 14 scenarios = 56 cells, all 56 simulated (Table 3
footer). The fourteen scenarios are, by design, not an arbitrary list: one scenario is the uninjected
NECB baseline; four are the historical GSS cycle years; three are the 2030 forecast bundled at a
conservative, central, and optimistic band; and six are single-axis sensitivity variants built on top of
the central 2030 bundle, two per scenario-lever channel.

- **Default (NECB).** No occupancy injection at all - every Space runs its untouched NECB default
  schedule. This is the uninjected control behind the office band-applicability finding in the
  Limitations chapter (⚠ check source for its full quoted EUI value, which belongs to Table 5 / Chapter
  5, not to this chapter).
- **2022.** All four channels injected at their observed-2022 GSS/tourism-statistics product.
- **2005, 2010, 2015.** The three earlier historical GSS cycle years, with office, retail, and
  residential injected; Hotel is deliberately absent from all three historical years, because the
  provincial tourism-statistics series behind the Hotel channel does not extend to a matching pre-2019
  Quebec coverage for these years (§4.4, and Chapter 7's limitation on the pre-2019 hotel gap).
- **B-cons, B-central, B-opt (2030).** The three named 2030 bundles, one per conservative / central /
  optimistic combination of the per-channel scenario levers below, with B-central as the reference point
  the six sensitivity scenarios are built against.
- **sens_office_cons, sens_office_opt.** B-central with the Office WFH band swapped to conservative or
  fullyhybrid. Residential is swapped together with Office in both of these scenarios, not
  independently: Residential's 2030 product is produced by the same function, keyed off the same
  office-band parameter, as Office's own 2030 product, so the two channels share one lever rather than
  each carrying its own. This is the concrete sense in which "Residential has no lever" (Table 2):
  Residential does not have a null 2030 axis, it has no axis independent of Office's.
- **sens_retail_cons, sens_retail_opt.** B-central with only the Retail in-store-share csv swapped to
  its conservative or optimistic 2030 value; Office and Residential stay at their central-band draw.
- **sens_hotel_cons, sens_hotel_opt.** B-central with only the Hotel SARIMA-band csv swapped to its
  conservative or optimistic 2030 value; Office and Residential stay at their central-band draw.

Each of the three GSS-linked channels therefore carries exactly one 2030 scenario lever - Office's WFH
band (conservative / hybrid / fullyhybrid), Retail's in-store share (0.90 / 0.97 default / 1.05), and
Hotel's SARIMA band (0.92 / 1.00 / 1.05) - and each lever is exercised both jointly, in the three B-*
bundles, and in isolation, in the corresponding pair of sens_* scenarios (Table 2). Residential carries
no independent lever of its own; its 2030 product moves only as a consequence of the Office WFH band, a
design choice made explicit in the campaign's own scenario-construction code rather than left implicit.
Figure S2 lays the four channels' levers side by side, so that Residential's deliberate absence of an
independent axis is legible as a design decision rather than as an omission.

---

**Figure S2.** *(insert `Figure_S02_scenario_levers.png` here)* - One scenario lever per channel: office, retail and hotel each carry a single three-position lever that can be re-run independently, and residential deliberately carries none.

---

### 4.4 Two Mandatory Probes

Two output-side probes are run before any Leg-3 campaign cell is accepted, and both exist because of a
specific defect found in the two-channel construction stage: a modulated schedule referenced by the
wrong IDF field passed every input-side check available at the time and was caught only when its
simulated output failed to differ from an unmodulated run (Chapter 3, §3.5). An input-side field
assertion closes that particular blind spot, but does not, by itself, guarantee that a campaign's
outputs actually carry the scenario signal they are supposed to carry. The two probes below are the
output-side complement to that input-side assertion.

**Probe 1 - scenario-differentiation.** Two distinct scenarios - for example B-central versus
sens_retail_opt - must produce EnergyPlus outputs that differ from one another. A pair of scenarios that
are supposed to differ in occupant schedule but return byte-identical simulation output is treated as an
automatic fail, on the same logic as the construction-stage defect: a schedule that looks correct on
disk but never reaches the simulated result is indistinguishable, at the output, from no injection at
all.

**Probe 2 - stale-output guard.** A wiring fix to the injector - or, more generally, any change to the
Step-7 schedule products the injector consumes - invalidates previously completed ("skip_done") cell
outputs that were produced before the fix. A campaign resume mechanism that silently treats an
already-populated output directory as done, without checking whether the code or the input products that
produced it have since changed, can allow two incompatible result sets to occupy the same output path
with no trace of which one is current. The guard that was first implemented fingerprinted only the
injector script itself; a subsequent correction extended it to also cover the Step-7 product files,
because a scenario's schedule content, not only the injector code, determines what gets injected, and a
changed product file with an unchanged injector script would otherwise leave a stale result undetected
at the same output path.

The scenario-differentiation probe is listed in Table 4 alongside the wiring field-reference assertion,
under the wiring-and-differentiation gate group made mandatory by the two-channel construction stage's
own lesson. The stale-output guard is a campaign-orchestration control rather than a per-cell validation
metric, and for that reason is not itself a Table 4 row; it is documented in the Step-8 campaign
implementation record cited below.

---

## Sources (this chapter)

- `Leg3_4-split/Step8_docs/3rdJ_08D_campaign_cells.py`, lines 1-70 (14-scenario list, the
  `sens_office_*` shared residential/office axis and its code-level justification, `Default_NECB`
  tag) and lines 350-367 (hotel deliberately absent from 2005/2010/2015).
- `Leg3_4-split/Step8_docs/3rdJ_08_implementation_improvements.md`: "Etat verrouille au 2026-07-28"
  table (IDF reuse, 36-byte MTL/CLG delta, channel-isolation), residential-channel correction note
  (4 channels on Y2022/B_*/sens_*, 3 on historicals, 0 on Default_NECB), "Defaut 3" section (stale
  output guard, injector-only fingerprint and its Step-7-product blind spot, corrected 2026-07-28),
  "Defaut 7" section (parsed occupiable-share and total-area figures for both towers).
- `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md`, STEP 8 box (two mandatory probes,
  scenario list summary, EUI gate bands) and `## VALIDATION GATES` (b)/(c) tables.
- `writing/tables/Table_02_channels.md` - per-channel scenario lever values.
- `writing/tables/Table_03_sim_domain.md` - tower areas, cities, climate zones, cell count.
- `writing/tables/Table_04_validation_gates.md` - wiring and scenario-differentiation gate rows.

No em dashes or en dashes.

---

**Table 3.** *(insert `Table_03_sim_domain.md` here)*

**Table 4.** *(insert `Table_04_validation_gates.md` here)*

