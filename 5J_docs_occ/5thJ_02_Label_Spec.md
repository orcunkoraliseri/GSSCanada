# 5J Label Spec: what the human labeller ticks on each permit text

Written 2026-09-26 by the manager (WP1, design doc section 5). Labeller: the author (D-5J-3 ruled (a));
a colleague labels 400 of the same texts blind. Edit in place. **Status: DRAFT v1; frozen by checksum
together with the gates (design doc section 7) before any model is scored.** Example texts marked
"real" were taken from the Montreal file on 2026-09-26 (upper case and a few accents lost in the file
itself). Toronto examples marked "real (Toronto)" are real rows of the Toronto permit files, chosen on
2026-09-26 from permits that were **not** drawn into the labelling sample (so no row you label is
pre-answered in this spec).

## 1. The task, in one paragraph

You see one permit text. For each of seven labels you tick **YES**, **NO** or **CAN'T TELL**. You judge
only the words in front of you, never the address, the year or what you know about the building.
You label what the permit **says the work is**, not whether the work was carried out.

## 2. The three answers

| Answer | Use it when |
|---|---|
| YES | The text names the work, in any wording, in French or English. A number, plural or singular does not matter. |
| NO | The text is clear enough that the work is not in it: it describes other work only, and nothing in it hides the event. |
| CAN'T TELL | The text is too short or too vague to decide ("rénovation intérieure", "travaux selon plans"), or a word could mean two things and the rest does not settle it. |

Rules that settle most doubt:
1. **A long text about other work is NO, not CAN'T TELL.** Only use CAN'T TELL when the text really could hide the event.
2. **Work on the building only.** Pool heat pumps, garden sheds, signs and fences are NO for the building labels.
3. **New work vs repair.** "Réparer / repair a window" is NO for W; "remplacer / replace / install new" is YES.
4. **Never guess from a contractor's name** or from the permit's category.

## 3. The seven labels

### W: windows replaced or added
YES: replacing, changing or installing windows or glazed doors; enlarging or adding window openings.
NO: closing up ("boucher") a window; window repair only; shop fronts on commercial parts.
- YES (real): "REMPLACER ONZE FENETRES EXISTANTE, DOIT ETRE CONFORME AU C.N.B. 1990"
- YES (real): "CHANGER LA FENETRE DE LA CUISINE"
- YES (real): "REMPLACER LES PORTES ET FENÊTRES, REFAIRE LES BALCONS ET ISOLER LA FONDATION" (W yes and I yes)
- YES (real, Toronto): "Proposal to replace basement window on the north elevation"; "Addition of header to all existing windows and doors, replacement of all existing windows and doors, repair of kitchen roof, addition of bathroom to second floor."
- YES (English): "Replace 6 windows on second floor"; "install new patio door"
- NO: "boucher 5 fenêtres, côté ouest" (openings closed); "repair window frame"
- Trap: "même ouverture" (same opening) is still W yes: it means the window is replaced in the existing hole.

### I: insulation added or improved
YES: adding, blowing in, spraying or upgrading insulation of walls, roof, attic, foundation, basement, crawl space ("vide sanitaire"), or re-insulating ("réisoler").
NO: **sound or fire separation** ("isolation acoustique", "coupe-feu", "mur mitoyen coupe-feu"); "isolation" of pipes only; insulation that is only part of a new structure.
- YES (real): "ISOLER LE VIDE SANITAIRE ET ISOLER LA VÉRANDA ARRIÈRE EXISTANTE"
- YES (real): "RÉISOLER LES MURS EXTÉRIEURS ... "
- YES (real): "ajouter de l'isolation" (curtain wall, ground floor)
- YES (real, Toronto): "Interior Alteration - Raising ceiling level, new insulation and kitchen renovation"; "Proposal for interior alterations to all floors (changes to floor layout, structural re-framing, and insulation replacement)."
- NO (real, Toronto): "Revision 1. Revision to remove the existing ceiling joists in the living room, dining room and kitchen area to accommodate a new insulated vaulted ceiling." (insulation only part of new structure)
- YES (English): "add attic insulation"; "spray foam basement walls"
- NO: "isolation acoustique entre logements"; "fire-rated separation"
- CAN'T TELL: "Isolation." alone, with no place named (real pattern): the word says insulation but the work may be fire or sound; tick CAN'T TELL.

