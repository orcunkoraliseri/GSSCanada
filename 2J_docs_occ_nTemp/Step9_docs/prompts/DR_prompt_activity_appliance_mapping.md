# Deep-research prompt — DR-2: activity→appliance weights, co-presence, seasonality, validation

**Purpose.** Step 9 (light version) bends the equipment/lighting schedules using our predicted
30-min activities. The prior reports established the *method*; this prompt pulls the concrete
**numbers** needed to implement it: the activity→appliance weights, the within-activity splits, the
sub-linear co-presence function, a seasonality decision, and access to Canadian validation data.
Paste the block below into a web-based deep-research LLM. Save the returned report into
`Step9_docs/deepResearch/`.

```
You are doing deep research on activity-based (time-use-driven) residential electricity load
modelling. I need to turn a qualitative activity->appliance crosswalk into concrete NUMBERS for a
Canadian EnergyPlus model. IMPORTANT: I already PREDICT each household's 30-minute activity sequence,
so I do NOT need stochastic activity GENERATION (no Markov chains / no switch-on dice). I need the
appliance-mapping WEIGHTS, power levels, scaling rules, and validation guidance.

ANCHOR SOURCES (prefer these; cite precisely with DOI/URL):
- Richardson, Thomson, Infield & Clifford (2010), Energy & Buildings 42(10), DOI 10.1016/j.enbuild.2010.05.023;
  Richardson et al. (2009) domestic lighting; Richardson et al. (2008) occupancy.
- McKenna & Thomson (2016) CREST integrated model (Applied Energy 165) + CREST v2 documentation
  (appliance list, rated/standby powers, mean durations, calibration scalars).
- Widen & Wackelgard (2010), Applied Energy 87(6); Widen et al. (2009).
- Armstrong, Swinton, Ribberink, Beausoleil-Morrison & Millette (2009), J. Building Performance
  Simulation 2(1); and the 2023 "Stochastic bottom-up load profile generator for Canadian
  households' electricity demand" (Building & Environment, DOI 10.1016/j.buildenv.2023.110466).

MY 14 ACTIVITY CATEGORIES (GSS): 1 Work, 2 Household work & maintenance, 3 Caregiving, 4 Purchasing,
5 Sleep, 6 Eating & drinking, 7 Personal care, 8 Education, 9 Socializing, 10 Passive leisure,
11 Active leisure, 12 Community/volunteer, 13 Travel, 14 Misc. (0 = away.)

END-USE BUCKETS: cooking (range/oven/microwave/kettle), dishwasher, clothes washer, clothes dryer,
TV/entertainment, computer/home-office, personal-care + domestic hot water (DHW), lighting; PLUS an
always-on baseload (fridge/freezer/standby) handled separately (do not assign it to activities).

DELIVER, with citations:

1) A NUMERIC activity->end-use WEIGHT table: for each of the 14 activities, which end uses it
   triggers and a relative weight (0-1) for how strongly it drives each. Explicitly mark the
   activities that map to NO active load (away: 4,12,13; inactive: 5 sleep).

2) WITHIN-activity sub-distribution where one activity spans several appliances. e.g. when
   "Household work & maintenance" occurs, the typical split among laundry (washer/dryer) vs
   dishwashing vs cleaning (vacuum) vs cooking-prep; when "Eating & drinking" occurs, the split
   among range/oven vs microwave vs kettle. Give fractions/probabilities and the source.

3) Appliance ACTIVE POWER (W) and typical CYCLE DURATION for each end use (range/oven, cooktop,
   microwave, kettle, dishwasher, clothes washer, clothes dryer, TV/set-top, desktop+monitor,
   laptop, hair dryer), preferring CREST/Richardson and Canadian (NRCan UEC) values.

4) A concrete CO-PRESENCE scaling function: the SUB-LINEAR rule for SHARED devices (TV, room
   lighting, cooking, dishwasher) as a function of the number of co-present active occupants, and
   the (approximately LINEAR) rule for PERSONAL devices (laptop, hair dryer, personal hot water).
   Write the exact functional form used by Richardson/CREST ("effective occupancy") and/or the
   2023 Canadian generator, with parameter values.

5) SEASONALITY: does an activity-based model need a winter-intensification correction for a Canadian
   multi-year (2005->2030) study, given that time-use surveys under-capture "staying in more in
   winter"? If yes, give the recommended approach (e.g. Fischer synPRO seasonal probability sets)
   and any Canadian seasonal factors per end use.

6) VALIDATION data: how to obtain and use the Canadian high-resolution measured end-use datasets —
   Saldanha & Beausoleil-Morrison (2012) "Measured end-use electric load profiles for 12 Canadian
   houses at high temporal resolution", Energy & Buildings 49 (DOI 10.1016/j.enbuild.2012.02.013);
   and Johnson & Beausoleil-Morrison (2017), 23 houses at 1-minute (Applied Thermal Engineering 114).
   Include download links/format and which metrics to compare (load shape, peak timing, diversity
   factor).

OUTPUT: (a) the numeric activity->end-use weight table; (b) within-activity sub-distributions;
(c) appliance power/duration table; (d) the co-presence function(s) written explicitly with
parameters; (e) a seasonality recommendation; (f) validation-data access notes. Full citations
(authors, year, title, venue, DOI/URL).
```
