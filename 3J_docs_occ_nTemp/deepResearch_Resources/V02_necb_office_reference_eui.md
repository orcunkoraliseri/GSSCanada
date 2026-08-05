# V02. NECB 2017/2020 office reference EUI for Canadian climate zones 6 and 7

Paste `00_MASTER_BRIEF_V2.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections required. **Section F is the deliverable.**

## Why we are asking

The gate `S9-EUI-office` fails. It requires all-fuel site EUI inside 100 to 200 kWh/m2.yr. Our office
channel reads about 85.4, and so does the **uninjected control**, which is the same building with no
occupancy schedules applied at all. Nothing in the occupancy model can move a number that is already
there before occupancy is applied, so the question is whether the floor of 100 is the right floor for
this building.

The band's own source document contradicts itself, and we want that resolved from primary sources
rather than from our own results. The document is
`Leg2_2-split/Step8_docs/deepResearch/Office Reference EUI (NECB 2020, ASHRAE 90.1, DOE-PNNL prototypes) - As-Modelled Bands.md`.
Three statements inside it disagree:

* **Table 7.1**, the one the gate actually uses: floor **100.0**, central 135.0, ceiling 200.0.
* **Line 21**: "NRCan/CanmetENERGY studies on Canadian office archetypes show that NECB 2017/2020
  compliant large offices average **80 to 140 kWh/m2.yr**."
* **Table 2.1**: "Reference / Tier 1 Baseline, **Fossil-Fuel Heated: 85.0 to 115.0** kWh/m2.yr"
  (Electrified: 110.0 to 140.0).

Our tower is fossil-fuel heated, confirmed in the IDF (`Boiler:HotWater`, natural gas, nominal thermal
efficiency 0.813). Our 85.4 sits inside the two statements the gate does not use and below the one it
does. Both dissenting statements attribute themselves to **CanmetENERGY**, and a previous verification
pass could not locate any such publication; the NRCan URL given for it returns 404.

We are not asking you to lower our floor. We are asking what the primary sources actually say.

## What we need

1. **Find or refute the CanmetENERGY source.** Table 2.1 and line 21 both claim a CanmetENERGY study of
   Canadian office archetypes under NECB. Establish whether such a study exists. If it does, cite it
   properly and give its tables. If after genuine search it cannot be found, say so explicitly with the
   search terms used. **That negative result is as valuable to us as a positive one**, because two of
   our bands currently rest on it.

2. **As-modelled office EUI under NECB.** For a NECB 2017 or NECB 2020 compliant large or medium office
   building in Canadian climate zone 6 (Montreal) and zone 7A (Calgary or Edmonton): total site EUI,
   all-fuel, kWh/m2.yr. **Split by heating fuel**, gas-fired against electrified, because Table 2.1
   splits on exactly that and the split is large (85 to 115 against 110 to 140). State the reference
   building convention each figure uses, since NECB Part 8 compares a proposed design against a
   dynamically generated reference rather than a fixed EUI target.

3. **The BTAP route.** CanmetENERGY publishes an open-source NECB archetype simulation framework
   (BTAP, the Building Technology Assessment Platform, and `btap_batch`). Its published result sets are
   exactly the kind of data we need. Establish what is published, at what resolution, for which NECB
   editions and climate zones, and extract the office rows.

4. **Space heating specifically.** Our office shortfall is concentrated in heating: about **17 percent**
   of office site energy against an expected 35 to 45 percent share. Where any source gives an end-use
   breakdown for a NECB-compliant office in CZ6 or CZ7, capture the heating share and the absolute
   heating EUI. This is the single most diagnostic number in this prompt.

5. **Empirical figures, separately.** NRCan commercial building benchmarking, ENERGY STAR Portfolio
   Manager Canada snapshots, CEUD office tables. Put these in a **separate table clearly labelled
   empirical**. They are context only. Our gate scores an as-modelled value and we will not mix the two.

6. **Is the 100 floor defensible?** Given what you find, say whether a floor of 100 is supportable for a
   gas-heated NECB 2017 office in CZ6 and CZ7. If the evidence supports a different floor, give it with
   **a separate citation for that endpoint**. If the evidence is insufficient to set a floor at all,
   say that; it is an acceptable and useful verdict.

## Named leads

CanmetENERGY Ottawa and Varennes publication lists; the `canmet-energy` GitHub organisation and its
BTAP and `btap_batch` repositories and published result sets; NRCan Office of Energy Efficiency;
National Research Council Canada NECB 2017 and NECB 2020 documentation and any published reference
building performance studies; NRCan CEUD commercial and institutional tables; NRCan ENERGY STAR
Portfolio Manager Canada data snapshots for offices; peer-reviewed Canadian work on NECB-compliant
archetypes and office stock modelling, including Concordia, ETS, Carleton and NRC-IRC output; the DOE
Building Energy Codes Program prototypes as the US comparator (but see prompt `V01`, which covers those
in detail, and do not duplicate that work here).

## Deliverable

Section B must give as-modelled office EUI rows with the heating fuel and climate zone stated on every
row, and a heating end-use share wherever one is published. Section D must classify each finding as a
**band change**, an **interpretation change**, or a **caveat only**, and a band change requires a
separate external citation for each endpoint. Section F must state, for a gas-heated NECB 2017 office
in CZ6 and CZ7, the as-modelled site EUI range the literature supports and what would count as a
failure rather than a difference.

Section G must record the outcome of item 1 plainly: CanmetENERGY source **found and cited**, or
**NOT FOUND** with the search terms.

If the honest conclusion is that the 100 floor can be neither confirmed nor replaced from available
sources, write that in Section A's first sentence.