### HP: heat pump installed
YES: heat pump, "thermopompe", "pompe à chaleur", "mini-split" for heating or cooling **the building**.
NO: pool heat pump; text names only "climatiseur" (that is AC, not HP).
- YES (real): "THERMOPOMPE" (contractor text, short but clear)
- YES (real): "POMPE A CHALEUR KEEPRITE MP-030 SERA DEPLACÉE POUR LA METTRE COUR ARRIÈRE" (an existing heat pump is moved; tick YES, the unit exists)
- NO (real): "Thermopompe dans la cour arrière pour piscine creusée" (pool)
- YES (real, Toronto): "HVAC - Proposed Second floor addition on the garage; the addition includes a living space and a bathroom; the proposed heating system is a ductless heat pump. Removal of a partition wall on the ground floor." (HP yes; the work is an addition, so N is NO)
- YES (English): "install ductless heat pump"; "replace furnace with heat pump"
- Note: in Montreal many "THERMOPOMPE" lines come with new row houses ("RANGÉE + THERMOPOMPE"). Tick HP yes **and** N yes when the text also builds a new building.

### AC: central or split air conditioning installed
YES: "climatisation", "climatiseur", "air conditionné", central A/C, split or rooftop cooling for the building.
NO: refrigeration, ventilation only, "ventilation" without cooling, portable or window units named as such.
- YES (real): "CLIMATISEUR"; "Installer un système de ventilation et climatisation dans une partie du bâtiment"
- YES (real, Toronto): "Install air conditioning system for 2nd and 3rd floors."; "Install new AC Unit to Ground Floor Unit #3 for future 'Starbucks'." (a shop unit in a mixed building: the text says AC installed, tick YES)
- NO (real, Toronto): "REVISION - deletion of the roof top A/C equipementHVAC - Construct new single family townhouse Lot 4" (AC is removed from the plans; N is YES)
- CAN'T TELL (real, Toronto): "Proposed replacement of existing HVAC system. Existing furnace and AC to be retained. New supply and retunr lines to be installed throughout home." (F and AC both CAN'T TELL: system replaced but the units stay)
- YES (English): "install central air conditioning"; "AC unit on roof"
- CAN'T TELL: "systèmes mécaniques" (may or may not include cooling)
- Rooftop units on commercial or institutional buildings are recorded as AC yes; the sampling frame is residential, so they rarely appear.

### F: heating system or fuel change
YES: replacing or converting the heating system or fuel: furnace, boiler, baseboards ("plinthes", "convecteurs"), oil tank removal, conversion between oil, gas and electric.
NO: the word "chauffage" only inside a list of trades; pipes; fireplace or stove work on its own.
- YES (real): "DÉMANTELER LA FOURNAISE ET LE RÉSERVOIR D'HUILE"; "REMPLACER LE SYSTÈME DE CHAUFFAGE"
- YES (real): "ENTRÉE ÉLECTRIQUE ET CHAUFFAGE ÉLECTRIQUE" (electric heating installed)
- CAN'T TELL (real): "TRAVAUX SUITE AUX INONDATIONS 2017 - CHARPENTE, ISOLATION, PLANCHER, ... ÉLECTRICITÉ, CHAUFFAGE": heating is a trade in a list; not clear it changes. Tick F = CAN'T TELL, I = YES (isolation named).
- YES (real, Toronto): "Proposal to install new furnace and duct work in basement of existing SFD-D dwelling."; "HVAC - Furnace Replacement"
- CAN'T TELL (real, Toronto): "HVAC - Alter HVAC system throughout the building." (a system is altered, not said to be replaced)
- NO (real, Toronto): "HVAC - alter h.v.a.c. plans 00-130756 by installing bedroom ventilation." (ventilation only)
- Trap (Toronto): "HVAC -" is the permit-type name, not information. F is YES only if replace, install, convert or new furnace / boiler / baseboard is stated; "HVAC - Alter" alone is CAN'T TELL.
- Trap: F yes and HP yes can both be ticked ("replace furnace with heat pump"), e.g. (real, Toronto) "Proposal to convert forced air heating (natural gas) to air-to-air electric heat pump units with central HRV for ventilation" is F yes and HP yes.

### N: new construction (reset event)
YES: a new building is being built ("construction d'un nouveau bâtiment", "new house", "rangée", "neuf"), or a rebuild after demolition.
NO: additions ("agrandissement") to an existing building; interior renovation; a new garage, shed or other outbuilding on its own.
- YES (real, Toronto): "TO DEMOLISH THE EXISTING SINGLE DWELLING & CONSTRUCT A NEW SINGLE DWELLING" (N yes and D yes); "HVAC - To construct a new detached dwelling with an integral garage."
- NO (real, Toronto): "To construct a new detached garage"
Why it matters: N resets the building's history, and HP / AC / windows in a new building are part of the new build, not a retrofit.

