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
floor areas are 72,623.1 m2 (Tall) and 135,857.6 m2 (SuperTall), parsed directly from the model geometry
as the sum of floor area times multiplier over the zones counted in the building total, reproducing
EnergyPlus's own total building area exactly (Table 3). Both towers stack the same four occupiable uses,
residential, office, retail and hotel, inside one envelope, plus amenity and service space carrying no
occupant-driven channel. This is the concrete meaning of four channels driving four uses inside one
building: the campaign does not compare four separate archetype buildings, it compares two buildings
that each already contain all four uses. Figure S1 gives the measured occupiable-area share carried by
each channel in each prototype, with the service and mechanical share shown separately because it is a
share of gross rather than occupiable floor area. The two prototypes do not divide their floor area
between the four uses in the same proportions, which is what makes the prototype axis a genuine
experimental factor rather than a size rescaling.

---

**Figure S1.** *(insert `Figure_S01_occupiable_shares.png` here)* - Occupiable-area share per channel.<!-- BUILD NOTE RESOLVED 2026-08-11. All three defects below are closed, by reverting the nine schematics to the script-drawn set after correcting the scripts rather than by another generation round. Figure 1 now draws nine boxes on one row (the generated replacement drew twelve, with STEP 5, 6 and 7 each twice and one box with no title); Figure 4's before/after panels and Figure 6's wiring-gate card carry their text; Figure S2 carries all nine scenario-lever values instead of "low / default / high"; the graphical abstract's peak-hour panel now places the four channel peaks at 12.1, 11.9, 12.3 and 18.9 h with the whole building at ~15 h, which is what Section 5.3 and Figure 10 report, where the generated version spread them across 09:00 to 17:00 under the heading "Four different hours". The stage names the scripts drew in their legends (the internal Leg-1 / Leg-2 / Leg-3 codes) were replaced with the manuscript's own wording before re-rendering. Every figure in the paper is now between 535 and 943 dpi at a 7 in printed width; nine of fifteen were below 500 before. The generated artwork is preserved at writing/submission/figures/**/*.2026-08-11_pre_mpl.png.bak and in Prompts_Images/. Original note follows. The nine schematic and abstract images were replaced on 2026-08-09 with author-generated images from writing/submission/figures/Prompts_Images/, on the author's explicit instruction after the following was put in front of them and reaffirmed ("juste utiliser ces images, vas-y"). The matplotlib originals and their vector PDFs are archived at writing/figures/archive_matplotlib_2026-08-09/ and the revert is a copy back. Three things are recorded here because they are visible in the shipped artwork and a reader or an editor will see them. FIRST, and the only one that touches a number: THIS figure, S1, is a data figure. The generated version reported the SuperTall bar as "4.0.1" and the Tall bar as "0.37", neither of which is a share, drew no axis, and carried a footnote that read "Mechanical, etelorgical ancr of coherotyl electrical and plumbingnoing) as a share of GROSS floor area", which is not English. The caption above says "Measured occupiable-area share", so the caption and the artwork disagreed, and the artwork stated a value the study does not. RESOLVED 2026-08-11: a second generated version was supplied and had the same defect with different digits ("3,610" and "2,071"), so S1 was taken out of the generate-from-a-prompt route entirely and re-plotted by writing/figures/SI/figS01_shares.py, which reads writing/tables/SI/Appendix_C_corrections.md section C.1 directly. Plotting is computation, not image creation, so this stays on the assistant's side of the 2026-08-09 rule. The shipped file is now 3744 x 3016 px, about 535 dpi at a 7 in printed width, and all five channel shares carry their measured value including retail and residential-common, which even the pre-2026-08-09 matplotlib version left blank because those two segments are too thin to hold a label inside the bar. Its prompt file is marked DO NOT GENERATE. SECOND: Figure 4's lower "raw / after projection" panel renders as two empty boxes, and Figure 6's "Hard Wiring Gate" box renders two blank grey bars where its two labels should be. Neither is wrong, both are incomplete. THIRD: every generated image is 1376 x 768 px, which at the 190 mm full page width is about 184 dpi against Elsevier's 500 dpi minimum for combination art; the figures they replaced were 5400 to 6600 px at 300 or 600 dpi. The stale vector PDFs were removed from both trees rather than left to disagree with the new PNGs, so there is now no vector version of Figures 1 to 6, S1 and S2. Figures 7 to 11 and S3 were NOT touched: no generated version exists for them and they carry the paper's measured results. -->

