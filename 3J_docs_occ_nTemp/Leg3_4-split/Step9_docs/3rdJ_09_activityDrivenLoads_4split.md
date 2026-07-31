# 3J Leg-3 — Step 9: Activity-Driven End-Use Loads (Four-Channel)
### Residential + Office + Retail + Hotel — equal treatment ≠ identical parameters; matched evaluation, per-channel benchmarks, dual-basis reporting

---

## 0. WHY THIS STEP EXISTS (and why it is quad-channel)

| Channel | Coupling driver | Headcount basis | BEM action | EUI benchmark (own) | Design |
|---|---|---|---|---|---|
| Residential | AT_HOME presence | HHSIZE | REPLACE | SHEU 2019 bands | inherited |
| Office | AT_WORK fraction | NECB density | MODULATE | PNNL as-modelled 135 [100–200]; SCIEU INFO | inherited |
| Retail ⚠️ | **customer** presence (People gains only) | NECB ~3.7 m²/p | MODULATE | dr_L3-02: 110 [80–155] PASS; 280 [150–380] INFO | NEW |
| Hotel ⚠️ | s(t) × monthly rate | NECB density | MODULATE (monthly) | dr_L3-03: 240 [180–300] PASS; 350 [220–480] INFO | NEW |

**Equal importance ≠ identical parameters** (pipeline STEP 9):
- **Retail:** lighting and HVAC follow **opening hours** (near-flat while open, off overnight); **plug loads follow staff, not footfall** — customer presence modulates People-driven gains only, while the staff-driven plug baseload stays in the NECB baseline. Floors kept: `Lmin = 0.15` egress lighting, `Pbase = 0.20` never-zero plug.
- **Hotel:** guest-room equipment + lighting scaled by `s(t) ×` monthly amplitude; amenity zones baseline (consistent with Step-7 v1 / OD-6). ~40–50 % of guest-room energy is presence-independent (dr_L3-05) — expect a damped response by construction.
- **Calibration anchor:** commercial magnitudes vs **NRCan SCIEU** (the commercial analogue of the residential SHEU anchoring), per channel.

## 1. SCOPE & DEPTH (honest statement)

Aggregate depth, as in Leg-2 Step 9: this step **reads** the Step-8 §8E agg tables — no re-simulation, no new coupling implementation (coupling lives in Step 7/8). Activity-resolved commercial loads remain out of scope (was already flagged "a Leg-3 candidate" in Leg 2; the decision here: the two NEW channels ship at the same aggregate depth first — deepening is post-paper work).

## 2. METHOD

- **§9.1** Presence-driven coupling audit per channel (verify the Step-8 §2.6/2.7-class floors from the agg tables).
- **§9.2** Aggregate EUI calibration, each channel vs its **own** benchmark, on the **dr_L3-10 dual basis** (CFA primary; occupiable-GFA share for the SCIEU/CEUD INFO comparison; basis stated on every table/figure) with hourly load-weighted central-plant attribution (done in §8D — consumed here).

## 3. INPUTS

`Step8_docs/outputs_step8/agg/{agg_annual, agg_peak, agg_diurnal, agg_meta}.csv` (with per-channel and per-end-use columns — the Leg-2 re-aggregation lesson: end-use diurnals captured from the start), benchmark band constants (§0 table).

## 4. RESULTS (skeleton — filled at run time)