### D: demolition (reset event)
YES: the building or a full unit is demolished ("démolition", "démolir le bâtiment").
NO: demolishing an interior wall, a shed, a garage or a balcony only.
CAN'T TELL: "démolir la partie ..." of a building without saying how much.
- YES (real, Toronto): "demolish existing 1 storey dwelling, build new 2 storey sfd" (D yes and N yes)
- NO (real, Toronto): "DEMOLISH INTERIOR PARTITIONS, RENOVATE SECOND FLOOR BATHROOM, KITCHEN AND BATHROOM. INSTALL SECOND BATHROOM IN BASEMENT."; "construct a 2-storey rear addition ... Also demolish detached garage at the rear" (garage only)
- CAN'T TELL (real, Toronto): "Demolition and reconstruction of exiting second floor with a new two storey addition at the rear of the existing house." (part of the house; how much is not said)

## 4. Text problems the labeller will meet

* The Montreal file has upper-case text and broken accents (a "�" replaces é, è, ô). Read through it.
* Some texts end with a contractor name in quotes or a « ... » block. Ignore the name.
* Several permits share one address and one date. Label each text on its own words.
* Copy-paste boilerplate ("DOIT ÊTRE CONFORME AU C.N.B. 1990") carries no information; ignore it.
* Toronto texts often start with a permit-type word ("HVAC -", "Plumbing -", "Drain -", "Revision 01 -"). **The prefix is NOT stripped**: 87 of the 2,600 texts still begin with "HVAC". It names the permit type, not the work: never tick a label from the prefix alone.
* Some Toronto texts are two permit descriptions glued together with no space ("...floorsHVAC - Proposal for..."). Label the words of the whole text.
* A "Revision" text that says work is deleted or removed from the plans ("deletion of the roof top A/C") is NO for that work.

## 5. What the labelling screen shows, and hides

Shows: the text only. Hides: address, date, borough, year built, keyword hits, any model output, and
the other labeller's answers. Row order is shuffled once, with a fixed seed written down.

## 6. Quality rules

* 400 of the texts appear twice in the labeller's list and, separately, in the colleague's list; Cohen's kappa per label (gate G5J.1, kappa ≥ 0.6).
* CAN'T TELL counts as its own answer in kappa; if a label falls under 0.6 it is merged or dropped **before** any model is scored, and the rule change is written here with the date.
* The labeller does not see any model output at any time. Labels are never made or corrected by a model.
* A text the labeller cannot read at all is marked BAD and replaced by the next row of the same stratum.

## 7. Open points for the manager (not the labeller)

* **Contractor lines are frequent for HP and AC in Montreal.** The keyword counts on the residential permit file are W 75,573 · I 5,372 · HP 2,583 · AC 1,057 · F 864 (all rows with text, accent-insensitive; not yet restricted to residential). So the design line "d near zero by rule for HP and AC" (WP4) is wrong for **new builds** and contractor add-ons: permits do name HP and AC. The rule must be limited to **retrofits in existing homes**. Recorded in the design Progress Log; WP4 will estimate d for HP and AC from data, not fix it at zero.
* Keyword hit counts above are a first read, not a result. The stratified sample uses them only to make sure rare events (HP, AC, F) appear often enough to score.
* Toronto examples above are real rows, checked against the sample by normalised text: none of them is in the labelling sample. Their answers are the manager's reading; the author may overrule any of them, and then the rule is edited here with the date.

## Progress Log
- 2026-09-26 (manager, later): Toronto examples replaced by real rows not in the sample (scratchpad `tor_ex.py`, normalised-text match against `sample_manifest.csv`). Found and fixed a wrong statement: the "HVAC -" prefix is NOT stripped in `labelling_sheet_author.csv` (87 of 2,600 texts start with HVAC; 80 flagged `hvac_prefix`). Added: N = NO for a lone garage or shed; revisions that delete work; glued texts. The data has 0 U+FFFD characters, so the "broken accent" warning stays as a soft note only.
- 2026-09-26 (manager): v1 written after a small keyword count on the Montreal file (script in the session scratchpad, counts only). D-5J-3 ruled (a).