---

### 4.2 The Two Cities

Two cities anchor the climate axis: Montréal (ASHRAE climate zone 6A) and Calgary (ASHRAE climate zone
7A). Each city is assigned its own typical-meteorological-year EnergyPlus weather file. The Montréal and
Calgary models for a given tower differ from one another by a climate-tag edit only, so that any EUI
difference observed between the two cities is attributable to climate rather than to a co-varying
geometry difference (Table 3).

---

### 4.3 The 56-Cell Campaign and Its Scenario Levers

The full campaign crosses two towers by two cities by fourteen scenarios, and all 56 cells were
simulated (Table 3). The fourteen scenarios are not an arbitrary list. One is the uninjected NECB
baseline, in which every Space runs its untouched code default schedule; it is the control behind the
office band-applicability finding of Chapter 5. Four are the historical GSS cycle years. In 2022 all
four channels are injected at their observed product, while in 2005, 2010 and 2015 only office, retail
and residential are: Hotel is deliberately absent from the three earlier years, because the provincial
tourism-statistics series behind it does not reach a matching pre-2019 Quebec coverage, a gap carried
into the limitations reported in Table 7. Three more scenarios are the 2030 forecast, bundled at a
conservative, a central and an optimistic combination of the per-channel levers, with the central bundle
as the reference point the sensitivity scenarios are measured against. The remaining six are
single-axis sensitivity variants of that central bundle, two per lever channel: the office variants
swap the work-from-home band to its conservative or fully-hybrid value, the retail variants swap only
the in-store share, and the hotel variants swap only the SARIMA band, in each case leaving the other
levers at their central draw.

Each of the three GSS-linked channels therefore carries exactly one 2030 lever, the office
work-from-home band, the retail in-store share (0.90, 0.97 default, 1.05) and the hotel SARIMA band
(0.92, 1.00, 1.05), and each is exercised both jointly in the three bundles and in isolation in its own
pair of sensitivity scenarios (Table 2). Residential carries no independent lever. Its 2030 product is
generated by the same function, keyed off the same work-from-home parameter, as the office product, so
the two channels share one axis rather than each carrying its own; residential is swapped together with
office whenever that lever moves. This is the concrete sense in which residential has no lever: not a
null axis, but no axis independent of office's. Figure S2 lays the four channels' levers side by side,
so that the absence is legible as a design decision rather than as an omission.

---

**Figure S2.** *(insert `Figure_S02_scenario_levers.png` here)* - One scenario lever per channel.

---

### 4.4 Two Mandatory Probes

Two output-side probes are run before any campaign cell is accepted, and both exist because of the
defect described in §3.5: a modulated schedule referenced by the wrong field passed every input-side
check available at the time and was caught only when its simulated output failed to differ from an
unmodulated run. An input-side field assertion closes that blind spot but cannot, by itself, guarantee
that a campaign's outputs carry the scenario signal they are supposed to carry.

The first probe tests scenario differentiation. Two distinct scenarios must produce simulation outputs
that differ from one another; a pair supposed to differ in occupant schedule but returning identical
output is an automatic fail, on the same logic as the original defect, because a schedule that looks
correct on disk but never reaches the simulated result is indistinguishable, at the output, from no
injection at all.

The second is a stale-output guard. Any change to the injector, or to the schedule products it consumes,
invalidates cell outputs produced before that change. A campaign resume mechanism that treats an
already-populated output as done, without checking whether the code or the inputs behind it have since
moved, allows two incompatible result sets to occupy the same place with no trace of which is current.
The guard first implemented fingerprinted only the injector; it was extended to cover the schedule
products as well, because a scenario's schedule content, not only the injector code, determines what
gets injected.

The differentiation probe is listed in Table 4 alongside the wiring assertion. The stale-output guard is
a campaign-orchestration control rather than a per-cell validation metric, and is not a Table 4 row.

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

**Table 3.** *(insert `Table_03_sim_domain.md` here)* - Simulation domain, 56 campaign cells.