- **§R1 — EUI vs benchmark**, per channel × archetype × basis, verdict column.
- **§R2 — Load shape & peak timing**: per-channel peak hour; the four-channel **coincidence story** (retail midday + office midday vs residential evening vs hotel overnight — the tower's diversity factor); metric definitions stated explicitly (per-run-mean vs diurnal-profile — the Leg-2 dual-definition caveat; pick one convention per table and label it).
- **§R3 — Scenario response (2030 bundles + sensitivities)**, per channel:
  - **G8o (office)** — inherited: WFH-modulation non-degenerate; conservative may sit ABOVE 2022 (return-to-office framing — 2022 already carries ~30 % WFH).
  - **G8r (retail, NEW)** — the in-store lever is non-degenerate: retail-zone energy responds monotonically to 0.90/0.97/1.05, and `|energy Δ%| ≤ |occ Δ%| + 1 pp` (damped, direction-agnostic — §7.2 form).
  - **G8h (hotel, NEW)** — the SARIMA band is non-degenerate: guest-room energy responds monotonically to low/central/high, monthly seasonality visible; same damped-response bound.
- **§R4 — Longitudinal 2005→2022**: per-channel midday/evening share trajectories; COVID break signatures (office ↓, retail ↓, resid ↑; hotel from the multiplier series).

## 5. EQUAL-TREATMENT LEDGER (the parity check)

Every analysis row computed AND reported for all four channels, each vs its own benchmark; genuine gaps flagged, not hidden. Known accepted gaps to declare up front: (a) hotel has no GSS-side behavioural depth (aggregate multiplier only — by construction); (b) retail staff invisible in GSS (staff loads live in the baseline — frame caveat, carried to the paper's limitations); (c) office end-use split availability per the Step-8 agg schema.

## 6. OUTPUTS (`Step9_docs/outputs_step9/`)

`step9_eui_by_channel.csv`, `step9_loadshape_peaks.csv`, `step9_scenario_response.csv`, `step9_longitudinal.csv`; figures: `fig_eui_4ch.png`, `fig_diurnal_4ch.png` (stacked coincident, winter+summer), `fig_diurnal_<channel>_enduse.png` ×4, `fig_peakhour_4ch.png`, `fig_scenario_4ch.png`, `fig_longitudinal_4ch.png`, `fig_hotel_monthly.png` (NEW — monthly amplitude vs energy); `step9_report.html`.

## 7. GATES (mapped to the Step-8 validator)

*(Table as originally specified — kept for provenance. The **implemented** set, with the three
re-specifications made 2026-07-31 and their reasons, is below it.)*

| Gate | Check | Maps to |
|---|---|---|
| EUI in band | per channel, as-modelled PASS / empirical INFO | §4.2/4.6/4.7 |
| EUI share sanity | ±2 pp vs occupiable shares | §4.10 |
| Peak-hour direction | office ~13h; retail 12–16h; resid 15–22h; hotel load-weighted overnight | §5.2 |
| Weekend structure | office WE<WD; retail Sat≥WD; hotel WE plateau shift | §5.3 |
| **G8o / G8r / G8h** | scenario non-degeneracy + damped bound per channel | §7.2 |
| Coincidence factor | stacked peak < Σ channel peaks (diversity) | §5.1 |
| Monthly seasonality (hotel) | energy follows multiplier | §5.4 |

#### Jeu implémenté (`3rdJ_09_activityDrivenLoads_4split.py`), 2026-07-31

| Gate | Statut | Note |
|---|---|---|
| `S9-EUI-{office,retail,hotel}` | PASS/FAIL | bande as-modelled, base **CFA** ; bande empirique en INFO seulement |
| `S9-EUI-residential` | INFO | aucune bande as-modelled (une tour n'est pas le parc SHEU) |
| `S9-BASIS` | INFO | 🔴 **arbitrage** : bandes issues de prototypes autonomes appliquées à des canaux empilés |
| `S9-SHARE` | **INFO — re-spécifiée** | la part d'énergie ne peut égaler la part de surface que si tous les canaux ont le même EUI ; nos propres bandes vont de 110 à 240. Critère insatisfiable, donc non scoré — jamais élargi |
| `S9-AREA` | **PASS/FAIL — nouvelle** | la moitié falsifiable de l'intention ±2 pp : Σ(surfaces) + non classé ≡ total ABUPS à 0,1 %, non classé < 1 % |
| `S9-PEAK-{office,retail}` | PASS/FAIL | pointe d'**occupation** dans la fenêtre **et** concentration R ≥ 0,30 |
| `S9-PEAK-residential` | **PASS/FAIL — re-spécifiée** | occupation soir > midi sur les cellules **injectées** ; la base NECB non injectée sert de contraste, pas de FAIL |
| `S9-PEAK-hotel` | INFO | occupé la nuit par construction ; aucune fenêtre diurne n'a de sens |
| `S9-INJECTION` | PASS/FAIL | l'injection bascule la forme midi-dominante → soir-dominante |
| `S9-RESID-EVENING` | INFO | la pointe **énergie** du soir de Leg 1-2 n'est pas reproductible ici (OD-7D) |
| `S9-D20` | INFO | décalage pointe énergie ↔ pointe occupation, par canal |
| `S9-WE-office` · `G8o/G8r/G8h` · `S9-COINC` · `S9-LONG-*` | PASS/FAIL | inchangées |
| `S9-PLATFORM` · `S9-CELLS` · `S9-SCHEMA` · `S9-FALLBACK` | PASS/FAIL / INFO | provenance et hygiène |

> **Pourquoi R ≥ 0,30.** Le caveat 3 dit « moyenne circulaire, pas arithmétique ». C'est vrai mais
> incomplet : une moyenne circulaire est **tout aussi vide** quand la longueur résultante est
> courte, car la direction est alors fixée par le bruit. Mesuré ici — retail R = 0,82 et bureau
> R = 0,66 (pointes de midi franches, moyenne interprétable) ; résidentiel R = 0,22 et hôtel
> R = 0,18, formes quasi antipodales (chez soi la nuit / absent à midi) dont les vecteurs
> s'annulent presque. C'est exactement pourquoi l'heure moyenne résidentielle errait entre 0,30 h
> et 23,62 h sur des cellules au comportement identique. Toute gate qui cite une heure moyenne
> doit d'abord vérifier R.

## 8. CAVEATS (paper-facing)

1. Dual-basis mismatch (CFA vs GFA-share) — state basis everywhere.
2. Damped scenario response is **by design** (only People/L/E gains modulated) — not a bug; cite the §7.2 direction-agnostic gate.
3. Metric-definition consistency: one peak-hour convention per table (Leg-2 14.8h-vs-16.1h lesson). **Hour-of-day is a circular quantity — use a circular mean, never an arithmetic mean** (a 2J plotting bug arithmetic-averaged a bimodal morning/evening population into a meaningless ~14.5h); where household-level and stock-aggregate statistics diverge legitimately, report both and label which is headline.
4. Retail staff / hotel guests frame caveats (GSS sees customers only / nothing).
5. Hotel amenity zones unmodulated in v1 (OD-6).
6. Ground-level EPW on a supertall (no altitudinal gradient).
7. **Cite sim-side evidence (G8r/G8h/§7.2), not input-side, as the modulation-signal proof** — the Leg-2 lesson (G8o vs §6.3).
8. Cross-era comparability: each cycle's channel products derive from that cycle's GSS pool (different underlying respondents by construction) — the longitudinal comparison is population-level, not a paired design; one manuscript sentence (the Leg-2 cross-era-pairing ticket, generalized).
9. If the multi-zone residential injection fix is ever cited: it is **energy-neutral on annual aggregates** (2J/Leg-2 verified — building totals conserved); claims scope to zone-level load distribution only, never "restored energy".
10. Report regeneration: after any data/rake change, re-render **every** embedded figure and stamp a regen token — a report built as an additive copy of its predecessor can carry stale charts under fresh prose (2J v6 shipped 7 pre-fix charts).

## 9. REFERENCES

Pipeline STEP 9; dr_L3-02/03/05/06/10; Leg-2 `3rdJ_09_activityDrivenLoads_2split.md` (template + G8o precedent); NRCan SCIEU 2019; SHEU 2019.

## Script

`3rdJ_09_activityDrivenLoads_4split.py` (reads agg tables; no re-simulation) + `run_step9_4split.sh` (sbatch, 7-day walltime). Report scorecard target: 0 FAIL, WARNs documented.

## Progress Log

*(append entries below — dated `###` entries with job IDs)*

### 2026-07-31 — Step 9 débloqué : le §8E n'existait pas, et les sorties Step-8 ne pouvaient pas le nourrir

**Ce document décrivait un Step 9 impossible à exécuter.** §3 déclare lire
`Step8_docs/outputs_step8/agg/{agg_annual, agg_peak, agg_diurnal, agg_meta}.csv`. Ces fichiers
n'existaient pas, et le script censé les produire — `3rdJ_08_simulation_4split_agg.py`, spécifié
depuis le 2026-07-02 au §8 du doc Step-8 — n'avait jamais été écrit. `outputs_step8/` ne contenait
que `historical_schedules/`. Le Step 9 n'était donc pas « à faire » : il était **sans entrée**.

Pire, les sorties de campagne existantes n'auraient de toute façon pas pu le nourrir correctement.
Trois défauts trouvés en remontant la chaîne (détail complet dans
`Step8_docs/3rdJ_08_implementation_improvements.md`, Défauts 5-6-7) :

| # | Défaut | Effet direct sur le Step 9 |
|---|---|---|
| 5 | Compteurs gaz aux noms **pré-EnergyPlus-9.4** (`Gas:Facility`…) → **13 884,91 GJ (53,5 % de l'énergie de site) rapportés à zéro** ; 3 usages finaux électriques absents (11,52 %) | Tous les EUI faux d'un facteur ~2. L'hôtel, dont l'ECS gaz (7 726,75 GJ) est le poste dominant, aurait été le plus faussé — face à la bande dr_L3-03 180-300, verdict inversé garanti |
| 6 | Variables de zone **non multipliées** par `Zones.Multiplier` (Σ = 25,4 % du compteur), et le multiplicateur moyen **diffère par canal** | Toute part par canal biaisée en faveur des canaux à faible multiplicateur — le retail au premier chef. Pas un mode commun : ne s'annule pas |
| 7 | Parts de surface documentées = gabarit (trois canaux à 24,4 % identiques ; mesuré 44,65 / 24,91 / 22,40 / **5,53**) | La gate **±2 pp** aurait comparé le modèle à un gabarit et échoué quoi que fasse le modèle |

**Ce qui a été fait, dans l'ordre.**

1. **Correctifs Step-8** (`3rdJ_08P_probe_driver.py`) : noms de compteurs corrigés (15 compteurs,
   2 totaux + 13 usages finaux), `Zones.Multiplier` appliqué avant agrégation par canal, ajout de
   `Zone Air System Sensible Cooling/Heating Energy` (sans quoi la répartition **horaire pondérée
   par la charge** verrouillée par dr_L3-10 était littéralement incalculable),
   `Zone Gas Equipment NaturalGas Energy` et `Water Use Equipment Heating Energy`.
2. **Deux gates de fermeture, implémentées et vues échouer avant d'être crues** :
   `fuel_closure` (Σ usages finaux ≡ `<Combustible>:Facility`, par combustible — la tripwire §6b-4
   déclarée depuis 2J Bug B et jamais écrite, ce qui est précisément pourquoi le Défaut 5 est passé)
   et `channel_closure` (Σ canaux ≡ compteur d'installation, ce qui prouve le multiplicateur).
   Validation : échec sur le vrai défaut (résidu 11,5216 % / compteur total absent), échec sur un
   manque injecté de 5 %, succès sur un jeu complet.
3. **`OUTPUT_SCHEMA_HASH`** ajouté à l'empreinte de reprise — sans lui, corriger les compteurs
   laissait les 56 cellules « faites » et la reprise les aurait toutes sautées.
4. **`3rdJ_08E_aggregate_4split.py` écrit** : le §8E manquant. Il **refuse** d'agréger une cellule
   dont les fermetures ne passent pas, plutôt que de produire un EUI amputé de la moitié de l'énergie.
5. **Re-simulation des 56 cellules** dans un `--outroot` neuf (`campaign_local_v2`), l'arbre
   précédent laissé intact. Cellule témoin vérifiée avant lancement : 0 compteur absent,
   `NaturalGas:Facility` = 13 884,9 GJ (concorde au tableau *End Uses* du même run), 5 fermetures à
   **0,000000 %** de résidu, 47/47 équipements ECS résolus, et — contrôle de régression —
   `Electricity:Facility` **identique** au run précédent : ajouter des objets `Output:*` ne
   perturbe pas le modèle.
6. **`3rdJ_09_activityDrivenLoads_4split.py` écrit** : §R1-R4, figures, scorecard, rapport HTML.
   Conventions imposées dans le code, pas en note de bas de page : heure de pointe en **moyenne
   circulaire** (caveat 3), EUI en **double base avec la base en colonne**, bande as-modelled =
   PASS / bande empirique = INFO.

**Leçon.** Une gate déclarée dans un document et absente du code est pire qu'une gate manquante :
elle occupe la place de celle qui aurait attrapé le défaut. La §6b-4 était écrite noir sur blanc
depuis 2J Bug B ; c'est son absence d'implémentation, pas son absence d'idée, qui a laissé passer
53 % de l'énergie du bâtiment.

### 🔴 Re-spécification de la gate « ±2 pp » (§7, ligne *EUI share sanity*) — décision à valider

En exécutant le Step 9 sur un jeu de test synthétique, la gate **±2 pp** a échoué sur 60 des 224
couples canal-cellule. Diagnostic : ce n'est **pas** un défaut du modèle, c'est de l'arithmétique.

La part d'énergie d'un canal n'égale sa part de surface **que si tous les canaux ont le même EUI**.
Or nos propres bandes as-modelled posent l'hôtel à 240 et le retail à 110 kWh/m²/an — un facteur
**2,2**. Un hôtel occupant 24,9 % de la surface est donc *obligé* de dépasser 24,9 % de l'énergie,
de bien plus que 2 pp. Formulée ainsi, la gate ne peut pas passer sur un bâtiment mixte : c'est une
gate qui **doit** échouer, aussi peu informative qu'une gate qui ne peut pas échouer.

Élargir la tolérance jusqu'à ce qu'elle passe est exactement le geste interdit ici (*ne jamais
assouplir un seuil pour effacer un FAIL*). Le remède prévu par la règle est la **re-spécification
sur une statistique qui survit à la transformation**. Donc :

- **`S9-SHARE` → INFO**, avec le rapport énergie/surface médian par canal affiché — ce rapport *est*
  l'EUI relatif, et il est déjà jugé contre sa propre bande par les gates `S9-EUI-*`. Rien n'est
  perdu ; le même contenu est simplement évalué là où un critère existe.
- **`S9-AREA` → nouvelle gate PASS/FAIL**, qui garde la moitié falsifiable de l'intention d'origine :
  Σ(surfaces des canaux) + non classé ≡ surface totale ABUPS à 0,1 %, et non classé < 1 % du brut.
  Elle échoue si le recensement Tag-2 rate une Space — le vrai risque que « ±2 pp » visait.

dr_L3-10 qualifie explicitement cette gate de *project-novel* (« ASHRAE 211 suggère la comparaison,
aucun code ne l'impose »), donc la re-spécifier ne contredit aucune littérature. **À confirmer par
l'utilisateur** : c'est un changement de statut d'une gate documentée, pas une correction de code.

### Trois résultats de fond, mesurés sur les 12 premières cellules réelles

**1. L'injection résidentielle change la FORME, pas seulement le niveau — c'est la preuve la plus
propre du travail.** Rapport occupation soir (17-22 h) / midi (11-14 h), profil jour de semaine :

| Cellule | ratio soir/midi | argmax |
|---|---:|---:|
| `Default_NECB` (base NECB, **non injectée**) | **0,22** | 09 h |
| Cellules injectées GSS | **2,34 – 7,37** (médiane 2,82) | 00-04 h |

La base de code est **dominée par le midi** ; l'injection la bascule en **dominée par le soir**. Un
simple ré-étalonnage de niveau ne pourrait pas produire ça. C'est une évidence *côté simulation*
(caveat 7) que le canal résidentiel porte du comportement et pas seulement une magnitude — la
proposition sur laquelle repose la thèse. Gate `S9-INJECTION`.

**2. La pointe résidentielle du soir en ÉNERGIE n'est pas reproductible en Leg 3.** L'occupation
monte bien le soir (point 1), mais l'énergie résidentielle culmine vers **12 h**, parce qu'OD-7D
laisse éclairage et prises résidentiels sur la ligne de base NECB plate — précisément les charges
qui produisaient la pointe du soir en Leg 1 et Leg 2. **Le signal comportemental est intact en
amont ; il n'a simplement aucune voie vers l'énergie.** C'est D-20 dans sa forme la plus tranchante,
et ça condamne toute affirmation Leg-3 sur la *demande énergétique* résidentielle du soir. Gate
`S9-RESID-EVENING`. **À porter au manuscrit.**

**3. 🔴 Décision utilisateur — les bandes d'EUI viennent de prototypes AUTONOMES.** EUI mesurés
(base CFA, médiane) : hôtel **207** (bande 180-300 ✅), résidentiel **122**, retail **77,7**
(bande 80-155, sous le plancher), bureau **72,9** (bande **100-200**, soit **27 % sous le
plancher**). Explication physique, pas correctif : un étage de bureau **au milieu d'une tour** a
quasiment toute son enveloppe en cloisons intérieures vers d'autres volumes conditionnés — ni
toiture, ni plancher sur terre-plein, et une centrale partagée dimensionnée pour l'ensemble. Un EUI
plus bas qu'un bâtiment de bureaux autonome est la **direction attendue**. **Aucun seuil n'a été
touché** : la gate échoue contre la bande telle que verrouillée, et la question — la bande
« autonome » reste-t-elle un critère PASS valable pour un canal empilé ? — est un arbitrage à
prendre explicitement. Elle interagit avec la question ouverte sur Leg-2 (bande bureau 135
[100-200] issue du job 1054800, possiblement calculée **électricité seule**). Gate `S9-BASIS`.

### Falsifiabilité vérifiée avant de citer le moindre PASS

`3rdJ_09_gate_falsifiability.py` (+ `3rdJ_09_synth_agg_fixture.py`, tous deux au dépôt, pas dans un
scratchpad — §6b-8) perturbe le jeu synthétique une gate à la fois et exige la transition
PASS → FAIL. **10/10 vues échouer** : levier bureau rendu dégénéré → `G8o` ; facteur de coïncidence
porté à 1,15 → `S9-COINC` ; 5 % de surface non classée → `S9-AREA` ; retail ×3 hors bande →
`S9-EUI-retail` ; pointe bureau décalée à 03 h → `S9-PEAK-office` ; week-end bureau ×12 →
`S9-WE-office` ; cellule retirée → `S9-CELLS` ; deux schémas de sortie mélangés → `S9-SCHEMA` ;
deux plateformes → `S9-PLATFORM` ; axe d'époque aplati → `S9-LONG-*`. Les gates non listées
partagent le chemin de code d'une gate testée (`S9-EUI-office/hotel`, `S9-PEAK-retail/residential`,
`G8r`/`G8h`).

Un bug réel est tombé de cet exercice : une cellule présente dans `agg_annual.csv` mais absente de
`agg_meta.csv` faisait planter le script au lieu de le signaler. Corrigé — la cellule orpheline est
exclue avec un avertissement, et `S9-CELLS` enregistre le manque.

**Corollaire méthodologique.** EnergyPlus **avait averti** quatre fois
(`Output:Meter: invalid Key Name="GAS:FACILITY" - not found.`). La session précédente avait classé
les 478 lignes `** Warning **` distinctes comme « toutes du dimensionnement bénin » à partir des
**5 motifs les plus fréquents**. Ces quatre-là apparaissaient une fois chacune. Un tri par fréquence
répond à « qu'est-ce qui est bruyant », jamais à « qu'est-ce qui est grave ».

### 2026-07-31 (fin) — Step 9 EXÉCUTÉ sur les 56 cellules : **17 PASS / 0 WARN / 3 FAIL / 7 INFO**

Chaîne complète bouclée : campagne 56/56 vérifiée sur artefacts → §8E (56/56, fermeture
d'attribution à 0,000000 % partout) → Step 9. Livrables dans `outputs_step9/` :
`step9_{eui_by_channel, loadshape_peaks, scenario_response, longitudinal}.csv`,
`step9_gates.json`, 5 figures, `step9_report.html`.

**Ce qui passe — et qui porte la thèse.**

| Gate | Résultat |
|---|---|
| `G8o` / `G8r` / `G8h` | **non dégénérés et monotones, 4/4 paires bâtiment×ville chacun.** Écarts \|opt−cons\|/central : bureau 3,12-4,64 %, retail 3,52-4,65 %, hôtel 1,17-1,59 %. Preuve **côté simulation**, pas côté entrée (caveat 7) |
| `S9-INJECTION` | l'injection résidentielle fait basculer l'occupation de **midi-dominante** (base NECB, ratio soir/midi **0,22**, argmax 09 h) à **soir-dominante** (GSS, **2,41**, plage 1,56-7,37, argmax 04 h). Changement de **forme** — inatteignable par un ré-étalonnage de niveau |
| `S9-COINC` | facteur de coïncidence **0,966** (0,952-0,977) sur 392 cellules-canaux : les quatre canaux ne culminent pas ensemble. La diversité de l'usage mixte, mesurée et non affirmée |
| `S9-PEAK-office` / `-retail` | pointe d'**occupation** dans la fenêtre, concentration R = 0,66 / 0,82 |
| `S9-PEAK-residential` | soir > midi sur **toutes** les cellules injectées |
| `S9-LONG-*` | axe d'époque non dégénéré sur les 4 canaux |
| `S9-AREA`, `S9-PLATFORM`, `S9-CELLS`, `S9-SCHEMA` | 56/56, une seule plateforme, un seul schéma de sortie |

**`S9-D20` — D-20 devient un nombre.** Décalage entre pointe d'énergie et pointe d'occupation :

| Canal | Décalage |
|---|---:|
| Bureau | **0,26 h** |
| Retail | **0,53 h** |
| Hôtel | 5,07 h |
| **Résidentiel** | **10,56 h** |

Les trois canaux commerciaux modulent People + Lights + Equipment : leur énergie suit leur occupation
à la demi-heure près. Le résidentiel ne module que People (OD-7D) : son énergie est pilotée par la
ligne de base NECB plate, à **plus de dix heures** de son occupation. C'est l'asymétrie D-20,
mesurée. Corollaire (`S9-RESID-EVENING`) : **la pointe résidentielle du soir en énergie — le résultat
titre de Leg 1 et Leg 2 — n'est pas reproductible ici.** L'occupation la montre toujours ; elle n'a
aucune voie vers l'énergie. À porter au manuscrit.

**Les 3 FAIL sont tous le même fait, et vont tous dans le même sens.**

| Canal | EUI mesuré (CFA, médiane) | Bande as-modelled | Écart |
|---|---:|---|---|
| Bureau | **71,1** (61,8-90,3) | 100-200 | −29 % sous le plancher |
| Retail | **75,4** (63,5-97,1) | 80-155 | −6 % |
| Hôtel | **178,3** (147,9-209,4) | 180-300 | −1 % |

Les trois sont **sous** leur plancher, jamais au-dessus. Les bandes viennent de prototypes
**autonomes** ; ici les canaux sont des étages empilés dans une seule tour, dont l'enveloppe est
presque entièrement en cloisons intérieures vers d'autres volumes conditionnés, avec une centrale
partagée dimensionnée pour l'ensemble. Un EUI plus bas est la **direction physiquement attendue**,
et la quasi-concordance du retail et de l'hôtel (−6 % et −1 %) contre l'écart du bureau (−29 %,
le canal le plus profondément enfoui) va dans le même sens.

🔴 **Aucun seuil n'a été touché.** La gate échoue contre la bande telle que verrouillée, et la
question — *une bande « autonome » reste-t-elle un critère PASS valable pour un canal empilé ?* —
est un **arbitrage utilisateur**, pas une décision de script. Elle est couplée à la question ouverte
sur Leg-2 : la bande bureau 135 [100-200] vient du job 1054800, dont le Step 9 ne garde que
`Electricity:Facility` / `office_elec` — donc possiblement **électricité seule** face à une bande
d'énergie totale. Voir `S9-BASIS`.

**Fermé (S9D-5, 2026-07-31)** : l'axe d'époque ne porte **aucun signal hôtel** (Y2005/Y2010/Y2015
sont des `DELIBERATE_CHANNEL_EXCEPTIONS`). La question posée ci-dessus dans une version antérieure
de ce document — « Y2015 est postérieur à 2011, pourquoi l'exclure ? » — reposait sur un
commentaire qui ne portait que la moitié courte de la raison (« hotel source data starts 2011 »,
qui ne vaut que pour l'AB). La vraie raison : la vérité-terrain hôtel du **Québec commence en
2019**, pas en 2011 (`3rdJ_06_hotel_sarima_4split.py:24-29` — AB 2011-01..2022-09, QC
2019-01..2022-12). Une courbe hôtel 2015 serait donc **AB seule**, et injecter un canal dans une
seule des deux villes du bras historique introduirait une **confusion province × canal** qui
contaminerait les quatre gates `S9-LONG-*`, pas seulement l'hôtel
(`3rdJ_08A_gen_historical_products_4split.py:12-20`, même décision, même raisonnement). L'exclusion
de Y2015 n'est donc pas arbitraire : elle est symétrique à celle de Y2005/Y2010, pour la même
raison. **Condition de réouverture** : l'apparition d'une source QC ouverte antérieure à 2019 (cf.
la piste OGLA/CKAN qui a déjà résolu l'AB) — auquel cas les trois époques historiques deviendraient
injectables ensemble, des deux côtés à la fois, pas Y2015 seule.
