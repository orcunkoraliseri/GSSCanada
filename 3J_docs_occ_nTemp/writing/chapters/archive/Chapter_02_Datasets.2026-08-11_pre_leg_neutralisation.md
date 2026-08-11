# 2 Datasets

Four occupancy channels drive four uses inside one stacked building: Residential, Office, Retail, and
Hotel. Three of the four channels are survey-derived; the fourth, Hotel, is deliberately sourced
outside the survey frame. This chapter inventories every input the four-channel generator and its
downstream simulation campaign consume. Channel provenance is summarized in Table 2; the simulation
domain built from the weather and prototype inputs described below is summarized in Table 3.

---

### 2.1 General Social Survey Time-Use Microdata (2005-2022)

The behavioural backbone for three of the four channels is the same four cross-sectional waves of the
Statistics Canada General Social Survey (GSS) Time-Use program used in the authors' prior work
(Statistics Canada, 2022; Iseri and Hachem-Vermette, under review b): Cycle
19 (2005), Cycle 24 (2010), Cycle 29 (2015), and the GSS Time Use 2022 cycle (GSSP). Residential
(AT_HOME) and Office (AT_WORK) presence are read from the harmonized diary exactly as in the two-channel
construction stage (Leg-2; see Chapter 3). The one new GSS-derived channel added for this paper is
Retail (AT_RETAIL): a customer-presence indicator constructed from the `occPRE` (location) and `occACT`
(activity) columns that were already carried in every cycle, so no new GSS variable was collected.
`occPRE`/`occACT` location-mapping coverage is per cycle: 2005 and 2010 use `PLACE = 06+07`; 2015 uses
`LOCATION = 306`; 2022 uses `LOCATION = 3306`. Grocery and general-merchandise shopping are not
separable in the 2015 and 2022 cycles, which record a single combined shopping-location bucket; the
AT_RETAIL derivation and its frozen OR-rule are given in full in Chapter 3 (§3.1) and in Table 2's
footnote.

One population that the GSS records but that this paper's Retail channel deliberately does not model
is retail staff: workers present in a store are coded by the survey as engaged in `AT_WORK`, not as a
retail-specific activity, so no GSS signal distinguishes a shopper from a cashier. Retail worker density
therefore stays on the NECB code baseline being modulated, and the Retail channel models customer
presence only (Table 2, footnote 2).

---

### 2.2 Census Public-Use Microdata for Dwelling-Stock and Workforce Linkage

The Statistics Canada Census Public-Use Microdata File (PUMF; Statistics Canada, 2021) provides the
dwelling-stock and workforce variables used to situate Residential and Office diary respondents within a representative building and
labour-force population. This linkage stage is unchanged from the two-channel construction stage
(Chapter 3, §3.3): dwelling type, tenure, and household-size variables anchor the Residential channel,
and NOC-by-NAICS occupation/industry crosswalks anchor the Office channel. Retail and Hotel do not use
the Census PUMF linkage. Retail is modelled at the population level against a single PNNL "Retail
Retail" archetype rather than through a per-respondent Census match, because the grocery/merchandise
split needed for a finer archetype lookup is not recoverable from the 2015/2022 GSS location codes
(§2.1). Hotel has no respondent-level archetype at all: guests are entirely outside the GSS sampling
frame, so the channel is driven by a province-level multiplier rather than by any individual linkage
record (§2.3).

---

### 2.3 Provincial Tourism Statistics as a Non-Survey Channel Source

Hotel is the one channel in this paper with no General Social Survey signal behind it at all: overnight
hotel guests are, by construction, outside the GSS Time-Use sampling frame, which samples the resident
population at their dwelling of record. Injecting the Hotel channel from a GSS-derived series would
therefore systematically under-occupy hotel zones, since the survey simply never interviews a guest
in a hotel room. This is a frame limitation, not a data-quality one, and it forces the Hotel channel to
be built from an entirely separate, non-survey data family: monthly provincial tourism statistics.

No StatCan table of monthly hotel-occupancy rates exists (a data-availability check run for this study); the paper therefore draws
on the two provincial data sources available for the cities in the simulation domain. For Quebec, the
source is the Institut de la statistique du Québec (ISQ) monthly hotel-occupancy series (Institut de la
statistique du Québec). For Alberta, the source is CBRE / Travel Alberta market reporting, with the
2005-2009 span of the Alberta series spliced from CBRE National Market Report archives (CBRE Limited
and Travel Alberta). Both provincial series carry YEAR, MONTH, province
(PR), occupancy rate, average daily rate (ADR), and RevPAR fields and span 2005-2022. This
tourism-statistics series is converted to a monthly multiplier by a SARIMA model with an explicit
COVID-19 indicator (Chapter 3, §3.4); it never passes through the three-head Transformer used for the
three GSS channels, because it has no respondent-level structure to condition on (Chapter 3, §3.2).

---

### 2.4 NECB / PNNL Prototype Building Stock

The building domain is the U.S. DOE / PNNL Tall and SuperTall mixed-use tower prototypes (U.S.
Department of Energy and Pacific Northwest National Laboratory), built to the NECB-2017 standard
(National Research Council Canada, 2017), reused from the two-channel construction stage without
modification to their
geometry. Total occupiable floor area, measured directly from the model geometry rather than assumed,
is reported per prototype in Table 3. Each prototype's Space objects carry an IDF `Tag 2` field that
functions as the per-Space routing key for occupancy injection (Chapter 3, §3.5): apartment tags,
office tags, retail tags, and guest-room tags each resolve to a distinct one of the four channels,
while amenity and service/MEP tags carry no occupant-driven channel and remain on the untouched NECB
default schedule.

---

### 2.5 Weather Files

The simulation domain spans two Canadian cities selected to bracket a one-zone climate contrast within
the campaign: Montréal (ASHRAE climate zone 6A) and Calgary (ASHRAE climate zone 7A). One Typical
Meteorological Year EnergyPlus weather file (EPW) is used per city. The two prototype IDFs (Montréal,
Calgary) differ from one another by geometry-preserving, climate-tag-only edits, so that EUI differences
between the two cities can be attributed to climate rather than to any building-geometry covariate
(Table 3). All simulations run in EnergyPlus v24.2 (U.S. Department of Energy, 2024). The full two-prototype-by-two-city-by-fourteen-
scenario, 56-cell campaign built from these weather and prototype inputs is defined in Chapter 4.

---

**Table 2.** *(insert `Table_02_channels.md` here)*

