<!-- ══════════════════════════════════════════════════════════════════════════════════════════════ -->
<!--  NAVIGATION BANNER — added 2026-08-04. Nothing below this banner has been edited or removed.  -->
<!-- ══════════════════════════════════════════════════════════════════════════════════════════════ -->

> # 🧭 START HERE — do not read this file front-to-back
>
> **This is an append-only chronological lab notebook, 7,600+ lines, bilingual (French to line ~790,
> English after). It records what was believed at each moment — including beliefs later shown wrong
> and struck _in place_.**
>
> ## → Read `3rdJ_L3_step9_READER_GUIDE.md` first (same folder).
>
> It gives, in ~6 pages: the project in 10 lines, the vocabulary, the current state, the 8-arm table,
> the 8 open questions, a **register of every claim that was later reversed**, and a section map.
>
> ### The three things a cold reader most needs to know
>
> 1. **Current score: 17 PASS / 0 WARN / 3 FAIL / 10 INFO.** The three FAILs — `S9-EUI-office`,
>    `S9-EUI-retail`, `S9-EUI-hotel` — are all *absolute EUI level vs an external band*, and have been
>    FAIL across all eight simulated arms. The other 27 gates are stable and passing, **including all
>    four that test the paper's actual claim** (`S9-INJECTION`, `G8o/G8r/G8h`, `S9-COINC`, `S9-D20`).
>
> 2. **🔴 None of the three FAILs is an occupancy problem.** The `Default_NECB` control — same
>    building, **no GSS injection at all** — measures office at **85.45** against a band floor of
>    **100**. The code's own reference implementation fails the band by 15 %, and injection moves
>    office *down*. Retail misses by **0.06 %** and **0.23 %** on 2 of 56 cells under an all-56 rule.
>    Hotel's resize moved the *uninjected* control too, so it is a plant effect. **See `§0.21`.**
>
> 3. **🔴 About one claim in twenty in this log was later reversed.** `T9-1`, `T9-2`, `T9-11` and
>    `T9-10`'s retail rule were cancelled or withdrawn; `FINDING 6`'s headline number and `FINDING 8`'s
>    mechanism were both wrong and corrected; the `R > 1.5` premise and the "stacked tower" explanation
>    were struck by measurement. **Check §2 of the reader's guide before quoting any paragraph.**
>
> ### Fast paths
>
> | you want | search for |
> |---|---|
> | current state + open questions | `§0.21` |
> | the latest result | `§0.19` (predictions) then `§0.20` (result) |
> | what each arm changed | `0.21.2` |
> | what was reversed | reader's guide §2 |
>
> _Sections `§0.18`–`§0.21` (2026-08-04) are the newest and the most self-contained._

---

<!-- ═════════════════════════════ ORIGINAL DOCUMENT BEGINS BELOW ══════════════════════════════════ -->

# 3J Leg-3 — Améliorations Step 9 : document d'implémentation

**Créé le 2026-07-31.** Doc de référence autoportant. Il traite **les trois arbitrages laissés
ouverts par l'exécution du Step 9** (17 PASS / 0 WARN / 3 FAIL / 7 INFO, 2026-07-31), demandés
ensemble par l'utilisateur le même jour :

1. **Lot A — les bandes d'EUI** (les 3 FAIL). Que fait-on d'une bande « prototype autonome »
   appliquée à un canal empilé ?
2. **Lot B — le précédent Leg-2** (`office 172,7 in band`, job 1054800). Était-il en électricité
   seule ?
3. **Lot C — l'axe d'époque et l'hôtel** (`Y2015` exclu). Faut-il l'inclure ?

Docs frères :

- `Leg3_4-split/Step9_docs/3rdJ_09_activityDrivenLoads_4split.md` — doc Step 9 faisant foi
- `improvements/3rdJ_L3_improvements_step5_6_7.md` — lot précédent (méthode, registre D-1..)
- `Leg3_4-split/Step8_docs/3rdJ_08_implementation_improvements.md` — état verrouillé Step-8

---

## Aim

Fermer les trois arbitrages **sans toucher un seul seuil pour effacer un FAIL**, et sans
re-simuler. Chaque décision doit sortir d'ici avec (a) une preuve tirée du code ou des artefacts,
(b) l'option écartée, (c) ce qui la renverserait, et (d) une gate **qu'on a vue échouer**.

**Coût total : aucune re-simulation.** Step 9 relit les agrégats §8E déjà sur disque. Le seul
input nouveau (l'exposition d'enveloppe par canal) se lit dans les 56 `run/eplusout.sql` qui
existent déjà sous `Step8_docs/campaign_local_v2/campaign_cf69d508/` (22 Go, 56 cellules,
vérifiées présentes le 2026-07-31). Lecture seule, pas d'EnergyPlus.

---

## Règle de méthode (héritée de `3rdJ_L3_improvements_step5_6_7.md`, inchangée)

1. **Colonnes consommées, pas md5.**
2. **Une gate doit être vue en train d'échouer** — refabriquer le défaut, montrer qu'elle lève.
   Toute gate créée ici entre dans `3rdJ_09_gate_falsifiability.py`, sans exception.
3. **Câblage au niveau IDF avant énergie.**
4. **Re-dériver, ne pas croire** — y compris un chiffre que j'ai moi-même écrit hier.
5. **Ne JAMAIS assouplir un seuil de gate** pour effacer un FAIL → **re-spécification** du critère
   + preuve empirique. Élargir une tolérance jusqu'à ce qu'elle passe est interdit ; remplacer un
   critère qui porte sur le mauvais objet ne l'est pas — c'est même la seule issue honnête.

---

## Ce qui a été re-dérivé avant d'écrire ce document

Tout ce qui suit a été lu dans le code ou les artefacts, pas repris du rapport de la veille.

| # | Fait | Source |
|---|---|---|
| V1 | Les 3 FAIL sont **tous sous le plancher**, jamais au-dessus : bureau 71,1 (0/56 en bande), retail 75,4 (12/56), hôtel 178,3 (28/56) | `outputs_step9/step9_gates.json` |
| V2 | Ordre des écarts = ordre d'enfouissement présumé : bureau −29 %, retail −6 %, hôtel −1 % | idem |
| V3 | **L'EUI Leg-2 n'est PAS en électricité seule.** `_eui_from_sql()` appelle `plotting.calculate_eui()`, qui somme la table SQL `End Uses (By Subcategory)` **sur toutes les colonnes de combustible**, n'excluant que les unités `m3` (l'eau). Le gaz y est. | `Leg2_2-split/Step8_docs/3rdJ_08_simulation_2split_agg.py:333-345` → `eSim_bem_utils_3J/plotting.py:292-347` |
| V4 | La restriction `Electricity:Facility` / `office_elec` de Leg-2 porte sur le **chemin diurne** (`keep_meters`), qui n'alimente jamais l'EUI | `Leg2_2-split/Step9_docs/3rdJ_09_activityDrivenLoads_2split.py:99-110` vs `:124-158` |
| V5 | **L'EUI « bureau » de Leg-2 est un EUI de TOUR, pas de canal.** La colonne `unit` vaut littéralement `tower` (n=252) ; `calculate_eui()` rend l'énergie et l'aire de **tout le modèle** | `Leg2_2-split/Step9_docs/outputs_step9/step9_eui_by_channel.csv` ligne `office,all,tower,252,172.7` |
| V6 | EUI de la tour Leg-3 : **100,4** kWh/m²/an (aire brute ABUPS, tous combustibles, médiane sur 56 cellules ; 90,8-115,3) ; **110,3** sur la base CFA des 4 canaux locatifs (99,7-127,3) | dérivé de `agg_meta.csv` (`site_energy_GJ` / `total_building_area_m2`) et de `step9_eui_by_channel.csv` |
| V7 | Donc **Leg-2 tour = 172,7 vs Leg-3 tour ≈ 100-110** : un facteur ~1,6 entre deux nombres qui décrivent le même type d'objet. Inexpliqué à ce jour. | V5 + V6 |
| V8 | L'exclusion hôtel des époques n'est **pas** motivée par « les données commencent en 2011 ». La vraie raison écrite dans le générateur : **la vérité-terrain QC commence en 2019** ; une courbe hôtel 2015 serait AB-seul → **confusion province × canal** dans tout le bras historique | `Step8_docs/3rdJ_08A_gen_historical_products_4split.py:12-20`, renvoyant à `Step6_docs/3rdJ_06_hotel_sarima_4split.py:24-29` |
| V9 | Le commentaire de `DELIBERATE_CHANNEL_EXCEPTIONS` ne porte que la moitié courte de la raison (« hotel source data starts 2011 ») — c'est **ce commentaire** qui a fait paraître l'exclusion de Y2015 arbitraire | `Step8_docs/3rdJ_08D_campaign_cells.py:352-357` |
| V10 | **`S9-LONG-hotel` PASSE (0,547-0,990 pp) sans pouvoir signifier ce qu'elle affirme** : l'hôtel est non injecté en Y2005/Y2010/Y2015 et injecté en Y2022, donc l'« écart d'époque » mélange un échelon injection on/off et du couplage thermique venant des trois autres canaux. Aucun comportement hôtel n'y est. | `3rdJ_09_...py:531-539` + V8 |
| V11 | Les 56 cellules de campagne ont bien leur `run/eplusout.sql` sur disque (pas d'archive à restaurer) | `Step8_docs/campaign_local_v2/campaign_cf69d508/*/run/` |

> **Correction assumée.** Le point « Leg-2 est peut-être en électricité seule », signalé à
> l'utilisateur le 2026-07-31 et inscrit dans la gate `S9-BASIS` et au §8 du doc Step 9, est
> **faux** (V3, V4). L'hypothèse venait d'un `keep_meters` lu dans le mauvais chemin de code. Le
> vrai écart entre les légs est ailleurs et il est plus important (V5, V7). Les deux endroits qui
> portent l'affirmation erronée sont corrigés en **T9-5**.

---

## Registre des décisions — 2026-07-31

### S9D-1 — Une bande « prototype autonome » cesse d'être un critère PASS/FAIL pour un canal empilé

- **Décision.** `S9-EUI-{office,retail,hotel}` passe en **INFO**, bande conservée mot pour mot
  comme provenance, écart et **signe** de l'écart reportés. Deux gates PASS/FAIL falsifiables la
  remplacent (S9D-2, S9D-3).
- **Preuve.** V1 + V2. Un canal enfoui au milieu d'une tour a une enveloppe presque entièrement
  en cloisons intérieures vers d'autres volumes conditionnés, pas de toiture, pas de dalle sur
  terre-plein, et une centrale partagée dimensionnée pour l'ensemble. Un prototype *Large Office*
  autonome est un **autre objet thermique**. Le critère ne porte pas sur une tolérance trop
  serrée : il porte sur le mauvais objet.
- **Ce n'est pas un assouplissement.** La règle interdit d'élargir une bande jusqu'à ce qu'un FAIL
  disparaisse. Ici la bande n'est ni élargie ni déplacée — elle est **retirée du rôle de juge** et
  remplacée par deux critères qui peuvent réellement échouer. C'est exactement le remède déjà
  appliqué à `S9-SHARE` (±2 pp) le 2026-07-31, pour la même raison de fond.
- **Écarté 1 — accepter les 3 FAIL tels quels.** Un tableau de bord définitivement rouge sur un
  fait qu'on sait explicable n'informe plus personne : au bout de trois numéros de version, un
  lecteur cesse de distinguer ce FAIL-là d'un vrai défaut. 0/56 cellules en bande sur le bureau
  n'est pas un signal, c'est un décalage de référentiel.
- **Écarté 2 — fabriquer des bandes « stacked-tower ».** Aucune source. Ce serait inventer un
  seuil pour le faire passer, c'est-à-dire l'interdit de la règle 5 sous un autre nom.
- **Renversé si** : le test de mécanisme S9D-3 échoue. Si le classement des écarts ne suit pas le
  classement d'exposition d'enveloppe, l'explication « canal empilé » est fausse, les FAIL
  redeviennent des défauts à instruire, et cette décision tombe. **C'est le point dur du lot A.**

> **RENVERSÉE 2026-07-31 — S9D-3 a échoué. S9D-1 tombe avec elle, comme prévu.**
> `S9-EUI-{office,retail,hotel}` **restent des gates PASS/FAIL inchangées**, et **restent FAIL**.
> `BENCH` n'est pas touché (vérifié ligne à ligne : identique à l'original).
> La clause était écrite avant de connaître le résultat ; elle est appliquée sans renégociation.
>
> Il faut nommer ce que cela coûte, car l'« Écarté 1 » ci-dessus reste vrai : on livre bien un
> tableau de bord rouge sur trois lignes. La différence est qu'on ne sait plus les expliquer.
> **Deux mécanismes ont été testés, deux ont été réfutés :**
> 1. *Enfouissement d'enveloppe* (S9D-3) → réfuté, corrélation du mauvais signe.
> 2. *Bande bureau contaminée par le défaut `calculate_eui()` de S9D-2* — hypothèse formée en
>    cours de route, en remarquant que le seul canal massivement déficitaire était le seul dont
>    `band_src` cite Leg-2. **Vérifiée avant d'agir, et fausse** : la bande (135, [100-200]) est
>    codée en dur dans `Leg2_2-split/Step9_docs/3rdJ_09_..._2split.py:50` et provient de
>    `Step8_docs/deepResearch/…As-Modelled Bands.md` — littérature NECB2020/90.1-2019. Le job
>    1054800 est le nombre **testé contre** cette bande, jamais sa source. Le défaut de
>    `calculate_eui()` ne la contamine pas.
>
> *Défaut de provenance à corriger au passage* : la chaîne `band_src` de Leg-3 dit
> `"NECB/PNNL as-modelled (Leg-2, job 1054800)"`, ce qui nomme un job de simulation là où la
> source est un document de recherche. C'est précisément ce qui m'a induit en erreur. À
> reformuler en `"NECB2020/90.1-2019 DOE-PNNL as-modelled band (deepResearch/…As-Modelled
> Bands.md ; reprise de Leg-2)"`. **La bande elle-même ne bouge pas** — seule son étiquette.
>
> **Les 3 FAIL sont donc remontés à l'utilisateur comme défauts non expliqués**, ce que le
> point 5 de la méthode de test globale exige explicitement. Pistes non instruites, à ne pas
> confondre avec des conclusions : densité de charges internes du canal bureau après injection
> GSS vs hypothèses du prototype ; part de la centrale partagée réaffectée au `service_MEP`
> plutôt qu'aux canaux locataires ; et le fait, non expliqué non plus, que **retail et hôtel
> soient à −5,7 % et −0,9 %** alors que le bureau est à −28,9 % — un écart propre au canal
> bureau, pas un biais général de la tour.

### S9D-2 — Le seul EUI comparable à une bande existante est celui de la TOUR

- **Décision.** Nouvelle gate PASS/FAIL `S9-EUI-TOWER` : EUI de la tour entière, tous combustibles,
  base explicite, contre la bande [100-200] du précédent NECB/PNNL — **le seul chiffre du projet
  calculé sur une tour** (V5).
- **Preuve.** V5 : Leg-2 n'a jamais validé un canal bureau, il a validé une tour (`unit=tower`).
  Leg-3 produit le premier EUI **de canal** du projet. Le précédent reste valable — sur son objet.
- **Réserve, à ne pas taire.** V6/V7 : la tour Leg-3 sort à ~100-110 contre 172,7 pour Leg-2. La
  gate telle que spécifiée serait donc **au bord de la bande, et une partie des cellules
  SuperTall en dessous**. Ce n'est pas une raison de bouger la bande : c'est la raison d'exécuter
  **T9-4** (réconciliation) *avant* de figer la gate. Si le facteur 1,6 s'explique par le
  dénominateur (aire conditionnée vs brute) ou par un double comptage de
  `End Uses By Subcategory`, le nombre de référence change — pas le seuil.
- **Renversé si** : T9-4 montre que les deux nombres ne décrivent pas le même objet (IDF différent,
  millésime différent, dénominateur différent). Alors il n'existe aucune bande tour valable et la
  gate ne doit pas être créée — on le dit, on ne la crée pas.

> **RÉSOLU 2026-07-31 — la gate n'est PAS créée. T9-2 est annulée.**
> T9-4 a tranché par une troisième voie, non anticipée : les deux nombres décrivent bien le
> **même objet** (mêmes fichiers `.idf` Leg-2 réutilisés littéralement par
> `3rdJ_08D_campaign_cells.py:130-169`, même EnergyPlus 24.2.0, dénominateur identique —
> `Net Conditioned = Total Building Area = 72 623,07 m²`, donc cause (i) écartée). C'est le
> **nombre de référence lui-même qui est faux**.
> **Mécanisme, vérifié indépendamment sur un `eplusout.sql` v24.2.0 réel**
> (`campaign_cf69d508/B_central__Tall__MTL`) : EnergyPlus écrit une table nommée
> `End Uses By Subcategory` sous **deux `ReportName` distincts** —
> `AnnualBuildingUtilityPerformanceSummary` (273 lignes, **GJ**, l'énergie annuelle) et
> `DemandEndUseComponentsSummary` (273 lignes, **W**, la puissance de pointe). La requête de
> `calculate_eui()` (`eSim_bem_utils_3J/plotting.py:293-299`) filtre sur `TableName` et **jamais
> sur `ReportName`** ; le garde-fou d'unité (`:319`, `if 'm3' in units: continue`) n'écarte que
> l'eau, pas les `W`. Chaque ligne de **watts** est donc additionnée telle quelle comme des kWh
> (`:345`, `else: val_kwh = val`).
> Mesure sur le SQL v242 : 7 837 731 kWh d'énergie légitime **+ 5 533 372 « kWh » qui sont des
> watts** = 13 371 103 → facteur **1,706×**.
> Recoupement : 172,7 / 1,706 ≈ **101,2** contre **100,4** mesurés côté Leg-3 sur la même tour
> (base ABUPS brute). Indicatif seulement — le ratio vient d'un autre run, ce n'est pas une
> dérivation — mais les deux légs s'accordent à ~1 % une fois le défaut retiré. **Le facteur 1,6
> n'était pas physique.** Indice corroborant : les trois médianes par archétype Leg-2
> (`Office_Knowledge` 172,6 / `Office_Public` 172,5 / `Office_Sales` 172,7) sont anormalement
> resserrées pour trois profils d'usage différents sur six villes — signature d'un artefact
> systématique dominant la variation architecturale réelle.
> **Conséquence.** On ne gate pas contre un nombre corrompu. À la place, un **INFO
> `S9-EUI-TOWER-INFO`** qui publie l'EUI tour Leg-3 (~100,4 brut / ~110,3 CFA locataires), cite
> la bande [100-200] comme contexte et **dit pourquoi elle n'est pas scorée**. Produire un 172,7
> corrigé exigerait de rouvrir Leg-2 (clos, paper-ready) : **décision utilisateur, hors périmètre
> de ce lot** — voir Progress Log, point d'escalade.
> *Note hors périmètre, consignée pour mémoire* : l'étiquette `CAN_CLG` ne pointe pas sur le même
> EPW dans les deux légs — **Winnipeg (7A) chez Leg-2, Calgary (Z7A) chez Leg-3**. Sans effet sur
> ce qui précède, mais à ne pas découvrir plus tard.

### S9D-3 — L'explication « canal empilé » doit être testée, pas invoquée

- **Décision.** Nouvelle gate PASS/FAIL `S9-EUI-EXPOSURE`. On mesure, par canal et par cellule,
  l'**exposition d'enveloppe** = surface de parois dont `ExtBoundaryCondition = Outdoors`
  (+ toiture + dalle sur terre-plein) rapportée à la CFA du canal. L'explication prédit une
  chose vérifiable : **le classement des expositions et le classement des écarts à la bande
  coïncident** (bureau le plus enfoui → écart le plus grand ; hôtel le moins → écart le plus
  petit). Testé par corrélation de rang, exigée positive et significative.
- **Preuve de plausibilité.** V2 : l'ordre observé (bureau −29 %, retail −6 %, hôtel −1 %) est
  déjà l'ordre attendu. Mais un ordre attendu **observé après coup** n'est pas une preuve — d'où
  la gate.
- **Écarté.** Laisser `S9-BASIS` en INFO explicatif seul. C'était l'état livré le 2026-07-31 :
  une explication non falsifiable, c'est-à-dire une excuse. Le projet a déjà payé ce genre de
  ligne (`S9-INJECTION` écrite incapable d'échouer, débusquée par la sonde le même jour).
- **Renversé si** : la corrélation est nulle ou négative. Dans ce cas S9D-1 tombe avec elle
  (voir « renversé si » ci-dessus) — les deux décisions sont volontairement liées.

> **RÉSOLU 2026-07-31 — la prédiction est FALSIFIÉE. La clause de renversement s'applique.**
> Prédit avant exécution : `exposition(bureau) < exposition(retail) < exposition(hôtel)`.
> Mesuré (56/56 cellules, ordre identique partout) : **`hôtel (0,325) < bureau (0,382) <
> retail (0,467)`**.
>
> | canal | exposition (médiane) | EUI CFA | écart au plancher |
> |---|---|---|---|
> | hôtel | **0,325** | 178,3 | **−0,9 %** |
> | bureau | 0,382 | 71,1 | **−28,9 %** |
> | retail | 0,467 | 75,4 | −5,7 % |
>
> L'hôtel est le canal **le plus enfoui** des trois et **le plus proche de sa bande**. C'est
> l'inverse exact du mécanisme invoqué. Spearman poolé **−0,171** (n=168, p=0,026 — pas « nul »,
> significativement **du mauvais signe**) ; médiane par cellule **−0,500** ; 39 % de rho positifs ;
> signe non constant sur les 4 paires bâtiment × ville.
> *Contrôle de parsing* : total d'enveloppe comparé à `EnvelopeSummary / Opaque Exterior / Gross
> Area` d'EnergyPlus → écart max **0,0004 %** sur 56 cellules. Ce n'est pas une erreur de mesure.
> *Limite honnête à connaître* : la géométrie ne varie qu'entre Tall et SuperTall, donc
> `exposure_ratio` ne prend que **2 valeurs distinctes** par canal. Le rho par cellule bouge parce
> que l'EUI se réordonne, pas l'exposition. Cela n'affecte pas le verdict — l'ordre réfutant est
> mesuré à l'identique dans 56/56 cellules — mais l'inférence porte sur 2 géométries, pas 56.
>
> **La gate `S9-EUI-EXPOSURE` n'est donc PAS créée en PASS/FAIL.** Scorer en permanence une
> hypothèse que l'on vient d'enterrer ajouterait un 4ᵉ FAIL sans informer personne. Ce qui est
> écrit à la place : un **INFO `S9-EUI-EXPOSURE`** qui publie le tableau ci-dessus, le rho, le
> contrôle à 0,0004 % et la conclusion — *l'explication « canal empilé » a été testée et réfutée*.
> La mesure reste au dossier ; c'est l'explication qui est retirée, pas le chiffre.

### S9D-4 — Leg-2 n'est pas rouvert ; une seule réconciliation bornée est faite

- **Décision.** Aucun résultat Leg-2 n'est recalculé, aucune conclusion Leg-2 n'est remise en
  cause, le manuscrit Leg-2 n'est pas touché. On exécute **une** vérification bornée et
  lecture-seule : d'où vient le facteur 1,6 entre 172,7 et ~100-110 (V7).
- **Preuve que la crainte initiale est levée.** V3 + V4 : l'EUI Leg-2 est tous combustibles.
  L'alerte « électricité seule » est retirée.
- **Pourquoi malgré tout une vérification.** Parce que S9D-2 **dépend** du nombre 172,7. Croire un
  nombre parce qu'il est publié est précisément la règle 4 violée. Trois causes candidates, toutes
  testables sur artefacts existants : (i) dénominateur — `conditioned_floor_area` chez Leg-2 vs
  aire brute ABUPS chez moi en V6 ; (ii) double comptage possible de
  `End Uses By Subcategory` (lignes de sous-catégorie **et** lignes agrégées sommées ensemble,
  `plotting.py:310-346`) ; (iii) IDF/millésime/ville différents.
- **Renversé si** : (ii) est confirmé. Alors le chiffre Leg-2 est surestimé, ce qui **est** un
  défaut Leg-2 — et à ce moment-là, et seulement à ce moment-là, on rouvre, avec l'utilisateur.

### S9D-5 — L'hôtel reste hors de l'axe d'époque ; c'est le commentaire qui était faux

- **Décision.** `Y2015` ne reçoit **pas** de canal hôtel. L'exclusion est maintenue. Ce qui change
  est **documentaire** : le commentaire de `DELIBERATE_CHANNEL_EXCEPTIONS` est réécrit avec la
  vraie raison, et la question ouverte au §8 du doc Step 9 est fermée.
- **Preuve.** V8 : la vérité-terrain hôtel **QC commence en 2019**. Une courbe 2015 serait
  AB-seule. Le bras historique porte deux villes ; injecter un canal dans une seule d'entre elles
  introduit une **confusion province × canal** qui contaminerait les quatre gates `S9-LONG-*`,
  pas seulement l'hôtel. L'argument « 2015 est postérieur à 2011 donc pourquoi l'exclure » était
  fondé sur V9 — un commentaire qui ne dit que la moitié courte de la raison.
- **Écarté — injecter l'hôtel en Y2015 pour AB seulement.** Renforcerait le volet longitudinal
  d'un canal en détruisant la comparabilité des deux villes sur tous les canaux. Mauvais échange.
- **Écarté — étendre la SARIMA QC en arrière jusqu'en 2015.** C'est de la fabrication. Interdit.
- **Renversé si** : une source QC ouverte antérieure à 2019 apparaît (cf. la piste OGLA/CKAN qui a
  déjà résolu l'AB). Alors les trois époques deviennent injectables **des deux côtés à la fois**,
  et il faut les traiter ensemble, pas Y2015 seul.

### S9D-6 — `S9-LONG-hotel` est un PASS creux et doit être re-spécifiée

- **Décision.** `S9-LONG-hotel` passe en **INFO**, avec le mécanisme nommé. La moitié falsifiable
  devient une gate propre : `S9-LONG-UNINJECTED` — **assertion** que l'hôtel est non injecté dans
  les trois époques historiques, lue depuis `DELIBERATE_CHANNEL_EXCEPTIONS` et **confrontée à la
  table de cellules**, plus quantification du résidu comme couplage.
- **Preuve.** V10. La gate mesure un écart de 0,547-0,990 pp et le présente comme une trajectoire
  d'époque. Or l'hôtel ne porte aucun produit variant par époque : ce qui bouge est (a) l'échelon
  injection on/off entre 2015 et 2022 et (b) le couplage thermique des trois autres canaux. Un
  PASS qui ne peut pas distinguer « comportement hôtel » de « injection allumée ailleurs » est
  exactement la famille de défauts que ce projet traque depuis trois jours.
- **Écarté — supprimer la gate.** On perdrait le garde-fou : si quelqu'un injecte un jour l'hôtel
  en historique sans mettre à jour la lecture, plus rien ne le signale. D'où l'assertion.
- **Renversé si** : S9D-5 est renversée (hôtel injectable en historique). La gate redevient alors
  une vraie gate longitudinale.

---

## Lot A — Re-spécification du critère EUI

### T9-1 — Rétrograder `S9-EUI-{c}` en INFO, sans toucher `BENCH` — **ANNULÉE 2026-07-31**

> **Non exécutée.** T9-3 a falsifié le mécanisme qui devait la porter (voir S9D-3 RÉSOLU et S9D-1
> RENVERSÉE). Les trois gates restent **PASS/FAIL** et restent **FAIL**. `BENCH` reste intact.
> L'ordre imposé par le plan — « T9-3 avant T9-1, jamais l'inverse » — a fait exactement ce pour
> quoi il était écrit : sans lui, les FAIL auraient été effacés d'abord et la justification
> cherchée ensuite, et le test n'aurait jamais été passé.
> Les étapes ci-dessous restent affichées non exécutées.

**Aim.** Retirer à une bande « prototype autonome » le rôle de juge d'un canal empilé, en
conservant intégralement sa provenance et le signe de l'écart.

**Steps.**
1. `3rdJ_09_activityDrivenLoads_4split.py`, boucle `for c in TENANT` du bloc `-- EUI in band --`
   (≈ `:287-305`) : statut `INFO` au lieu de `PASS`/`FAIL`.
2. Le détail doit rester **plus** informatif qu'avant, pas moins : n cellules dans la bande,
   médiane, plage, **écart signé au plancher en %**, et la mention explicite que le critère PASS
   est désormais porté par `S9-EUI-TOWER` + `S9-EUI-EXPOSURE`.
3. `BENCH` (`:70-79`) **n'est pas modifié** — ni valeur, ni source. C'est la garantie vérifiable
   qu'aucun seuil n'a bougé.
4. `S9-BASIS` absorbe le renvoi vers la gate de mécanisme et perd l'hypothèse « électricité
   seule » (voir T9-5).

**Expected result.** 3 lignes INFO au lieu de 3 FAIL, bandes identiques dans le fichier,
`git diff` sur `BENCH` **vide**.

**Test method.** `diff` du bloc `BENCH` avant/après = 0 ligne. Le rapport HTML doit toujours
afficher les bandes 100-200 / 80-155 / 180-300 et la figure `fig_eui_4ch.png` doit conserver ses
rectangles verts aux mêmes ordonnées.

---

### T9-2 — Gate `S9-EUI-TOWER` (conditionnelle à T9-4) — **ANNULÉE 2026-07-31**

> **Issue retenue : « aucune gate + un INFO qui dit pourquoi »**, la seconde branche prévue au
> paragraphe *Expected result* ci-dessous. Motif dans S9D-2 (RÉSOLU) : le nombre de référence
> 172,7 est gonflé ~1,706× par un défaut de `calculate_eui()` (fusion de deux tables E+ homonymes,
> énergie GJ + puissance W). Il ne décrit pas le bâtiment, donc il ne peut pas servir de seuil.
> **Ce qui est écrit à la place** : un INFO `S9-EUI-TOWER-INFO` publiant l'EUI tour Leg-3 sur ses
> deux bases (~100,4 brut / ~110,3 CFA locataires), citant [100-200] comme **contexte non scoré**,
> et nommant le défaut. Aucune sonde de falsifiabilité n'est due (un INFO ne peut pas échouer —
> c'est précisément pourquoi il ne prétend rien).
> Les étapes 1-4 ci-dessous restent en place **non exécutées**, pour que la bifurcation soit
> lisible plutôt que effacée.

**Aim.** Juger l'EUI sur l'objet pour lequel une bande existe réellement : la tour.

**Steps.**
1. **Attendre T9-4.** Cette gate n'est écrite qu'une fois le nombre de référence réconcilié.
2. EUI tour = `site_energy_GJ` × 277,778 / dénominateur, **dénominateur = celui que T9-4 aura
   établi comme identique à celui de Leg-2**. La colonne de base est nommée dans la sortie, jamais
   en note de bas de page (convention §Step-9 déjà en vigueur).
3. PASS/FAIL contre la bande retenue par T9-4, provenance citée (`job 1054800`, `unit=tower`).
4. Reporter dans le détail les deux bases (brute et CFA) — V6 les donne : 100,4 et 110,3 — pour
   qu'un lecteur voie l'effet du dénominateur au lieu de le subir.

**Expected result.** Une gate PASS/FAIL de plus, ou — si T9-4 conclut que les objets diffèrent —
**aucune gate** et un INFO qui dit pourquoi. Les deux issues sont acceptables ; inventer la gate
malgré une réconciliation ratée ne l'est pas.

**Test method.** Sonde de falsifiabilité : injecter un `site_energy_GJ` ×2 sur une cellule et
vérifier que la gate lève.

---

### T9-3 — Gate `S9-EUI-EXPOSURE` (le test de mécanisme — pièce maîtresse du lot)

**Aim.** Transformer « un EUI plus bas est la direction physiquement attendue » d'argument en
mesure. Sans cette tâche, T9-1 n'est qu'un déplacement de statut.

**Steps.**
1. Nouveau script `Step9_docs/3rdJ_09X_envelope_exposure.py`, **lecture seule**, itérant les 56
   `campaign_local_v2/campaign_cf69d508/<tag>/run/eplusout.sql`.
2. Par zone : surface des `Surfaces` avec `ExtBoundaryCondition = Outdoors` (murs + toitures +
   fenêtres) et surfaces `Ground`. Zone → canal par la **même** correspondance Tag-2 que §8E —
   importée, jamais réimplémentée (règle « une seule source de vérité », cf. Défaut 1 du lot
   Step-8).
3. Sortie : `outputs_step9/step9_envelope_exposure.csv`
   (`cell_tag, channel, ext_area_m2, ground_area_m2, cfa_m2, exposure_ratio`).
4. Gate `S9-EUI-EXPOSURE` dans Step 9 : sur les 4 canaux (l'hôtel, le retail, le bureau ont une
   bande ; le résidentiel entre comme point supplémentaire via son écart au contexte SHEU),
   corrélation de rang de Spearman entre `exposure_ratio` et l'écart relatif au plancher de bande.
   **PASS ssi ρ > 0 sur au moins 90 % des cellules** et signe cohérent sur les 4 paires
   bâtiment × ville.
5. Prédiction écrite **avant** l'exécution, dans le docstring : bureau = exposition la plus faible,
   hôtel = la plus forte parmi les trois canaux à bande. Si l'exécution la contredit, c'est le
   résultat, on ne réécrit pas la prédiction.

**Expected result.** Soit la prédiction tient — et S9D-1 est fondée, l'explication passe dans le
manuscrit avec un chiffre —, soit elle ne tient pas — et **T9-1 est annulée**, les 3 FAIL
redeviennent des défauts à instruire.

**Test method.** Sonde : permuter les `exposure_ratio` entre canaux et vérifier que la gate lève.
Contrôle indépendant : la somme des `ext_area_m2` par cellule doit correspondre à l'aire
d'enveloppe totale du modèle (croisement ABUPS/`eplusout.eio`) à 1 % près.

**⚠️ Contrainte machine.** Lecture SQL locale sur 22 Go : traiter **une cellule à la fois**, fermer
la connexion à chaque itération, ne jamais charger les 56 en mémoire. La machine ne peut pas être
redémarrée à distance.

---

## Lot B — Le précédent Leg-2

### T9-4 — Réconciliation bornée de l'EUI tour entre les deux légs

**Aim.** Expliquer le facteur ~1,6 entre 172,7 (Leg-2, V5) et ~100-110 (Leg-3, V6), **sans rien
recalculer chez Leg-2**.

**Steps.**
1. **Dénominateur.** Relever ce que `calculate_eui()` a réellement rendu comme aire
   (`conditioned_floor_area` sinon `total_floor_area`, `plotting.py:274-289`) sur un run Leg-2, et
   le comparer au `total_building_area_m2` ABUPS employé en V6. Un écart de dénominateur explique
   une partie connue de l'écart et se corrige par le choix de base, pas par un seuil.
2. **Double comptage.** Sur **un seul** `eplusout.sql` Leg-2 : comparer la somme de
   `End Uses By Subcategory` (ce que fait `calculate_eui`) à la table `End Uses` et au
   `Site Energy` de l'ABUPS. Si le premier dépasse les deux autres, le double comptage est
   confirmé et chiffré.
3. **Même objet ?** Vérifier que le run Leg-2 utilisé pour 172,7 porte bien la même famille d'IDF
   tour que la campagne Leg-3 (nom d'IDF, millésime, ville, version E+).
4. Conclusion écrite en trois lignes, avec le nombre retenu pour T9-2 — ou le refus motivé de
   créer T9-2.

**Expected result.** Une cause identifiée parmi (i)/(ii)/(iii), chiffrée. Aucun fichier Leg-2
modifié.

**Test method.** Les trois nombres du point 2 (`End Uses By Subcategory`, `End Uses`,
`Site Energy` ABUPS) mis côte à côte dans le Progress Log. La cohérence, ou son absence, est
lisible directement.

**Périmètre — à ne pas déborder.** Si (ii) est confirmé : **s'arrêter**, l'écrire, remonter à
l'utilisateur. Leg-2 est fermé et paper-ready ; sa réouverture est une décision utilisateur, pas
une conséquence automatique de cette tâche.

---

### T9-5 — Retirer l'affirmation « électricité seule », partout

**Aim.** Une hypothèse fausse (V3, V4) écrite dans une gate et dans un doc devient, en deux
versions, un fait que plus personne ne vérifie.

**Steps.**
1. `3rdJ_09_activityDrivenLoads_4split.py`, texte de `S9-BASIS` (≈ `:317-329`) : supprimer
   « it interacts with the open question of whether the Leg-2 office precedent … was itself
   computed electricity-only ». Remplacer par le fait établi : précédent Leg-2 = **tous
   combustibles** (`calculate_eui`), et **de tour**, pas de canal (`unit=tower`).
2. `3rdJ_09_activityDrivenLoads_4split.md` §8 : même correction, avec les références de ligne V3/V5.
3. Ajouter la conséquence utile : Leg-3 produit le **premier EUI par canal** du projet ; le
   précédent Leg-2 ne l'a jamais validé parce qu'il ne portait pas sur cet objet.

**Expected result.** Zéro occurrence de « electricity-only » / « électricité seule » à propos de
Leg-2 dans Step9.

**Test method.** `grep -rn "electricity-only\|électricité seule" Step9_docs/` → vide.

---

## Lot C — Axe d'époque et hôtel

### T9-6 — Écrire la vraie raison de l'exclusion hôtel

**Aim.** Supprimer la cause de la question, pas seulement la question (V8, V9).

**Steps.**
1. `Step8_docs/3rdJ_08D_campaign_cells.py:352-357` : remplacer les trois commentaires
   « hotel source data starts 2011 » par la raison complète — **vérité-terrain QC à partir de
   2019** ; une courbe 2015 serait AB-seule ; injecter dans une seule province crée une confusion
   province × canal sur **tout** le bras historique. Renvoyer à
   `Step8_docs/3rdJ_08A_gen_historical_products_4split.py:12-20` et
   `Step6_docs/3rdJ_06_hotel_sarima_4split.py:24-29`.
2. `3rdJ_09_activityDrivenLoads_4split.md` §8, dernier paragraphe : la question ouverte
   « Y2015 est postérieur à 2011 — pourquoi l'exclure ? » est **fermée**, avec la réponse et la
   condition de réouverture (S9D-5 : une source QC ouverte antérieure à 2019).
3. Aucune donnée, aucun produit, aucune cellule de campagne n'est touché.

**Expected result.** Le prochain lecteur — humain ou agent — ne repose pas la question.

**Test method.** Relecture ciblée des trois emplacements. Le commentaire doit nommer **2019** et
le mot « confond/confusion », sinon il retombe dans le défaut V9.

---

### T9-7 — Re-spécifier `S9-LONG-hotel`

**Aim.** Un PASS qui ne peut pas être faux ne protège rien (V10).

**Steps.**
1. `3rdJ_09_...py:531-539` : pour le canal hôtel, statut **INFO**, avec le mécanisme nommé
   explicitement — écart d'époque = échelon injection on/off (2015→2022) + couplage thermique des
   trois autres canaux ; **aucun comportement hôtel n'y entre**.
2. Nouvelle gate PASS/FAIL `S9-LONG-UNINJECTED` : l'hôtel doit être **absent** de
   `_expected_channels()` pour Y2005/Y2010/Y2015 **et** absent des cellules de campagne
   correspondantes. Importer `DELIBERATE_CHANNEL_EXCEPTIONS` depuis
   `3rdJ_08D_campaign_cells.py` — ne pas recopier la constante.
3. `S9-LONG-{office,retail,residential}` restent PASS/FAIL, inchangées.
4. Le détail d'INFO cite le résidu chiffré (0,547-0,990 pp) comme **mesure du couplage**, ce qui
   est une information réelle et neuve : c'est l'ordre de grandeur de l'interaction thermique
   entre canaux d'une même tour.

**Expected result.** 1 PASS creux en moins, 1 gate falsifiable en plus, et un chiffre de couplage
utilisable au manuscrit.

**Test method.** Sonde : ajouter `hotel` aux canaux attendus de `Y2015` dans un fixture et
vérifier que `S9-LONG-UNINJECTED` lève.

---

### T9-8 — Étendre la sonde de falsifiabilité aux nouvelles gates

**Aim.** Règle de méthode 2, sans exception. `3rdJ_09_gate_falsifiability.py` a déjà débusqué
`S9-INJECTION` (écrite incapable d'échouer) le 2026-07-31 ; toute gate créée ici y passe.

**Steps.** Ajouter un cas par gate créée — `S9-EUI-TOWER` (si créée), `S9-EUI-EXPOSURE`,
`S9-LONG-UNINJECTED` — chacun refabriquant le défaut que la gate prétend attraper.

**Expected result.** Sonde verte : **chaque** gate PASS/FAIL du Step 9 a été vue échouer au moins
une fois. Les gates rétrogradées en INFO (T9-1, T9-7) sortent du périmètre de la sonde — et la
sonde doit le dire, pour qu'on ne lise pas leur absence comme une couverture.

**Test method.** `py -3 3rdJ_09_gate_falsifiability.py` — sortie listant, gate par gate,
`fail-observed: yes/no`.

---

## Ce qui n'est PAS touché

| Élément | Raison |
|---|---|
| `BENCH` — les 3 bandes as-modelled | Garantie vérifiable qu'aucun seuil n'a bougé (S9D-1) |
| La campagne 56 cellules | Aucune re-simulation. Tout se relit dans §8E + les SQL existants |
| §8E, Step 8, Step 7, Step 6, Step 5 | Hors périmètre. Rien ici ne remonte en amont |
| Tout fichier sous `Leg2_2-split/` | Leg-2 est fermé et paper-ready. T9-4 est **lecture seule** |
| Les produits hôtel, la SARIMA, les données AB/QC | S9D-5 : rien n'est fabriqué |

---

## Ordre d'exécution

```
T9-3  (exposition d'enveloppe)  ─┐   indépendantes, parallélisables
T9-4  (réconciliation Leg-2)    ─┘
        │            │
        ▼            ▼
T9-1 (INFO)      T9-2 (gate tour, conditionnelle au verdict de T9-4)
        │            │
        └─────┬──────┘
              ▼
T9-5, T9-6, T9-7  (documentaire + re-spec, aucune dépendance)
              ▼
T9-8  (sonde de falsifiabilité)
              ▼
Ré-exécution du Step 9 → nouveau scorecard, tables, figures, HTML
```

**T9-3 avant T9-1**, jamais l'inverse : la rétrogradation en INFO n'est légitime que si le test de
mécanisme la porte. Exécuter T9-1 d'abord, c'est effacer les FAIL puis chercher une justification.

---

## Faut-il ré-exécuter le Step 9 ? — Oui, et **seulement** le Step 9

- Step 9 lit les agrégats `Step8_docs/outputs_step8/agg/*.csv`, déjà produits et vérifiés
  (fermetures carburant et canal à 0,000000 %, 56/56 cellules, un seul schéma `db4e729f`).
- Rien dans ce document ne modifie une entrée de simulation, un produit d'occupation, un IDF ou
  un fichier §8E. **Aucun job cluster, aucun EnergyPlus.**
- Coût : la relecture SQL de T9-3 (56 fichiers, une cellule à la fois) puis quelques minutes de
  Step 9. Sortie régénérée : scorecard, 4 tables, 5 figures, HTML.

---

## Test method — global

Le lot est fermé quand **les cinq** conditions tiennent :

1. `git diff` sur le bloc `BENCH` = **vide** (aucun seuil déplacé).
2. `3rdJ_09_gate_falsifiability.py` : **toute** gate PASS/FAIL du Step 9 vue échouer au moins une
   fois, les nouvelles comprises.
3. `S9-EUI-EXPOSURE` exécutée et son verdict **écrit tel quel** — y compris s'il annule T9-1.
4. `grep "electricity-only\|électricité seule"` sur `Step9_docs/` → vide.
5. Le scorecard final ne contient **aucun FAIL non expliqué par un mécanisme mesuré** — et si un
   FAIL subsiste faute de mécanisme, il reste FAIL et il est remonté à l'utilisateur, pas absorbé.

---

## Progress Log

*(une entrée datée par tâche, avec les nombres re-dérivés, pas recopiés)*

### 2026-07-31 — T9-6 · exclusion hôtel documentée (lot C)

`Step8_docs/3rdJ_08D_campaign_cells.py:345-357` — le commentaire de
`DELIBERATE_CHANNEL_EXCEPTIONS` portait « hotel source data starts 2011 », qui est la date de
début **AB seulement** et donnait à Y2015 l'air d'un choix arbitraire. Remplacé par la vraie
raison : **la vérité-terrain QC commence en 2019**
(`Step6_docs/3rdJ_06_hotel_sarima_4split.py:24-29` — AB 2011-01..2022-09, QC 2019-01..2022-12),
donc une courbe hôtel 2005/2010/2015 serait **AB-seule** → confusion province × canal
contaminant les quatre gates `S9-LONG-*`, pas seulement l'hôtel. Condition de réouverture
écrite dans le code (S9D-5). §8 du doc Step-9 mis à jour.

**Re-dérivé, pas recopié** : ré-import du module après édition →
`[('Default_NECB', frozenset()), ('Y2005', frozenset({'office','residential','retail'})),
('Y2010', idem), ('Y2015', idem)]`. **Les valeurs sont inchangées** — commentaire seul.
Zéro re-simulation.

*Correction de chemin* : ma spécification citait `3rdJ_06_hotel_sarima_4split.py` sans son
dossier ; le fichier est sous **`Step6_docs/`**, pas `Step8_docs/`. Corrigé en V8 et en T9-6.

### 2026-07-31 — T9-5 + T9-7 · fausse alerte purgée, gate vide remplacée (lots B et D)

**T9-5.** Le texte `S9-BASIS` affirmait que l'EUI Leg-2 était électricité seule. C'était **ma
propre erreur de la veille**, pas un constat. Retirée du `.py` et du `.md`, remplacée par les
faits avec références fichier:ligne (tous combustibles ; `unit=tower`, donc Leg-2 n'a jamais
validé un canal bureau — Leg-3 produit le premier EUI **de canal** du projet).
Vérifié : `grep "electricity-only"` → **0 occurrence** dans les sources `.py`/`.md`.
Restent deux occurrences dans `outputs_step9/step9_gates.json` et `step9_report.html` —
**artefacts générés**, ils disparaissent à la ré-exécution ; à re-vérifier après.

**T9-7.** `S9-LONG-hotel` passait à vide (V10) : l'hôtel est non injecté en Y2005/10/15 et
injecté en Y2022, donc son « écart d'époque » de 0,547-0,990 pp est un échelon injection on/off
plus du couplage thermique venant des trois autres canaux — aucun comportement hôtel dedans.
Rétrogradée en **INFO** ; remplacée par une gate falsifiable **`S9-LONG-UNINJECTED`** qui vérifie
que les canaux exclus le sont bien, en important
`DELIBERATE_CHANNEL_EXCEPTIONS`/`_expected_channels`/`build_campaign_cells` depuis
`3rdJ_08D_campaign_cells.py` (source unique — jamais ré-implémentés). **FAIL explicite si
l'import échoue**, pour qu'une gate muette ne puisse pas se déguiser en gate verte.
Exécution isolée contre les artefacts courants : 12 cellules historiques, **0 portant un canal
hôtel** → la gate passerait. `py -3 -m py_compile` OK.

**Vérifié moi-même, pas pris au mot** (règle : ne pas croire un before/after consigné) : `BENCH`
(`3rdJ_09_...py:91-100`) est **identique ligne pour ligne** à l'original — bureau 135/[100-200],
retail 110/[80-155], hôtel 240/[180-300], résidentiel sans bande. **Aucun seuil n'a bougé.**

### 2026-07-31 — T9-4 · réconciliation Leg-2 : le nombre de référence est corrompu (lot B)

Voir S9D-2 (RÉSOLU) pour le détail. Résumé des trois causes candidates :
- **(i) dénominateur — ÉCARTÉ.** `Net Conditioned = Total Building = 72 623,07 m²`,
  `Unconditioned = 0` des deux côtés. Rien à réduire.
- **(iii) objets différents — ÉCARTÉ.** Leg-3 réutilise **littéralement** les `.idf` Leg-2
  (`3rdJ_08D_campaign_cells.py:130-169`), même EnergyPlus 24.2.0.
- **(ii) double comptage — CONFIRMÉ**, mais par un mécanisme plus grave que celui que j'avais
  supposé : ce ne sont pas des lignes agrégat+sous-catégorie sommées ensemble, c'est la **fusion
  de deux `ReportName` homonymes**, dont l'un est en **watts**.

**Re-dérivé moi-même sur `campaign_cf69d508/B_central__Tall__MTL/run/eplusout.sql` (v24.2.0,
la version réellement utilisée par Leg-2 — l'agent n'avait qu'un proxy en v22.1)** :

| ReportName | TableName | Unités | Lignes |
|---|---|---|---|
| `AnnualBuildingUtilityPerformanceSummary` | `End Uses By Subcategory` | **GJ** | 273 |
| `DemandEndUseComponentsSummary` | `End Uses By Subcategory` | **W** | 273 |

Ce que `calculate_eui()` additionne réellement : **7 837 731 kWh** légitimes **+ 5 533 372 W
comptés comme des kWh** = **13 371 103** → facteur **1,706×**.
Recoupement : 172,7 / 1,706 ≈ **101,2** vs **100,4** mesurés côté Leg-3 sur la même tour.
Indicatif et non une dérivation (le ratio vient d'un autre run), mais les deux légs s'accordent
à ~1 % une fois le défaut retiré : **le facteur 1,6 n'était pas physique**.

**Conséquence** : T9-2 annulée (voir sa section). **Aucun fichier sous `Leg2_2-split/` n'a été
modifié** — contrainte respectée.

> **⚠ POINT D'ESCALADE — décision utilisateur, non tranchée par ce lot.**
> Leg-2 est clos et paper-ready, et son EUI office publié (172,6 / 172,5 / 172,7 selon
> l'archétype) est gonflé d'environ 1,7×. Le corriger, c'est rouvrir Leg-2. Ce lot **s'arrête
> ici** et ne fait aucune recommandation sur le manuscrit. Correctif minimal si la décision est
> prise un jour : filtrer `ReportName = 'AnnualBuildingUtilityPerformanceSummary'` dans
> `plotting.py:293-299`, ou réutiliser la méthode Leg-3 (somme de meters avec clôture
> d'attribution, `3rdJ_08E_aggregate_4split.py:270-284`, déjà auto-vérifiée à 0,000000 %).

### 2026-07-31 — T9-3 · le test de mécanisme échoue ; T9-1 annulée (lot A)

Nouveau : `3rdJ_09X_envelope_exposure.py` + `outputs_step9/step9_envelope_exposure.csv`
(336 lignes = 56 cellules × 6 canaux, les 4 canaux locataires + `residential_common` et
`service_MEP` en contexte). Zone→canal **importé** de `3rdJ_08E_aggregate_4split.py` (source
unique), `ExtBoundCond == 0` → Outdoors, `< 0` → Ground, aire nette × Multiplier de zone.

**Contrôle de parsing indépendant** : total d'enveloppe vs `EnvelopeSummary / Opaque Exterior /
Gross Area` d'EnergyPlus → écart **max 0,0004 %** sur 56 cellules. Le mécanisme n'est pas
disqualifié par une erreur de mesure.

**Re-dérivé par moi depuis le CSV, pas repris du log de l'agent** (médianes, Spearman poolé,
rho par cellule, rho par paire bâtiment × ville) : résultats identiques à ceux rapportés.

| canal | exposition | EUI CFA | écart plancher |
|---|---|---|---|
| hôtel | 0,325 | 178,3 | −0,9 % |
| bureau | 0,382 | 71,1 | −28,9 % |
| retail | 0,467 | 75,4 | −5,7 % |

Prédit `bureau < retail < hôtel` ; mesuré `hôtel < bureau < retail` dans **56/56 cellules**.
Spearman poolé **−0,171** (n=168, p=0,026), médiane par cellule **−0,500**, 39 % de rho positifs,
signe non constant sur les 4 paires. → **prédiction falsifiée**.

**Conséquences appliquées sans renégociation** : S9D-1 renversée, **T9-1 annulée**, les trois
`S9-EUI-{c}` restent **FAIL**. `S9-EUI-EXPOSURE` devient un **INFO** (publier la mesure, retirer
l'explication) plutôt qu'une gate scorant une hypothèse morte.

**Hypothèse de rechange formée puis abandonnée, consignée pour qu'elle ne resurgisse pas.**
Le seul canal massivement déficitaire étant le seul dont `band_src` cite Leg-2, j'ai supposé que
la bande bureau héritait du défaut `calculate_eui()` (135/1,706 ≈ 79, intervalle [59-117] où 71,1
tomberait dedans). **Vérifié avant d'agir : faux.** `OFFICE_EUI_BAND = (135.0, 100.0, 200.0)` est
codée en dur (`Leg2_2-split/Step9_docs/3rdJ_09_..._2split.py:50`), sourcée de
`Step8_docs/deepResearch/…As-Modelled Bands.md` (littérature NECB2020/90.1-2019) ; le job 1054800
est le nombre testé **contre** elle. La bande est saine.

**État final des 3 FAIL : défauts non expliqués, remontés à l'utilisateur** (point 5 de la méthode
de test globale). Deux mécanismes testés, deux réfutés. Ce qui reste à instruire est listé en fin
de S9D-1 — et notamment pourquoi l'écart est **spécifique au canal bureau** (−28,9 %) et non
partagé par retail (−5,7 %) et hôtel (−0,9 %).

### 2026-07-31 — Les deux INFO écrits, l'étiquette corrigée, Step 9 ré-exécuté

`S9-EUI-EXPOSURE` (INFO) et `S9-EUI-TOWER-INFO` (INFO) écrits dans
`3rdJ_09_activityDrivenLoads_4split.py`, tous deux **recalculés en code**, rien codé en dur.
`S9-EUI-EXPOSURE` dégrade proprement si le CSV d'exposition manque (INFO explicite, pas de crash).

**Re-dérivé par moi depuis `step9_gates.json` régénéré** — les deux INFO reproduisent exactement
mes propres nombres : exposition 0,325 / 0,382 / 0,467 ; écarts −0,9 / −28,9 / −5,7 % ; Spearman
−0,171 (p = 0,026, n = 168) ; tour 100,4 (base ABUPS brute, plage 90,8-115,3) et 110,3 (base CFA
locataires sommée, plage 99,7-127,3).

**Étiquette de provenance (libellé seul)** : `BENCH["office"]["src"]` passe de
`"NECB/PNNL as-modelled (Leg-2, job 1054800)"` — qui nommait un job de simulation là où la source
est un document de recherche, et qui m'a induit en erreur — à
`"NECB2020/90.1-2019 DOE-PNNL as-modelled band (Step8_docs/deepResearch/...As-Modelled Bands.md ;
repris de Leg-2)"`. **Vérifié après coup : 135,0 / 100,0 / 200,0 et les trois autres entrées de
`BENCH` sont intactes.**

**Step 9 ré-exécuté** (lecture des agrégats §8E sur disque ; aucune simulation EnergyPlus, aucun
job cluster) → **17 PASS / 0 WARN / 3 FAIL / 10 INFO**, 30 gates au total. Les 3 FAIL nommés sont
bien `S9-EUI-office`, `S9-EUI-retail`, `S9-EUI-hotel` — **toujours présents**, ce qui était la
condition explicite. Tables, 5 figures et HTML régénérés.
`grep -rn "electricity-only" Step9_docs/` → **vide**, artefacts générés compris. Le point 4 de la
méthode de test globale est satisfait.

*Corrigé dans la foulée* : `S9-EUI-TOWER-INFO` écrivait « bande [100-200], central 172,7 », ce qui
fusionnait deux objets distincts. Reformulé : la bande est de la littérature et elle est **saine**
(central **135**) ; **172,7 est la valeur que Leg-2 a mesurée contre elle**, et c'est ce nombre
mesuré — pas la bande — qui est gonflé de 1,706×. Step 9 ré-exécuté après correction.

### 2026-07-31 — T9-8 · la sonde de falsifiabilité, et ce qu'elle ne regardait pas

`S9-LONG-UNINJECTED` ne lit pas `--agg-dir` : elle importe `3rdJ_08D_campaign_cells.py` par un
chemin fixe. Perturber les CSV d'agrégats ne peut donc pas l'atteindre. La sonde patche le vrai
fichier Step-8 (`Y2015` réclame l'hôtel comme canal attendu) le temps d'un sous-processus, puis
le restaure dans un `finally` avec assertion post-restauration, plus une assertion qui **échoue si
le texte cible a changé en amont** — sans quoi la perturbation deviendrait un no-op silencieux et
la gate passerait pour testée. **Vérifié de mon côté** : MD5 de `3rdJ_08D_campaign_cells.py`
identique avant/après (`dca23502…`), sur les trois exécutions.

**Ce que ma contre-vérification a trouvé — la sonde ne se surveillait pas elle-même.** Elle
n'évaluait que la gate **nommée** par chaque cas et affichait « 13/13 SEEN FAILING ». Or plusieurs
gates basculent à chaque perturbation, et surtout : la question « reste-t-il une gate PASS que
**rien** ne fait tomber ? » n'était jamais posée. En la posant :

> **`G8r` — l'une des trois gates G8 sur lesquelles repose la thèse — n'avait jamais été vue
> échouer.** Ni `S9-PEAK-retail`. Pas vacuous : simplement jamais testées, ce qui est
> indistinguable tant que personne ne demande.

Corrigé : cas `G8r` (levier retail rendu dégénéré, miroir de `G8o`), cas `S9-PEAK-retail` (retail
qui culmine à 03:00, miroir de `S9-PEAK-office`), et le cas EUI généralisé aux **trois** canaux à
bande. Surtout, un bloc **COVERAGE** ajouté en fin de sonde : il croise *toutes* les sorties
perturbées contre le baseline et **fait échouer la sonde** s'il subsiste une gate PASS que rien
n'a fait tomber. Il a immédiatement rattrapé deux cas de plus (`S9-EUI-office`, `S9-EUI-hotel` —
qui échouent bel et bien sur les vraies données, mais que la fixture synthétique met en PASS sans
qu'aucun cas ne les perturbe).

**Résultat final, ré-exécuté et vérifié par moi** : **17/17 gates nommées SEEN FAILING**,
**COVERAGE 20/20**, `py_compile` OK sur les deux fichiers.

### 2026-07-31 — Clôture du lot

**Scorecard : 17 PASS / 0 WARN / 3 FAIL / 10 INFO** (30 gates).
Les 3 FAIL, avec leur détail tel que régénéré :

| gate | cellules en bande | médiane | plage |
|---|---|---|---|
| `S9-EUI-office` | **0/56** dans [100-200] | 71,1 | 61,8-90,3 |
| `S9-EUI-retail` | 12/56 dans [80-155] | 75,4 | 63,5-97,1 |
| `S9-EUI-hotel` | **28/56** dans [180-300] | 178,3 | 147,9-209,4 |

Ce détail, non disponible au moment d'écrire le plan, **renforce** le constat de S9D-1 : l'hôtel
est à moitié en bande et le retail à un cinquième, tandis que le bureau est à **0/56**. L'écart
n'est pas un biais de référentiel commun à la tour — il est **propre au canal bureau**.

Les 5 conditions de la méthode de test globale : (1-3) satisfaites ; (4) `grep "electricity-only"`
vide, artefacts générés compris ; (5) **satisfait au sens strict** — les 3 FAIL subsistent faute
de mécanisme, ils restent FAIL et sont remontés à l'utilisateur, non absorbés.

**Non tranché, en attente de l'utilisateur** — deux points, aucun ne bloquant ce lot :
1. Le **manuscrit Leg-2**, dont l'EUI office publié est gonflé ~1,7× (voir T9-4). Aucun fichier
   Leg-2 n'a été touché.
2. Les **3 FAIL EUI** eux-mêmes, désormais des défauts instruits mais non expliqués.

---

# Post-closure investigation — 2026-07-31 (written in English, per the standing rule adopted this day)

> This section reopens **only** the second of the two items left "Non tranché" at closure above:
> the 3 EUI FAILs, "défauts instruits mais non expliqués". They are now explained. No gate is
> modified by this section and no Leg-2 file is touched.

## S9D-7 — The 3 FAILs are 3 different phenomena, and only 2 share a cause

The prior investigation searched for **one** mechanism behind all three deficits. That framing is
why it kept failing: T9-3's exposure-rank test looked for a single ordering variable across three
deficits that do not share a cause. The refutation recorded above was sound; the composite was the
error.

Method: compare each channel against the `Default_NECB` run of the **same** geometry, envelope,
climate and plant. Only the schedules differ, so the comparison isolates the GSS injection from
the building specification. Cell `__SuperTall__CLG`, CFA basis, kWh/m2/yr.

| channel | uninjected | injected | band | reading |
|---|---|---|---|---|
| retail | **92.2** | 70.6 | 80-155 | uninjected **is inside the band** -> the FAIL is 100 % an injection effect |
| office | 85.7 | 68.9 | 100-200 | **already below the floor before injection** |
| hotel | 178.1 | 178.7 | 180-300 | injection-neutral (+0.4 %); median 178.3 is **0.9 %** under the floor |

So the office 31 kWh/m2 shortfall splits into ~17 caused by the injection and ~14 that predates it.

Office end-use decomposition (B_central vs Default_NECB): interior_equipment 11.3 vs 27.8
(-59 %), interior_lighting 7.5 vs 13.8 (-45 %), heating 23.3 vs 14.6 (**+60 %**). Heating rising
as internal gains fall is physically coherent — the model is behaving correctly; the *level* is
what is wrong.

**Two candidate explanations were tested and refuted before the one below was accepted:**

- *Unallocated service/MEP energy depresses the tenant channels.* Refuted: the `eui_GFAshare`
  column already performs that reallocation and gives office **64.4** vs CFA 65.5 — reallocation
  *lowers* the number. 14.9 % of tower energy sits outside the tenant channels, but service_MEP
  also holds 20.6 % of gross area.
- *A longitudinal WFH-growth signal drives it.* Refuted: the era axis is flat (Y2005 71.0 ->
  Y2022 70.5). The effect is GSS diaries vs prototype schedules, present at every era.

## S9D-8 — Located defect: the injector collapses People, Lights and Equipment onto one curve

`eSim_bem_utils/commercial_integration.py:646-661` writes the **same** `Schedule:Compact` object
to all three load classes:

```python
for obj_class, sch_field in [
    ("PEOPLE",            "Number_of_People_Schedule_Name"),
    ("LIGHTS",            "Schedule_Name"),
    ("ELECTRICEQUIPMENT", "Schedule_Name"),
]:
    ...
    setattr(obj, sch_field, sch_names[channel])   # one occupancy curve, all three classes
```

Measured on the canonical campaign (`campaign_local_v2/campaign_cf69d508`, INJ_HASH `cf69d508`),
zone `OpenOffice`, weekday:

| | `Default_NECB` | `B_central` |
|---|---|---|
| equipment schedule | `NECB-A-Electric-Equipment` — mean 0.513, **night floor 0.20 (22.2 %)** | `MXU_Office_People_...` — mean 0.187, floor 0.0031 (**0.7 %**) |
| lights schedule | `OfficeLarge BLDG_LIGHT_SCH_2013` (its own object) | `MXU_Office_People_...` — **same object as People** |
| people schedule | `NECB-A-Occupancy` — mean 0.358, floor 0.00 | `MXU_Office_People_...` |

Design levels (`Watts/Area`) are **identical** between the two runs — office equipment 7.5028 W/m2,
LPD 6.566 / 10.441 / 7.965 W/m2 — confirming that only the schedules changed and that the ratio
arithmetic below is valid. This is consistent with the module's own stated discipline that
densities are never scaled (`:275`, `:550`); the schedule *shape* was the unguarded dimension.

**Verification that the parse is correct:** schedule-mean ratio 0.1872/0.3583 = **0.5225**
reproduces the independently measured occupancy energy ratio 358.04/685.32 = **0.5224** from
`agg_diurnal.csv` to four significant figures.

### The fourth channel is an accidental control group

| channel | equip+lights night floor, injected | EUI effect of injection |
|---|---|---|
| office | 22.2 % -> **0.7 %** | -20 % |
| retail | 22.2 % -> **0.0 %** | -23.5 % |
| **hotel** | 22.2 % -> **20.0 % (preserved)** | **+0.4 %** |
| residential | not lights/equip-injected (OD-7D exemption, `:442`) | — |

The channels that lost their standby floor are exactly the channels whose EUI collapsed; the one
that kept a floor kept its EUI. This is a controlled comparison already present in the campaign
data, and the hypothesis survived it.

**Important caveat — the hotel's floor is not protection.** The injector applies no floor
anywhere. Hotel guestroom occupancy simply never drops below 0.20 on its own, so the collapse was
harmless there by accident. The defect is present in all three commercial channels; only its
consequence differs.

## What this does and does not fix

Floor-preserving reconstruction, applying the occupancy modulation only to the above-floor portion
of the prototype equipment schedule:

```
corrected mean     = 0.20 + (0.5125 - 0.20) x 0.5225 = 0.363   (vs 0.187 as injected)
ratio to prototype = 0.363 / 0.5125                  = 0.709   (vs 0.365 as injected)
office equipment   = 27.8 x 0.709                    = 19.7 kWh/m2  (vs 11.3)  -> +8.4
```

Lighting is subject to the same defect but is **not quantified here**: the prototype object
`OfficeLarge BLDG_LIGHT_SCH_2013` is a `Schedule:Year`, not a `Schedule:Compact`, and was not
resolved by this probe. Its gross recovery is bounded above by 13.8 - 7.5 = **6.3 kWh/m2**.

So gross electric recovery for office is at most ~14.7 kWh/m2, and the **net** EUI gain is smaller
still, because restored internal gains displace part of the +8.7 kWh/m2 of heating the injection
currently adds. Office would move from 68.9 to roughly 75-80.

**The floor is 100. Fixing this defect does not rescue `S9-EUI-office`.** It corrects a real
modelling error and closes ~17 of the 31 kWh/m2 gap; the remaining ~14 is the pre-injection
deficit (85.7 vs 100), which is a Step-8 building-specification question, not a Step-9 one.

For **retail** the outcome is genuinely uncertain and worth the re-sim: uninjected 92.2 is inside
the band, the lost floor is the full 22.2 %, and a corrected run could plausibly return the channel
to PASS. For **hotel** this defect is not the cause and the 0.9 % band-edge miss stands.

## Recommendations — not yet executed, pending user decision

- **T9-9 — fix the injector.** Give LIGHTS and ELECTRICEQUIPMENT their own transform of the
  occupancy series rather than the series itself, preserving each prototype schedule's standby
  floor: `f_load(t) = floor + (1 - floor) * normalised_occupancy(t)`, with `floor` read from the
  schedule being replaced rather than hard-coded. This touches `commercial_integration.py` only.
- **T9-10 — do not widen any band.** The remedy for these FAILs is the injector fix plus an
  honest statement of the residual, never a wider band (standing rule; see the closure of T9-1).
- **Re-sim scope.** A corrected run changes every injected cell, so this is a full campaign, which
  is currently blocked. Recommend fixing the code and holding the re-sim until the campaign
  unblocks — the FAILs are now *explained*, which was the actual gap.
- **`S9-EUI-{c}` re-specification, still recommended.** Compare each channel against its own
  `Default_NECB` run on identical geometry (a like-for-like object) and keep the literature band
  as INFO, as `S9-EUI-TOWER-INFO` already is. Note this would *not* have hidden anything here:
  office fails the prototype band uninjected too, and that failure is the informative one.

### Reproduction

Both probes are read-only and live in the session scratchpad (`sched_probe.py`, `sched_probe2.py`).
They parse `campaign_local_v2/campaign_cf69d508/{Default_NECB,B_central}__SuperTall__CLG/injected.idf`
directly; no campaign artefact was modified by this investigation.

---

## T9-9 EXECUTED — injector fixed and verified, re-sim NOT run (2026-07-31)

Code staged and tested; **no campaign artefact regenerated, no gate touched, no band changed.**

### What changed

`eSim_bem_utils/commercial_integration.py` (762 -> 1025 lines). New parameter
`inject_mixed_use(..., preserve_load_standby_floor: bool = True)`.

- PEOPLE wiring **unchanged** — still gets the raw occupancy schedule.
- LIGHTS / ELECTRICEQUIPMENT now get a derived `Schedule:Compact`
  `f_load(t) = floor + (1 - floor) * occ(t)`, one object per `(channel, floor)`.
- `floor` is **read from the prototype schedule the object already carries**
  (`_schedule_standby_floor`), never hard-coded. Handles `Schedule:Compact`, `:Constant`,
  `:Year -> :Week:Daily/:Week:Compact -> :Day:Hourly/:Day:Interval/:Day:List`.
- **Design days are excluded**, and this is load-bearing, not cosmetic: `OfficeLarge
  BLDG_LIGHT_SCH_2013 Winter Design Day` is a flat **0**, so a naive global minimum returns
  floor = 0.0 and `floor + (1-floor)*occ` silently collapses back to `occ` — the fix would have
  been a no-op that still looked applied.
- Objects whose floor cannot be resolved (`Schedule:File`, missing, already `MXU_*`) are **left
  on their prototype schedule** and recorded in `result["floor_unresolved"]` + the provenance
  file. They are never silently given the defective occupancy schedule.
- `result["floor_applied"]` and new `.provenance.txt` lines record every re-floored object with
  its prototype schedule, resolved floor and provenance string.

### Verification

**1. Floor resolver vs hand-read prototype values — 4/4 PASS**

| schedule | resolved | class path |
|---|---|---|
| `NECB-A-Electric-Equipment` | **0.200** | `schedule:compact` (design days excluded) |
| `OfficeLarge BLDG_LIGHT_SCH_2013` | **0.045280057** | `:year -> :week:daily` (design days excluded) |
| `RetailStandalone BLDG_LIGHT_SCH_2013` | **0.05** | `:year -> :week:daily` |
| `RetailStandalone BLDG_LIGHT_BACK_SCH_2013` | **0.05** | `:year -> :week:daily` |

Design-day exclusion confirmed to bite: naive global min = **0.0**, excluded min = **0.0453**.
Unresolvable cases (`MXU_*`, missing) correctly return `None` rather than defaulting.

**2. Regression — the legacy path is intact.** Re-ran the real
`B_central__SuperTall__CLG` injection from the real source IDF
(`SuperTallBuilding_90.1-2019_6A_Buffalo_NECB17_Z7A_v242.idf`) with the real Step-7 CSVs
(`INPUTS_HASH` 85773432) at `preserve_load_standby_floor=False`, and diffed against the closed
campaign artefact (md5 `e20764fd46bb9d74257f5171e1cc9474`):

- 11,466 vs 11,488 objects; **22 objects differ, ALL of them `Output:Meter` / `Output:Variable`**
  reporting requests that the campaign driver adds *after* `inject_mixed_use` returns.
- **0 differences in PEOPLE, LIGHTS, ELECTRICEQUIPMENT or any `MXU_*` schedule.**

So the closed campaign remains exactly reproducible with the flag off.

**3. Fixed path, same cell — 25 objects re-floored, 0 unresolved**

| channel | class | prototype schedule | floor | derived |
|---|---|---|---|---|
| office | ELECTRICEQUIPMENT | `NECB-A-Electric-Equipment` | 0.200 | `MXU_Office_Load_f200_*` |
| office | LIGHTS | `OfficeLarge BLDG_LIGHT_SCH_2013` | 0.0453 | `MXU_Office_Load_f045_*` |
| retail | ELECTRICEQUIPMENT | `NECB-A-Electric-Equipment` | 0.200 | `MXU_Retail_Load_f200_*` |
| retail | LIGHTS | `RetailStandalone BLDG_LIGHT_{,BACK_,ENTRY_}SCH_2013` | 0.05 | `MXU_Retail_Load_f050_*` |
| hotel | ELECTRICEQUIPMENT | `NECB-A-Electric-Equipment` | 0.200 | `MXU_Hotel_Load_f200_*` |
| hotel | LIGHTS | `HotelLarge BLDG_LIGHT_GUESTROOM_SCH_2013` | 0.05 | `MXU_Hotel_Load_f050_*` |

Hotel's 24 monthly blocks verified elementwise against `floor + (1-floor)*occ` (PASS), zero
floor violations on either hotel schedule.

**4. Effect on schedule means** (weekday, time-weighted)

| load | prototype | as-injected (defective) | fixed |
|---|---|---|---|
| office equipment | 0.5125 | 0.1872 | **0.3497** |
| office lighting | 0.3976 | 0.1872 | **0.2240** |
| retail equipment | 0.5125 | 0.1982 | **0.3585** |
| retail lighting | ~0.05 floor | 0.1982 | **0.2382** |
| hotel equipment | 0.5125 | 0.3950 | **0.5160** |

### Projected EUI effect — and the honest limit

Scaling the measured office end-use energies by the schedule-mean ratio:

| office end use | as-injected | projected fixed | delta |
|---|---|---|---|
| interior_equipment | 11.3 | 21.1 | **+9.8** |
| interior_lighting | 7.5 | 9.0 | **+1.5** |
| **gross electric** | | | **+11.3 kWh/m2/yr** |

This supersedes the +8.4 estimate in S9D-8, which used a different above-floor derivation than
the formula actually implemented.

**Net EUI gain will be smaller than +11.3**, because restored internal gains displace part of the
+8.7 kWh/m2 of heating the injection currently adds (and add some cooling). Office moves from
**68.9 toward ~76-80 against a band floor of 100 — still FAIL.** The fix corrects a real defect;
it does not erase the office gate, and the ~14 kWh/m2 pre-injection deficit is untouched.

Likely to change more than expected: **hotel**. Its equipment mean is restored almost exactly to
prototype (0.516 vs 0.5125), and hotel sits only 0.9 % under its floor at 178.3 — so hotel may
well cross into band. That was NOT the goal of this fix and it is not evidence for it; it is a
prediction to check against the re-sim, recorded here **before** the run so it can fail.

**Retail** remains the genuinely uncertain one: uninjected 92.2 is inside the band, equipment mean
recovers 0.198 -> 0.359, so a return to PASS is plausible but unproven.

### Not done, deliberately

- **No re-simulation.** A corrected run invalidates all 56 cells; the campaign is blocked.
- **No lighting-diversity model.** Re-imposing the floor still leaves lighting strongly
  occupancy-coupled, whereas real open-plan lighting is zone-switched (the prototype peaks at
  0.815 regardless of occupancy). Encoding that is a research decision, not a bug fix, and is
  left open for the user.
- **No gate or band edited.** `S9-EUI-{c}` stay PASS/FAIL and stay FAIL.
- **No Leg-2 file touched.**

---

## T9-10 EXECUTED — lighting diversity model, calibrated and simulated (2026-07-31)

T9-9 fixed a defect. It did **not** fix the modelling error the defect was hiding: after T9-9,
lighting is still `floor + (1 - floor) * occ`, i.e. strictly proportional to head-count. Real
lighting is not. This section closes the item S9D-8 explicitly left open for the user.

### The model

LIGHTS only. ELECTRICEQUIPMENT keeps the T9-9 floor form, deliberately — plug loads **are**
per-person, so that form is already correct there.

```
f_light(t) = floor + (peak - floor) * g(t)

  office   g = 1 - (1 - occ(t))^n     zone coincidence: fraction of switched lighting zones
                                      of n workstations holding >= 1 occupant
  retail   g = 1 - staff_shoulder_flag(t)     open/closed gate — NOT head-count
  hotel    g = occ(t)                 (n = 1: one room, one occupant, one switch)
```

`peak` is now read from the replaced prototype schedule the same way `floor` already was
(design days excluded). This matters on its own: the T9-9 form implicitly peaks at 1.0, so a
fully-occupied office could draw **more** lighting power than the NECB prototype ever asks for
(`OfficeLarge BLDG_LIGHT_SCH_2013` peaks at 0.815).

Three channels, three different physics. Treating them uniformly is what produced S9D-8 in the
first place.

**Retail is the clearest correction and needed no new data.** A shop with 3 customers is lit
exactly like a shop with 30; retail lighting tracks opening hours. That signal was already in
the pipeline and was being thrown away: `staff_shoulder_flag`
(`3rdJ_07_aug_to_bem_4split.py:527`, flag=1 ⟺ NECB baseline ≤ 0.10 ⟺ closed/staff-only) is
loaded by `load_retail_series()` into `"<dt>_staff_shoulder"` at
`commercial_integration.py:517` and, before this change, **read by nothing** — verified by
repo-wide grep. Consequence to note: the flag derives from the NECB baseline proxy, so the open
window is fixed across scenarios and eras. Retail lighting therefore becomes scenario-invariant
— the intended physical claim (WFH does not change store hours), but it does mean
`sens_retail_{cons,opt}` no longer moves retail *lighting*, only people and plug loads.

### Calibration of the office exponent — fitted to NECB, not to a gate

`n` was **not** tuned to make an EUI gate pass. It was fitted against the NECB prototype
schedule itself, using a pre-WFH year, so the WFH bundles play no part in choosing it:

> Run the 2022 **observed** office occupancy (`office_presence_multiplier_2022.csv`,
> `Office_Knowledge` / `BAND=observed`) through the model and ask which `n` reproduces
> `OfficeLarge BLDG_LIGHT_SCH_2013`'s own weekday mean of **0.3976**.

| n | weekday mean | error vs prototype |
|---|---|---|
| 1 | 0.2400 | −39.6 % |
| 2 | 0.3401 | −14.5 % |
| **3** | **0.3976** | **−0.0 %** |
| 4 | 0.4350 | +9.4 % |
| 5 | 0.4622 | +16.2 % |
| 6 | 0.4837 | +21.7 % |
| 8 | 0.5175 | +30.2 % |

A matching scalar mean is one number and could be coincidence, so the hourly shape was checked
as a separate test with the prediction written first (*"if n=3 is real, r > 0.9 and the largest
residuals sit at the shoulders"*):

- Pearson r vs prototype **0.9743** (n=1: 0.9681)
- RMSE **0.0875** vs n=1's 0.2263 — a **61 % reduction**
- four largest residuals at hours **6, 7, 8, 16** — exactly the shoulders, where a diary-derived
  arrival ramp is *expected* to differ from NECB's step from 0.27 to 0.815

n = 3 workstations per switched lighting zone is also physically plausible.

### The cost, stated plainly

Raising n shrinks the WFH lever on lighting. Span from the 2030 conservative band to
fullyhybrid:

| n | 1 | 2 | 3 | 4 | 6 | 8 |
|---|---|---|---|---|---|---|
| span | −14.7 % | −11.2 % | **−7.8 %** | −5.0 % | −1.5 % | **+0.2 %** |

At n=8 — the textbook open-plan figure — the span **inverts**: the lever is gone, the residual
is noise. n=8 also overshoots the prototype by 30 %, so it is not usable here regardless. n=3
keeps a real, signed WFH signal *and* matches the prototype.

That the lighting WFH response shrinks is the model's substantive claim, not a defect: lighting
is switched per zone, so plug loads — not lights — should carry most of the WFH effect.
Post-COVID metered studies report exactly that asymmetry. It weakens a "WFH cuts office
lighting" reading and strengthens the model's credibility; that is a finding, not a loss.

### Code

`eSim_bem_utils/commercial_integration.py`. New parameter
`inject_mixed_use(..., lighting_model: dict = None)` — **opt-in, off by default**.

- `_schedule_standby_floor` was generalised to `_schedule_extremum(idf, name, agg, ...)`, with
  `_schedule_standby_floor` (min) and new `_schedule_peak` (max) as thin wrappers. Design-day
  exclusion applies to both.
- new `apply_lighting_diversity()`; new constants `LIGHTING_MODEL_ZONE` (office_n=1, the
  no-change default) and `LIGHTING_MODEL_CALIBRATED` (office_n=3).
- LIGHTS whose **peak** cannot be resolved are recorded in `floor_unresolved` and left on their
  prototype schedule — the same discipline as the floor, never a silent fallback to linear.
- `result["light_diversity_applied"]` + `lighting_model` / `n_light_diversity_applied` /
  `light_diversity …` lines in the provenance file.

`3rdJ_08D_campaign_driver.py`: new `--lighting-model {none|calibrated|nK}` and
`--no-standby-floor`; the resolved arm is recorded in `manifest["arm"]`.

### Verification — 7 predictions written before running, 7 PASS

| | prediction | result |
|---|---|---|
| P1 | the 4 floors T9-9 measured come back unchanged after the refactor | PASS |
| P2 | office lights peak = 0.815041, not 1.0 (design-day exclusion holds on max) | PASS — naive global max over all day schedules is **120.0** |
| P3 | `lighting_model=None` reproduces the T9-9 artefact byte-identically | PASS — md5 `ba5595827b9b8544a89f3c09470e0e3b` both sides |
| P4 | retail weekday lighting takes exactly two levels, flat within each | PASS — {0.05, peak} |
| P5 | n=1 mean < T9-9 mean (peak 0.815 replaces implicit 1.0) | PASS — 0.1894 < 0.2240 |
| P6 | n=8 mean > n=1 mean | PASS — 0.4590 > 0.1894 |
| P7 | 0 unresolved objects in every arm | PASS |

P3 is the load-bearing one: it is the whole safety claim of the resolver refactor.

Also confirmed: office **equipment** weekday mean is `0.349742` in all three arms to 6 dp — the
lighting model provably does not touch plug loads. Retail resolves **three** distinct lighting
prototypes with different peaks (main 0.900, back 0.704, entry 0.738), each getting its own
derived schedule.

### Campaign — moved to Speed, two arms

Speed resources released 2026-07-31, so the campaign that T9-9 had to leave blocked is running.

| arm | tasks | `--lighting-model` | content |
|---|---|---|---|
| A | 0–55 | `none` | T9-9 standby-floor fix only |
| B | 56–111 | `calibrated` | T9-9 + T9-10 (office_n=3, hotel_n=1, retail open/closed) |

The pre-fix behaviour is **not** re-run — it is already the closed `campaign_cf69d508` set, so
the three-way comparison is available without spending 56 more runs.

Infrastructure: `/speed-scratch/o_iseri/step8_4split/campaign/`, EnergyPlus 24.2.0 via the
`ep_wrappers/energyplus` Singularity shim the §P probes already proved, python
`envs/step4/bin/python`. 525 MB of inputs uploaded as one archive; **untarred through `sbatch`,
never on the login node.**

### Predictions for the re-simulation — recorded BEFORE the runs finish, so they can fail

Arm A carries forward the T9-9 predictions unchanged: office moves from 68.9 toward ~76–80
against a band floor of 100 and **still FAILs**; **hotel may cross into band** from 178.3;
retail is genuinely uncertain (uninjected 92.2 is inside the band).

Arm B, new and specific:

1. **Office lighting rises further in B than in A** (weekday schedule mean 0.2240 → ~0.34), but
   the office EUI gate still **FAILs** — the ~14 kWh/m² pre-injection deficit is untouched by
   anything in T9-9 or T9-10.
2. **Retail EUI rises in B relative to A**, because retail lighting goes to a flat open-hours
   peak instead of tracking shopper counts.
3. **Hotel is nearly unchanged between A and B** — hotel keeps n=1; only the peak rescaling
   (1.0 → 0.8) moves it, and it should move it *down* slightly.
4. **The office WFH lighting signal (B_cons → B_opt) is smaller in B than in A**, by roughly the
   14.7 % → 7.8 % span ratio. If it is *not* smaller, the model did not land.

Prediction 4 is the one worth watching: it is the direct, measurable consequence of the whole
change, and it is the one that would most cleanly falsify it.

### Not done

- **No gate or band edited.** `S9-EUI-{c}` stay PASS/FAIL and stay FAIL until a run says otherwise.
- **No Leg-2 file touched.**
- The Step-7 retail NECB baseline is still the **provisional proxy** flagged at
  `3rdJ_07_aug_to_bem_4split.py:20-45` (no real NECB Table A-8.4.3.2.(1)-A retail occupancy
  table exists in the repo). T9-10 now makes retail *lighting* depend on that proxy's open/closed
  threshold, so this open item is more load-bearing than it was — recorded, not resolved.

### Launch record + a near-miss that nearly invalidated the whole campaign

Validation job **1170491** (mine, buggy: it omitted `--engine local` on the dry-runs) then
**1170492** (clean): EnergyPlus **24.2.0-94a887817b** through the wrapper, **0/56 cells with
unresolved inputs**, cell 3 smoked 2 days in both arms, exit 0 both times. Campaign array
**1170493**, `--array=0-111%20`.

Provenance confirms the arms are really different:

| | arm A (`none`) | arm B (`calibrated`) |
|---|---|---|
| `preserve_load_standby_floor` | True | True |
| `n_floor_applied` | 25 | 25 |
| `lighting_model` | `None` | `{office_n: 3, hotel_n: 1, retail_mode: open_closed}` |
| `n_light_diversity_applied` | 0 | **13** |

Arm B emits **no** `MXU_*_Load_f045/f050` (lighting) schedules at all — only `Load_f200`
(equipment). That is the cleanest available proof that the model routes LIGHTS and leaves plug
loads on the T9-9 form.

**🔴 The near-miss.** Job 1170491 died with
`ImportError: cannot import name LIGHTING_MODEL_ZONE from
/speed-scratch/o_iseri/step8_4split/upload/eSim_bem_utils/commercial_integration.py`
— i.e. the freshly uploaded injector under `campaign/repo/` was **not** the one being imported.
Cause: `3rdJ_08P_probe_driver.py:94` runs `sys.path.insert(0, UPLOAD)` at **module-import**
time as a cluster fallback, and `3rdJ_08D_campaign_driver.py` loads that module at import time
(`_load_module`). So the probe harness'''s own upload tree shadowed **both** `PYTHONPATH` and
`--repo-root`, and `--repo-root` silently did not mean what it says.

What makes this worth recording rather than just fixing: **it failed loudly only because the new
code added a new NAME.** T9-9 and T9-10 both happened to extend the module'''s API. Had either been
a behaviour-only change — a different floor formula, a corrected peak — all 56 cells would have
run to completion against the **old** injector, produced clean SQL, passed every row-count and
attribution gate, and been indistinguishable from a successful re-simulation. The campaign would
have silently re-measured the defect it was launched to fix.

Fix (in `3rdJ_08D_campaign_driver.py` only — the probe driver is a closed artefact and was NOT
modified): re-assert `repo_root` at the front of `sys.path`, drop any already-bound
`eSim_bem_utils` from `sys.modules`, print `[setup] eSim_bem_utils resolved from: <path>`,
and **hard-fail** if that path falls outside `--repo-root`. Verified in 1170492:
`resolved from: /speed-scratch/.../campaign/repo/eSim_bem_utils/commercial_integration.py`.

Generalisable rule: **a cluster job must state which copy of its own code it loaded.** Version
tags in filenames and `PYTHONPATH` are not evidence; `module.__file__` is.

---

## ARM A RESULTS — T9-9 standby floor only, 56/56 cells (2026-07-31)

Aggregated on Speed with `3rdJ_08E_aggregate_4split.py` (job 1170685) into
`campaign/agg_A_t99/`. Compared cell-by-cell against the closed pre-fix set
`INJ_HASH=cf69d508`. Arm A is `INJ_HASH=898d033a`.

Integrity first, because a delta between two trees that are not otherwise identical means
nothing: the 56 `cell_tag`s are the **same set**, `max |area_A − area_pre| = 0 m²` on every
channel (the injector did not touch geometry), and `attribution_closed=True` on all 112
aggregations with residual ≤ 1e-6.

### Channel EUI, CFA basis, median over 56 cells

| channel | pre-fix | arm A | Δ | Δ % | band | in-band pre | in-band A | gate |
|---|---|---|---|---|---|---|---|---|
| office | 71.08 | **80.03** | +8.92 | +12.6 % | [100, 200] | 0/56 | **0/56** | FAIL |
| retail | 75.43 | **84.05** | +9.55 | +11.7 % | [80, 155] | 12/56 | **38/56** | FAIL |
| hotel | 178.29 | **180.94** | +3.92 | +2.3 % | [180, 300] | 28/56 | **28/56** | FAIL |
| residential | 120.70 | 120.89 | +0.39 | +0.3 % | — | — | — | INFO |
| residential_common | 53.82 | 53.72 | −0.09 | −0.2 % | — | — | — | INFO |
| service_MEP | 59.04 | 58.44 | −0.58 | −1.0 % | — | — | — | INFO |

**No threshold was moved.** All three banded gates stay FAIL.

### Verdict on the predictions recorded before the runs

1. *"office moves from 68.9 toward ~76–80 and still FAILs"* — **HELD.** The `68.9` in this
   document is the §P probe figure (line 793), a single cell; the campaign's own basis gives a
   pre-fix median of **71.08**, mean 70.63. Re-derived rather than reused: 71.08 → **80.03**,
   inside the predicted window, and **0/56 cells in band, unchanged**. The ~14 kWh/m² deficit is
   pre-injection and nothing in T9-9 touches it, exactly as stated.
2. *"hotel may cross into band from 178.3"* — **the prediction was not answerable as posed, and
   that is the finding.** The median does cross (178.29 → 180.94 against a floor of 180), but
   that crossing is meaningless: the hotel distribution is strictly **bimodal by geometry** and
   the band floor sits in the empty gap between the two clusters.

   | geometry | pre median | arm A median | in-band |
   |---|---|---|---|
   | SuperTall CLG | 149.4 | 153.2 | 0/14 → 0/14 |
   | SuperTall MTL | 161.5 | 165.3 | 0/14 → 0/14 |
   | Tall CLG | 195.3 | 199.2 | 14/14 → 14/14 |
   | Tall MTL | 208.0 | 211.9 | 14/14 → 14/14 |

   **Not one cell of 56 lies in [170, 182)** in either tree. The hotel FAIL is a *SuperTall*
   effect — a geometry/exposure question — and no occupancy or load-schedule fix can move it,
   because the failing cells are 15–30 kWh/m² below the floor, not 2. Quoting the hotel median
   against the band floor is a reporting error waiting to happen and should be dropped in favour
   of the per-geometry split.
3. *"retail genuinely uncertain"* — **the largest movement of the three.** 12/56 → **38/56**
   in band, median 75.43 → 84.05, crossing the floor of 80. Also cleanly split by climate:
   MTL goes 5/14 → **14/14** in both towers, CLG only 1/14 → 5/14. Retail now passes in Montréal
   and fails in the milder city; the residual gap is again geometry/climate, not schedule.

### Where the energy actually landed (sum over 56 cells, GJ/yr)

| channel | end use | pre-fix | arm A | Δ |
|---|---|---|---|---|
| office | interior_equipment | 96 592 | 170 367 | **+73 775 (+76.4 %)** |
| office | interior_lighting | 61 411 | 74 906 | +13 495 (+22.0 %) |
| hotel | interior_equipment | 90 366 | 105 635 | +15 269 (+16.9 %) |
| retail | interior_equipment | 12 805 | 20 248 | +7 443 (+58.1 %) |
| hotel | interior_lighting | 50 915 | 53 112 | +2 198 (+4.3 %) |
| retail | interior_lighting | 10 293 | 12 169 | +1 876 (+18.2 %) |
| office | **heating (gas)** | 166 592 | 133 055 | **−33 536 (−20.1 %)** |
| retail | heating (gas) | 14 744 | 11 537 | −3 207 (−21.8 %) |
| hotel | heating (gas) | 112 021 | 106 903 | −5 119 (−4.6 %) |
| office | cooling | 32 877 | 35 796 | +2 920 (+8.9 %) |

Two things worth stating rather than leaving implicit:

- **Residential, residential_common and service_MEP lighting and equipment are unchanged to
  0.00 %** — a specificity check that passes. T9-9 lives in `inject_mixed_use`, which touches
  only the three commercial channels; those three channels' EUIs still move by a few tenths of
  a percent, purely through their share of the shared plant.
- **Heating falls while cooling rises**, by roughly the right magnitudes. A restored 22 % plug
  standby floor is an all-night internal gain; gas heating dropping 20 % in office and 22 % in
  retail while electric cooling rises 9 % is the physically expected signature and not something
  the fix was tuned to produce. It is also why office EUI rises only +12.6 % while office
  equipment rises +76 % — the fuel switch eats most of it.

### Office WFH lever in arm A — the reference arm B must beat

Recorded now, **before** arm B finishes, so prediction 4 can fail. `sens_office_cons →
sens_office_opt`, arm A:

| basis | SuperTall CLG | SuperTall MTL | Tall CLG | Tall MTL |
|---|---|---|---|---|
| office **lighting** GJ | **−16.14 %** | **−16.13 %** | **−16.42 %** | **−16.41 %** |
| office equipment GJ | −9.47 % | −9.47 % | −9.47 % | −9.47 % |
| office total EUI | −3.30 % | −2.61 % | −3.89 % | −3.08 % |

The equipment lever is identical to 2 dp across all four geometries and both climates — correct,
since plug loads are schedule-driven and climate-independent; that it comes out invariant is a
free consistency check on the aggregator's channel attribution.

**Prediction 4, now quantified:** the calibration table put the n=1 → n=3 span ratio at
−14.7 % → −7.8 %, i.e. **0.53**. Arm A's measured lighting lever is −16.2 % (mean of the four),
so arm B should land near **−8.6 %**, and in any case strictly between −16.2 % and 0. If arm B's
office lighting lever is **not smaller in magnitude than −16.2 %**, the zone-coincidence model
did not land and T9-10 must be withdrawn.

### Not done

- No band, threshold or gate edited. Three FAILs stand.
- Arm B still running (88/112 tasks complete at the time of writing); no A-vs-B number exists yet.
- The hotel SuperTall deficit and the retail CLG deficit are now *located* but not *explained* —
  both look like envelope/exposure effects, which is `3rdJ_09X_envelope_exposure.py`'s subject,
  not T9-9's.

---

## OFFICE END-USE DECOMPOSITION — is the office FAIL a category error or a missing load? (2026-07-31)

The office gate fails on all 56 cells. Two explanations demanded opposite responses, so they were
separated before any gate was touched:

* **category error** — the band comes from a *freestanding* Large Office prototype, the channel is
  a slab buried mid-tower;
* **missing loads** — the office channel is genuinely short of end-uses the prototype counts.

The separator needs no external benchmark and no new run. The campaign already contains a
`Default_NECB` cell: same IDF, same geometry, same plant, **NECB's own default schedules**, no
occupancy bundle. Whatever `Default_NECB` cannot reach is not the occupancy model's doing.

### Office end-use intensity, arm A, kWh/m²/yr on office CFA (median over the 4 geometries)

| end use | Default_NECB | Y2005 | Y2022 | B_cons | B_central | B_opt | B_central ÷ NECB |
|---|---|---|---|---|---|---|---|
| interior_equipment | 27.78 | 23.93 | 23.61 | 23.35 | 22.20 | 21.14 | 0.799 |
| heating (gas) | 14.23 | 16.14 | 16.75 | 17.05 | 18.12 | 19.12 | 1.274 |
| **dhw** | **12.19** | **12.19** | **12.19** | **12.19** | **12.19** | **12.19** | **1.000** |
| interior_lighting | 13.80 | 11.02 | 10.72 | 10.42 | 9.53 | 8.73 | 0.691 |
| fans | 6.01 | 5.63 | 5.59 | 5.46 | 5.36 | 5.27 | 0.892 |
| cooling | 5.55 | 5.17 | 5.09 | 5.04 | 4.96 | 4.86 | 0.893 |
| pumps | 3.56 | 3.11 | 3.07 | 3.02 | 2.98 | 2.95 | 0.837 |
| heat_recovery | 1.52 | 1.57 | 1.57 | 1.59 | 1.59 | 1.59 | 1.045 |
| heat_rejection | 0.65 | 0.67 | 0.67 | 0.67 | 0.66 | 0.65 | 1.010 |
| **TOTAL** | **85.29** | 79.42 | 79.26 | 78.80 | **77.60** | 76.50 | **0.910** |

### Answer: it is BOTH, and the split is now measured

**`Default_NECB` office = 85.29 kWh/m², against a band floor of 100.** Running NECB's own
schedules in this tower still lands **15 % below** the band that was derived from NECB's
standalone Large Office prototype. That component of the FAIL cannot be attributed to the
occupancy chain — it is the category error, and it is now demonstrated rather than argued.

The occupancy bundles account for the rest: B_central is **0.910 ×** `Default_NECB`, i.e. about
**9 %**. Of the 22 kWh/m² total shortfall to the floor, roughly **15 belong to the benchmark and
7 to the occupancy model.**

**No missing end-use category was found.** All nine end uses are present, attribution closes to
≤1e-6 on every cell, and the deficits are spread proportionately (lighting 0.69, equipment 0.80,
fans/cooling/pumps 0.84–0.89) rather than concentrated in one absent line item. The "missing
loads" hypothesis is refused for office — with one exception, below, which is worse.

Heating moves the *other* way (1.274 ×): fewer people, less internal gain, more gas. That is the
same signature T9-9 produced and it is a consistency check passing, not a defect.

### The finding that outranks the office question: DHW does not respond to occupancy at all

`dhw` is **12.19 kWh/m² in every single office column, to 2 dp** — identical for the NECB
default, for 2005, for 2022 and for all three 2030 bundles. Checked directly across all 14
scenarios of `Tall__MTL`:

| channel | DHW spread over the 14 scenarios (GJ/yr) | relative spread |
|---|---|---|
| hotel | 4063.69 – 4064.01 | 0.008 % |
| office | 1084.57 – 1084.72 | 0.014 % |
| residential | 2590.56 – 2590.92 | 0.014 % |

That residual spread is the allocation denominator jittering, not a response. **Domestic hot
water is frozen.** The injector modulates `PEOPLE`, `LIGHTS` and `ELECTRICEQUIPMENT`; it never
touches `WATERUSE:EQUIPMENT`, so the most canonically occupancy-driven load in the building is
the one load that ignores occupancy.

Its weight is not marginal:

| basis | DHW share |
|---|---|
| residential channel | **47.6 %** |
| hotel channel | **36.7 %** |
| office channel | 15.2 % |
| retail channel | 9.1 % |
| **whole tower, site energy** | **26.8 %** |

**Roughly 27 % of the tower's energy is, by construction, insensitive to every scenario, era and
sensitivity lever in this study** — and it is *most* insensitive exactly in the two channels
(residential, hotel) whose occupancy this leg was built to model. Any statement of the form "WFH
changes tower energy by X %" is currently computed on a base a quarter of which cannot move.
This is a scope limitation that must be stated in the manuscript whether or not it is fixed; it
also mechanically damps every lever reported in Steps 8–9.

Recorded, not fixed. Fixing it means driving `WATERUSE:EQUIPMENT` flow-rate fraction schedules
from the same occupancy series, which is a Step-7/8 specification change, not a bug fix.

### Prediction for arm B, written before arm B lands

T9-10 calibrated `office_n=3` so the injected office lighting schedule reproduces the NECB
prototype's weekday mean. If that calibration is real, then in arm B:

* **office `interior_lighting` for B_central rises from 9.53 to approximately 13–14 kWh/m²**,
  i.e. to roughly the `Default_NECB` value of **13.80** — because that is precisely what matching
  the prototype schedule mean means, expressed in energy;
* office TOTAL rises from 77.60 to roughly **80–82**, so the office gate **still FAILs** — the
  15 kWh/m² benchmark component is untouched by anything in T9-10;
* `interior_equipment` stays at **22.20** unchanged, since the lighting model provably does not
  touch plug loads.

If office lighting in arm B lands materially above ~15 kWh/m², the calibration overshot and n
must come down.

---

## T9-11 — occupancy-driven service hot water (2026-07-31) — CODE COMPLETE, 8/8 PREDICTIONS PASS

Closes the finding the arm-A end-use decomposition surfaced: DHW was **26.8 % of whole-tower
site energy and completely occupancy-invariant** (residential 47.6 % of channel energy, hotel
36.7 %, office 15.2 %, retail 9.1 %; spread across the 14 scenarios of `Tall__MTL` = 0.008–0.014 %,
i.e. allocation-denominator jitter, not a response). The injector modulated PEOPLE / LIGHTS /
ELECTRICEQUIPMENT and never touched `WATERUSE:EQUIPMENT`.

### Model

```
f_dhw(t) = floor + (peak - floor) * occ(t)          LINEAR, n_zone = 1
```

Water draw is a per-capita event rate — a restroom or a shower serves one person at a time — so
T9-10's zone-coincidence exponent is a **lighting** concept and is deliberately kept out of DHW.
`floor` and `peak` come from the prototype flow-fraction schedule the object already carries,
through the same `_schedule_extremum` resolver, design days excluded. Keeping the prototype's own
peak matters more here than anywhere else: `Peak_Flow_Rate` was **sized** against that maximum, so
a model that let the fraction reach 1.0 would silently inflate the plant's design draw.

Resolved prototypes (SuperTall): OfficeLarge BLDG_SWH 0.00–0.57 · RetailStandalone BLDG_SWH
0.00–0.62 · HotelLarge BLDG_SWH 0.15–0.60 · HotelLarge GuestRoom_SWH 0.15–0.80 ·
ApartmentHighRise APT_DHW 0.01–1.00.

### Channel resolution

`WaterUse:Equipment` carries a **blank `Zone Name`**, so these objects cannot ride the
zone→channel map. `_wateruse_channel_map()` applies two rules, both read off the IDF:
(1) the Space name embedded in `"<Space> Service Water Use <x>gpm <T>F"`, classified by Tag-2;
(2) for plant-level units with no Space prefix (`Booster`, `Laundry`), the prototype token in the
flow-fraction schedule name. This is the **same rule** `3rdJ_08P_probe_driver.py:715-732` uses to
attribute DHW energy when *reporting* — duplicated rather than imported (the reporting side must
stay able to read a tree from any injector version), so P7 asserts the two agree object-by-object.
If they ever diverged, injection and attribution would describe different buildings.

Residential DHW is handled **inside `inject_residential`**, because that is the only place the
per-Space drawn household series exist: each apartment's hot water now follows *its own*
household, not a building-average profile.

### Scope call: hotel laundry is EXCLUDED, and it is not a small exclusion

`HotelLarge LAUNDRY_SWH_SCH` (49.6 % of tower design DHW flow) + `LaundryRoom_SWH_Sch_Post2004`
(4.2 %) = **53.8 % of design flow, left on their prototype schedules.** Laundry *volume* scales
with guest-nights, but it is washed in **batches** whose intra-day shape is an operating decision,
not a presence curve — driving it by instantaneous guest presence would move the wash load to
03:00, when guests are in their rooms. The correct model scales the prototype's batch shape by a
daily/monthly occupancy factor against a **fixed cross-scenario reference**, and choosing that
reference is a specification decision, not a bug fix. Left open rather than guessed, and recorded
in code so a partial fix is not read as a complete one: **after T9-11 roughly 54 % of design DHW
flow, concentrated in the hotel channel, still does not respond to occupancy.**

### Code

- `commercial_integration.py`: `DHW_MODEL_PER_CAPITA`, `_wateruse_channel_map()`,
  `_wateruse_space_of()`, `_dhw_excluded()`, the `_derived_dhw_schedule_for()` closure, the
  WATERUSE dispatch block, `inject_residential(..., dhw_model=)`, and
  `inject_mixed_use(..., dhw_model=None)` — **opt-in, off by default**.
- Provenance gains `dhw_model`, `n_dhw_applied`, `n_dhw_excluded`, `n_dhw_unresolved`, one
  `dhw <channel> '<proto>' -> floor=… peak=…` line per distinct prototype, plus explicit
  `dhw_EXCLUDED` / `dhw_UNRESOLVED` lines. Unresolved floor/peak leaves the object on its
  prototype and is recorded — never a silent fallback, same discipline as T9-9/T9-10.
- `3rdJ_08D_campaign_driver.py`: `--dhw-model {none|per_capita}`, arm recorded in
  `manifest["arm"]`.

### Verification — 8 predictions written before running

| | prediction | result |
|---|---|---|
| P1 | `lighting_model=None, dhw_model=None` still reproduces the T9-9 artefact byte-identically | **PASS** — md5 `ba5595827b9b8544a89f3c09470e0e3b` both sides; T9-11 is invisible when off |
| P2 | 0 unresolved, exactly 2 excluded, and only the LAUNDRY objects | **PASS** — `F55 Hotel_bot_Laundry`, `Laundry` (30.6 gpm) |
| P3 | applied/excluded counts per channel | **mis-specified → re-specified → PASS** (below) |
| P4 | every derived schedule inside its prototype's [floor, peak] | **PASS** — office [0.0018, 0.2578] ≤ 0.57 · hotel [0.1905, 0.6214] ⊂ [0.15, 0.80] · retail [0, 0.5713] ≤ 0.62 · residential [0.01, 1.00] |
| P5 | office DHW weekday mean falls vs the prototype's | **PASS** — 0.1067 vs 0.2100 time-weighted, **−49.2 %** (two harness defects first, see below) |
| P6 | office DHW differs between B_cons and B_opt | **PASS** — 0.117992 → 0.095750, a **−18.85 %** WFH lever where it was EXACTLY 0.00 % before |
| P7 | injector channel map == reporting-side resolver, object by object | **PASS** — 71 objects, 0 disagreements |
| P8 | PEOPLE/LIGHTS/EQUIP wiring identical with DHW on vs off | **PASS** — 128 objects compared, identical |

**P3 was mis-specified, not falsified.** I wrote the expected counts from the **Tall** tower's
inventory (47 objects) while the test runs the **SuperTall** tower (71). Re-stated as the
conservation check that was the actually-falsifiable part — *applied + excluded == the object
count read independently from the source IDF, zero unresolved* — it **PASSES**: 71 objects,
channel map `{retail 2, hotel 24, office 4, residential 41}`, 0 unresolved, 69 applied + 2
excluded = 71, hotel 24 − 2 laundry = 22 applied.

**P5 has failed twice for harness reasons, both worth recording** because both are the kind of
error that would have produced a confident wrong number:
1. the Compact-only parser returned `None` — `OfficeLarge BLDG_SWH_SCH` is a
   `Schedule:Year → Week:Daily → Day:Interval` graph, not a `Schedule:Compact`;
2. the replacement graph reader indexed `Schedule:Day:Interval` as `times=obj[5::2]`, which is
   the **value** column (the layout is `[class, Name, TypeLimits, Interpolate, Time1, Value1, …]`,
   so times are `4::2`), giving a `nan` denominator and a `+nan %` "result".

The injector itself was never affected: `_schedule_extremum` resolved office DHW floor 0.00 /
peak 0.57 off that same graph, and its `schedule:week:daily` branch excludes design days **by
field index**, so it keeps the weekday profile even where one day object serves both
`SmrDsn|Wkdy`. Fixed in the harness; P5 then PASSES at −49.2 % (0.1067 vs the prototype weekday mean of 0.2100).

### Not done

- **Not simulated.** No campaign has been run with `--dhw-model per_capita`; every number above
  is schedule-level, from the injector and the IDF.
- Hotel laundry (≈54 % of design DHW flow) still occupancy-invariant, deliberately — see above.
- No band, gate or threshold touched. No Leg-2 file touched.

---

### Campaign 1170493 — CLOSED, 112/112 (2026-07-31)

The 56-cell x 2-arm array left the queue with **112 COMPLETED, 0 FAILED, 0 TIMEOUT**. Arm B's
output tree `out_B_lm3/campaign_898d033a` carries **56** cell directories, matching arm A.
Aggregation for arm B submitted as job **1170745** (`3rdJ_08E_aggregate_4split.py --campaign-dir
out_B_lm3/campaign_898d033a --outdir agg_B_lm3`); arm A's aggregate (job 1170685) is already
downloaded and analysed above.

Array throttle was restored to 20 after the arm A aggregation, as agreed; the temporary drop to 7
existed only to break the `AssocGrpCpuLimit` deadlock (association cap `cpu=32`, the array's
8 x 4 CPUs consumed all of it and array tasks won every freed slot ahead of the aggregation job).

**Arm B analysis is PENDING the aggregate.** The predictions it will be judged against are the
ones already written above, before arm B landed — the office lighting level (~13-14 kWh/m2,
overshoot if materially above 15), office total still FAIL, equipment unchanged at 22.20, and the
WFH lever shrinking from -16.2 % toward ~-8.6 %. None of them has been touched since.

Note on scope: arm B carries `dhw_model=None`. It was launched before T9-11 existed, so **no
simulated DHW number will come out of this campaign** — T9-11 remains schedule-level only.

---

## ARM B ANALYSED — T9-10 lands on office, and BREAKS retail (2026-07-31)

Aggregation job **1170745**, 11:41 wallclock, `agg_B_lm3`. Integrity first, before any delta:
56 cells both arms, identical cell tags, `INJ_HASH=898d033a` both, `attribution_closed=True`
everywhere, `max|attribution_residual_rel| = 3.29e-16`, and **`max |area_B - area_A| = 0 m2`** —
the injector did not touch geometry, so every delta below compares the same building.

### Channel EUI, CFA basis, median over the 56 cells

| channel | pre-fix | arm A | arm B | B−A % | band | in-band pre → A → B | gate B |
|---|---|---|---|---|---|---|---|
| office | 71.08 | 80.03 | **82.69** | +4.5 % | [100,200] | 0/56 → 0/56 → 0/56 | FAIL |
| retail | 75.43 | 84.05 | **95.39** | +14.8 % | [80,155] | 12/56 → 38/56 → **56/56** | **PASS** |
| hotel | 178.29 | 180.94 | **179.72** | −1.0 % | [180,300] | 28/56 → 28/56 → 28/56 | FAIL |
| residential | 120.70 | 120.89 | 120.78 | −0.2 % | — | INFO | INFO |

### The seven pre-recorded predictions: 6 PASS, 1 FAIL (narrow), 0 falsifiers fired

| | prediction (written before arm B landed) | result |
|---|---|---|
| A1 | office lighting rises further in B than A, office gate still FAILs | **PASS** — 9.53 → 14.65 kWh/m², 0/56 |
| A2 | retail EUI rises in B relative to A | **PASS** — 84.05 → 95.39 |
| A3 | hotel nearly unchanged, moving *down* slightly (peak 1.0 → 0.8) | **PASS** — 180.94 → 179.72, −1.00 % |
| A4 | office **lighting** WFH lever smaller in magnitude than −16.2 % | **PASS** — −16.14/−16.13/−16.42/−16.41 → **−10.46/−10.46/−10.61/−10.61** |
| B1 | office `interior_lighting` B_central lands 13–14 kWh/m² | **FAIL** — 14.65 |
| B2 | office TOTAL 80–82 and the gate still FAILs | **PASS** — 81.07, 0/56 |
| B3 | office `interior_equipment` unchanged at 22.20 | **PASS** — 22.20, +0.00 % |

**A4 is the load-bearing one and it passed.** The stated falsifier — *"if arm B's office lighting
lever is not smaller in magnitude than −16.2 %, the zone-coincidence model did not land and T9-10
must be withdrawn"* — did not fire. Predicted ~−8.6 % from the n=1→n=3 span ratio, measured
−10.5 %, strictly between −16.2 % and 0.

**B1 failed on a band I set too tight, not on the withdrawal criterion.** 14.65 is outside
[13,14] but below the stated overshoot threshold (*"materially above ~15 → the calibration
overshot and n must come down"*), so n stays at 3. It sits **+6.2 % above `Default_NECB`'s
13.80**. Recorded as a miss, not re-banded.

**My own P4 test was mis-coded and is corrected here.** `analyse_armB.py` evaluated the lever on
office *total* EUI (−3.30 → −3.26 %, which does not shrink monotonically across all four
geometries) when the prediction at line 1332 is explicitly on office **lighting GJ**. The
prediction stands as written; the script tested the wrong column.

Specificity is exact: `residential`, `residential_common` and `service_MEP` lighting **and**
equipment move by **+0.0000 %** between arms, and office equipment by **+0.00 %**. T9-10 touched
only what it claims to touch.

### 🔴 The retail gate PASSES for the wrong reason — retail lighting is now FROZEN

`retail` going 38/56 → **56/56** must **not** be reported as a fix. Retail lighting energy,
`Tall__MTL`, all 14 scenarios:

| arm | retail `interior_lighting` GJ across the 13 injected scenarios | spread |
|---|---|---|
| A | 143.01 (B_cons) … 212.33 (Y2005) | **80.6 %** |
| B | **339.0211 in every single one, identical to 4 dp** | **0.0 %** |

Only the uninjected `Default_NECB` cell (258.28) differs. T9-10's retail rule
`g = 1 − staff_shoulder_flag` is a **binary open/closed flag read off the NECB proxy schedule**,
not off the occupancy series — so retail lighting no longer responds to occupancy, to era, or to
any sensitivity lever. It is the **DHW pathology reproduced exactly**, this time in the one
channel whose gate it makes pass, and on top of that it sits **+31.3 % above NECB's own retail
lighting** (339.02 vs 258.28) because "open" is held at full peak with none of NECB's ramps.

So the retail PASS was bought by deleting the signal the study exists to measure. It also
inverts the physics downstream in a self-consistent way — retail gas heating −28.0 %, cooling
+8.9 %, fans +9.0 % — which makes the whole retail channel look better behaved while being less
informative than arm A.

**Recommendation: withdraw the retail component of T9-10 and re-specify it.** Office (n=3) and
hotel (n=1) are sound and are kept. Retail needs a form that keeps an occupancy-dependent term —
an open-hours *minimum* under a zone-coincidence curve, e.g.
`g = max(open_flag · k, 1 − (1 − occ)^n)` — rather than a flag that replaces occupancy outright.
Until then **arm A is the defensible retail number and the retail gate stays FAIL**; no band or
threshold was touched to reach either verdict.

Note this makes the open item at `3rdJ_07_aug_to_bem_4split.py:20-45` (the provisional NECB
retail occupancy proxy) load-bearing exactly as flagged before the campaign — the flag driving
this is derived from that proxy.

### Not done

- No band, threshold or gate edited. Office and hotel FAILs stand; the retail PASS is **rejected
  on mechanism**, not by moving its band.
- T9-11 (DHW) is **not in this campaign** — both arms carry `dhw_model=None`. Still schedule-level.
- Hotel remains bimodal (SuperTall 149–165 vs Tall 195–212, nothing in [170,182)); unchanged by B.

---

## T9-12 — retail lighting re-specified, the T9-10 open/closed form WITHDRAWN (2026-07-31)

Acts on the arm B finding above. The withdrawn form `g = 1 - staff_shoulder_flag` is a binary
flag off the NECB **proxy** schedule and carries no occupancy, so it froze retail lighting at
339.0211 GJ across all 13 injected scenarios and put it +31.3 % above NECB's own. Replacement,
one free scalar:

```
g(t) = open(t) * [ k + (1 - k) * occ(t) ]        open(t) = 1 - staff_shoulder_flag(t)
```

`k` is the share of retail lighting switched by **store hours** (ambient, merchandising, egress —
lit whether or not a shopper is in the aisle); `(1 - k)` is the share tracking activity (task,
point-of-sale, back-of-house). **The two behaviours already simulated are its endpoints**: k=1 is
exactly the withdrawn form, k=0 is pure occupancy gated by opening hours. So k interpolates
between two arms whose energy we have measured — it is not a new degree of freedom invented to
hit a target.

### Calibration of k — same criterion as `office_n`, and NOT any EUI gate

Run the 2022 **observed** retail occupancy through the form; ask which k reproduces
`RetailStandalone BLDG_LIGHT_SCH_2013`'s own weekday mean of **0.4521** (floor 0.05, peak 0.90).

| k | weekday mean | vs prototype | retail lever (cons→opt) |
|---|---|---|---|
| 0.00 | 0.3139 | −30.6 % | +12.83 % |
| 0.50 | 0.4298 | −4.9 % | +3.65 % |
| **0.60** | **0.4530** | **+0.2 %** | **+2.69 %** |
| 0.75 | 0.4878 | +7.9 % | +1.50 % |
| 1.00 | 0.5458 | +20.7 % | **+0.00 %** ← the withdrawn form |

Four calibration predictions were written before the sweep and **4/4 PASS**: k=1 reproduces the
freeze exactly (span 0.000000 %); the span is monotone decreasing in k; a k strictly inside (0,1)
matches the prototype mean; and the calibrated span is non-zero but damped versus k=0.

**Shape was checked too**, because a mean match is one scalar — the same bar `office_n` was held
to. RMSE against the prototype's hourly weekday profile: **0.1572 at k=0.60**, versus 0.2336 at
k=0 and 0.2275 at k=1 — a **31 % reduction on the withdrawn form**, and k=0.60 beats *both*
endpoints. The RMSE optimum is k=0.50 (0.1543); **k=0.60 is kept because matching the prototype
mean was the pre-registered criterion** and switching to an RMSE fit after seeing the sweep would
be exactly the post-hoc move this log exists to prevent. The 1.9 % RMSE difference is recorded as
the sensitivity.

**One shape prediction was FALSIFIED and the reasoning behind it was wrong.** I predicted r would
be flat in k "because k rescales the lit level inside a fixed open window and cannot move the
timing". It is not flat — r spans 0.870–0.918 and peaks near k≈0.40 — because occupancy *varies
inside* the open window, so k does change the profile's shape there, not merely its level. r is
therefore weak evidence either way, and is recorded only so it is not later quoted as support it
cannot give.

### What it costs and what it buys

The retail `sens_retail_cons → sens_retail_opt` lever returns from **+0.00 % (frozen)** to
**+2.69 %** on the schedule weekday mean — deliberately far below the k=0 value of +12.83 %.
Store hours genuinely *do* damp the retail signal; that was the defensible half of the T9-10
argument and it is kept. What is not kept is the claim that the damping is total.

### Code

- `commercial_integration.py`: `apply_lighting_diversity(..., k_open=1.0)` — **the default is the
  old behaviour exactly**, so every existing caller is unaffected; `retail_mode` gains
  `"open_hours_mix"` and now **raises** on an unknown value instead of falling through;
  `LIGHTING_MODEL_CALIBRATED_V2` (office_n=3, hotel_n=1, retail k=0.60).
  `LIGHTING_MODEL_CALIBRATED` is left **frozen and marked withdrawn** so arm B stays exactly
  reproducible — the campaign keeps its control.
- `3rdJ_08D_campaign_driver.py`: `--lighting-model calibrated_v2`. `calibrated` still resolves to
  the withdrawn form and its help text now says so.

**Open item, reduced but not resolved:** `open(t)` still derives from the provisional NECB retail
occupancy proxy at `3rdJ_07_aug_to_bem_4split.py:20-45`. T9-12 *mixes* that proxy with a real
occupancy series instead of substituting for it, so the proxy's weight drops from 100 % to 60 %.

### Verification — 8 predictions written before running, 8 PASS (2 after re-specification)

| | prediction | result |
|---|---|---|
| V1 | `k_open=1.0` default is the literal withdrawn T9-10 formula | **PASS** — 48/48 slots, max diff **0.00e+00** |
| V2 | `lighting_model=None` still byte-identical to the T9-9 artefact | **PASS** — md5 `ba5595827b9b8544a89f3c09470e0e3b` |
| V3 | `open_hours_mix(k=1.0)` **is** `open_closed`, not an approximation of it | **PASS** — all 3 retail LIGHTS schedules identical |
| V4 | retail responds to the scenario again | **PASS** — withdrawn `+0.0000 %` → T9-12 `+2.54 %` |
| V5 | recovered main-floor lever in [+2.5, +3.0] % | **PASS after re-specification** — +2.54 % |
| V6 | level matches the NECB prototype | **PASS after re-specification** — 0.4530 vs 0.4521, **+0.21 %** |
| V7 | office/hotel lighting and all PEOPLE/EQUIPMENT wiring untouched | **PASS** — schedules and wiring identical |
| V8 | an unknown `retail_mode` raises instead of falling back silently | **PASS** — `ValueError` |

**V1 is the load-bearing safety claim** and it is exact, not approximate: the new `k_open`
argument defaults to the old behaviour bit-for-bit, so arm B remains reproducible and the
campaign keeps its control. V3 makes the same point structurally — the withdrawn model is a
*member* of the new family, so "k=1 vs k=0.60" is a like-for-like comparison.

**V5 and V6 both failed first for the same harness defect, worth recording.** Retail carries
**three** lighting prototypes with different peaks (main 0.900, back 0.7038, entry 0.7380), each
getting its own derived schedule; `sorted(...)[0]` picked the **back-space** schedule (key
`p704` sorts first) and then compared it against the **main** sales floor's prototype mean. Wrong
schedule, wrong reference. Re-run against all three, each against **its own** prototype, the
levers are +2.54 / +2.45 / +2.47 % (all `+0.0000 %` under the withdrawn form).

**V6 then failed a second time, and that one was a mis-specified test, not a defect.** It was
checking a `B_central` cell — a 2030 WFH bundle — against a criterion fitted on **2022 observed**
occupancy in a different province. A 2030 bundle *must* sit below 2022; measuring it against the
2022 target and calling the difference an error is testing a fit on data it was not fitted to.
Re-stated on the calibration's own cell it passes, and the added directional check passes too:

| cell / arm | main-floor weekday mean | vs prototype 0.4521 |
|---|---|---|
| Y2022 / T9-12 | **0.4530** | **+0.21 %** |
| B_central / T9-12 | 0.4195 | −7.22 % |
| Y2022 / withdrawn | 0.5458 | +20.73 % |

The middle row is the fix working: the 2030 WFH bundle now *moves* retail lighting, and moves it
**down**, which under the withdrawn form was impossible by construction.

### Not done

- **Not simulated.** No campaign has run with `--lighting-model calibrated_v2`; every T9-12 number
  is schedule-level. The retail EUI gate stays **FAIL on arm A's number** — the arm B PASS is
  rejected on mechanism and no band was touched to reach either verdict.
- Office (`n=3`) and hotel (`n=1`) are unchanged and were re-verified as untouched (V7).
- T9-11 (DHW) remains unsimulated and independent of this change.

---

### Campaign arms C and D — LAUNCHED (2026-07-31)

The requested configuration is arm D (`calibrated_v2` + `per_capita`). It is being run as **two**
arms, not one, so the two changes can be **attributed** rather than confounded:

| arm | tasks | `--lighting-model` | `--dhw-model` | isolates |
|---|---|---|---|---|
| C | 0–55 | `calibrated_v2` | `none` | **C − B** = the pure T9-12 retail-lighting effect |
| D | 56–111 | `calibrated_v2` | `per_capita` | **D − C** = the pure T9-11 DHW effect (~27 % of site energy) |

Running D alone would move retail lighting and service hot water simultaneously and no delta in it
could be assigned to either. Same 112 tasks and the same wallclock class as the A/B campaign.
Arms A (`out_A_t99`) and B (`out_B_lm3`) are closed, are **not** re-run, and stay on disk as the
controls.

Upload: `commercial_integration.py` md5 `39a6e24e…` and `3rdJ_08D_campaign_driver.py` md5
`a48fccd1…`, both verified byte-identical on the cluster. The injector was written to **both**
`campaign/repo/eSim_bem_utils/` **and** `upload/eSim_bem_utils/` — the second is the tree that
shadowed `PYTHONPATH` in the 2026-07-31 near-miss, so a stale copy cannot serve old code from
there. Both the validation job and every array task additionally `import
LIGHTING_MODEL_CALIBRATED_V2, DHW_MODEL_PER_CAPITA` and **exit non-zero** if it fails, which turns
that failure mode from silent into fatal.

Pre-flight job **1170768** asserts, and can fail on: 0/56 unresolved cells; both smoke runs exit 0;
arm C provenance contains `open_hours_mix` and `retail_k_open': 0.6`; arm C has `dhw_model=None`;
arm D has `n_dhw_unresolved=0`, `n_dhw_excluded=2` (the two LAUNDRY objects) and
`n_dhw_applied > 0`. The array is submitted only if it prints VALIDATION PASS.

**Predictions for arms C and D, recorded before the runs finish:**

1. **C vs B, retail EUI FALLS** from 95.39 toward ~88–91, and retail lighting stops being frozen:
   the 13 injected scenarios must show a non-zero spread where arm B had 339.0211 GJ in all of
   them. If retail lighting is still identical across scenarios in arm C, T9-12 did not land.
2. **C vs B, office and hotel are UNCHANGED** to within noise — T9-12 touches retail only, and
   V7 already proved this at schedule level. Any office/hotel movement means leakage.
3. **The retail gate does NOT stay 56/56.** Arm B's PASS was bought by the freeze; removing it
   should put retail back near `Default_NECB` (87.6–97.1) and the gate becomes genuinely
   uncertain. A PASS here would be meaningful where arm B's was not.
4. **D vs C, DHW stops being flat.** Office `dhw` was 12.19 kWh/m² in every scenario column to
   2 dp; in arm D it must differ between B_cons and B_opt. The schedule-level lever was −18.85 %,
   so expect a visible but smaller energy lever.
5. **D vs C, hotel moves LEAST in relative terms** despite DHW being 36.7 % of its energy, because
   ~54 % of design DHW flow is the excluded laundry. If hotel DHW moves as much as residential,
   the laundry exclusion did not hold.

#### Launch record — and a pre-flight that failed for the right reason

Upload verified by checksum on both trees. Pre-flight **1170768 FAILED**, and the failure was
**mine, not the code's**: the provenance glob was `smoke_C/*/injected.idf.provenance.txt` while
the driver writes `smoke_C/campaign_<hash>/<tag>/`, so `$PC`/`$PD` were empty and seven assertions
fired on empty files (`grep: : No such file or directory`). Both smoke runs had exited **0** and
both provenance files existed.

Worth recording rather than quietly fixing, for two reasons. First, the previous validation script
(`validate_campaign.sh`, used to clear the A/B campaign) carries the **same one-level glob** — it
never noticed because it only *printed* the provenance and asserted nothing. That is the vacuous
gate pattern again: a check that cannot fail because it never looks at what it claims to check.
Second, the fix is not just the glob: the script now **exits FATAL when the provenance path
resolves empty**, so an empty variable can never again be read as a failed assertion or, worse,
as a pass.

Re-run **1170770**: **VALIDATION PASS**, 04:51. The assertions that had to hold, and did:

| check | arm C | arm D |
|---|---|---|
| `lighting_model` | `retail_mode='open_hours_mix', retail_k_open=0.6` | same |
| `dhw_model` | `None` | `channels=(office, retail, hotel, residential)`, exclude `LAUNDRY` |
| `n_dhw_applied` | 0 | **45** |
| `n_dhw_excluded` | 0 | **2** — both LAUNDRY objects, named in the provenance |
| `n_dhw_unresolved` | 0 | **0** |
| dry-run | 0/56 unresolved | 0/56 unresolved |

45 applied on the **Tall** tower against 69 on SuperTall is the expected difference in object
count, not a discrepancy — the same trap that mis-specified T9-11's P3.

Array **1170771** submitted, `--array=0-111%20`, tasks 0–7 running immediately, the rest
`AssocGrpCpuLimit` as usual (association cap `cpu=32`).

A manager prompt for the next session, written so it needs no memory of this one, is at
`improvements/3rdJ_L3_manager_prompt_2026-08-01.md`.

---

## Campaign C/D closed 112/112 — 2026-08-01

`sacct -X -j 1170771` → **112 COMPLETED**, zero FAILED/TIMEOUT, queue empty. Both output roots
carry exactly 56 cell directories:

| arm | outroot | cells |
|---|---|---|
| C (`calibrated_v2`, DHW off) | `campaign/out_C_lm3v2/campaign_39a6e24e` | 56 |
| D (`calibrated_v2` + `per_capita`) | `campaign/out_D_full/campaign_39a6e24e` | 56 |

Aggregation submitted: **1171043** (arm C → `agg_C_lm3v2`), **1171044** (arm D → `agg_D_full`).

The five predictions recorded 2026-07-31 *before* these runs stand unedited and are the next
thing to test. The load-bearing one: arm B's retail `interior_lighting` was **339.0211 GJ in all
13 injected scenarios**; if arm C still shows a zero spread there, T9-12 did not land.

---

## Arms C/D verdict — 4 PASS, 1 FAIL — 2026-08-01

Aggregation `1171043`/`1171044` COMPLETED (12:00 / 17:54, exit 0:0). Integrity clears first:
56 cells per arm, `INJ_HASH=39a6e24e` for C and D (`898d033a` for A/B), `attribution_closed=True`
everywhere, `max|attribution_residual_rel| ≤ 3.35e-16`, identical cell tags across all four arms,
and **`max|area_C − area_B| = max|area_D − area_C| = 0 m²`** — geometry untouched, arms comparable.

### Channel EUI (CFA), median over 56 cells

| channel | armA | armB | armC | armD | C−B % | D−C % | band | in C | in D |
|---|---|---|---|---|---|---|---|---|---|
| office | 80.03 | 82.69 | 82.70 | 79.31 | +0.03 | −4.47 | [100,200] | 0/56 **FAIL** | 0/56 **FAIL** |
| retail | 84.05 | 95.39 | **90.05** | 87.66 | **−6.00** | −2.76 | [80,155] | 56/56 | **47/56 FAIL** |
| hotel | 180.94 | 179.72 | 179.75 | 173.73 | +0.02 | −3.27 | [180,300] | 28/56 **FAIL** | 28/56 **FAIL** |
| residential | 120.89 | 120.78 | 120.79 | **145.62** | +0.02 | **+22.29** | — | INFO | INFO |
| residential_common | 53.72 | 53.47 | 53.48 | 53.49 | +0.06 | 0.00 | — | INFO | INFO |
| service_MEP | 58.44 | 59.41 | 59.47 | 59.47 | +0.10 | 0.00 | — | INFO | INFO |

### A harness defect found and corrected before any verdict was recorded

The first pass reported P1 and P4 as FAIL on a **vacuous test**. `cell_tag` is
`<scenario>__<geometry>__<city>`, so pivoting `index=cell_tag, columns=scenario` yields exactly one
non-NaN per row and every "cross-scenario spread" is 0 **by construction** — it printed
`spread == 0` for arm B *and* arm C alike, and `nan` levers, with `Mean of empty slice` warnings as
the tell. This is the same failure class as the earlier vacuous gates: a test that cannot fail is
also a test that cannot pass. Corrected unit = the **geometry-city group** (4 of them), scenario as
the varying axis inside it (`analyse_armCD_fix.py`). P2 was **not** re-derived — its 0.05 %
threshold was written before the runs and stands as written.

### The five predictions, as written 2026-07-31

**P1 — PASS.** Retail EUI 95.39 → **90.05** (−5.61 %), inside the predicted 88–91. The freeze is
broken: arm B held retail `interior_lighting` at one value in **4/4** geometry-city groups
(Tall__MTL = 339.0211 GJ in all 13 injected scenarios, as recorded); arm C spreads
**24.46–46.17 GJ (9.2–11.8 %)** in every group, 0/4 frozen. Arm C's `B_central` retail lighting
(1278.97 GJ summed) lands on `Default_NECB` (1279.05 GJ) — the k=0.60 calibration reproduces the
NECB prototype's own weekday mean, which is what it was calibrated to.

**P2 — FAIL as written.** Threshold was "unchanged to within noise", operationalised at 0.05 %.
Measured `max|C−B|`: office **0.101 %**, hotel **0.081 %**, service_MEP **0.305 %**. The threshold
is not being relaxed. The mechanism is identified and is *not* injector leakage: in the C-vs-B
specificity table **every** off-retail delta is `heating`/`cooling`/`pumps`/`fans`/`heat_recovery`/
`heat_rejection` — there is **no** change to any `interior_lighting` or `equipment` end use outside
retail. Retail lighting −20.62 % removes internal gain, so retail `heating` NaturalGas **+14.60 %**
and the shared central plant follows (service_MEP heating +0.50 %). Recorded as a FAIL whose cause
is thermal coupling through shared plant, not a boundary violation.

**P3 — PASS.** Arm B's 56/56 was bought by the freeze. Arm C is 56/56 but now on a genuinely
variable quantity (EUI range 80.90–97.16, sd 5.119, vs arm B 87.41–101.97, sd 4.651 — the floor is
now 0.9 above the band edge, not 7.4), and **arm D falls to 47/56**. The gate has been seen failing,
so arm C's PASS is a real PASS where arm B's was not.

**P4 — PASS on the claim, wrong on the magnitude.** Office DHW cross-scenario spread
**0.0086 % → 30.36 %**; the B_opt-vs-B_cons lever goes **−0.004 % → −22.13 %**. Every channel goes
flat→live (retail 0.008→53.6 %, hotel 0.009→5.83 %, residential 0.011→16.74 %). The prediction said
"expect a visible but **smaller**" lever than the −18.85 % schedule-level figure; the energy lever is
**−22.13 %, i.e. larger**. The directional claim holds, the damping expectation does not.

**P5 — PASS.** On the DHW end use itself: hotel **−8.73 %**, retail −28.44 %, office −29.38 %,
residential **+40.78 %**. Hotel moves least by a factor of 3.3 against the next channel, consistent
with ~54 % of design DHW flow being the deliberately excluded laundry. (The first pass scored this
on *channel-total* EUI and returned `retail`; the prediction text is explicit that it is about DHW —
"if hotel DHW moves as much as residential" — so the DHW basis is the specified one.)

### New open item — residential DHW rises 40.78 % under `per_capita`

The largest single effect in the campaign is not one of the five predictions: arm D raises
residential DHW NaturalGas **214,298 → 302,166 GJ (+41.0 %)**, pushing the residential channel EUI
120.79 → **145.62 (+22.3 %)**. All other channels *fall* under `per_capita` (office −29 %,
retail −28 %, hotel −9 %). This asymmetry needs a specification answer before arm D is usable:
whether `f_dhw(t) = floor + (peak−floor)·occ(t)` is meant to preserve the annual design flow per
channel, or whether a residential occupancy profile that is high overnight legitimately integrates
above the flat design schedule. Until that is settled, **arm C is the defensible product and arm D
is diagnostic** — and note the retail gate's 56/56 → 47/56 fall is driven entirely by arm D's DHW.

**Gates unchanged: office FAIL 0/56, hotel FAIL 28/56 both stand. No band, threshold or gate has
been edited.**

---

## T9-11 residential +40.8 % — hypothesis and predictions, written BEFORE the test — 2026-08-01

**Note first that T9-11's own pre-recorded expectation is already falsified.** `commercial_integration.py:672-675`
says, verbatim: *"DHW falls in every channel (our occupancy series run below the prototype schedules'
own means), office and residential most"*. Residential rose **+40.78 %**. The prediction was written
before the simulation, and the simulation refuted it. That is the gate working.

**HYPOTHESIS H.** The map `f_dhw(t) = floor + (peak − floor)·occ(t)` (`:651`) is anchored on the
prototype schedule's **extrema** — `floor` from `_schedule_standby_floor`, `peak` from
`_schedule_peak` (`:1023-1024`) — and nothing in it preserves the prototype's **mean**. Annual draw
volume is proportional to the mean, not the extrema. For `ApartmentHighRise APT_DHW` the documented
range is **0.01–1.00** (`:659`), so `f ≈ occ(t)` almost exactly. Residential occupancy is high
overnight, when a DHW *draw* schedule is near its floor — nobody showers at 03:00, but they are
home. So residential integrates far above the prototype draw shape and volume rises. Office and
retail have occupancy ≈ 0 nights and weekends against prototype floors up to 0.57, so they fall.
The error is the same class as the one the laundry exclusion was written to avoid (`:661-670`):
**instantaneous presence is not draw rate.**

**PREDICTIONS, falsifiable, recorded before running.** `agg_annual.csv` carries `peak_W` alongside
`energy_J` per (channel, end_use, fuel), so load factor LF = mean/peak is derivable per arm.

- **H1 (the discriminator).** Residential DHW `peak_W` is **essentially unchanged** C→D (|Δ| < 5 %)
  while energy rises 40.8 %. Both schedules reach the same maximum 1.00, so only the mean moved.
  *If `peak_W` also rose by ~41 %, H is REFUTED* and the defect is a magnitude/sizing error
  (`Peak_Flow_Rate` re-scaled) rather than a shape error.
- **H2.** Residential DHW load factor rises by ~41 % and office/retail LF falls by ~29 %; the LF
  ratio must reproduce the energy ratio once the peak change is divided out.
- **H3.** Arm D residential DHW LF ≈ the residential **occupancy** LF taken from the independent
  `people` metric in `agg_diurnal.csv` (within ~15 %), because floor 0.01 / peak 1.00 makes
  `f ≈ occ`. Office must NOT match as tightly — its prototype floor (up to 0.57) survives the map
  and lifts the derived schedule above its own occupancy. *If arm D residential DHW LF is far from
  the occupancy LF, the schedule being written is not the occupancy series and H is wrong about
  which term dominates.*
- **Not a test:** the cross-channel sign split (residential up, office/retail down, hotel least) is
  already observed and cannot re-confirm the hypothesis that was built to explain it.

### Result: H REFUTED as stated, and H2 was a third vacuous test — 2026-08-01

| channel | energy D/C | peak_W D/C | LF C | LF D | LF D/C |
|---|---|---|---|---|---|
| residential | **+40.78 %** | **+31.76 %** | 0.5263 | 0.5623 | +6.85 % |
| office | −29.38 % | −39.41 % | 0.2576 | 0.3002 | +16.55 % |
| retail | −28.44 % | +3.12 % | 0.3164 | 0.2196 | −30.61 % |
| hotel | −8.73 % | −7.64 % | 0.4582 | 0.4528 | −1.18 % |

- **H1 REFUTED.** Residential DHW `peak_W` rose **+31.76 %**, not the predicted <5 %.
- **H2 was VACUOUS — a third one.** I defined LF = E/(h·P) and then "tested" whether
  `E_D/E_C = (LF_D/LF_C)·(P_D/P_C)`. Substituting the definition, that is `E_D/E_C = E_D/E_C`. The
  residual came back `+0.0000 %` for all four channels — the signature of an identity, not of
  agreement. It cannot fail and confirms nothing. Struck.
- **H3 NOT CONFIRMED.** Every channel's arm-D DHW LF sits *below* its occupancy LF (residential
  −27.1 %, office −15.5 %), and the predicted ordering inverted: office was **tighter** than
  residential, the opposite of the prediction.

**But the H1 refutation is itself confounded, and I am not treating it as the answer.** `peak_W` here
is summed over 56 cells and over two fuels whose mix shifted under arm D (residential DHW gas
+41.0 %, electricity +17.7 %); a sum of non-coincident per-cell peaks across fuels is not the
schedule's maximum. Provenance confirms the inputs are exactly as documented — `dhw residential
'ApartmentHighRise APT_DHW_SCH' -> floor=0.01 peak=1.0`, `n_dhw_applied=45`, `n_dhw_excluded=2`,
`n_dhw_unresolved=0` — and `apply_lighting_diversity` (`:630`) clamps to `max = peak`, so at
**schedule** level the maximum cannot have moved. Meter peak and schedule peak are different
objects; the proxy is what failed, not necessarily the hypothesis.

### Decisive test, predictions written BEFORE running

Arm D's injected IDF contains **both** families — the now-unreferenced prototype `APT_DHW_SCH` and
the 45 `MXU_Residential_DHW_HH*` schedules that replaced it. Measuring them directly removes every
meter-side confound. Time-weighted expansion of the `Until:` blocks to 24 hourly values per
daytype, design days excluded; derived family weighted by how many `WaterUse:Equipment` objects
reference each.

- **H1b.** `max` of every `MXU_Residential_DHW_*` = **1.00** = `max(APT_DHW_SCH)`. *If any derived
  schedule exceeds 1.00, `apply_lighting_diversity` is not doing what `:630` says and the defect is
  in the clamp.*
- **H2b (the real test).** WD/WE-weighted (5:2) mean of the derived family ÷ mean of `APT_DHW_SCH`
  = **1.41 ± 0.08**, reproducing the observed +40.78 % energy rise. This is *not* an identity: it is
  computed from schedule geometry inside the IDF and compared against a meter total from a separate
  artefact. *If it lands far from 1.41, the annual mean of the schedule is not what is driving the
  energy change and the cause is elsewhere.*

### MECHANISM CONFIRMED from the hourly artefact — T9-11 is mis-specified for every channel — 2026-08-01

`dhw_hourly.csv` (8760 rows per channel per cell) is the direct artefact and needs no meter-side
inference. Cell `B_central__Tall__MTL`, arm C vs arm D:

| channel | annual C | annual D | Δ | max MJ/h C → D | Δ peak |
|---|---|---|---|---|---|
| residential | 1684.83 GJ | 2299.47 GJ | **+36.48 %** | 394.22 → 384.73 | **−2.41 %** |
| office | 719.75 | 419.93 | −41.66 % | 315.87 → 142.82 | −54.79 % |
| hotel | 2572.98 | 2361.29 | −8.23 % | 927.13 → 886.37 | −4.40 % |
| retail | 56.38 | 31.33 | −44.43 % | 19.75 → 17.92 | −9.24 % |

**Residential DHW hourly shape, share of the daily total:**

| | 00 | 02 | 04 | **06** | 09 | 12 | 15 | 18 | 21 | 23 |
|---|---|---|---|---|---|---|---|---|---|---|
| arm C | 0.47 | 0.08 | 1.57 | **7.95** | 6.49 | 4.19 | 4.43 | 5.72 | 4.33 | 1.34 |
| arm D | 5.02 | 5.54 | 5.66 | 5.45 | 2.94 | 2.53 | 3.72 | 4.09 | 4.19 | 4.56 |

- **Night (00:00–05:00) share: 8.34 % → 32.86 %, a 3.94× rise.**
- **Peak draw hour moves from 06:00 to 04:00.**
- Diurnal peak-to-mean collapses 1.907 → 1.359 — the profile flattens toward the occupancy curve.
- Hourly **max is unchanged (−2.41 %)**, which confirms **H1b at cell level**: the clamp holds and
  the schedule maximum did not move. It also confirms the earlier `peak_W` +31.76 % was exactly the
  bad proxy I flagged — a sum of non-coincident per-cell peaks across two fuels whose mix shifted.

**The defect is a specification error, and it is the one T9-11's own comment warned about.**
`:664-665` excludes laundry because *"driving it by instantaneous guest presence would move the wash
load to 03:00, when guests are in their rooms."* That is precisely what T9-11 then did to
residential **showers** — the peak draw hour is now 04:00. `f_dhw(t) = floor + (peak−floor)·occ(t)`
treats draw rate as proportional to instantaneous presence, but showering, handwashing and cooking
are *scheduled behaviours*, not presence-proportional. Being home asleep at 04:00 is presence with
no draw. The reasoning that justified excluding laundry applies to all of DHW.

This is **not** a residential-only problem. Office −41.7 % with its peak halved (−54.8 %) is the same
error with the sign flipped: zero occupancy nights and weekends drives the office draw below its own
circulation floor. Residential rises only because residential occupancy is the one channel that is
high when a draw schedule should be near zero.

**Consequence: arm D is not usable as a product.** Arm C stands as the defensible deliverable
(T9-12 only, DHW untouched, gates unchanged). T9-11 needs re-specification before any re-run:
the correct form modulates the prototype's daily **volume** by an occupancy factor while preserving
its intra-day **shape** — i.e. the treatment `:666-667` already reserved for laundry, applied to all
four channels. Choosing the cross-scenario reference for that factor remains the open specification
decision. **No band or gate has been edited; arm D's retail 47/56 is a consequence of this defect,
not evidence about retail.**

Pre-registered H1b/H2b (direct schedule measurement inside the IDF) submitted as job `1171053`;
H1b is already corroborated by the unchanged hourly max above.

---

## T9-13 — DHW volume scaling. RE-SPECIFICATION of T9-11 (withdrawn) — 2026-08-01

Implemented in `eSim_bem_utils/commercial_integration.py`, opt-in, off by default. T9-11
(`DHW_MODEL_PER_CAPITA`) is left in the file untouched so arm D stays reproducible; it is
**withdrawn as a model**, not deleted as an artefact.

### The form

    f_new(t) = s_proto(t) · r(d) / R          r(d) = mean(occ_d) / mean(occ_ref_d)
    Peak_Flow_Rate' = Peak_Flow_Rate · R      R    = max_d r(d)

`s_proto` is the prototype flow-fraction schedule's own time-weighted hourly profile, carried
through **untouched** — intra-day shape, peak hour and night share are preserved *by construction*.
Daily volume scales exactly by `r(d)`, since
`volume(d) ∝ P·R · mean(s)·r(d)/R = P·mean(s)·r(d)`. Dividing the shape by `R` and multiplying
design flow by `R` keeps `max(f_new) = max(s_proto)`, so the Fraction bound is never violated and
the schedule never silently clips — clipping would truncate volume and break the model's own promise.

**No-op property.** If occupancy equals the reference, `r = R = 1`, `f_new = s_proto` and
`Peak_Flow_Rate` is unchanged: the model reduces to the untouched prototype bit-for-bit. A model
that cannot reproduce its own null case cannot be trusted to report a lever. Asserted by T1.

### The reference, and why it is forced

The injector runs **one scenario per IDF** and has no cross-scenario view, so "relative to
`Default_NECB`" is not computable in-run. Normalising to the injected series' own annual mean is
degenerate — it forces annual DHW to be scenario-invariant, restoring the original T9-11 complaint.
The prototype **PEOPLE** schedule is the one anchor that is fixed across scenarios, present in every
IDF, and physically right: NECB sized this DHW volume against that many person-hours; our scenario
supplies a different number; the ratio is per-capita daily volume done correctly.

Ordering is load-bearing: the reference is captured **before** the PEOPLE dispatch loop, because
afterwards the object carries an `MXU_*` schedule and `_schedule_daytype_profiles` correctly refuses
it. One representative PEOPLE object per channel, and which one is recorded in the provenance.

### Laundry is no longer a special case

T9-11 excluded laundry because a presence-driven *rate* would move the wash to 03:00. T9-13 never
touches intra-day shape, so the batch shape survives untouched and only its daily volume scales with
guest-nights — precisely the "correct model" the T9-11 comment described but could not implement.
`exclude_schedule_tokens` therefore defaults to **empty**; the parameter is kept so the exclusion can
be reinstated for comparison. This closes the open item "~54 % of design DHW flow still
occupancy-invariant".

### A real bug the tests caught

The first version of the time-weighted expander skipped any block naming a design day. Prototypes
write `For: Weekdays SummerDesignDay WinterDesignDay` as **one** block, so that rule discarded the
weekday profile entirely (T6 failed with `StopIteration`). Corrected to skip **design-day-only**
blocks. `_schedule_extremum` keeps the looser any-token rule deliberately — it is validated against
the prototypes for T9-9/T9-10 floors and peaks, and changing it would silently move numbers in
closed campaigns. The two rules now differ on purpose, and the divergence is commented in both.

Separately, `_schedule_extremum` **cannot** be reused for a mean: it collects a flat list of values,
so a value spanning 8 h and one spanning 1 h each appear once. T6 measures the error — the
time-weighted mean of a 1-hour spike is `0.041667`, the unweighted mean is `0.333333`, an **8×**
overstatement. Hence a separate resolver rather than another `agg`.

### Diagnostics — `audit_dhw_shape_preservation`

Shape preservation is an identity here, so it is **asserted**, not assumed. Per applied object:

| check | asserts |
|---|---|
| D1 | night share (00:00–05:00 of the daily total) identical to the prototype's |
| D2 | peak hour identical to the prototype's |
| D3 | `max(f_new) ≤ max(s_proto)` — the bound was not restored by clipping |
| D4 | volume ratio **achieved** equals `r(d)` **intended** |
| D5 | no object silently saturated at `r_max` |

An **empty** audit reports FAIL, not PASS — a gate that never ran is not a gate that passed (T5).
Results land on `result["t9_13_audit"]` and in the provenance file as `t9_13_audit_pass=`,
`t9_13_VIOLATION …`, `t9_13_reference …`, and one `t9_13 <channel> … nightshare=a->b peakhour=x->y
max=m->n noop= clipped=` line per distinct `(channel, r_wd, r_we)`.

### The gate has been seen failing

Per the standing rule, the audit was run against **T9-11's actual defect** (T4), not a synthetic one:
fed the `floor + (peak−floor)·occ` output on a realistic residential draw profile it reports
`night share 0.0354 → 0.3730`, `peak hour 7h → 0h`, and fails **D1, D2 and D4**. This diagnostic
would have caught arm D before it consumed 56 runs.

**22/22 primitive tests pass** (`test_t9_13.py`): no-op identity, shape preservation, exact volume
ratio, Fraction-bound safety, audit-passes-on-good, audit-fails-on-T9-11, empty-is-FAIL, and the
time-weighted expander. T9-9 / T9-10 / T9-11 / T9-12 outputs verified unchanged.

### Two specification choices SURFACED, not buried — your call

1. **`peak_policy`** — default `"rescale"`: `Peak_Flow_Rate` rises with `R` when our occupancy
   exceeds NECB's. Physically consistent (more person-hours really is a larger design draw) but it
   **does change plant design flow**, which T9-11 was rightly careful about. Alternative `"cap"`
   forbids `R > 1`, preserving prototype sizing at the cost of under-serving busier scenarios.
2. **`r_max = 3.0`** — a runaway guard, not a tuning knob. Any object hitting it is reported CLIPPED
   (D5) so a silent saturation cannot be read as a clean result.

Neither is chosen by evidence. **Not simulated yet** — T9-13 has been tested at the primitive level
only. No campaign has been run with it, and no gate has moved. Arm C remains the deliverable.

### Verified against the REAL IDF — the resolver, and a blocker that would have shipped silently

**The prototype DHW schedules are not `Schedule:Compact`.** Job `1171059` on the real tower:
205 Compact, 9 Constant, 126 **Year**, 147 Week:Daily, 425 Day:Interval — and **all 7** distinct
WaterUse:Equipment flow-fraction schedules (47 objects) are `SCHEDULE:YEAR`. The first version of
`_schedule_daytype_profiles` handled only Compact and Constant, so T9-13 would have marked every
object `dhw_unresolved` and produced a **whole-building no-op** — correctly recorded, and useless.
Extended to the full `Year → Week:Daily/:Compact → Day:Interval/:Hourly/:List` chain and re-verified
on the pre-injection tower (job `1171061`, injector md5 `9c2328ef`): **DHW 7/7 resolved, 0
unresolved.**

| prototype schedule | mean_wd | max_wd | peak_h | night share |
|---|---|---|---|---|
| `ApartmentHighRise APT_DHW_SCH` | 0.5242 | 1.0000 | 07 | 0.0358 |
| `HotelLarge GuestRoom_SWH_Sch` | 0.3333 | 0.8000 | 07 | 0.1500 |
| `HotelLarge BLDG_SWH_SCH` | 0.3750 | 0.6000 | 07 | 0.1222 |
| `OfficeLarge BLDG_SWH_SCH` | 0.2100 | 0.5700 | 12 | 0.0000 |
| `RetailStandalone BLDG_SWH_SCH` | 0.2450 | 0.6200 | 12 | 0.0000 |
| `HotelLarge LAUNDRY_SWH_SCH` | 0.2917 | 1.0000 | 17 | 0.0000 |
| `HotelLarge LaundryRoom_SWH_Sch_Post2004` | 0.2917 | 1.0000 | 17 | 0.0000 |

The residential prototype's own night share is **0.0358** — arm D ran it at **0.3286**. That is the
defect measured against its own source, independently of the hourly artefact.

### The reference had to be re-specified too — `prototype_people` is not viable on this tower

The same probe found the tower carries **exactly one** PEOPLE schedule for every channel:

    NECB-A-Occupancy   mean_wd = 0.3583   peak_h = 9   mean_we = 0.0000

Two independent reasons it cannot serve as the reference:

1. `r_we = mean(occ_we) / 0` is **undefined** → all 47 objects unresolved → silent no-op.
2. It is **not commensurate**. Scaling residential draw against an office-shaped NECB curve that is
   zero on Saturdays compares "fraction of residents at home" with "NECB office occupancy". Patching
   the zero would not make the ratio mean anything.

So the reference is now `reference="baseline_series"`: a per-channel **weekly-mean occupancy of the
baseline scenario**, i.e. the *same series as the target*, computed once offline and held constant.
This is the "FIXED cross-scenario reference" the T9-11 comment named as a specification decision.
Well-posed (same units, same construction), and the per-scenario injector still never needs a
cross-scenario view. `Default_NECB` then gets `r = 1` exactly — the no-op case — absolute DHW stays
at the calibrated NECB level, and every other scenario moves relative to it, which is the lever
T9-11 was trying to create. `DHW_MODEL_VOLUME_SCALED_PROTO_PEOPLE` is kept for IDFs that do carry
per-channel prototype occupancy; on this tower it reports every object unresolved, loudly.

`reference_occ_mean` ships **empty**. A channel missing from it is reported `dhw_unresolved` with the
reason and is never defaulted to 1.0 — a defaulted reference would fabricate a no-op and report it
as a result.

### Blocking next action, and it is a specification decision

**T9-13 cannot run until the four baseline weekly-mean occupancies are computed** from the baseline
scenario's Step-7 CSVs (`office_presence_multiplier_2030.csv`,
`hotel_schedule_multiplier_2030_central.csv`, `BEM_Schedules_4split_2030_central.csv`, retail).
**Which scenario is the baseline is your call** — `Default_NECB` is the natural choice (it makes the
uninjected cell the exact no-op), but `B_central` is defensible if the levers should be read
relative to the central 2030 bundle instead. I have not guessed it.

Still open and unchanged: `peak_policy` (`rescale` vs `cap`), `r_max = 3.0`.

### CORRECTION to the blocking decision as I stated it — 2026-08-02

The paragraph above is wrong and is struck. It offered `Default_NECB` as the baseline "because it
makes the uninjected cell the exact no-op". Two errors, and the second one is worse than the first.

**1. The argument was vacuous.** `3rdJ_08D_campaign_cells.py:234` declares
`{"tag": "Default_NECB", "channels": {}}` — *no injection at all*, confirmed again by
`DELIBERATE_CHANNEL_EXCEPTIONS = {"Default_NECB": frozenset()}` at `:353`. The injector never runs
in that cell. It is therefore an exact no-op under **every** candidate reference, so the property
separates zero candidates. This is the same failure mode as the three vacuous tests already logged
above (arms C/D P1/P4/P5, and H2): a statement that cannot come out false was presented as evidence.
It was caught by reading the scenario definition, not by reasoning about it.

**2. `Default_NECB` cannot be the baseline at all.** `reference="baseline_series"` requires a
per-channel occupancy series *of our construction* to take a weekly mean of. `Default_NECB` has none
— that is precisely what makes it the control. The choice is between the **injected** scenarios.

**Recommendation, and the reasoning is falsifiable.** `Y2022` — `"2022 observed cycle"`,
`3rdJ_08D_campaign_cells.py:236-238`, all four channels present. The prototype's DHW volume is a
*present-day* engineering calibration, so the person-hours it is implicitly divided by should be the
*present-day* occupancy from the same series. Then `r(d)` for any 2030 bundle reads as "person-hours
relative to today", which is the lever T9-11 was trying to create, and the historical panel reads as
change from today with the correct sign. `B_central` is the alternative — it anchors on a *projected*
future, which makes the observed year Y2022 move and gives the historical years `r != 1` against a
scenario that has not happened.

Consequence to carry: Y2005/Y2010/Y2015 carry **no hotel channel** (`DELIBERATE_CHANNEL_EXCEPTIONS`,
QC hotel ground truth starts 2019). Under a Y2022 reference, hotel is simply not injected in those
three years — consistent, not a gap, but it must be stated when the hotel DHW lever is reported.

Code comment at `eSim_bem_utils/commercial_integration.py` corrected the same day; the struck claim
is preserved there too rather than deleted.

Still open and unchanged: `peak_policy` (`rescale` vs `cap`), `r_max = 3.0`.

### Next session — handoff written 2026-08-02

Manager prompt for the next session: `improvements/3rdJ_L3_manager_prompt_2026-08-02.md`
(predecessor `..._2026-08-01.md` archived to `improvements/prompts/`).

First task is deliberately **not** "pick a baseline". It is: compute the per-channel weekly-mean
occupancy for **every** candidate reference in one pass and print the table. The choice then costs
one line instead of a re-run, and the sensitivity of `r` to the choice becomes visible *before* it is
made rather than after.

---

## Task 1 EXECUTED — the reference table, 2026-08-02

Script: `t913_reference_table.py` (scratchpad), run locally with `py -3`. It mirrors
`commercial_integration.py::_channel_occ_24` and the three product loaders exactly rather than
re-implementing them from the docs: 48→24 by pair-average, retail weekend = `mean(sat24, sun24)`,
hotel = unweighted mean of the 12 monthly 24-h vectors, residential = per-household 24-h
`Occupancy_Schedule` filtered by `RESIDENTIAL_DTYPE_APARTMENT = ['HighRise', 'MidRise']`. Scenario→file
wiring taken from `3rdJ_08D_campaign_cells.py:_build_scenarios()` (`:194-300`), not guessed.
7175 eligible households in every residential product, 0 dropped for incomplete 24-h records.

### Weekly-mean occupancy, `mean_wd` / `mean_we`

Office and residential are city-independent; retail and hotel carry a `PR` column, so both are shown.

| scenario | office | retail QC | retail AB | hotel QC | hotel AB | residential |
|---|---|---|---|---|---|---|
| Y2022 | 0.2530 / 0.0651 | 0.3104 / 0.2615 | 0.3554 / 0.2618 | 0.3573 / 0.3682 | 0.3624 / 0.3735 | 0.6355 / 0.7321 |
| B_cons | 0.2070 / 0.1622 | 0.1964 / 0.1769 | 0.1839 / 0.1907 | 0.3696 / 0.3809 | 0.3502 / 0.3609 | 0.7491 / 0.7665 |
| B_central | 0.1872 / 0.1353 | 0.2117 / 0.1906 | 0.1982 / 0.2055 | 0.4017 / 0.4140 | 0.3891 / 0.4010 | 0.7688 / 0.7871 |
| B_opt | 0.1680 / 0.1126 | 0.2291 / 0.2064 | 0.2145 / 0.2225 | 0.4298 / 0.4430 | 0.4085 / 0.4210 | 0.7774 / 0.8069 |
| Y2005 | 0.2605 / 0.0682 | 0.3469 / 0.1869 | 0.3467 / 0.1994 | — absent — | — absent — | 0.6260 / 0.7399 |
| Y2010 | 0.2449 / 0.0598 | 0.3360 / 0.1939 | 0.3187 / 0.2055 | — absent — | — absent — | 0.6333 / 0.7252 |
| Y2015 | 0.2720 / 0.0682 | 0.3077 / 0.2286 | 0.2934 / 0.2144 | — absent — | — absent — | 0.6233 / 0.7483 |
| sens_office_cons | 0.2070 / 0.1622 | 0.2117 / 0.1906 | 0.1982 / 0.2055 | 0.4017 / 0.4140 | 0.3891 / 0.4010 | 0.7491 / 0.7665 |
| sens_office_opt | 0.1680 / 0.1126 | 0.2117 / 0.1906 | 0.1982 / 0.2055 | 0.4017 / 0.4140 | 0.3891 / 0.4010 | 0.7774 / 0.8069 |
| sens_retail_cons | 0.1872 / 0.1353 | 0.1964 / 0.1769 | 0.1839 / 0.1907 | 0.4017 / 0.4140 | 0.3891 / 0.4010 | 0.7688 / 0.7871 |
| sens_retail_opt | 0.1872 / 0.1353 | 0.2291 / 0.2064 | 0.2145 / 0.2225 | 0.4017 / 0.4140 | 0.3891 / 0.4010 | 0.7688 / 0.7871 |
| sens_hotel_cons | 0.1872 / 0.1353 | 0.2117 / 0.1906 | 0.1982 / 0.2055 | 0.3696 / 0.3809 | 0.3502 / 0.3609 | 0.7688 / 0.7871 |
| sens_hotel_opt | 0.1872 / 0.1353 | 0.2117 / 0.1906 | 0.1982 / 0.2055 | 0.4298 / 0.4430 | 0.4085 / 0.4210 | 0.7688 / 0.7871 |

### `r` under the recommended `Y2022` reference

| scenario | office `r_wd`/`r_we`/**R** | retail QC **R** | retail AB **R** | hotel QC **R** | hotel AB **R** | residential **R** |
|---|---|---|---|---|---|---|
| Y2022 | 1.000 / 1.000 / **1.000** | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| B_cons | 0.818 / 2.493 / **2.493** 🔴 | 0.677 | 0.728 | 1.034 | 0.966 | 1.179 |
| B_central | 0.740 / 2.079 / **2.079** 🔴 | 0.729 | 0.785 | 1.124 | 1.074 | 1.210 |
| B_opt | 0.664 / 1.731 / **1.731** 🔴 | 0.789 | 0.850 | 1.203 | 1.127 | 1.223 |
| Y2005 | 1.030 / 1.049 / **1.049** | 1.117 | 0.975 | n/a | n/a | 1.011 |
| Y2010 | 0.968 / 0.919 / **0.968** | 1.082 | 0.897 | n/a | n/a | 0.997 |
| Y2015 | 1.075 / 1.049 / **1.075** | 0.991 | 0.826 | n/a | n/a | 1.022 |
| sens_office_cons | **2.493** 🔴 | 0.729 | 0.785 | 1.124 | 1.074 | 1.179 |
| sens_office_opt | **1.731** 🔴 | 0.729 | 0.785 | 1.124 | 1.074 | 1.223 |
| sens_retail_cons | **2.079** 🔴 | 0.677 | 0.728 | 1.124 | 1.074 | 1.210 |
| sens_retail_opt | **2.079** 🔴 | 0.789 | 0.850 | 1.124 | 1.074 | 1.210 |
| sens_hotel_cons | **2.079** 🔴 | 0.729 | 0.785 | 1.034 | 0.966 | 1.210 |
| sens_hotel_opt | **2.079** 🔴 | 0.729 | 0.785 | 1.203 | 1.127 | 1.210 |

`r_max = 3.0` is never reached at channel level, under any of the 13 candidate baselines.

### 🔴 FINDING 1 — the `R > 1.5` flag fires, and it is office-weekend, under every baseline

The prompt asked for `R > 1.5` to be flagged because a large `R` resizes the water heater and mixes a
plant-sizing effect into a schedule lever. It fires 89 times across the 13 candidate baselines. The
pattern is not noise:

- Under `Y2022`, **office R = 1.73–2.49 in all nine 2030-family cells**, and it is `r_we` that does
  it every time — `r_wd` is 0.66–0.82, i.e. *below* 1. Weekday office presence falls under WFH, as
  expected; weekend presence *rises* from 0.0651 to 0.113–0.162.
- The split is between products, not between bands. All four "observed"-band office series
  (Y2022, Y2005, Y2010, Y2015) sit at `mean_we` 0.060–0.068; all three 2030 bands sit at 0.113–0.162.
  So `r_we ≈ 2` is a **level shift between the observed and the projected office product on
  weekends**, and any observed-year baseline inherits it (Y2010 is worst: office R up to 2.71).
- Choosing a 2030 baseline does not remove the flag, it moves it onto retail: under `B_cons`, retail
  R = 1.57–1.93 for Y2022 and the three historical years.

**No baseline makes the flag go away.** The honest options are (i) accept the resize and report it,
(ii) `peak_policy="cap"`, or (iii) exclude office from the T9-13 channel tuple. Note that under
`"cap"` with `r_we ≈ 2` the weekend flow fraction is multiplied by ~2 with `R` held at 1, so it
clips at the Fraction bound — `audit_dhw_shape_preservation` D3/D4 would then fire. That is the audit
working, not a bug, but it means `"cap"` and office-in-scope are close to incompatible on this stock.

**This is a question about the office product, not about T9-13**, and it should be answered before
the office DHW lever is reported: is a 2.5× rise in weekend at-work fraction from 2022 to the
conservative 2030 band intended by Step-7, or an artefact? T9-13 will faithfully propagate whichever
it is.

### FINDING 2 — residential `r` is per-household, and 8.9–28.6 % of apartments exceed 1.5

The channel-level residential `R` (1.00–1.22) is the pool mean and is *not* what the injector
applies: `inject_residential` scales each apartment by its own drawn household
(`commercial_integration.py:1519-1524`). Spread of per-household `r_wd` against the Y2022 pool mean:

| scenario | min | p50 | p95 | max | % > 1.5 | % > 3.0 |
|---|---|---|---|---|---|---|
| Y2022 | 0.000 | 0.951 | 1.574 | 1.574 | 8.96 | 0.00 |
| B_cons | 0.000 | 1.213 | 1.574 | 1.574 | 24.10 | 0.00 |
| B_central | 0.000 | 1.246 | 1.574 | 1.574 | 28.04 | 0.00 |
| B_opt | 0.000 | 1.279 | 1.574 | 1.574 | 28.56 | 0.00 |
| Y2005 / Y2010 / Y2015 | 0.000 | 0.918–0.951 | 1.541–1.574 | 1.574 | 6.97–8.25 | 0.00 |

`r_max = 3.0` is never hit — the ceiling is `1/0.6355 = 1.574`, a household home 24/7. But roughly a
quarter of apartments get `Peak_Flow_Rate × >1.5` in the 2030 cells. Same plant-sizing caveat as
office, distributed across 47 objects instead of concentrated in one.

**Pre-registered failure mode.** 11 of 7175 households (0.15 %) have `mean_wd == 0` and 9 have
`mean_we == 0` (none have both). If one of them is drawn, its weekday flow fraction becomes
identically zero, `argmax` returns hour 0, and **`audit_dhw_shape_preservation` D2 fires** ("peak hour
p → 0"). Writing this down now so that if the audit FAILs after arm E it is not mistaken for a shape
bug: with `n_spaces` per tower in the low hundreds the probability of drawing at least one is not
small. D1 will *not* catch it — night share is `NaN` for an all-zero day and the NaN guard at
`:1176` tests the prototype, not the new value.

### 🔴 FINDING 3 — DEFECT: residential never takes the T9-13 path under `baseline_series`

Found by reading the call chain, not by running it. `inject_residential` gates T9-13 on

```python
if dhw_model.get("reference") == "prototype_people":     # commercial_integration.py:1508
```

but the shipped `DHW_MODEL_VOLUME_SCALED` declares `reference = "baseline_series"`
(`:1083`). The commercial path gates on **both** values (`_t9_13 = ... in ("prototype_people",
"baseline_series")`, `:1826-1827`); the residential path gates on one. So as the code stands today,
arm E would run **office/retail/hotel on T9-13 and residential on the refuted T9-11 rate model**
(`:1552-1576`, `apply_lighting_diversity(occ, floor, peak)`), silently.

It is worse than a plain no-op: `_proto_occ["residential"]` *is* populated and passed in as
`dhw_reference` (`:2130`), so the provenance would carry a T9-13 reference that nothing consumed, and
`audit_dhw_shape_preservation` filters on `model == "T9-13_volume_scaled"` (`:2147`) — the residential
records carry no `model` key, so they are excluded from the audit and the gate would report **PASS on
the commercial objects while residential silently ran the model that produced +40.78 %**. That is a
seventh vacuous-test shape: a gate that passes because the failing objects are outside its filter.

Fix required before arm E — one line at `:1508` to accept both references, plus a check that the
audit's applied-record filter cannot silently drop a channel. Not applied yet; awaiting the baseline
decision so both changes go into one build and one md5.

---

## The `R > 1.5` flag, measured against the real IDF — 2026-08-02

The user asked the right question and it overturned the premise: *is office DHW even material, and
shouldn't the office weekend already be low in the prototype?* Both halves were checked directly on
`Leg2_2-split/.../office_idfs_v242/CAN_MTL/TallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v242.idf`
(the pre-injection tower, read-only), 47 `WaterUse:Equipment` objects, schedules resolved through
`Schedule:Year → Week:Daily → Day:Interval`. Script: `dhw_probe.py` (scratchpad).

### How the tower's design DHW actually splits

| channel | n objects | Σ Peak_Flow_Rate (m³/s) | weekday daily volume | we/wd | share of weekday volume |
|---|---|---|---|---|---|
| hotel | 15 | 2.579e-3 | 67.36 | 0.998 | **63.0 %** |
| residential | 27 | 5.301e-4 | 24.01 | **1.000** | 22.5 % |
| office | 2 | 6.587e-4 | 11.95 | **0.311** | 11.2 % |
| retail | 2 | 3.785e-5 | 0.80 | 0.781 | 0.7 % |
| booster (unattributed) | 1 | 8.391e-5 | 2.72 | 1.017 | 2.5 % |

Office DHW is middling — not negligible, not dominant. Retail DHW is **0.7 %**, which is worth
carrying into how much weight the retail DHW result deserves. The hotel laundry alone
(`Laundry Service Water Use 30.6gpm 180F`, 1.931e-3 m³/s) is 75 % of hotel design flow.

### The prototype office DHW schedule already has the quiet weekend

`OfficeLarge BLDG_SWH_SCH`:

```
wd  max=0.570  mean=0.2100   0 0 0 0 0 0 .07 .19 .35 .38 .39 .47 .57 .54 .34 .33 .44 .26 .21 .15 .17 .08 .05 .05
we  max=0.145  mean=0.0652   0 0 0 0 0 0 .07 .07 .10 .12 .12 .15 .13 .14 .10 .09 .09 .06 .06 .06 .06 .08 .04 .04
```

we/wd = 0.311. Stable weekday, quiet weekend, exactly as expected. Residential is the opposite —
**flat, we/wd = 1.000**, no weekend structure at all, so for residential the volume lever is the only
thing that can move DHW.

### 🔴 The prompt's premise is FALSE on this stock, and is struck

The prompt says *"a large `R` means the water heater is resized, which mixes a plant-sizing effect
into what is meant to be a schedule lever"*. Measured: the tower's six `WaterHeater:Mixed` objects are
**hard-sized, not autosized** — tank `1.13562 m³`, capacity `87921.3 W`, plus one 0.0227 m³ / 8000 W
booster. Nothing in the SWH plant responds to `Peak_Flow_Rate`.

And the `R` in `Peak_Flow_Rate' = P·R` is exactly cancelled by dividing the shape by `R`:

```
flow(t) = Peak_Flow_Rate' · f_new(t) = (P·R) · (s(t)·r_d/R) = P · s(t) · r_d
```

`R` does not appear. Peak instantaneous flow as a fraction of `P`, office, Y2022 reference,
B_central (`r_wd = 0.740`, `r_we = 2.079`):

| day type | prototype max | × r | result |
|---|---|---|---|
| weekday | 0.570 | 0.740 | **0.422** |
| weekend | 0.145 | 2.079 | **0.301** |

Both **below** the prototype's own weekday peak of 0.570. Nothing is oversized, nothing goes unmet,
and the weekend never overtakes the weekday. The `R > 1.5` flag is real arithmetic but has **no
physical consequence on this stock**. It would matter on an IDF with an autosized SWH plant; that
condition is now recorded as the thing to re-check if the stock ever changes.

### DECISION (user, 2026-08-02): baseline = `Y2022`; office `R` = accept and report

Both confirmed by the user. No gate, band or threshold was touched.

Pre-registered consequence, computed before the run (5 weekday / 2 weekend day weighting on the
prototype volumes 11.95 wd / 3.71 we):

| bundle | r_wd | r_we | predicted annual office DHW change |
|---|---|---|---|
| B_cons | 0.818 | 2.493 | **+0.3 %** |
| B_central | 0.740 | 2.079 | **−11.2 %** |
| B_opt | 0.664 | 1.731 | **−21.8 %** |

`B_cons` landing flat *despite* a 2.5× weekend ratio is the sharpest of the three — it is not a
number that could be produced by accident, and it is stated here before arm E runs.

---

## 🔴 FINDING 4 — BLOCKER. The scalar reference double-counts the day-type asymmetry

Found while filling in the Y2022 numbers, i.e. by trying to use the interface rather than by reading
it. `commercial_integration.py:1840` builds the baseline reference as **one scalar held flat across
both day types**:

```python
_proto_occ[_ch] = {"wd": [_fv] * 24, "we": [_fv] * 24}
```

and `apply_dhw_volume_scaling` then computes `r_wd = mean(occ_wd)/_fv`, `r_we = mean(occ_we)/_fv`
against that same `_fv`. Two consequences, and the second is disqualifying:

**1. The baseline scenario is not a no-op.** A no-op needs `r_wd = r_we = 1`, i.e.
`mean(occ_wd) = mean(occ_we) = _fv`. For office Y2022 those are `0.2530` and `0.0651` — no scalar
satisfies both. With a 5/2-weighted weekly mean `_fv = 0.19932`, the *baseline year itself* would come
out `r_wd = 1.269`, `r_we = 0.327`. The reference scenario would move.

**2. It applies our occupancy's weekday/weekend asymmetry on top of the prototype's.** With a common
`_fv`, `r_we / r_wd = mean(occ_we)/mean(occ_wd) = 0.0651/0.2530 = 0.257` for office. The prototype
schedule *already* carries a we/wd asymmetry of `0.311` (measured above). T9-13 would multiply them:
`0.311 × 0.257 = 0.080`. Office weekend DHW would collapse to 8 % of weekday instead of the intended
31 %, and it would be reported as an occupancy result. The whole point of T9-13 is that the intra-day
and inter-day-type *shape* comes from the prototype and only the *volume* comes from occupancy; a
scalar reference violates that on the day-type axis.

Note this makes the Part-2 table above the **correct** target semantics, not the code's: it was
computed with day-type-matched ratios (`r_wd = twd/bwd`, `r_we = twe/bwe`), which is what gives the
baseline `r = 1.000` exactly and leaves the prototype's day-type asymmetry untouched.

**Fix:** `reference_occ_mean` must accept a per-day-type mapping
`{channel: {"wd": x, "we": y}}`, with the scalar form kept working (and meaning "flat", for an IDF
where that is genuinely intended). Applied together with the `:1508` residential-gate fix so arm E
carries one injector md5.

### Test-suite gap found at the same time

`test_t9_13.py`, the file the 22/22 primitive-test PASS at line 2193 is attributed to, **does not
exist anywhere in the repo**. It was written to a scratchpad in the 2026-08-01 session and lost with
it. So the certification of T9-13 is currently an unreproducible claim in this document. It is being
rewritten into the repo as a tracked file rather than re-created in a scratchpad, and extended to
cover FINDING 3 and FINDING 4.

---

## Build applied — 2026-08-02, injector md5 `56d6e324`

Four changes, one build, one md5, all in `eSim_bem_utils/commercial_integration.py`:

| # | site | change |
|---|---|---|
| 1 | `:1094-1112` | `reference_occ_mean` filled with the **Y2022** per-day-type means (user decision) |
| 2 | `:1876-1912` | reference builder accepts `{channel: {"wd": x, "we": y}}`; bare scalar still works and is now labelled `FLAT` in the provenance (FINDING 4) |
| 3 | `:1543` | residential T9-13 gate accepts `baseline_series`, not just `prototype_people` (FINDING 3) |
| 4 | `:1198-1257`, `:2192` | audit gains **D6** — a channel requested in `dhw_model["channels"]` that contributes 0 audited objects is a FAIL. `expect_channels` is the intersection with the channels the scenario actually injects, so `DELIBERATE_CHANNEL_EXCEPTIONS` (hotel in Y2005/Y2010/Y2015) stays legal |

**Shipped reference (Y2022, `mean_wd` / `mean_we`):**

```
office       0.253013 / 0.065079     retail       0.310422 / 0.261454   (PR=QC)
hotel        0.357275 / 0.368193     residential  0.635497 / 0.732074
```

Retail and hotel are PR-dependent and these are the QC values; `reference_occ_mean` is one national
map for the whole campaign, so the **CLG cells do not get `r = 1.000` in the baseline year** — they
get the AB/QC offset (retail AB `r_wd = 1.145`, hotel AB `r_wd = 1.014`). Deliberate: one denominator
keeps the city axis comparable, where a per-PR reference would make `r` mean something different in
each city. Recorded in the code comment so nobody reads it as a bug.

**Arms A–D are unaffected.** `DHW_MODEL_PER_CAPITA` (`:911`) carries no `"reference"` key, so
`.get("reference")` is `None`, which is not in `("prototype_people", "baseline_series")` — the
residential gate change cannot reach arm D's path. `expect_channels` defaults to `()`, so the audit's
behaviour for every existing caller is byte-identical.

**`eSim_tests/test_t9_13.py` — 40/40 pass** (`py -3 eSim_tests/test_t9_13.py`, exit 0). Tracked in the
repo this time. The suite uses the *real* `OfficeLarge BLDG_SWH_SCH` profile rather than a toy one.
Every audit check is tested in its failing direction: D0, D1, D2, D3, D4, D5, D6 and the empty-list
case each have a test that makes them fire. T29 is the one that matters most — it shows the same
input **passes** without `expect_channels` and **fails** with it, which is the proof that D6 closes
FINDING 3's hole rather than a check that was already implied.

T39/T40 pre-register the all-zero-occupancy household: `r_wd = 0` produces an identically zero
weekday schedule and the audit fires **D2**. If arm E returns D2 violations naming
`MXU_Residential_DHWv2_*`, that is this known edge case (11/7175 households), not a shape bug.

One test bug was found and fixed during the run, not carried: T36 initially failed because the test
rebound `ref` to the office entry and then iterated `ref.values()` over two floats. The config was
correct; the assertion was not.

### 🔴 FINDING 5 — the driver did not know `volume_scaled`

The handoff prompt's Task 3 says arm E is `--lighting-model calibrated_v2 --dhw-model volume_scaled`.
It was not runnable: `3rdJ_08D_campaign_driver.py:352-360` accepted only `none` and `per_capita` and
would have exited 1 on all 56 tasks. Now wired (`:350-378`, driver md5 `8164c10b`), with two guards
that exist because of how this project fails:

- **Empty `reference_occ_mean` → `[FAIL]` and exit 1, before anything runs.** Without it, every
  `WaterUse:Equipment` object reports `dhw_unresolved` and the arm becomes a silent whole-building
  no-op that still produces 56 plausible result directories. That is the arm-D shape exactly.
- **A flat scalar reference → `[WARN]`** naming FINDING 4, so the double-count cannot re-enter
  quietly through a hand-edited config.

`--dhw-model per_capita`'s help text now states it is REFUTED and kept only to reproduce arm D.

### Arm E submit script

`3rdJ_08D_campaign_speed_armE.sh` — 56 cells, `--array=0-55%20`, `-t 7-00:00:00`, out
`campaign/out_E_dhwvol`, modelled on the A/B script. Lighting is pinned to `calibrated_v2`, i.e.
**arm C's exact setting**, so `E − C` moves one variable. The script echoes the injector md5 into
every task log so the artefact records which build produced it.

### Status: local work COMPLETE, cluster work NOT STARTED

Done locally: reference table, baseline decision, four injector fixes, driver wiring, submit script,
40/40 tests. Not done: scp, pre-flight validation, **the falsifiable predictions**, the array, the
aggregate. The predictions must be written into this document *before* the `sbatch`, not after — the
office numbers (+0.3 % / −11.2 % / −21.8 %) are already recorded above and are the start of that
list, not the whole of it.

## Upload + pre-flight submitted — 2026-08-02, job `1171322`

Five files to `/speed-scratch/o_iseri/step8_4split/campaign/`, all verified byte-size-identical to
their local originals (md5 is asserted inside the job itself, not on the login node):

`repo/eSim_bem_utils/commercial_integration.py` · `repo/eSim_tests/test_t9_13.py` (new dir) ·
`repo/.../Step8_docs/3rdJ_08D_campaign_driver.py` · `.../3rdJ_08D_campaign_speed_armE.sh` ·
`validate_E.sh`

**`validate_E.sh` is built so it can fail, and the failing values are arm D's own artefact.** Arm D's
smoke provenance (`smoke_D/campaign_39a6e24e/B_central__Tall__MTL`) reads
`n_dhw_applied=45  n_dhw_excluded=2  n_dhw_unresolved=0`. Arm E must read **47 / 0 / 0** — the two
`LAUNDRY` objects move from *excluded* to *applied*, because T9-13 never touches intra-day shape and
so no longer needs to exclude a batch process. If the script prints PASS while showing 45/2, it
tested nothing. Also asserted, each with a stated expected value:

- injector md5 `== 56d6e324…` **from the file Python actually imported** (the 2026-07-31 shadowing
  near-miss), and a FATAL if `reference_occ_mean` is empty or holds a flat scalar
- the 40 primitive tests, re-run on the cluster copy rather than trusted from here
- `t9_13_audit_pass=True` with `n_audited == 47`
- a `t9_13_reference` line **and** at least one emitted schedule for **each of the four channels** —
  this is D6 enforced on the real artefact, the thing that would have caught FINDING 3
- at least one `noop=False` (cell 3 is `B_central`; if everything is a no-op the lever is dead)
- zero `t9_13_VIOLATION` lines
- lighting still `open_hours_mix` at `k_open=0.6`, i.e. **arm C's exact setting** — otherwise
  `E − C` is not a pure DHW delta

The 56-run array is **not** submitted. Next: read `logs/validate_E_1171322.out`, then write the
falsifiable predictions here, then `sbatch 3rdJ_08D_campaign_speed_armE.sh`.

### Pre-flight result — `1171322` COMPLETED 2026-08-02 10:54, VALIDATION PASS

| check | expected | measured |
|---|---|---|
| imported injector md5 | `56d6e324…` | `56d6e3241df20d45f3831770dbcba5a2` ✅ |
| primitive tests on the cluster copy | 40/40 | **40/40** ✅ |
| cells with unresolved inputs | 0/56 | **0/56** ✅ |
| `n_dhw_applied` / `excluded` / `unresolved` | **47 / 0 / 0** (arm D: 45 / 2 / 0) | **47 / 0 / 0** ✅ |
| `t9_13_audit_pass`, `n_audited` | True, 47 | **True, 47**, counts `D1..D6 all 0` ✅ |
| reference + emitted schedule per channel | all 4 | all 4 ✅ |
| lighting | `open_hours_mix`, `k_open=0.6` | identical to arm C ✅ |

The two `LAUNDRY` objects moved from *excluded* to *applied* exactly as predicted — this is the check
that arm D's own artefact would have failed.

**Independent confirmation of the offline reference table.** The injector computed its own `r` from
the shipped reference; those numbers were never given to it. `B_central__Tall__MTL` (PR=QC):

| channel | predicted `r_wd` / `r_we` (offline table) | measured in the provenance |
|---|---|---|
| office | 0.7398 / 2.0788 | `0.739834 / 2.078756` |
| retail | 0.6819 / 0.7292 | `0.68192 / 0.72918` |
| hotel | 1.1244 / 1.1244 | `1.124391 / 1.124393` |
| residential | per-household, ceiling `1/0.635497 = 1.5736` | max drawn `r_wd = 1.573572` |

Two things worth recording honestly rather than quietly enjoying:

- **`D1` has no discriminating power on office or retail.** Their prototype DHW night share is
  identically `0.0`, so `0.0 → 0.0` cannot fail. D1 does bite on hotel (`0.122222`) and residential
  (`0.035771`), and D2/D3/D4 bite everywhere. Stated so the "counts all zero" line is not read as
  six independent confirmations when for two channels it is four.
- The residential per-household spread is live in the artefact: drawn `r_wd` runs `0.458958` to
  `1.573572` in a single cell. The pool mean is not what any individual apartment gets.

---

## Arm E — PREDICTIONS, written before the array was submitted

Baseline for every comparison is **arm C** (`agg_C_lm3v2`), identical in every respect except that
its `WaterUse:Equipment` objects keep the prototype flow-fraction schedule. `E − C` is therefore the
pure T9-13 effect. Each prediction states what result would refute it.

**P1 — the identity T9-11 violated.** In `dhw_hourly.csv` for `B_central__Tall__MTL`, residential
night 00–05 share stays at the prototype's **0.0358** (arm D drove it to 0.3286) and the peak draw
hour stays **06:00** (arm D moved it to 04:00). `audit_dhw_shape_preservation` returns
`pass=True, n_audited=47` on **56/56** cells with zero violations.
*Refuted by:* any night share above 0.05, any peak-hour move, or any `t9_13_VIOLATION` line — with
one pre-registered exception: a drawn household with `mean_wd == 0` (11 of 7175) yields an all-zero
weekday schedule and fires D2 legitimately. That exception is admissible **only** if the violating
object name matches `MXU_Residential_DHWv2_*` and its `r_wd` is `0.0`.

**P2 — office DHW stops being flat, with sign and magnitude fixed in advance.** Arm C reports office
DHW `12.19 kWh/m²` in every column to 2 dp. Arm E, relative to arm C: **B_cons +0.3 %,
B_central −11.2 %, B_opt −21.8 %**, tolerance ±3 pp. Derived from the prototype's own 11.95 wd /
3.71 we daily volumes at 5/2 day weighting and the measured `r`s — not fitted to anything.
*Refuted by:* office DHW still flat to 2 dp; or B_cons outside ±3 %; or the ordering
cons > central > opt breaking. B_cons is the sharp one: it must come out **flat despite
`r_we = 2.493`**, because the weekday fall and the weekend rise nearly cancel. A model that merely
"scales DHW with occupancy" cannot produce that.

**P3 — hotel DHW now moves, and this is the direct reversal of arm D's P5.** Laundry is no longer
excluded, and hotel `r_wd ≈ r_we ≈ 1.1244` is nearly day-type-uniform, so hotel DHW rises
**+12.4 %** (±2 pp) in `B_central`. Arm D reported hotel DHW **−8.7 %** with laundry frozen.
*Refuted by:* hotel DHW moving less than +5 %, which would mean the laundry objects are still not
scaling despite `n_dhw_excluded=0`. This is the prediction most able to fail, and hotel is 63.0 % of
the tower's design DHW volume, so it also dominates the whole-building number.

**P4 — residential moves with occupancy and does NOT repeat +40.8 %.** Pool means give
`r_wd = 1.210`, `r_we = 1.075` for `B_central`, so residential DHW rises **+8 % to +18 %**.
*Refuted by:* a rise above +25 % (the T9-11 signature), a fall, or any residential night-share
change. Caveat stated in advance: `r` is per-household and the 27 drawn apartments are a sample of
the pool, so the realised mean may sit off the pool mean; the band is wide for that reason and
narrowing it after the fact would be cheating.

**P5 — non-DHW end uses move only through thermal coupling, and the bound is stated first.**
`|Δ| < 0.5 %` on every non-DHW end use in every channel. The mechanism is the gas water heaters'
tank and distribution losses landing in their zones; there is no path from a flow-fraction schedule
to lighting or plug loads.
*Refuted by:* any non-DHW end use moving ≥ 0.5 %, or any lighting/equipment change at all outside
that coupling — which would mean T9-13 touched something it must not.

**P6 — integrity, checked before any delta is quoted.** Identical 56 cell tags across arms C and E,
`attribution_closed=True` in all 56, and `max |area_E − area_C| = 0 m²`.
*Refuted by:* any of the three failing, in which case no `E − C` number is reported at all.

**What is NOT predicted, deliberately.** Whether any EUI gate changes verdict. Office is ~15 kWh/m²
short on the standalone-prototype band before occupancy enters, and DHW is 11.2 % of that channel's
water volume; nothing here is expected to rescue `S9-EUI-office`. If a gate does flip, that is a
result to explain, not a target that was aimed at.

**Array submitted after this section was written:** job `1171323`, `--array=0-55%20`,
`out_E_dhwvol`, submitted 2026-08-02 at 11:0x.

### `agg_armE.sh` — staged while the array runs

Uploaded to `campaign/agg_armE.sh`, built from `agg_armC.sh`, ready to fire the moment the array
lands. Two deliberate differences:

1. **The campaign directory is discovered, not hard-coded**, and the job stops with FATAL unless it
   resolves to exactly one directory whose name is `campaign_56d6e324`. Pre-flight `1170768` died on
   a hand-written glob that assumed one directory level too few, and the *older* validate script
   carried the same bug and never noticed — because it asserted nothing. It also refuses to
   aggregate unless all **56** result dirs exist, so a partial arm cannot be silently averaged.
2. **P1 is swept over all 56 cells inside the job**, not left as 56 files to read one at a time
   afterwards: counts of `t9_13_audit_pass=True`, `n_audited=47`, `n_dhw_excluded=0`,
   `n_dhw_unresolved=0`, `t9_13_VIOLATION` lines and `clipped=True`. If any violation exists it
   prints every one, so the pre-registered residential zero-occupancy exception (`MXU_Residential_
   DHWv2_*` with `r_wd=0.0`) can be told apart from a real shape bug rather than assumed to be it.

It also dumps the distinct `r_wd`/`r_we`/`R` triples actually applied per channel across all 56
cells, which is the direct cross-check of the offline reference table at campaign scale.

### Scoring written BEFORE the results existed — `3rdJ_09E_score_armE.py`

Authored 2026-08-02 while `1171323` was still running, i.e. **before any arm E result existed**.
That ordering is the whole point: the thresholds in the file cannot have been chosen to fit the
data, because the data did not exist when they were written. The file says so in its own docstring
and ends with "A MISS IS RECORDED, NOT REPAIRED."

It scores P1–P6 mechanically and **refuses to quote any `E − C` delta if P6 fails** on cell tags.
Two decisions fixed in advance rather than after seeing numbers:

- **P5 materiality rule.** A percentage on a tiny end use is noise, so an end use is scored only if
  it is ≥ 1 % of its channel's total energy in arm C. Smaller ones are reported and the count of
  skipped ones is printed — chosen now so it cannot become a way to drop an inconvenient mover.
- **P1 is split.** Its 56-cell half lives in `agg_armE.sh` (provenance sweep); its hourly half needs
  a `dhw_hourly.csv` pair and reports **UNTESTABLE** if not supplied. UNTESTABLE counts as a failure
  of the run, never as a pass — same rule as the empty-audit case.

**The scorer has been seen failing.** Run against itself (`--arm-c X --arm-e X`, i.e. "arm E changed
nothing"), it gives **2 PASS / 3 FAIL / 1 UNTESTABLE**: P6 and P5 pass (identical inputs really are
identical and really do move 0 %), and **P2, P3, P4 fail** — exactly the predictions that require
arm E to have done something. A scorer that returned all-PASS on a null comparison would be the
eighth vacuous test on this project.

Incidentally that run re-confirms the frozen-DHW baseline from a third direction: in the old
aggregate, office DHW is `6489.37 / 6489.28 / 6489.46 GJ` across cons/central/opt — a spread of
**0.003 %**, which is the "12.19 kWh/m² in every column" figure seen in energy units.

### Scratchpad scripts moved into the repo

The same failure that lost `test_t9_13.py` was about to repeat with two more files, so both are now
tracked in `Leg3_4-split/Step9_docs/`:

| was (scratchpad, would have been lost) | now |
|---|---|
| `t913_reference_table.py` | `3rdJ_09E_reference_table.py` — builds the per-channel reference table for **every** candidate baseline |
| `dhw_probe.py` | `3rdJ_09E_dhw_prototype_probe.py` — reads the prototype tower's 47 `WaterUse:Equipment` objects and their resolved day-type profiles; the source of the 63/22.5/11.2/0.7 % split and the `we/wd = 0.311` office figure |

Every number quoted in the two sections above is now re-derivable from the repo rather than from a
session that no longer exists.

---

## 🔴🔴 FINDING 6 — the 2022 and 2030 office products are built from DIFFERENT POPULATIONS

Found while waiting on `1171323`, by chasing the office `r_we ≈ 2` that the reference table exposed.
It is a **Step-7 issue, not a T9-13 issue**, and its reach is much wider than DHW.

### The code

`3rdJ_07_aug_to_bem_4split.py`, two call sites of the same builder:

```python
# 2022 -- from the augmented STOCK                                    (:869)
office_out = build_office_multiplier(stock, "observed", lookup)

# 2030 -- from the D2030 PROJECTION POOL, directly                    (:964-967)
for band in BANDS:
    band_slice = d30[d30["BAND"] == band].copy()
    part = build_office_multiplier(band_slice, band, lookup)
```

The residential product **immediately above** the 2030 office block does use the assembled stock
(`df_band = assemble_2030(office_band, ...)`, `:953`). So the two channels that the code comments
describe as *"Residential + Office (share the office/WFH BAND axis)"* are, for 2030, built from two
different frames: residential from the stock with 2030 activity columns drawn into it, office from
the raw 2030 pool.

### The tell, in the shipped files' own `n_persons` column

`Office_Knowledge`, `DAYTYPE = {1: Weekday, 2: Weekend, 3: Weekend}` (`:155`):

| product | source | `n` weekday | `n` weekend | ratio |
|---|---|---|---|---|
| `office_..._2022.csv` observed | augmented stock | 3383 | 1365 | **2.48 : 1** |
| `office_..._2015.csv` observed | historical stock | 4324 | 4287 | 1.01 : 1 |
| `office_..._2030.csv` — all three bands | D2030 pool | **1928** | **3856** | **1 : 2** |

`3856 = 2 × 1928` exactly, and the same counts appear for `conservative`, `hybrid` and
`fullyhybrid`. With Sat and Sun both mapping to Weekend, that means strata 1, 2 and 3 each hold
exactly 1928 office-employed persons — the 2030 pool is **balanced by construction**, i.e. each
person carries a diary for every day type. The observed GSS stock is not: a respondent has one diary
day, so weekend office workers are whoever happened to be surveyed on a weekend.

### What this does and does not contaminate

- **Within-2030 comparisons are CLEAN.** `cons` vs `hybrid` vs `fullyhybrid` all come from the same
  1928/3856 pool, so the WFH lever — the headline office result, `−16.2 % → −10.5 %` after T9-10 —
  compares like with like. Nothing above is challenged.
- **Across-era office comparisons are NOT.** Any 2022→2030 or historical→2030 office statement is
  partly a difference of populations and estimands, not only of behaviour. That includes the office
  `r_wd = 0.740 / r_we = 2.079` now driving T9-13, the `S9-LONG-*` era gates for office, and the
  plain-language claim "office presence falls under WFH" when stated against the observed year.
- The weekday direction survives inspection (2030 weekday 0.207/0.187/0.168 all *below* 2022's
  0.253, as WFH predicts). It is the **weekend** that inverts: 0.065 observed → 0.113–0.162
  projected, in all three bands, with the weekend peak hour identical (14 h) in both.

### What I did NOT do, deliberately

I did not rebuild the office product from `assemble_2030`'s output to "see if the weekend drops".
That would silently change a frozen Step-7 design and every downstream artefact, mid-campaign, on my
own initiative. **The honest next step is a measurement, not a fix**: build the office multiplier
both ways on the same band and report the two weekend means side by side. If they agree, the two
sources are interchangeable and this is a documentation matter. If they diverge, the 2030 office
product is measuring pool composition and the era axis needs re-specification — a manuscript-level
decision, and the user's.

Nor is it established that the projection's weekend behaviour is *wrong*. A balanced pool giving
every worker a projected weekend diary is a legitimate design; it is simply not the same estimand as
the observed year's, and the two are currently subtracted from each other as if they were.

**Impact on arm E: none mechanically.** T9-13 propagates whatever the office product says, and the
predictions recorded above are stated against arm C, which carries the identical office series. But
if P2 lands, the office DHW result must be reported with this caveat attached, not as a clean
behavioural finding.

### FINDING 6 MEASURED — the sources DISAGREE, and the era jump is mostly a frame effect

`3rdJ_09E_office_source_probe.py` (read-only; imports the real Step-7 `build_office_multiplier` and
`assemble_2030` rather than re-implementing them, so it measures the pipeline's logic, not mine).
It builds the office multiplier **both ways on the same band** and compares. All three bands:

| band | source | `n_wd` | `n_we` | `mean_wd` | `mean_we` | weekend vs 2022 |
|---|---|---|---|---|---|---|
| conservative | **pool (shipped)** | 1928 | 3856 | 0.2070 | 0.1622 | **×2.49** |
| conservative | stock (residential path) | 3383 | 1365 | 0.1228 | 0.0803 | ×1.23 |
| hybrid | **pool (shipped)** | 1928 | 3856 | 0.1872 | 0.1353 | **×2.08** |
| hybrid | stock (residential path) | 3383 | 1365 | 0.1064 | 0.0716 | ×1.10 |
| fullyhybrid | **pool (shipped)** | 1928 | 3856 | 0.1680 | 0.1126 | **×1.73** |
| fullyhybrid | stock (residential path) | 3383 | 1365 | 0.1064 | 0.0580 | **×0.89** |
| 2022 observed | stock | 3383 | 1365 | 0.2530 | 0.0651 | — |

Pool vs stock **on the same band**: weekday **+58 % to +76 %**, weekend **+89 % to +102 %**. The
stock-built version reproduces the 2022 product's own frame exactly (`n = 3383 / 1365`), which is
what makes it the apples-to-apples comparison.

**So the ×2 weekend jump that produced T9-13's office `r_we = 2.079` is very largely a frame
effect.** Built through the same path as the 2022 product and as the 2030 *residential* product, the
weekend rise is ×1.10 for hybrid and **falls to ×0.89 for fullyhybrid** — i.e. under the fully
hybrid scenario weekend office presence goes *down* relative to today, which is the physically
sensible reading. The shipped product says it goes up 73 %.

**The WFH lever survives in both frames, with a different magnitude.** Weekday cons → opt:
pool `0.2070 → 0.1680` = **−18.8 %**; stock `0.1228 → 0.1064` = **−13.4 %**. Direction and ordering
are preserved, so the within-2030 lever result is not overturned — but it is ~29 % smaller in the
consistent frame.

**Nobody gains a gate from this, which is worth saying explicitly.** The stock frame gives *lower*
office occupancy everywhere, so it lowers office internal gains and would push `S9-EUI-office`
**further below** its 100 floor, not towards it. Whichever frame is chosen, it cannot be chosen
because it rescues a FAIL — there is nothing to rescue in that direction.

**One observation flagged, not interpreted:** under the stock frame `hybrid` and `fullyhybrid` give
an identical weekday mean to 4 dp (`0.1064` both) while their weekends differ (0.0716 vs 0.0580).
That may be a rounding coincidence or it may mean the band axis is weak on weekdays in that frame.
It needs its own check before anyone relies on it.

### What this changes, and what it does not

- **Unchanged:** everything computed *within* the 2030 family — the T9-10 office `n=3` calibration,
  the WFH lever's existence and ordering, arms A–E's internal comparisons, and all of arm E.
- **Now carries a caveat:** every office statement that crosses the era boundary — 2022→2030 and
  historical→2030 — including T9-13's office `r`, the `S9-LONG-*` office gate, and the narrative
  sentence "office presence falls under WFH" when said against the observed year.
- **Still not fixed, deliberately.** Repointing `:964-967` at `assemble_2030`'s output is a one-line
  change that would alter a frozen Step-7 product and every downstream artefact including four
  closed campaigns. That is a manuscript-level decision and it is the user's, not mine. The
  measurement is now on file so the decision can be made on numbers.

### The historical half — measured, and it NARROWS the finding

There are in fact **three** frames on the office era axis, not two. The historical years are built as
`build_office_multiplier(complete_day_types(assembled), ...)`
(`3rdJ_08A_gen_historical_products_4split.py:237,247`), while Y2022 is built on the **raw** stock
with no day-type completion (`3rdJ_07:869`). Three constructions:

| product | frame | `n_wd` / `n_we` |
|---|---|---|
| Y2005 / Y2010 / Y2015 | stock → `demo_assemble` → `complete_day_types` | 4324 / 4287 (~1:1) |
| Y2022 | raw stock | 3383 / 1365 (2.48:1) |
| 2030 bands | D2030 pool, direct | 1928 / 3856 (1:2) |

Before assuming that makes the historical panel suspect too, I applied **both** frames to the *same*
2022 data (`--era`), which isolates frame from year:

| frame applied to the same 2022 data | `n_wd` | `n_we` | `mean_wd` | `mean_we` |
|---|---|---|---|---|
| raw stock (= shipped Y2022) | 3383 | 1365 | 0.2530 | 0.0651 |
| completed (= historical years) | 4324 | 4287 | 0.2533 | 0.0671 |

**Weekday +0.10 %, weekend +3.07 %.** The completed frame reproduces the 2015 file's own counts
exactly (4324 / 4287), confirming the identification — and the means barely move. `complete_day_types`
donor-draws to fill missing day types, so it changes *n* without changing the *mean*: it is
behaviour-preserving.

**So the historical ↔ 2022 office comparison is CLEAN**, and `S9-LONG-office` across
2005/2010/2015/2022 is not challenged. The defect is specific to the **2030 pool bypassing
`assemble_2030`**, and nothing else. That is a narrower and much better-supported claim than "the era
axis has three frames", which is what the counts alone would have suggested — and it is the opposite
of the direction I expected when I started the check.

---

## USER DECISIONS — 2026-08-02, all five open items ruled on

| # | item | decision |
|---|---|---|
| 1 | 2030 office frame (FINDING 6) | **FIX.** Every cycle's schedules must come from the same sample pool; the current split is a conflict, not a limitation. Rebuild and re-issue the office product. |
| 2 | `S9-EUI-office` | **Investigate how to resolve it** — manager's call on method, Progress Log updated as it goes. |
| 3 | Hotel gate | **SPLIT** by geometry. |
| 4 | Retail NECB proxy | **FREEZE and DOCUMENT** as a stated limitation. |
| 5 | Leg-2 office EUI 1.706× | **PUBLISH THE CORRECTION**; Leg-2 stays read-only. |

### 🔴 The collision between decisions 1 and 2, stated before either is acted on

Decision 1 makes decision 2 **harder, not easier**, and this must be on record before any work starts
so that nobody later reads a worsening number as a regression.

Fixing the office frame moves the 2030 office occupancy *down* — weekday `0.1872 → 0.1064`,
weekend `0.1353 → 0.0716` for the central band. Lower occupancy means lower internal gains, which
means office EUI **falls further below** the 100 floor it already misses at ~82. So the correct fix
to the frame will make `S9-EUI-office` fail *worse*. There is no version of decision 1 that helps
decision 2, and I will not present it as if there were.

### What "resolve the failure" can and cannot mean here

The instruction is that a research paper cannot present a failing result. Taken literally against a
band, that would mean widening `[100, 200]` until office fits — which is the one move this project
has banned all the way through, and the reason six vacuous tests were caught rather than shipped. So
I am reading it the only way that is compatible with the rest of the work: **the failure must be
genuinely resolved, not made to disappear.** Three routes exist, and only the third is honest here:

1. *Fix the model until office rises into band* — ruled out by measurement. The pre-injection
   `Default_NECB` office is already **85.29** against a floor of 100, so ~15 of the 22 kWh/m² gap
   exists before any occupancy model touches the building. No occupancy work can close it, and
   decision 1 widens it.
2. *Widen or drop the band* — banned, and it would invalidate the gate rather than satisfy it.
3. **Re-derive a band that is valid for the object being measured.** `[100, 200]` is sourced from
   **standalone** office prototypes; what is being scored is an office *channel stacked inside a
   mixed-use tower*, sharing a centrally-sized plant and with 3 of 6 façades interior. Those are not
   the same building, and comparing one to the other is a category error that happens to look like a
   FAIL. This is exactly the reasoning the user just approved for the hotel gate in decision 3.

Route 3 is the plan, with the same guard the hotel split gets: **the new expectation must be sourced
independently from the literature, before looking at what our number is.** A band fitted to our own
82 would be decision 2 solved by cheating, and would be worse than leaving the FAIL standing. If no
defensible channel-level source exists, the result is reported as a measured limitation with the
mechanism attached — which is a finding, not a failure.

### Sequencing — arm E is NOT cancelled

## 🔴🔴 CORRECTION — FINDING 6's headline number was WRONG. My control was invalid.

Written 2026-08-02, immediately on discovering it, before any product was written to disk.

**What I claimed:** that pool-vs-stock was worth "+58…+76 % weekday, +89…+102 % weekend", and that
the ×2 weekend jump from 2022 to 2030 was "very largely a frame effect".

**What is actually true:** that comparison used `assemble_2030()` as the "correct" frame, and
`assemble_2030()` is not a valid frame for the office channel at all. It draws a **random** pool row
per stock row within `DDAY_STRATA` and copies its diary block across, with no occupational matching.
Measured:

| frame | office-employed WRK mean | ALL persons WRK mean |
|---|---|---|
| real stock (2022 diaries) | 0.254911 | 0.245461 |
| `assemble_2030(hybrid)` | 0.109950 | **0.110243** |
| `assemble_2030(fullyhybrid)` | 0.104492 | **0.103421** |

In the real data office workers work more than the population. After `assemble_2030` the office
subset and the whole population are **identical to three decimals** — the occupation signal is gone,
because office workers were handed random people's diaries. So the ~−40 % I attributed to "frame"
was mostly dilution in my own control, not a defect in the shipped product.

**The guard caught it before anything was written.** `3rdJ_07R_regen_office_2030.py` refuses to write
unless band monotonicity survives; the refit gave `hybrid` and `fullyhybrid` an identical weekday
mean (0.1064) and it exited 1. That is the 0.1064 coincidence flagged earlier as "needs its own
check" — it was not a coincidence, it was the signal being destroyed.

### The valid comparison, and the real answer

The D2030 pool carries `NOCS`, `LFTAG`, `AGEGRP`, `SEX` and `DDAY_STRATA`, so an
**occupation-matched** assembly onto the stock frame is possible — the same idea the historical years
use (`demo_assemble`, `3rdJ_08A:180`), with a tier ladder adapted to the columns the 2030 pool has
(it has no `MARSTH`/`HHSIZE`, which is why `demo_assemble` cannot be reused verbatim):

```
tiers: [AGEGRP,SEX,LFTAG,NOCS] -> [AGEGRP,SEX,NOCS] -> [NOCS,LFTAG] -> [AGEGRP,SEX,LFTAG] -> []
       each + DDAY_STRATA
```

`Office_Knowledge`, stock frame (`n = 3383 / 1365`, i.e. the 2022 frame), monotonic on **both** day
types:

| band | shipped (pool) wd / we | NOCS-matched stock wd / we | frame effect |
|---|---|---|---|
| conservative | 0.2070 / 0.1622 | 0.2198 / 0.1694 | +6.2 % / +4.4 % |
| hybrid | 0.1872 / 0.1353 | 0.2025 / 0.1378 | +8.2 % / +1.8 % |
| fullyhybrid | 0.1680 / 0.1126 | 0.1759 / 0.1044 | +4.7 % / −7.3 % |

Weekend ratio vs 2022: shipped ×2.49 / ×2.08 / ×1.73 → matched **×2.60 / ×2.12 / ×1.60**.

**So the ×2 weekend rise is REAL behaviour in the 2030 diaries, not a frame artefact.** The frame
inconsistency is genuine and still worth fixing — the user's requirement that every cycle come from
the same sample pool stands on its own — but it is worth **±8 %**, not ±60–100 %.

### Three earlier statements are hereby struck

1. "The ×2 weekend jump is very largely a frame effect." **False.** It is behavioural.
2. "Fixing the frame moves office occupancy down and makes `S9-EUI-office` fail worse." **False** —
   the correct fix moves office occupancy *up* by ~5–8 % on weekdays. The collision I flagged between
   decisions 1 and 2 is real in direction but roughly an order of magnitude smaller than stated, and
   it now points the other way: slightly *toward* the band, nowhere near enough to reach it.
3. "Under the consistent frame, fullyhybrid weekend presence falls below today (×0.89)." **False** —
   that ×0.89 was the diluted control. Matched, it is ×1.60.

The lesson is the one this project keeps re-learning: a comparison is only as good as its control,
and I did not test my control before trusting it. What saved it was a guard written to fail — the
monotonicity check — not my own reading of the numbers.

---

## DECISION 1 IMPLEMENTED — office 2030 product re-issued, 2026-08-02

### Code

`3rdJ_07_aug_to_bem_4split.py` gains two functions and one call-site change:

| what | where | note |
|---|---|---|
| `demo_assemble_2030(stock, pool)` | new | occupation-matched assembly. Ported from `3rdJ_08A::demo_assemble` with a tier ladder adapted to the 2030 pool's columns — it has **no `MARSTH`/`HHSIZE`**, so 08A's ladder cannot be reused verbatim, but it **has `NOCS`**, which is what matters for an office curve. Ladder: `[AGEGRP,SEX,LFTAG,NOCS] → [AGEGRP,SEX,NOCS] → [NOCS,LFTAG] → [AGEGRP,SEX,LFTAG] → []`, each `+ DDAY_STRATA`. |
| `build_office_2030_product(lookup, d2030_path)` | new | the all-bands file, built once, called by **both** `main()` and the regeneration script so the two cannot drift |
| the `d30[d30["BAND"] == band]` slice | `main()` | replaced by a call to the above |

`assemble_2030()` is **unchanged and still correct for residential** — a whole-household occupancy
aggregate is not an occupation-conditioned curve. The reason it is wrong for office is recorded in
the code next to the measurement that proves it, not just in this log.

`3rdJ_07R_regen_office_2030.py` — targeted regeneration. It rebuilds *only* the office file, because
re-running Step-7's full 2030 command would also rewrite the frozen
`BEM_Schedules_4split_2030_{cons,central,opt}.csv` products that a running campaign depends on and
that this fix does not affect. It backs up the predecessor, runs Step-7's own office gates, and
**refuses to write unless band monotonicity survives** — which is exactly what stopped the first,
invalid version from reaching disk.

### Result

| band | before (pool frame) wd / we | after (matched stock frame) wd / we | Δ |
|---|---|---|---|
| conservative | 0.2070 / 0.1622 | **0.2198 / 0.1694** | +6.18 % / +4.43 % |
| hybrid | 0.1872 / 0.1353 | **0.2025 / 0.1378** | +8.17 % / +1.83 % |
| fullyhybrid | 0.1680 / 0.1126 | **0.1759 / 0.1044** | +4.71 % / −7.34 % |

- `n_persons` now **3383 / 1365** — the 2022 product's own frame. Same pool, same construction,
  every cycle comparable.
- Band monotonicity `cons > hybrid > fullyhybrid`: **True on weekday and weekend** (the first
  attempt failed this and was refused).
- Step-7 office gates: **PASS** (archetype domain, `AT_WORK_fraction ∈ [0,1]`, grid completeness).
- WFH lever, weekday cons → fullyhybrid: **−18.84 % → −19.97 %** — preserved, slightly stronger.
- `AT_WORK_fraction ∈ [0, 0.5604]`, `multiplier ∈ [0, 1]`, 432 rows, 3 bands × 3 archetypes.

### Provenance

| file | md5 |
|---|---|
| `office_presence_multiplier_2030.csv` (new) | `575d17e55f32f8b5ec493ff590833d94` |
| `office_presence_multiplier_2030_BAK_2026-08-02.csv` (predecessor, kept) | `1536c98c5358ece477290d45f0505e4f` |

The predecessor is preserved on disk beside the new file, not deleted and not overwritten — same
discipline as the D2030 `_C` → `_C_v2` promotion.

### What is now stale

Every **2030-family** cell's office channel: the 9 scenarios `B_{cons,central,opt}`,
`sens_office_{cons,opt}`, `sens_retail_{cons,opt}`, `sens_hotel_{cons,opt}` — 36 of the 56 cells.
`Y2022`, `Y2005`, `Y2010`, `Y2015` are **untouched**; they already used this frame. No 2030 office
number may be quoted from arms A–E until those cells are re-run.

## Sequencing — arm E is NOT cancelled

Arm E (`1171323`) is running against the *old* office product, and stays. Its purpose is `E − C`,
and arm C carries the identical office series, so the DHW mechanism result is **frame-independent**:
P1 (shape preservation), P3 (hotel laundry), P4 (residential) and P5 (coupling bound) are unaffected
by decision 1. What decision 1 does invalidate is arm E's **office** `r` values and therefore P2's
specific numbers, which will need re-deriving against the rebuilt product. Cancelling 24+ completed
runs to avoid re-deriving one prediction would be the more expensive mistake.

---

## 🔴🔴 FINDING 7 — the 2030 RETAIL channel is built from the UNCALIBRATED pool — 2026-08-02

Found while chasing the open lead left by FINDING 6 ("does retail have the same defect class?").
It does not have the same defect. It has a **worse** one, and the frame question turned out to be
the smaller half of it.

### How it was found, including the probe that was wrong first

`3rdJ_09E_retail_frame_probe.py` compared the shipped 2030 retail base against a stock-frame control
and returned an enormous effect — shape deviation 0.69, weekday level ratio 0.42, peak hour moving
11 → 16. Taken at face value that is a catastrophic frame effect.

It is not, and the FINDING 6 correction is the reason it was checked instead of reported. **The
control had a confound.** It drew from `D2030` = `..._C_v2.csv`, the *calibrated* 2030 pool, while
the shipped retail base is built by `3rdJ_06_retail_lever_4split.py::load_pooled_raw()` from
`2030_diaries_{band}_raw.csv`, the *raw* pool. The probe varied **two** things at once — frame and
calibration — so it could prove neither.

`3rdJ_09E_retail_source_probe.py` separates them: three sources, one quantity, same treatment, and
a self-check that the RAW reconstruction reproduces the shipped column before any verdict is quoted
(`max|diff| = 9.9e-17`, so the probe is measuring what actually ships).

### The measurement

`ret30` mean, per DDAY_STRATA, per PR. RAW and CAL are the **same 111,024 rows** — same frame, same
construction — so every difference below is calibration, not population.

| day | PR | RAW (ships) | CAL (`_C_v2`) | CAL/RAW | peak RAW (clock) | peak CAL (clock) |
|---|---|---|---|---|---|---|
| Weekday | ALL | 0.02396 | 0.00994 | **0.415** | 13 | 16 |
| Weekday | QC | 0.02387 | 0.00981 | **0.411** | **11** | **16** |
| Weekday | AB | 0.02316 | 0.00949 | **0.410** | 14 | 16 |
| Saturday | ALL | 0.02348 | 0.03355 | 1.429 | 13 | 14 |
| Saturday | QC | 0.02027 | 0.03153 | 1.555 | 14 | 14 |
| Saturday | AB | 0.02337 | 0.03227 | 1.381 | 13 | 14 |
| Sunday | ALL | 0.02098 | 0.02233 | 1.064 | 13 | 13 |
| Sunday | QC | 0.02049 | 0.02149 | 1.049 | 14 | 15 |
| Sunday | AB | 0.02026 | 0.02115 | 1.044 | 11 | 13 |

Peak hours are **clock** hours (`ret30` slot 1 = 04:00; `np.roll(arr, 8)` applied, as Step-7 does).
The first version of this probe printed diary-origin indices and was corrected before anything was
recorded — the +4 h offset is a bug this project has already paid for once.

### The weekly contrast — the tell

Saturday / weekday mean retail presence:

| PR | observed 2022 | RAW (ships) | CAL | RAW/OBS | CAL/OBS |
|---|---|---|---|---|---|
| ALL | 2.687 | **0.980** | 3.375 | **0.365** | 1.256 |
| QC | 2.661 | **0.849** | 3.215 | **0.319** | 1.208 |
| AB | 2.571 | **1.009** | 3.399 | **0.393** | 1.322 |

In observed Canadian time use, people are at retail ~2.7× more on Saturday than on a weekday. The
shipped 2030 base says **0.98 — no weekend at all.** The calibrated pool says 3.38, which slightly
over-shoots the observed anchor but is the right phenomenon. The retail channel's defining weekly
signal is absent from the artefact the retail channel is built on.

### Why this exists — it is a wiring gap, not a modelling choice gone wrong

Step-6 produced **two** retail treatments, and only one of them is wired to the BEM:

| artefact | built from | retail treatment | consumed by |
|---|---|---|---|
| `at_retail_fraction_2030_{shift,plateau,renaissance}.csv` | `2030_diaries_*_raw.csv` | amplitude lever only | **Step-7 `build_retail_product_2030` → the BEM** |
| `..._C_v2.csv` | the calibration chain | retail-cap stage, targets observed-2022 × lever | every OTHER 2030 channel |

`3rdJ_06_retail_lever_4split.py`'s own docstring states the split plainly: *"This script is a pure
post-hoc AMPLITUDE LEVER on the RAW model-generated 2030 retail-fraction profile — it does NOT
modify any diary CSV (that is `3rdJ_06_calibrate_C_4split.py`'s retail-cap stage's job, which
targets observed-2022 × lever instead)."* Both halves were built as designed. What was never
decided is **which of the two the BEM should read**, and Step-7 reads the un-calibrated one.

### What actually propagates to EnergyPlus — stated so this is not over-read

`build_retail_product_2030` normalises **each `(Day_Type, PR)` group by its own base peak**, and
`commercial_integration.py:1311` injects `multiplier` = 0.95 × that normalised shape. Therefore:

- the 0.41–1.56 **level** ratios — **do NOT propagate.** Divided out.
- the Saturday/weekday **contrast** — **does NOT propagate.** Each day type self-normalises, in both
  sources. The 0.98-vs-2.69 table above is evidence about which artefact is trustworthy; it is
  **not** a claim that energy moves. Recorded this way deliberately: a 2.7× number is exactly the
  kind that gets quoted downstream as an energy effect once it loses its caption.
- the within-day **shape**, and the weekday **peak hour** — **DO propagate.** QC weekday retail
  peaks at **11:00** in the shipped product and at **16:00** in the calibrated pool. A five-hour
  shift in the retail channel's daily peak is material, and it lands in all 2030-family cells.

### Status: DOCUMENTED, NOT FIXED — this is a scope decision, not a manager call

Rewiring `build_retail_product_2030` to the calibrated source would (a) re-open Step 6, which is
CLOSED, (b) change the retail channel in every 2030 cell, and (c) invalidate the arm-C/arm-E retail
results that the T9-12 re-spec was just built on. That is a larger move than the office fix, which
touched one Step-7 product and nothing frozen. **Not doing it unilaterally.**

Two options, with honest costs:

| | option A — leave as is | option B — rewire to `_C_v2` |
|---|---|---|
| what it means | the retail channel's 2030 shape is un-calibrated and does not carry the observed weekend pattern | retail joins every other channel on the canonical calibrated source |
| cost | zero re-simulation; a stated limitation in the manuscript | re-open Step 6's wiring, re-run all 36 2030-family cells (can be merged with the FINDING-6 office re-run — same 36 cells) |
| risk | a reviewer asks why retail alone bypasses calibration, and there is no answer that is not "it was not noticed" | the T9-12 retail lighting re-spec (k=0.60) was calibrated against the *current* shape and would need re-checking |

The merge in option B's cost row is the thing that makes it cheap **now and only now**: the FINDING-6
office re-run already has to touch exactly those 36 cells. Doing both in one campaign costs one
campaign; doing them separately costs two. That window closes as soon as the office re-run is
launched.

**Recommendation: option B, merged into the FINDING-6 re-run**, because "retail bypasses the
calibration every other channel uses" is not a limitation that survives review as a stated caveat —
it reads as an error, and it is one. But this is the user's call, and the office re-run is being
held until it is made.

### Note on a vacuous check, logged rather than quietly dropped

`3rdJ_09E_retail_frame_probe.py` contains a COMPOSITION CHECK meant to prove its control had not
homogenised the population (the test that would have caught the FINDING 6 error). It reported:

```
real stock            : employed 0.015894   all 0.015898
assemble(conservative): employed 0.015809   all 0.015806
```

Employed and all-persons are identical **in the real stock too** — retail presence simply is not
occupation-differentiated. So the discriminator has no signal to lose, and the check **cannot fail**
whatever the control does. That is vacuous-test kind #7 for this project: *a guard whose
discriminator is constant in the ground truth.* It is left in the file with this note attached
rather than deleted, because the pattern is the point — a guard copied from where it worked to
where it has nothing to measure.

The control was validated instead by the RAW-reproduces-shipped-column check
(`max|diff| = 9.9e-17`), which **can** fail and which the source probe refuses to report past.

---

## DECISION 3 — splitting the hotel gate. Sourced, and it does NOT go the way it looks — 2026-08-02

User ruling: *"3 — diviser."* Split `S9-EUI-hotel` by geometry, with the same guard the office band
gets: **the new expectation must be sourced independently, not fitted to our number.**

### Full disclosure before any band is proposed

I already know the current result: `S9-EUI-hotel` = **28/56 cells inside [180, 300]**, median
**178.3**, range 147.9–209.4 — a 0.9 % miss at the floor. Nothing below can be presented as
blind. The protection against fitting is therefore not ignorance but **rule-first**: each candidate
band is derived from a stated selection rule applied to `dr_L3-03_hotel_eui_bands_REPORT.md`
(locked **2026-07-02**, a month before this question was asked), and every rule is reported —
including the one that makes the FAIL **much worse**.

### Rule R1 — amenity classification. dr_L3-03 mandates this split in its own words

> *"The validator must distinguish between limited-service hotels (modeled as Small Hotel prototypes
> with EUI ~180 kWh/m²·yr) and full-service properties (modeled as Large Hotel prototypes with EUI
> ~240–300 kWh/m²·yr). The inclusion of intensive laundry facilities, commercial kitchens, or
> swimming pools can shift the EUI by over 100 kWh/m²·yr."* — dr_L3-03 §Caveats, *Amenity Inclusion*

> *"For hotel floors embedded as a podium or zone inside a tall mixed-use tower, the **Large Hotel
> prototype** is the superior as-modelled anchor."* — dr_L3-03 §C.4, *Prototype Selection*

Which one is our tower? This is a **fact about the IDF**, settled without reference to any EUI.
`SuperTallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v242.idf` contains:

| evidence | line |
|---|---|
| `F55 Hotel_bot_Cafe ZN` | 1163 |
| `F55 Hotel_bot_Laundry ZN` | 1181 |
| `F72 Hotel_top_Banquet ZN` | 1373 |
| `F72 Hotel_top_Kitchen ZN` | 1409 |
| `HotelLarge Kitchen_Elec_Equip_SCH`, `HotelLarge Kitchen_Gas_Equip_SCH` | 4630–4743 |
| `HotelLarge LAUNDRY_SWH_SCH`, `HotelLarge LaundryRoom_SWH_Sch_Post2004` | 6611–6656 |

Cafe, commercial kitchen, banquet hall and commercial laundry, carrying schedules the prototype
itself names **`HotelLarge`**. The tower's hotel channel is **unambiguously full-service, and it is
literally built from the DOE Large Hotel prototype.**

**R1's verdict: the applicable band is [240, 300], not [180, 300].** The floor 180 is, in
dr_L3-03's own justification, *"a compliant Small Hotel prototype"* — a different building from
ours. Under R1 the hotel gate goes from **28/56 to 0/56**, and the 0.9 % miss becomes a ~26 % miss.

**This is recorded first, and deliberately.** Decision 3 was granted to make a gate defensible, and
the first defensible rule found makes the result far worse. Reporting the other rule without this
one would be exactly the move this project has spent six vacuous-test findings learning not to make.

### Rule R2 — code-vintage and climate-zone matching

The same report insists on basis-matching for fuel coverage and floor area (§Caveats). The identical
discipline applied to *code vintage* and *climate zone* selects different rows of its Table 2 — and
they are an unusually exact match to our model:

| source row (dr_L3-03 Table 2) | code | CZ / city | band |
|---|---|---|---|
| NECB 2017 Hotel Archetype Study, CanmetENERGY 2020 | **NECB 2017** | **CZ 6 (Montreal)** | **140 – 220** |
| NECB 2017 Hotel Archetype Study, CanmetENERGY 2020 | **NECB 2017** | **CZ 7 (Calgary)** | **160 – 240** |

Our IDFs are named `..._NECB17_...` and the campaign's two cities are **MTL** and **CLG** —
Montreal and Calgary. Same code, same country, same two cities. No other row in Table 2 is Canadian
*and* code-matched; every other row is a US PNNL/ASHRAE prototype.

**R2's verdict: split the gate by climate zone**, which is the "by geometry" split the ruling asked
for and which the present single band ignores outright — every row of Table 2 shows CZ 7 running
above CZ 6, yet `S9-EUI-hotel` scores Montreal and Calgary cells against one band.

### The two rules CONFLICT, and I cannot resolve it from what is on file

R1 says [240, 300] (worse). R2 says [140, 220] / [160, 240] (better). The disagreement reduces to
one unanswered question:

> **Is the CanmetENERGY NECB 2017 hotel archetype a full-service or a limited-service property?**

If full-service, R2 is the better-matched source and supersedes R1 — R1's Small-vs-Large correction
is a *within-PNNL-family* adjustment that a Canadian NECB archetype does not need. If
limited-service, R2's band describes a different building too, and R1 stands: [240, 300], 0/56.

dr_L3-03 does not say. Answering it requires the CanmetENERGY *Commercial Archetypes Performance
Study* (2020) itself, which is not in `deepResearch/`. **Until that is read, adopting R2 would be
choosing the band that rescues the gate over the band that condemns it, on no evidence.** That is
the move that is banned.

### What is therefore implemented: the split as INFO, not as the PASS criterion

`S9-EUI-hotel` **keeps** its band [180, 300] and **keeps** its FAIL. Alongside it, two new
**INFO-only** gates report the climate-split view so the question is visible in every run instead of
living in this document:

| gate | cells | band | source | role |
|---|---|---|---|---|
| `S9-EUI-hotel-CZ6-INFO` | MTL only | 140 – 220 | dr_L3-03 T2, NECB 2017 / CanmetENERGY 2020 | INFO |
| `S9-EUI-hotel-CZ7-INFO` | CLG only | 160 – 240 | dr_L3-03 T2, NECB 2017 / CanmetENERGY 2020 | INFO |
| `S9-EUI-hotel-FULLSVC-INFO` | all 56 | 240 – 300 | dr_L3-03 §Caveats + §C.4 (R1) | INFO |

Three views, one of which is much harsher than the status quo, all reported together. **No FAIL is
erased by this change**, so it cannot be an instance of widening a band to make a failure disappear.

**Blocking item for the user, and it is small:** obtain the CanmetENERGY 2020 archetype study and
determine whether its hotel archetype is full-service. One answer promotes `-CZ6/-CZ7` to the PASS
criterion; the other promotes `-FULLSVC` and the hotel gate fails harder than it does today. Both
outcomes are acceptable; picking without the answer is not.

---

## DECISION 4 — retail NECB proxy: FROZEN and DOCUMENTED — 2026-08-02

User ruling: *"4 — geler et documenter."*

### What is frozen

`necb_retail_baseline_proxy(day_type, hour)` in `3rdJ_07_aug_to_bem_4split.py` supplies the
open/closed envelope for the retail channel. Where it returns ≤ 0.10 the hour is marked
`staff_shoulder_flag = 1` and the GSS-derived multiplier is **replaced** by the NECB baseline value
rather than modulated by it (`:670-672`). It is a hand-written approximation of the NECB retail
schedule, not the NECB schedule read from a prototype IDF.

**Frozen as of 2026-08-02.** No further tuning. Any future change requires re-running every cell
that carries a retail channel, and the T9-12 lighting re-spec (`k = 0.60`) is calibrated against
this exact envelope.

### The limitation, stated for the manuscript

1. **It is a proxy, not a source.** The office and hotel channels take their baselines from the
   prototype IDF objects themselves (`OfficeLarge BLDG_LIGHT_SCH_2013`, `HotelLarge LAUNDRY_SWH_SCH`
   and siblings). Retail alone uses a function written to resemble one. The 0.10 threshold that
   decides open-vs-closed is a modelling choice with no cited source.
2. **It is load-bearing.** `staff_shoulder_flag` does not merely annotate — it *overrides* the
   occupancy signal for every hour it fires. Those hours are, by construction, hours in which the
   GSS diaries have no influence on the retail schedule at all.
3. **It was nearly load-bearing in the wrong direction.** The T9-12 arm-B analysis found the retail
   lighting component PASSing *for the wrong reason* — the lighting was frozen, driven by the
   discarded `staff_shoulder_flag` rather than by the occupancy term the re-spec introduced. The
   proxy's reach is easy to underestimate; it has already produced one vacuous pass.

### Related but NOT the same thing — do not let this absorb FINDING 7

Decision 4 concerns the **open/closed envelope**. FINDING 7 concerns the **source of the retail
occupancy signal itself** (raw vs calibrated 2030 pool). They are independent defects in the same
channel, and FINDING 7 is the larger one. Freezing the proxy does not address it, and the manuscript
limitation written here must not be allowed to read as if it covers both.

---

## DECISION 5 — the Leg-2 office-EUI correction is PUBLISHED — 2026-08-02

User ruling: *"5 — publier le correction, tu as raison."* Leg-2 stays **read-only**; the correction
is published as a manuscript caveat, and no file under `Leg2_2-split/` is touched.

### The mechanism — verified, and not in doubt

`calculate_eui()` (`eSim_bem_utils_3J/plotting.py:293-299`) filters EnergyPlus's tabular output on
`TableName` and **never on `ReportName`**. EnergyPlus writes a table named `End Uses By
Subcategory` under **two** report names: `AnnualBuildingUtilityPerformanceSummary` (273 rows, **GJ**
— annual energy) and `DemandEndUseComponentsSummary` (273 rows, **W** — peak demand). The unit guard
at `:319` skips only `m3`, so every **watt** row is summed as if it were a kWh (`:345`).

Measured on a real v24.2.0 `eplusout.sql`: 7,837,731 kWh of legitimate energy **+ 5,533,372 "kWh"
that are watts** = 13,371,103 → a **1.706×** inflation. Corroborating signature: Leg-2's three
office-archetype medians (`Office_Knowledge` 172.6 / `Office_Public` 172.5 / `Office_Sales` 172.7)
are implausibly tight for three different use profiles across six cities — a systematic artefact
dominating the real architectural variation.

### 🔴 What CANNOT be published yet, and why — this is the whole difficulty of decision 5

**The 1.706 factor was measured on a Leg-3 run** (`campaign_cf69d508/B_central__Tall__MTL`), not on
the Leg-2 run that produced 172.7. The improvement log already says so in as many words:
*"Indicatif seulement — le ratio vient d'un autre run, ce n'est pas une dérivation."*

So `172.7 / 1.706 ≈ 101.2` is an **indication of magnitude, not a corrected value**. The watt
contamination depends on that run's own peak-demand rows; a different building, city and schedule
set gives a different ratio. Publishing "101.2" would put a number into the literature that nobody
derived — and a corrigendum is the last place that is acceptable.

The 100.4 cross-check has a second, separate problem: it is the **whole-tower** EUI on the raw ABUPS
basis, while 172.7 is the **office channel**. The ~1 % agreement is suggestive, not like-for-like,
and must not be presented as a validation of a specific corrected office figure.

### What decision 5 therefore requires before the corrigendum can carry a number

One bounded, **read-only** job: run the corrected EUI query against **Leg-2's own** `eplusout.sql`
files and measure Leg-2's own watt contamination per archetype. This modifies no `Leg2_2-split/`
file — it reads simulation output that already exists — and it yields the factor and the corrected
office EUI that the corrigendum can actually stand behind. Estimated cost: one `sbatch`, minutes.

### Draft caveat text — two versions, and which one is honest today

**Version A — publishable NOW, no number:**

> **Corrigendum — office EUI.** The office end-use intensities reported in this work were computed
> by a routine that merged two identically-named EnergyPlus tabular outputs
> (`AnnualBuildingUtilityPerformanceSummary`, in GJ, and `DemandEndUseComponentsSummary`, in W),
> causing peak-demand quantities in watts to be aggregated as annual kilowatt-hours. The reported
> office EUI values are therefore inflated by a systematic factor. On a comparable building the
> measured inflation is approximately 1.7×. The error is confined to the EUI post-processing
> routine: the simulations, schedules, occupancy model, and every occupancy quantity reported in
> this work are unaffected, and no conclusion of the paper depends on the office EUI level.

**Version B — publishable only AFTER the read-only re-measurement above**, identical to A with the
final sentences replaced by the measured factor and the corrected per-archetype values.

**Recommendation: version B**, because "inflated by approximately 1.7×" invites precisely the
question the corrigendum exists to close. But version A is available immediately if the manuscript
timeline does not allow the re-measurement, and A is honest — it claims only what was measured.

### What must accompany it, and what must not

- **Must:** the statement that occupancy results are untouched. The defect sits in reporting
  arithmetic downstream of every scientific claim the paper makes.
- **Must NOT:** any claim that the published **band** was also affected. That hypothesis was formed
  and then **checked and refuted** (log, 2026-07-31): `OFFICE_EUI_BAND = (135.0, 100.0, 200.0)` is
  hard-coded from the NECB2020/90.1-2019 literature review, not derived from any simulation. **The
  band is sound; only the measured value is inflated.** This one is easy to get backwards — it was
  once, in this very log — and getting it backwards in print would be worse than the original error.
- **Must NOT:** any edit to a `Leg2_2-split/` file. The corrigendum is authored in the Leg-3
  improvement record and carried into the manuscript by hand.

### Adjacent discrepancy, logged here so it is not discovered by a reviewer

The label `CAN_CLG` does **not** resolve to the same weather file in the two legs — **Winnipeg (7A)
in Leg-2, Calgary (Z7A) in Leg-3**. This has no bearing on the EUI defect above, but any text that
compares a Leg-2 "CLG" result to a Leg-3 "CLG" result is comparing two different cities.

---

# ARM E — RESULT. Scored against the pre-registered predictions — 2026-08-02

Array `1171323`: **56/56 COMPLETED**. Aggregation job `1171404`: exit 0, 56/56 cells, attribution
closes against site energy on every cell (≤ 1e-6 relative). Aggregate at
`campaign/agg_E_dhwvol`, campaign dir `out_E_dhwvol/campaign_56d6e324` (hash verified against the
injector md5 `56d6e324`).

## THE SCORECARD — 2 PASS / 3 FAIL / 1 UNTESTABLE

Produced by `3rdJ_09E_score_armE.py`, written and committed **while the array was still running**.
No tolerance in that file has been touched since. Reproduce with:

```
py -3 3rdJ_09E_score_armE.py --arm-c agg_C_lm3v2 --arm-e agg_E_dhwvol
```

| | prediction | result | verdict |
|---|---|---|---|
| **P6** | same 56 cells, identical areas | 56 vs 56, identical; max \|ΔArea\| = **0.0 m²** over 392 (cell,channel) pairs | **PASS** |
| **P2** | office DHW `B_cons +0.3` / `B_central −11.2` / `B_opt −21.8` %, ±3 pp | **+21.68 / +8.38 / −3.69 %** | **FAIL** |
| **P3** | hotel DHW `B_central` **+12.4 %** ±2 pp | **+15.31 %** | **FAIL** |
| **P4** | residential DHW `B_central` **+8…+18 %** | **+51.40 %** | **FAIL** |
| **P5** | non-DHW end uses bounded at 0.5 % | **0 of 616** material end uses exceed it (70 skipped as < 1 % of channel total) | **PASS** |
| **P1** | night share + peak hour unchanged | hourly pair not supplied | **UNTESTABLE** |

**A miss is recorded, not repaired.** Nothing below revises a threshold.

## P5 is the strongest result in the arm, and it deserves saying plainly

Every non-DHW end use in the tower moved by less than 0.5 %, across 616 material
(scenario × channel × end-use) combinations. The largest mover in the entire campaign is
`residential_common / pumps` at **+0.207 %**. T9-13 changes water volumes and nothing else — the
thermal coupling bound predicted in advance held everywhere, with two orders of magnitude to spare.
The materiality rule (≥ 1 % of channel total, 70 skipped) was fixed before the run and is reported,
not hidden.

## P2 — the office miss is a systematic **offset**, and the mechanism it tested SUCCEEDED

The prediction was wrong by roughly the same amount in all three bundles: **+21.4 / +19.6 / +18.1
pp**. A uniform offset with the ordering intact is not a failed mechanism, it is a mis-calibrated
level. What the prediction was actually about:

| | arm C | arm E |
|---|---|---|
| office DHW spread across the 3 bundles | **0.004 %** | **23.318 %** |
| ordering `cons > central > opt` | — | **True** |

Arm C's office DHW was flat to four decimal places — the WFH axis had **no effect whatsoever** on
office hot water. That was the defect T9-13 exists to fix, and it is fixed: the spread is now
23.3 % and it runs in the physically correct direction. The pre-registered *numbers* missed; the
pre-registered *claim* ("office DHW stops being flat") is confirmed.

**And P2's numbers were already known to be superseded before the array finished.** The Sequencing
note written at the time of DECISION 1 states it: arm E ran against the **pre-FINDING-6** office
product, so its office `r` values (weekend ratios ×2.49 / ×2.08 / ×1.73) are the old ones. The
corrected product gives ×2.60 / ×2.12 / ×1.60. P2 must be re-derived against the rebuilt product
and re-scored. **This is a reason to re-run, not an excuse for the miss** — P2 failed as
pre-registered, and that stands in the record regardless of what the re-run says.

## P3 — the hotel miss is 0.91 pp, and the mechanism claim is unambiguously confirmed

Predicted +12.4 ± 2.0 (i.e. ≤ +14.4). Measured **+15.31 %**. The scorer's own detail line fixed the
mechanism threshold in advance: *"Arm D reported −8.7 % with laundry frozen. A move < +5 % means
laundry still is not scaling."* The move is +15.3 %, three times that threshold, and it reverses
arm D's sign.

**Hotel laundry is scaling. Arm D's P5 is reversed.** The magnitude tolerance was too tight by
0.91 pp; the tolerance is not being widened.

## 🔴 P4 — the interesting one. It is NOT the T9-11 blow-up, and the volume identity HOLDS

Residential DHW came in at **+51.40 %** against a predicted +8…+18 %, above even T9-11's +40.8 %.
The obvious reading — "the blow-up is back" — is **wrong**, and three independent measurements say
so.

### 1. The `r` distribution cannot produce +51 %

`probe_resid_r.sh` (job `1171406`), per-household residential `r`, arm E:

| cell | r_wd mean | median | p90 | max | frac > 2 | r_we mean |
|---|---|---|---|---|---|---|
| `B_cons__Tall__MTL` | 1.0873 | 1.0818 | 1.5736 | 1.5736 | **0.000** | 1.1056 |
| `B_central__Tall__MTL` | 1.1225 | 1.1474 | 1.5736 | 1.5736 | **0.000** | 1.0898 |
| `B_opt__Tall__MTL` | 1.1559 | 1.1146 | 1.5736 | 1.5736 | **0.000** | 1.1525 |
| `Y2022__Tall__MTL` | **0.9841** | 0.9507 | 1.4752 | 1.5736 | **0.000** | **0.9792** |

No tail, no household above 2.0, max 1.574. T9-11's signature was a *shape* break (night share
8.34 % → 32.86 %, peak hour 06:00 → 04:00); nothing here resembles it, and the 56-cell provenance
sweep found **0 saturation, 0 exclusions, 0 unresolved**.

### 2. Arm C is not a confound — it had NO DHW modulation at all

| channel | arm C ÷ arm C's own `Default_NECB` |
|---|---|
| residential | **1.000** |
| office | **1.000** |
| hotel | **1.000** |
| retail | **1.000** |

Arm C's DHW is bit-identical to the uninjected prototype in every channel and every scenario. So
`E/C` **is** `E/prototype`, and the r values above should predict it directly.

### 3. The decisive case: `Y2022`, where `r ≈ 1` and scaling must be a no-op

The T9-13 reference **is** Y2022, so `r ≈ 1` there by construction, and the measurement confirms it
(0.9841 / 0.9792). Yet Y2022 residential DHW **energy** is **1.412 ×** the prototype.

`3rdJ_09E_dhw_identity_probe.py` (job `1171407`) was written to catch an injector defect — it
parses both injected and uninjected IDFs and computes the quantity annual volume actually follows,
`Σ Peak_Flow_Rate × (5·mean_wd + 2·mean_we)/7`, over all 27 residential `WaterUse:Equipment`
objects, 0 unresolved on both sides.

```
INJECTED   Y2022__Tall__MTL       SUM V = 2.680707e-04
UNINJECTED Default_NECB__Tall__MTL SUM V = 2.778796e-04
VOLUME RATIO = 0.9647              (identity requires ~0.98)
```

**The identity holds.** The probe was built to find a defect and found none: T9-13's construction
(`Peak' = P·R`, `f = s·r/R`, so `R` cancels and volume ratio = weighted mean of `r`) is implemented
correctly. The parse is confirmed by the injected schedules' own signature — on each household's
argmax day type the mean is *exactly* the prototype's 0.5242 (there `r = R`, so `f = s`), and below
it on the other day type. That is precisely what the formula predicts, object by object.

### So what P4 actually found

> **Residential DHW volume went DOWN 3.5 %. Residential DHW energy went UP 41.2 %.**

The energy change is **not** occupancy, **not** the `r` values, and **not** the volume. It is
introduced somewhere between the water draw and the fuel meter — the obvious suspect being that
`Peak_Flow_Rate` rose per household (e.g. 3.919e-06 → 4.907e-06 m³/s, +25 %) against **hard-sized**
water heaters, but that is a hypothesis and it is **not yet tested**.

This reframes P4 completely. It is not a failed occupancy model; it is a located, quantified,
unexplained gap between volume and energy in the DHW plant, and it is the single most important
open item in Step 9. **P4 remains FAIL.** Explaining a number is not the same as passing a
prediction, and the +51.4 % stands in the scorecard.

### The next probe, specified now so it cannot be shaped by the answer

Decompose the residential DHW **energy** for `Y2022__Tall__MTL`, arm E vs `Default_NECB`, into
water-heating load, tank/standby losses, pump energy and any recovery/backup term, from
`eplusout.sql`. **Prediction, written before running it:** if the peak-flow hypothesis is right,
the *water-heating* component tracks volume (≈ 0.96 ×) and the excess sits almost entirely in
tank/standby or recovery terms. If instead the water-heating component is itself ≈ 1.41 ×, the
hypothesis is refuted and the fault is in the draw temperature or the end-use attribution, not the
plant sizing.

## P1 — the provenance half, and a spec gap in the audit

The hourly half is UNTESTABLE (no `dhw_hourly.csv` pair supplied). The 56-cell provenance sweep in
`agg_armE.sh` gives the other half:

| check | result |
|---|---|
| cells excluded == 0 | **56 / 56** |
| cells unresolved == 0 | **56 / 56** |
| `r` saturated at `r_max` | **0** (expect 0) |
| `t9_13_audit_pass=True` | **50 / 56** |
| VIOLATION lines | **2** |

The 6 non-passes, enumerated (`1171406`), are **two different things**:

- **4 × `Default_NECB__{Tall,SuperTall}__{MTL,CLG}`, `n_audited=0`, all six counts zero.** These
  are the **uninjected control cells**. They contain no T9-13 objects, so the audit has nothing to
  examine, and the "empty audit = FAIL" rule — added deliberately so a silently-skipped audit could
  never read as a pass — fires on them. **This is the rule working as designed on a case it was
  not written for.** It is a spec gap, not a defect: the audit should report **N/A** for a cell
  with no injection, and `n_audited=0` should remain a FAIL everywhere else. Left as-is and logged
  rather than patched mid-analysis, because loosening an empty-audit guard while reading results is
  how vacuous tests get born.
- **2 × `Y2015__SuperTall__{CLG,MTL}`, `n_audited=47`, `D2 = 1`.** One genuine shape violation,
  the same object in both: `F38 Resi_bot_S_Apartment_4 Service Water Use 0.06gpm 140F`, peak hour
  **7 → 0**. Real, small (1 object of 47, in 2 cells of 56), and **not** covered by the
  pre-registered residential zero-occupancy exception, which required `r_wd = 0.0`. **Recorded as
  an unexplained shape violation**, not waved through.

### Correction to `agg_armE.sh`'s own expectation

The sweep reports `audited==47 objects : 24/56` as though 47 were universal. It is not — the actual
distribution across the 56 cells is:

```
26 cells  n_audited=47
20 cells  n_audited=71
 6 cells  n_audited=31
 4 cells  n_audited=0     (the Default_NECB controls)
```

`47` was read off a single smoke cell and generalised. The check is **mis-specified, not failing**:
different geometries carry different object counts. It should assert *per geometry*, and until it
does, that line of the sweep output means nothing and must not be quoted.

## Where arm E leaves T9-13

| claim | status |
|---|---|
| DHW volume scales exactly as specified, `R` cancels | **VERIFIED** at the IDF level, 0.9647 vs 0.98 |
| non-DHW end uses are untouched | **VERIFIED**, 0/616 above 0.5 % |
| office DHW stops being flat and moves with the WFH axis | **VERIFIED**, spread 0.004 % → 23.3 %, correct ordering |
| hotel laundry scales (arm D's freeze is gone) | **VERIFIED**, −8.7 % → +15.3 % |
| the predicted magnitudes | **3 of 3 missed** (P2 offset ~+20 pp, P3 by 0.9 pp, P4 by ~33 pp) |
| residential DHW energy responds to volume | **REFUTED** — volume −3.5 %, energy +41.2 % |

T9-13's **mechanism** is sound and is now demonstrated. T9-13's **energy predictions** are not, and
the reason is a plant-side effect nobody in this project has yet looked at.

---

# 🔴🔴🔴 FINDING 8 — T9-13 REPLACES specialised DHW schedules instead of scaling them — 2026-08-02

This is the mechanism behind P3 and a large part of P4. It is a real defect, it is proven at the
IDF level, and it means arm E's DHW numbers cannot be quoted as they stand.

## How it was found

The P4 follow-up probe was written with a hypothesis and both branches of its refutation stated in
advance (`3rdJ_09E_dhw_energy_probe.py`, job `1171408`):

> *HYPOTHESIS: `Peak_Flow_Rate` rose against hard-sized water heaters, so the plant spends more time
> in recovery. IF TRUE the water-heating component tracks volume (~0.96×) and the excess sits in
> tank/standby terms. IF FALSE the water-heating component is itself ~1.41× and the fault is in the
> draw temperature or the end-use attribution, not plant sizing.*

**The hypothesis was REFUTED.** `Water Use Equipment Heating Energy` totals **×1.389** — the draw
energy itself moved. And because the probe reported *every* water-related series rather than only
the ones the hypothesis needed, the culprit was visible in the per-object rows.

## The evidence

`Y2022__Tall__MTL` (arm E) vs `Default_NECB__Tall__MTL`, `Water Use Equipment Heating Energy`:

| object | uninjected (J) | injected (J) | ratio |
|---|---|---|---|
| **`LAUNDRY SERVICE WATER USE`** | 9.1147e+11 | 2.7598e+12 | **×3.028** |
| **`F30 HOTEL_BOT_LAUNDRY SERVICE WATER USE`** | 2.6625e+11 | 3.7251e+11 | **×1.399** |
| `F31-F37 HOTEL_MID_*_GUESTRM` (all 8) | — | — | ×1.136 (uniform) |
| `F38 HOTEL_TOP_KITCHEN SERVICE WATER USE` | 4.2705e+11 | 4.2605e+11 | ×0.998 |
| `BOOSTER SERVICE WATER USE` | 2.9766e+11 | 2.9631e+11 | ×0.995 |

The guest rooms move uniformly at ×1.136 — that is the legitimate `r` effect. The kitchen and the
booster do not move. **Only the two laundry objects move anomalously.**

## The cause — a schedule SUBSTITUTION, and `Peak_Flow_Rate` proves it

The same `WaterUse:Equipment` object, uninjected vs injected:

| | `Peak_Flow_Rate` | `Flow Rate Fraction Schedule Name` |
|---|---|---|
| **NECB** `Laundry Service Water Use 30.6gpm 180F` | `0.00193056` | **`HotelLarge LAUNDRY_SWH_SCH`** |
| **arm E** same object | `0.001930562` | **`MXU_Hotel_DHWv2_r1000w1000_Y2022__Tall__MTL`** |
| **NECB** `F30 Hotel_bot_Laundry ... 2.56gpm 140F` | `0.000161725` | **`HotelLarge LaundryRoom_SWH_Sch_Post2004`** |
| **arm E** same object | `0.0001617252` | **`MXU_Hotel_DHWv2_r1000w1000_...`** |

**`Peak_Flow_Rate` is unchanged to seven significant figures in both cases** — as it must be, since
this is `Y2022`, where `r = 1.000` and therefore `Peak' = P·R = P`. The provenance line agrees:

```
t9_13 hotel 'HotelLarge BLDG_SWH_SCH' r_wd=1.0 r_we=1.000001 R=1.000001 peak_mult=1.000001
            nightshare=0.122222->0.122222 peakhour=7->7 max=0.6->0.599999 clipped=False
```

The T9-13 *scaling* is a faithful no-op. **100 % of the ×3.028 comes from the object being pointed
at a different schedule.** A commercial laundry's draw profile — concentrated in a few operating
hours, low daily mean — was replaced by the hotel channel's generic guest-room DHW curve, whose
daily mean is roughly three times higher.

The injector's own log shows it knew about these schedules and could not characterise them:

```
dhw hotel 'HotelLarge LAUNDRY_SWH_SCH'              -> floor=-1.0 peak=-1.0
dhw hotel 'HotelLarge LaundryRoom_SWH_Sch_Post2004' -> floor=-1.0 peak=-1.0
```

`floor=-1.0 peak=-1.0` are sentinels: the laundry schedules were recognised as hotel-channel DHW
schedules but their floor/peak were not derived — and they were then superseded wholesale rather
than skipped.

## Why the audit could not see it — vacuous-test kind #8

`audit_dhw_shape_preservation` reported **`n_audited=47`, all six counts zero, PASS** on this cell.
It is not broken and it is not vacuous in the earlier senses. It has a different blind spot:

> **The audit verifies the transformation it performed. It never verifies the assignment it
> changed.**

D1–D5 compare each schedule T9-13 *wrote* against the schedule it was *derived from*. For the
laundry objects there is no such pair — T9-13 did not transform `HotelLarge LAUNDRY_SWH_SCH` at
all; it left that schedule alone and re-pointed the `WaterUse:Equipment` object somewhere else. A
before/after check on schedules is structurally incapable of seeing a change of *which* schedule an
object uses. D6 (channel coverage), added this same day, checks that every expected channel appears
— not that every object kept a schedule of its own kind.

This is kind #8 for the project: *a guard that audits the objects it edited, on a change that
happens to the objects it did not.*

## 🔴 CORRECTION to what I wrote about P3 earlier today

Earlier in this same log I wrote, of P3:

> *"Hotel laundry is scaling. Arm D's P5 is reversed. The mechanism claim is unambiguously
> confirmed."*

**That is now shown to be confirmed for the wrong reason, and I am striking it.** Hotel laundry is
indeed no longer frozen — but it is moving because its schedule was *replaced*, not because `r`
modulates it. The `Y2022` cell settles it: there `r = 1.000`, so a correctly-implemented T9-13 must
leave laundry untouched, and instead `F30 Hotel_bot_Laundry` moves ×1.399.

P3's numeric verdict is unchanged (**FAIL**, +15.31 % vs +12.4 ± 2.0). What changes is that the
consolation — "the magnitude missed but the mechanism worked" — is withdrawn. The mechanism did not
work. It produced motion by substitution.

This is the seventh time in this project that a PASS-shaped result has turned out to rest on a
mechanism nobody checked, and the third time I have had to strike a claim of my own within hours of
writing it. The pattern is consistent enough to be worth naming: **a result that matches the
predicted direction is the easiest place to stop looking.**

## What FINDING 8 does and does NOT explain

Honest accounting, because the temptation is to let one good mechanism absorb every open number:

- **P3 (hotel, +15.31 %)** — substitution is a direct contributor (`F30` ×1.399), alongside the
  legitimate ×1.136 on all eight guest-room objects. **Largely explained.**
- **P4 (residential, +51.40 %)** — the big `Laundry Service Water Use 30.6gpm 180F` is attributed
  to the **residential** channel by the aggregator (it carries no zone prefix). Its rise is
  9.11e+11 → 2.76e+12 J = **+1848 GJ**, against a residential channel rise of 15452 → 21819 GJ =
  **+6366 GJ**. So substitution explains **about 29 %** of P4. **The remaining ~71 % is still
  unexplained**, and the 27 apartment objects' own volume identity holds at 0.9647. Not claiming
  more than the arithmetic supports.
- **The `Y2022` office channel (+28.6 % at `r ≈ 1.0`)** — the office restroom objects moved
  **×0.952**, i.e. *down*, while the office channel total rose. That is an **attribution** question,
  not a schedule question, and it is untouched by FINDING 8.

## Consequences

1. **Arm E's DHW numbers must not be quoted.** P2/P3/P4 all sit downstream of this defect.
2. **The fix is small and local**: an object whose schedule cannot be characterised
   (`floor=-1.0 peak=-1.0`) must be **skipped and logged**, never re-pointed at the channel's
   generic curve. Scaling a specialised schedule in place is the correct behaviour; substituting it
   is not.
3. **The audit needs an assignment check** (call it D7): for every `WaterUse:Equipment` object,
   assert that its post-injection `Flow Rate Fraction Schedule Name` is either unchanged or is the
   T9-13 derivative *of its own original schedule* — never another object's. This is the check that
   would have caught FINDING 8 on the smoke test, before 56 cells were run.
4. **Re-run required after the fix.** This merges naturally with the FINDING-6 office re-run and
   the FINDING-7 retail decision — all three touch the same campaign.

---

## P1 IS TESTABLE AFTER ALL — final scorecard **3 PASS / 3 FAIL / 0 UNTESTABLE** — 2026-08-02

The first scoring run reported P1 UNTESTABLE for want of an hourly file. That was **my error, not a
missing artefact**: every cell already writes `dhw_hourly.csv` beside `injected.idf`. Found while
listing a cell directory for the FINDING 8 investigation.

```
py -3 3rdJ_09E_score_armE.py --arm-c agg_C_lm3v2 --arm-e agg_E_dhwvol \
       --dhw-hourly-c agg_C_lm3v2/dhw_hourly.csv --dhw-hourly-e agg_E_dhwvol/dhw_hourly.csv
```

Cell `B_central__Tall__MTL`, residential column:

| | arm D (T9-11) | **arm E (T9-13)** |
|---|---|---|
| night 00–05 share | 0.0834 → **0.3286** | 0.0834 → **0.0828** |
| peak draw hour | 06:00 → **04:00** | 06:00 → **06:00** |

> **P1 PASS.** The identity T9-11 destroyed is preserved by T9-13 to within 0.0006 on the night
> share, with the peak hour unmoved.

This is the single most important result in arm E, and it is worth separating from everything else
in this log: **T9-13's re-specification of T9-11 works.** Volume scaling changes how much water is
drawn without changing when it is drawn — which is exactly what it was written to do, and exactly
what its predecessor failed to do.

### Final scorecard

| | verdict | one line |
|---|---|---|
| P1 | **PASS** | shape preserved — the T9-11 failure does not recur |
| P5 | **PASS** | 0 of 616 material non-DHW end uses above 0.5 %; worst mover +0.207 % |
| P6 | **PASS** | 56/56 cells, max \|ΔArea\| = 0.0 m² over 392 pairs |
| P2 | **FAIL** | office DHW moved +21.7 / +8.4 / −3.7 % vs predicted +0.3 / −11.2 / −21.8 |
| P3 | **FAIL** | hotel +15.31 % vs +12.4 ± 2.0 — and see FINDING 8, the motion is substitution |
| P4 | **FAIL** | residential +51.40 % vs +8…+18 % — ~29 % explained by FINDING 8, ~71 % open |

**3 PASS / 3 FAIL / 0 UNTESTABLE.** No tolerance was altered at any point. The three passes are the
structural claims (shape, isolation, integrity); the three failures are all magnitude predictions,
and two of the three are now known to sit downstream of a located defect.

---

# 🔴🔴 CORRECTION TO FINDING 8 — the mechanism recorded above is WRONG — 2026-08-02 (evening)

FINDING 8's **conclusion stands**: specialised DHW schedules are replaced, arm E's DHW numbers are
unquotable, a re-run is required. **Its mechanism does not**, and the fix specified from it (D-A:
"skip objects whose floor/peak cannot be characterised") would have been a **no-op that looked like
a fix** — the eighth vacuous shape, arrived at from the other direction.

## What was claimed

> *"The injector logged `floor=-1.0 peak=-1.0` on both — it could not characterise them and
> superseded them instead of skipping them."*

## Why that is false, from the code

`commercial_integration.py:2151-2155` — the T9-13 branch writes, for **every** applied object:

```python
result["dhw_applied"].append(
    {"name": we.Name, "channel": channel, "prototype_schedule": proto,
     "floor": None, "peak": None, "derived_schedule": target_sch, ...})
```

`:2283-2288` — the provenance writer, with its own comment saying so:

```python
# floor/peak are None under T9-13 (it uses no extremum); -1 keeps the tuple sortable if a
# future run ever mixes the two models in one IDF.
-1.0 if r["floor"] is None else r["floor"],
```

So `floor=-1.0 peak=-1.0` is **the T9-13 encoding of "this model uses no extremum"**, emitted for
the guest rooms as much as for the laundry. It is not a failure sentinel. `_schedule_standby_floor`
and `_schedule_peak` — the functions that CAN return `None` for a real characterisation failure —
are at `:2162-2163`, on the **T9-11 branch**, which arm E never took (`continue` at `:2160`).

The laundry objects were never "not characterised". They passed `_schedule_daytype_profiles`
successfully, produced valid `new_wd/new_we`, and were recorded as applied.

## The actual defect — a cache-key collision, `commercial_integration.py:2080-2094`

```python
def _t9_13_schedule_for(channel, r_wd, r_we, new_wd, new_we):
    key = (channel, round(float(r_wd), 4), round(float(r_we), 4))
    if key in _t9_13_cache:
        return _t9_13_cache[key]          # <-- new_wd / new_we DISCARDED
    nm = (f"MXU_{channel.capitalize()}_DHWv2_"
          f"r{int(round(key[1]*1000)):04d}w{int(round(key[2]*1000)):04d}_{tag}")
```

**The key does not contain the source schedule.** `new_wd/new_we` are the caller's per-object shape
and are used **only on a cache miss**. `r_wd`/`r_we` are computed from the *channel's* occupancy
(`_channel_occ_24`) against the *channel's* reference — they are identical for every object in a
channel. Therefore:

> **Within one channel, every `WaterUse:Equipment` object collapses onto ONE schedule, built from
> whichever object the iteration reached first.**

The generated name is itself the proof — `MXU_Hotel_DHWv2_r1000w1000_<tag>` encodes channel and `r`
and carries **no shape identity**. FINDING 8's own evidence table shows both laundry objects and the
guest rooms pointing at that one name. That is not a fallback; it is a hash collision by design.

`Peak_Flow_Rate` is correct per object (`:2146-2148`, computed from that object's own `info`) while
the schedule is wrong — which is exactly the signature observed, and which the
"could-not-characterise" story cannot explain.

## Residential carries the same defect class — `:1577`

```python
key = (hh_id, round(info["r_wd"], 4), round(info["r_we"], 4))
```

`hh_id` narrows it, but `r_wd/r_we` are functions of the **household occupancy only** — not of the
object's prototype schedule. Two `WaterUse:Equipment` objects in the same apartment Space with
different prototype schedules collide. The 0.9647 volume identity holding is weak evidence that this
tower is 1:1 Space-to-object, **not** proof; the fix must cover both paths and the assertion must be
measured, not assumed.

## Why the audit cannot see it — kind #8, restated correctly

`audit_dhw_shape_preservation:1197` iterates `applied` and reads **only `rec["t9_13"]`**, the `info`
dict returned by `apply_dhw_volume_scaling`. That dict is computed per object and is always
internally consistent, whatever schedule was subsequently assigned. D1-D5 therefore audit *the
arithmetic the injector performed*, never *the object it wrote into the IDF*. The earlier statement
— "the audit verifies the transformation it performed, never the assignment it changed" — was the
right diagnosis attached to the wrong cause.

## Consequence for D-A

D-A as put to the user is **withdrawn and replaced**:

| | withdrawn | replacement |
|---|---|---|
| fix | skip objects with `floor=-1.0 peak=-1.0` | put the source schedule in the cache key (both paths) |
| effect | **none** — no object takes that branch under T9-13 | one schedule per (channel, source schedule, r) |
| audit | D7 "schedule is unchanged or the derivative of its own original" | D7 as stated, but read **from the saved IDF**, not from `dhw_applied` |

D7 must re-open the written IDF and compare each object's `Flow_Rate_Fraction_Schedule_Name` against
the schedule *derived from that object's own prototype*. A D7 implemented over `dhw_applied` would
inherit the exact blindness it exists to close: `rec["derived_schedule"]` records the **cached** name,
so the collision would still read as a pass.

**Falsifiable prediction, written before the fix runs:** on `Y2022__Tall__MTL`, where `r = 1.000`,
the fixed injector must produce a **bit-identical** DHW result to `Default_NECB__Tall__MTL` for
every hotel object — `LAUNDRY SERVICE WATER USE` back to ~9.11e+11 J (from 2.76e+12), `F30
Hotel_bot_Laundry` back to ~2.66e+11 J (from 3.73e+11), guest rooms back to ×1.000 (from ×1.136).
If the guest rooms do **not** return to ×1.000, the collision was not the whole mechanism and this
correction is itself incomplete.

Note the guest-room prediction is the discriminating one: the ×1.136 was recorded above as "the
legitimate `r` effect", but at `r = 1.000` there is no legitimate `r` effect to have. That number
should not have been accepted as legitimate when it was written.

---

# Progress Log — FINDING 8 fix implemented (cache-key collision) — 2026-08-02 (evening)

**Employee session.** Scope: code fix + upload + smoke test. Campaign NOT launched (cell count is
the user's open call).

## TASK 1a — commercial path, `commercial_integration.py`

`_t9_13_schedule_for` now takes `proto` and keys on it:

```python
def _t9_13_schedule_for(channel, proto, r_wd, r_we, new_wd, new_we):
    key = (channel, str(proto).strip().upper(),
           round(float(r_wd), 4), round(float(r_we), 4))
    ...
    nm = (f"MXU_{channel.capitalize()}_DHWv2_{_sched_token(proto)}_"
          f"r{int(round(key[2]*1000)):04d}w{int(round(key[3]*1000)):04d}_{tag}")
```

Call site updated to pass `proto`. New module-level `_sched_token(proto)` (beside `_floor_key`):
upper-case, keep `[A-Z0-9]`, collapse the rest to `_`, truncate to 40 — and **above 40 chars it
appends an 8-hex MD5 of the full normalised prototype string**, so a truncation collision cannot
silently re-create the bug the token exists to fix. Two guards on top of that, both able to fail:

- `_t9_13_name_owner`: same generated name for two different keys → `AssertionError`, not a
  silent merge.
- `len(nm) > 100` → `AssertionError` (EnergyPlus alpha-field limit). A truncated Name would
  either break the reference or merge two schedules; both are worse than an abort.

Token behaviour on the real hotel schedules, verified locally:

| prototype | token | full name length |
|---|---|---|
| `HotelLarge LAUNDRY_SWH_SCH` | `HOTELLARGE_LAUNDRY_SWH_SCH` | 58 |
| `HotelLarge LaundryRoom_SWH_Sch_Post2004` | `HOTELLARGE_LAUNDRYROOM_SWH_SCH_POST2004` | 71 |
| `HotelLarge BLDG_SWH_SCH` | `HOTELLARGE_BLDG_SWH_SCH` | 55 |

No hash suffix is triggered on any real schedule in this IDF family, and nothing approaches 100
chars — so the names are of one convention throughout, as required.

## TASK 1b — residential path

Same change at the T9-13 branch of `inject_residential`:
`key = (hh_id, UPPER(proto), r_wd, r_we)`, name
`MXU_Residential_DHWv2_HH{hh_id}_{token}_r####w####`, with the same name-owner and length guards.

**Measurement, not assumption** (1b's explicit instruction): the injector now counts distinct
`(Space, prototype schedule)` pairs against the number of residential objects it saw and writes
both to the provenance (`residential_dhw_objects=`, `residential_dhw_space_proto_pairs=`) plus a
console line saying which of the two conclusions the count supports. **The number will be read off
the smoke-test provenance, not guessed here** — the log's own earlier note that the 0.9647 volume
identity is "weak evidence, not proof" of 1:1 is exactly why this is measured.

## TASK 1c — D7, read from the SAVED IDF

New `audit_dhw_assignment(saved_idf_path, applied, proto_before, ...)`, deliberately **not**
implemented over `result["dhw_applied"]`: `rec["derived_schedule"]` stores the *cached* name, so a
D7 built on it would have passed on arm E — the exact blindness it exists to close.

- `_we_proto_before` is snapshotted at the top of `inject_mixed_use`, before either DHW path
  writes, because both overwrite `Flow_Rate_Fraction_Schedule_Name` in place.
- After `idf.saveas`, the output IDF is **re-opened** and every `WaterUse:Equipment` object is
  checked: its assigned schedule is either **unchanged** from the source, or parses as
  `MXU_*_DHWv2_[HH<id>_]<TOKEN>_r####w####[_tag]` with `<TOKEN> == _sched_token(its own original
  schedule)`. Token comparison is **exact**, via `_DHWV2_NAME_RE` — a substring test would let
  `LAUNDRY_SWH_SCH` pass against `HOTELLARGE_LAUNDRY_SWH_SCH`'s schedule, which is the same
  family of near-miss the fix is about.
- A record in `dhw_applied` that claims a `prototype_schedule` the source IDF did not have is
  itself a D7 violation.
- Secondary check kept even though it is currently redundant: one derived name serving two
  distinct source schedules. It survives a change to the name grammar that the token parser
  would not.
- Wired into `t9_13_audit["counts"]["D7"]`, into `["violations"]`, into the `pass` verdict, and
  into the provenance as `t9_13_d7_pass=... n_wateruse=... n_own_derivative=... n_unchanged=...`
  plus one `t9_13_derived_name <name>` line per distinct derived schedule.

## TASK 1d — empty-audit N/A (open item 5)

`t9_13_audit["pass"]` is now tri-state and `["verdict"]` is `PASS` / `FAIL` / `N/A`. `N/A` is
emitted **only** when the cell requested no DHW channels at all (`_expect == ()`) *and* audited 0
objects *and* has no violations — the 4 `Default_NECB` controls. `n_audited == 0` with a non-empty
`_expect` stays a **FAIL**. D7 still runs on an N/A cell (it has untouched objects to check) and
can still turn it into a FAIL.

## TASK 1e — `agg_armE.sh` (open item 4)

The universal `n_audited == 47` assertion is **removed**, not widened: it was wrong for 30 of 56
cells (actual 47×26, 71×20, 31×6, 0×4), so its output line meant nothing. Replaced by a check that
can actually fail — *two cells with the same geometry and the same `channels_requested` must audit
the same number of objects* — reported as a full `(geometry, channels) -> n_audited` table with a
`NBAD` count of non-constant groups. Also added: verdict distribution (PASS/FAIL/N-A separated),
a D7 pass/fail/**absent** sweep (absent = a cell produced by the pre-fix injector), and the deduped
list of `MXU_*_DHWv2_*` names created across the arm.

Injector md5 after all of TASK 1: **`456301f5`** (was `56d6e324`).

Local `import` + token/regex round-trip verified. Nothing simulated yet — that is TASK 4.

---

# Progress Log — TASK 2: FINDING 7 option B, retail rewired to the calibrated pool — 2026-08-02

## The change — one thing

`3rdJ_07_aug_to_bem_4split.py::build_retail_product_2030` no longer reads
`at_retail_fraction_2030_{scenario}.csv` (built by Step-6's lever script from the RAW pool). It now
pools **`D2030` = `..._C_v2.csv`**, md5 `5aa74f44`, the same calibrated source every other 2030
channel uses. `assert_d2030_is_c` runs on the file it reads.

Everything else is preserved on purpose:

- **All 111,024 rows, all 3 bands, no band filter.** The lever files pooled all bands; so does
  this. FINDING 7's premise is that RAW and CAL are the *same rows*, so the difference is
  calibration and not frame — a band filter would destroy that. Asserted (`>= MIN_2030_ROWS`).
- **The lever still comes from `_derive_retail_lever()`**, i.e. from the Step-6 lever file's own
  `multiplier` column, which that function already asserts is a uniform scalar. The lever files
  remain the source of truth for the *scalar*; they are no longer the source of the *shape*.
- **Base / levered discipline unchanged**: `ret48 = sub[RET].mean()` → `np.roll(arr, 8)` → uniform
  lever → normalise against the **un-levered** pooled base peak, mirroring the 2026-07-28 fix.
- `RETAIL_LEVER_FILES` kept, with a comment stating what it is and is not the source of now.

**One thing the prompt got wrong, corrected by measurement.** The prompt specified
`PR ∈ {2→QC, 4→AB}`. That is the **2022 stock's** region remap. `_C_v2` carries **raw GSS province
codes** — `value_counts` gives `24 → 21,087` and `48 → 12,528` rows — and
`3rdJ_09E_retail_source_probe.py` already used 24/48. Using 2/4 would have selected the wrong
provinces and produced an empty-or-wrong channel. Coded as `D2030_RETAIL_PR = {"QC": 24, "AB": 48}`
with the measurement in the comment, and the function hard-fails on an empty PR selection rather
than shipping a silent zero.

Regeneration is a standalone `3rdJ_07R_regen_retail_2030.py` calling the *same* three functions the
pipeline call site calls — `--year 2030 --bundle X` would have rewritten four unrelated products,
and `--sens retail` covers only cons/opt.

## Pre-registered acceptance check — written and snapshotted BEFORE the rewire ran

`Step9_docs/3rdJ_09F_retail_rewire_check.py`. Thresholds taken from the FINDING 7 table already in
this log, not from the new product. The `--before` snapshot was taken against the shipped files
first and **reproduced every pre-registered "before" value exactly** — so the check is anchored to
the artefact, not to a story about it.

### A — what must move

| id | what | before | after | required | verdict |
|---|---|---|---|---|---|
| A1 | QC Weekday peak clock hour | 11 | **16** | 11 → 16 | **PASS** (all 3 bands) |
| A2 | AB Weekday peak clock hour | 14 | **16** | 14 → 16 | **PASS** (all 3 bands) |
| A3 | QC Saturday/Weekday contrast | 0.849 | **3.215** | 0.849 → 3.215 | **PASS** |
| A4 | AB Saturday/Weekday contrast | 1.009 | **3.399** | 1.009 → 3.399 | **PASS** |
| A5 | pooled-ALL Sat/Wd contrast, at source | RAW 0.980 | CAL **3.375** | 0.980 → 3.375 | **PASS** |

A5 is measured at the **source**, not on the product, and said so before it ran: the product only
carries `PR ∈ {QC, AB}` while the log's 0.98/3.38 row is `PR_GROUP='ALL'`. The 2022 observed anchor
re-derives at **2.687**, matching the log. The peak did move, so the rewire took effect.

Measured on `at_retail_fraction`, deliberately, not on `multiplier`: `multiplier` is overwritten by
the NECB proxy baseline wherever `staff_shoulder_flag == 1`, so its argmax can be pinned by the
proxy instead of by the occupancy source under test. That is the discarded-flag trap this channel
has already fallen into once (T9-10 retail, arm B).

### B — what must NOT move

| band | peak(multiplier) | required 0.95×lever | rows / PR / Day_Type | mult ∈ [0,1] |
|---|---|---|---|---|
| cons | 0.8550 | 0.8550 | 288 / {AB,QC} / 3 | ✓ |
| central | 0.9215 | 0.9215 | 288 / {AB,QC} / 3 | ✓ |
| opt | 0.9975 | 0.9975 | 288 / {AB,QC} / 3 | ✓ |

`run_retail_gates` H2/R1 passed unchanged for all three bands, and H5 lever ordering still holds.

**VERDICT: PASS**, 0 of 21 checks failed. No tolerance was touched.

## Artifacts

| file | new md5 | predecessor (`_BAK_2026-08-02`, kept on disk) |
|---|---|---|
| `retail_presence_multiplier_2030_cons.csv` | `82b425b5` | `0e3b256e` |
| `retail_presence_multiplier_2030_central.csv` | `11414644` | `cf8721c6` |
| `retail_presence_multiplier_2030_opt.csv` | `700398d0` | `f7152e5a` |

## 🔴 FLAG, not fixed — T9-12 `k = 0.60`

The T9-12 retail lighting re-spec calibrated `k = 0.60` **against the shape that just changed**
(see the k-sweep table earlier in this log: k=0.60 was picked for weekday-mean +0.2 % and lever
+2.69 %). Those two numbers were computed on the RAW-sourced retail shape whose weekday peak sat at
11:00. With the peak now at 16:00 they no longer describe the configuration that ships. **`k` needs
re-checking against the calibrated shape before any retail lighting result is quoted.** Per the
prompt: flagged, deliberately **not** re-tuned — re-tuning it now would be fitting the lever to the
first shape that appeared after a source change nobody has validated downstream yet.

## Scope note

This invalidates the arm-C/arm-E **retail** results, as FINDING 7 predicted it would. Nothing has
been re-simulated; the 2030-family campaign is the user's open call.

---

# Progress Log — TASK 3 upload + TASK 4 smoke launched (job 1171438) — 2026-08-02

## TASK 3 — office product uploaded, md5 verified ON the cluster

`squeue -u o_iseri` was empty before overwriting anything — arm E is finished, so the
mid-array-corruption risk the upload was being held for is gone.

| file | local md5 | cluster md5 after `scp` | was on cluster |
|---|---|---|---|
| `office_presence_multiplier_2030.csv` | `575d17e5` | **`575d17e5`** ✓ | `1536c98c` (the predecessor) |
| `eSim_bem_utils/commercial_integration.py` | `456301f5` | **`456301f5`** ✓ | `56d6e324` (pre-fix) |
| `retail_presence_multiplier_2030_cons.csv` | `82b425b5` | **`82b425b5`** ✓ | `0e3b256e` |
| `retail_presence_multiplier_2030_central.csv` | `11414644` | **`11414644`** ✓ | `cf8721c6` |
| `retail_presence_multiplier_2030_opt.csv` | `700398d0` | **`700398d0`** ✓ | `f7152e5a` |

`office_presence_multiplier_2030_BAK_2026-08-02.csv` (`1536c98c`) stays on disk locally, as
instructed. Also uploaded: `3rdJ_07_aug_to_bem_4split.py`, `3rdJ_07R_regen_retail_2030.py`,
`agg_armE.sh`, `3rdJ_09F_smoke_f8fix.py`, `3rdJ_09F_retail_rewire_check.py`, `smoke_f8fix.sh`.

## TASK 4 — smoke test SUBMITTED, job **1171438**

`sbatch smoke_f8fix.sh`, `-p ps`, `--mem=16G`, **`-t 7-00:00:00`**. Nothing ran on the login node.

Two cells into a fresh `out_F_f8fix`:

- **cell 0 = `Default_NECB__Tall__MTL`** — injects nothing. Re-run rather than reused so that
  open item 5's new **N/A** verdict and D7-over-untouched-objects are actually exercised. A gate
  has to be seen working.
- **cell 1 = `Y2022__Tall__MTL`** — the T9-13 reference year, `r = 1.000`, so DHW must be a
  bit-for-bit no-op.

Two guards, both able to stop the job:

- the wrapper **refuses to run** unless the injector md5 is `456301f5`. A smoke test accidentally
  run on the pre-fix injector would produce arm-E numbers and read as a reproduction.
- the scorer FAILs if no `t9_13_d7_pass` line exists (i.e. a pre-fix cell), and FAILs — loudly,
  as **VACUOUS** — if it cannot find the `F31–F37 *GUESTRM` objects at all, rather than reporting
  a pass over an empty set.

Predictions are constants inside `3rdJ_09F_smoke_f8fix.py`, transcribed from the table above
before the run. Tolerance `|ratio − 1| ≤ 0.002`; the guest rooms' arm-E excess is 136× that band,
so nothing that matters can hide inside it. The scorer also reports **every other**
`WaterUse:Equipment` object against the same no-op requirement even though no prediction was
registered for them — at `r = 1.000` a correct T9-13 is a no-op on all of them, and only reporting
the objects the hypothesis needs is the failure mode this log already has seven names for.

Plus a cross-check the prompt did not ask for: the new `Default_NECB` cell is scored **against the
old arm-E `Default_NECB`**, to confirm the reference itself did not move under the new injector.
If it did, every ratio in the main table is measured against a shifted baseline.

Result to follow when the job lands.

---

# Progress Log — IDF-level verification of the FINDING 8 fix (local, pre-simulation) — 2026-08-02

Ran `inject_mixed_use` locally on the smoke cell's own inputs (`Y2022__Tall__MTL`, v242 Tall IDF,
`calibrated_v2` lighting, `volume_scaled` DHW) — injection only, no EnergyPlus. This settles the
mechanism question at the IDF level while the cluster job simulates.

## The collision, gone

`MXU_*_DHWv2_*` schedules created, **per channel**:

| channel | before the fix | after the fix | the source schedules now kept apart |
|---|---|---|---|
| hotel | **1** | **4** | `HotelLarge BLDG_SWH_SCH`, `HotelLarge GuestRoom_SWH_Sch`, `HotelLarge LAUNDRY_SWH_SCH`, `HotelLarge LaundryRoom_SWH_Sch_Post2004` |
| office | 1 | 1 | `OfficeLarge BLDG_SWH_SCH` — only one prototype exists |
| retail | 1 | 1 | `RetailStandalone BLDG_SWH_SCH` — only one prototype exists |
| residential | 27 | 27 | `ApartmentHighRise Apt_DHW_Sch`, one per household |

**33 distinct schedules, up from 30.** The whole delta is the hotel channel, and it is exactly the
four prototypes FINDING 8 said were collapsing onto one. `MXU_Hotel_DHWv2_r1000w1000_Y2022` — the
name with no shape identity in it — no longer exists; the four replacements are
`MXU_Hotel_DHWv2_HOTELLARGE_LAUNDRY_SWH_SCH_r1000w1000_Y2022` and its siblings. Office and retail
staying at 1 is not the fix failing: each of those channels genuinely has one prototype, so one
schedule is the correct cardinality.

## D7 — and it ran on the file, not on the dict

```
[T9-13 audit PASS] 47 objects: shape, peak hour, night share and Fraction bound all preserved
[D7 PASS] 47 WaterUse:Equipment objects in the saved IDF: 47 on a derivative of their OWN
          schedule, 0 unchanged, 0 pointing at another object's schedule
counts = {D1:0, D2:0, D3:0, D4:0, D5:0, D6:0, D7:0}
```

Re-read from the saved IDF, token-matched exactly against each object's own original schedule.
Longest generated name is 71 characters (`..._HOTELLARGE_LAUNDRYROOM_SWH_SCH_POST2004_...`), well
inside EnergyPlus's 100-character alpha field, so no hash-suffix form was triggered and every name
follows one convention. No name-collision assertion fired.

## TASK 1b's measurement — answered, and it is the boring answer

```
[FINDING 8 measure] residential objects=27 distinct (Space, prototype schedule) pairs=27
                    -> 1:1, this path was NOT colliding
```

**27 objects, 27 distinct `(Space, prototype)` pairs.** The residential path is 1:1 in this tower,
so the collision never fired there — the log's earlier caution that the 0.9647 volume identity was
"weak evidence, not proof" was right to insist on measuring it, and the measurement agrees with the
weak evidence. The fix is applied to that path anyway: it is 1:1 *in this IDF*, which is a property
of the building, not of the code.

## What this does NOT yet show

Nothing here is energy. The IDF says the right objects now carry the right schedules; whether
`LAUNDRY SERVICE WATER USE` returns to ~9.1147e+11 J and whether the guest rooms return to ×1.000
is what job 1171438 is running, and it is the only thing that closes FINDING 8.

---

# Progress Log — D7 and the N/A verdict SEEN FAILING, not just passing — 2026-08-02

This project has eight recorded kinds of vacuous gate. A new gate that reports PASS on the first
cell it meets is not evidence of anything, so both new checks were made to fail on purpose before
either was believed.

## 1. The name-collision assert — first line of defence

Re-created the pre-fix behaviour by forcing `_sched_token` to return one constant for every
prototype (which is what "the source schedule is not in the key" amounts to). The injector
**aborted** rather than merging:

```
T9-13 schedule-name collision: 'MXU_Hotel_DHWv2_COLLAPSED_r1000w1000_BROKEN' generated for BOTH
  ('hotel', 'HOTELLARGE BLDG_SWH_SCH', 1.0, 1.0)
  and ('hotel', 'HOTELLARGE LAUNDRYROOM_SWH_SCH_POST2004', 1.0, 1.0)
```

## 2. D7 itself — against FINDING 8's exact signature

The assert above cannot catch a collision whose *name* does not clash (the pre-fix code, where the
name carried no shape identity at all), so D7 was tested directly. Took the good injected IDF,
re-pointed **both** laundry objects at the guest-room derived curve — literally the substitution
FINDING 8 documented — re-saved, and ran `audit_dhw_assignment` against the uninjected tower as
`proto_before`:

```
[D7 FAIL] 2 violations over 47 objects
  D7 F30 Hotel_bot_Laundry Service Water Use 2.56gpm 140F:
     assigned 'MXU_Hotel_DHWv2_HOTELLARGE_GUESTROOM_SWH_SCH_r1000w1000_Y2022' carries source token
     'HOTELLARGE_GUESTROOM_SWH_SCH' but this object's own schedule is
     'HotelLarge LaundryRoom_SWH_Sch_Post2004' -- it is on ANOTHER object's derived schedule
  D7 Laundry Service Water Use 30.6gpm 180F:
     ... own schedule is 'HotelLarge LAUNDRY_SWH_SCH' -- it is on ANOTHER object's derived schedule
```

**Exactly the two objects in FINDING 8's evidence table, with the correct diagnosis, and 45 clean.**
D7 would have caught this before 56 cells were run. That is the claim made for it in the FINDING 8
correction, and it is now demonstrated rather than asserted.

## 3. The N/A verdict — exercised, and it is narrow

`Default_NECB__Tall__MTL` injected locally with `--dhw-model volume_scaled`:

```
[T9-13 audit FAIL] 0 objects audited -- a gate that never ran is not a PASS
[T9-13 audit N/A]  this cell requested no DHW channels -- nothing to audit, and nothing injected
[D7 PASS] 47 WaterUse:Equipment objects: 0 on a derivative of their own schedule,
          47 unchanged, 0 pointing at another object's schedule
t9_13_audit_pass=None   t9_13_audit_verdict=N/A   t9_13_d7_pass=True n_unchanged=47
```

Both lines are printed on purpose. The inner FAIL-on-empty rule still fires and is still visible;
the N/A is an explicit relabel of that one case, gated on `channels_requested=[]`, not a widening
of the rule. And the cell is not unchecked: **D7 ran over all 47 objects and required every one to
be byte-identical to the source IDF.** A control cell that silently modified something would still
FAIL.

## Verified locally, both cells

| | `Y2022__Tall__MTL` | `Default_NECB__Tall__MTL` |
|---|---|---|
| verdict | PASS | **N/A** |
| n_audited | 47 | 0 |
| D1–D7 counts | all 0 | all 0 |
| D7 | PASS, 47 own-derivative | PASS, 47 unchanged |

---

# Progress Log — TASK 4 SMOKE TEST, measured result — 2026-08-02

Jobs: **1171438** (2 cells, simulated) · **1171441/1171442** (rescore) · **1171443** (attribution)
· **1171445** (residual diagnosis) · **1171446** (peak-flow check). Campaign **NOT** launched.

Both E+ runs completed clean: return code 0, fuel-closure residual 0.0000 % on Electricity and
NaturalGas, channel-closure 0.0000 % on lights / equip / gasequip.

The scorer in job 1171438 died before printing anything: a multi-line f-string, legal on the local
Python 3.13 (PEP 701) and a `SyntaxError` on the cluster's 3.10. **My local `py_compile` was not a
valid check and I had treated it as one.** Fixed, and the rescore job now compiles the scorer under
the actual interpreter and refuses to score if it does not. No re-simulation was needed — the
`.sql` files persist.

## The smoke table — predicted vs measured

`Y2022__Tall__MTL` / `Default_NECB__Tall__MTL`, `WATER USE EQUIPMENT HEATING ENERGY`, annual J.
Predictions are the pre-registered ones from the task prompt; none were altered.

| object | arm E | predicted | measured | verdict |
|---|---|---|---|---|
| `LAUNDRY SERVICE WATER USE` | x3.028 (2.7598e+12 J) | x1.000 (~9.1147e+11 J) | **x1.000** (9.1145e+11 J) | **PASS** |
| `F30 HOTEL_BOT_LAUNDRY` | x1.399 (3.7251e+11 J) | x1.000 (~2.6625e+11 J) | x1.019 (2.7124e+11 J) | **FAIL** |
| `F31-F37 HOTEL_MID_*_GUESTRM` (all 8) | x1.136 | x1.000 | **x1.000** (worst dev 0.0000) | **PASS** |
| `F38 HOTEL_TOP_KITCHEN` | x0.998 | x1.000 | x0.995 | **FAIL** |
| `BOOSTER SERVICE WATER USE` | x0.995 | x1.000 | x0.995 | **FAIL** |

Plus 4 objects that carried no pre-registered prediction and are off the no-op requirement:
`F1`/`F2 RETAIL_*_BACKSPACE` x0.923, `F3-F11`/`F12-F20 OFFICE_RESTROOM` x0.952.

**Scorer verdict as run: 9 PASS / 7 FAIL.** That is the recorded result. The misses are not
repaired. What follows is what they are, measured — not an argument for discounting them.

## The discriminating case passed

The prompt named the guest rooms as the case that decides whether the correction is complete:
*"if they do not return to x1.000 the correction is incomplete."* All 8 went x1.136 -> **x1.000**,
worst |ratio - 1| = 0.0000. The main laundry went x3.028 -> x1.000. **FINDING 8 is fixed.**

At the IDF level: the hotel channel went from **1** DHWv2 schedule to **4**, one per prototype
(`BLDG_SWH_SCH`, `GuestRoom_SWH_Sch`, `LAUNDRY_SWH_SCH`, `LaundryRoom_SWH_Sch_Post2004`); 33
distinct `MXU_*_DHWv2_*` names total. Office and retail stay at 1 because each genuinely has one
prototype — that is not the collision, and the scorer prints the per-channel count so a channel
stuck at 1 cannot pass unnoticed.

## Attribution — the fix, or something else? (job 1171443)

Scoring arm-E-Y2022/arm-E-NECB against fixed-Y2022/fixed-NECB per object separates the two:

| group | arm E | fixed | d = fixed/armE | attribution |
|---|---|---|---|---|
| 12 guest rooms (F31-F37 + F38) | 1.136 | **1.000** | 0.8800 | moved by the fix |
| `LAUNDRY` | 3.028 | **1.000** | 0.3303 | moved by the fix |
| `F30 HOTEL_BOT_LAUNDRY` | 1.399 | 1.019 | 0.7281 | moved by the fix, 95 % of the error removed |
| `F38 HOTEL_TOP_KITCHEN` | 0.998 | 0.995 | 0.9976 | moved by the fix |
| `BOOSTER` | 0.995 | 0.995 | **1.0000** | **the fix never touched it** |
| retail x2, office restroom x2 | 0.923 / 0.952 | 0.923 / 0.952 | **1.0000** | **the fix never touched them** |
| residential F22-F29 (13) | — | — | ~1.004 | moved by the fix |
| residential F21 (13) | — | — | 1.0000 | untouched |

29 objects moved, 18 did not. **So three of the seven misses are objects the fix provably did not
touch** (d = 1.0000 exactly): the pre-registered claim that BOOSTER would return from x0.995 to
x1.000 was simply a wrong prediction — it was never a collision victim. That is a mis-prediction
recorded as a FAIL, not a fix that fell short.

Reference-cell sanity: worst |ratio - 1| between the new NECB and the arm-E NECB = **1.6e-5** over
47 objects. My script labelled that "REFERENCE MOVED" because its threshold was 1e-6; the threshold
is too tight for E+ re-run reproducibility. Recording the number and the mislabel rather than
quietly loosening it — 1.6e-5 is four orders below anything discussed here.

## What the residuals actually are — FINDING 9 (job 1171445)

Hypothesis formed before measuring: `_build_compact_fields_2dt` rebuilds every modulated schedule
on **two** day types (weekday / weekend). Any prototype whose **Saturday and Sunday profiles
differ** cannot survive that, even at r = 1.000, because two source profiles are folded into one.

Tested by predicting each object's ratio from the **schedules alone** — calendar-weighted annual
mean of the rebuilt `Schedule:Compact` over the annual mean of the source `Schedule:Year ->
Week:Daily -> Day:Interval`, never reading the energy results:

| prototype | Sat == Sun? | predicted | measured | agrees? |
|---|---|---|---|---|
| `RetailStandalone BLDG_SWH_SCH` | no | 0.9234 | 0.923 | yes |
| `OfficeLarge BLDG_SWH_SCH` | no | 0.9524 | 0.952 | yes |
| `HotelLarge BLDG_SWH_SCH` (booster, kitchen) | no | 0.9953 | 0.995 | yes |
| `HotelLarge GuestRoom_SWH_Sch` | YES | 1.0000 | 1.000 | yes |
| `HotelLarge LAUNDRY_SWH_SCH` | YES | 1.0000 | 1.000 | yes |
| `HotelLarge LaundryRoom_SWH_Sch_Post2004` (F30) | YES | 1.0000 | 1.019 | **no** |

**Confirmed for every commercial object but one, to three decimals, from the schedule structure
alone.** This is a distinct, pre-existing defect — call it **FINDING 9** — and it is *not* caused
by the FINDING 8 fix (d = 1.0000 for all of these). It has been in every DHW arm run to date:
retail DHW volume -7.7 %, office -4.8 %, hotel BLDG_SWH_SCH -0.5 %, at r = 1.000 where T9-13 is
supposed to be a no-op. **Flagged, not fixed** — it is outside this prompt's scope.

Residential is deliberately *not* predicted by that column: peak flow is rescaled per household
(`peak_policy: rescale`), which the schedule-only predictor excludes by construction. Job 1171446
confirms the split — commercial peaks change only in the 6th significant figure (x1.000001, a float
round-trip through eppy) while residential peaks move x0.711...x1.574. Designed behaviour.

## The one residual with no explanation

`F30 HOTEL_BOT_LAUNDRY`, measured x1.019 against a schedule-only prediction of exactly 1.0000 (its
prototype has Sat == Sun, so the rebuild is lossless) and a peak-flow ratio of 1.000001.

- candidate (a) *the injector rescaled its peak flow* — **excluded by measurement** (job 1171446).
- candidate (b) *plant-loop coupling*: the main `LAUNDRY` draw on the same service-water system
  fell 67 %, which can move loop and mains temperatures and hence another object's heating energy
  at unchanged flow. **Untested. Recorded as the remaining candidate, not as the answer.**

1.9 % on one hotel object. It is a FAIL against a pre-registered 1.000 and it stays a FAIL.

## Audit, D7, names

```
Y2022__Tall__MTL      t9_13_audit_verdict=PASS  n_audited=47
                      counts={'D1':0,'D2':0,'D3':0,'D4':0,'D5':0,'D6':0,'D7':0}
                      t9_13_d7_pass=True n_wateruse=47 n_own_derivative=47 n_unchanged=0 n_violations=0
                      residential_dhw_objects=27 residential_dhw_space_proto_pairs=27
                      33 distinct MXU_*_DHWv2_*  ->  Hotel=4, Office=1, Residential=27, Retail=1
Default_NECB__Tall__MTL  t9_13_audit_verdict=N/A  pass=None  n_audited=0
                      t9_13_d7_pass=True n_wateruse=47 n_own_derivative=0 n_unchanged=47
```

The 6 non-residential names: `MXU_Hotel_DHWv2_HOTELLARGE_{BLDG_SWH_SCH, GUESTROOM_SWH_SCH,
LAUNDRYROOM_SWH_SCH_POST2004, LAUNDRY_SWH_SCH}_r1000w1000_Y2022__Tall__MTL`,
`MXU_Office_DHWv2_OFFICELARGE_BLDG_SWH_SCH_r1000w1000_...`,
`MXU_Retail_DHWv2_RETAILSTANDALONE_BLDG_SWH_SCH_r1000w1000_...`. Longest is 71 chars, inside the
100-char limit, so no hash-suffix form was triggered and all names follow one convention.

The **arm-E** provenance for the same cell records `counts={'D1'..'D6'}` and **zero**
`t9_13_derived_name` lines — the pre-fix injector recorded neither the derived names nor D7, which
is precisely why the collision ran 112 cells undetected.

## Gap: the volume identity could not be re-verified

The only water variable in these `.sql` files is `Water Use Equipment Heating Energy` (plus the
`WaterSystems:` meters). `WATER USE EQUIPMENT TOTAL VOLUME` is not requested, so every volume
column reads nan and the log's **0.9647 volume identity was not re-checked in this cell**. Stated
as a gap, not scored as a pass. Residential aggregate energy moved 1.6848e+12 -> 1.6452e+12 J
(0.9764) — informational, since residential r is per household at Y2022 by design.

## Status

- TASK 1 (FINDING 8 cache-key collision) — **fixed and confirmed at the energy level.**
- TASK 2 (FINDING 7 retail rewire) — done, 21/21 pre-registered checks PASS.
- TASK 3 (office product upload) — done, md5 verified on the cluster.
- TASK 4 (smoke test) — **run; 9 PASS / 7 FAIL recorded as measured.** 3 of the 7 are objects the
  fix provably never touched, 3 more are FINDING 9, 1 (F30, 1.9 %) is unexplained.
- **Campaign NOT launched.** The cell count is the user's open call.
- Open, flagged not fixed: **FINDING 9** (2-day-type rebuild loses Sat != Sun); F30's 1.9 %;
  T9-12's `k = 0.60` needs re-checking after the retail rewire; volume identity unverified here.

New artefacts (all under `Leg3_4-split/`): `Step9_docs/3rdJ_09F_smoke_delta.py` (attribution),
`Step9_docs/3rdJ_09F_daytype_loss.py` (FINDING 9 diagnosis), `Step9_docs/3rdJ_09F_peakflow_check.py`,
`Step8_docs/{rescore,delta,daytype}_f8fix.sh`.

---

# Progress Log — FINDING 9 FIXED (code + gate), smoke LAUNCHED — 2026-08-02

Injector md5 `456301f5` -> **`1601f10f`** (2874 -> 2970 lines). Unit suite 40/40 -> **58/58**.
Smoke job **1171448** (arm G, `out_G_f9fix`, same two cells as arm F so the comparison is
object-by-object). Campaign still NOT launched.

## The defect, located

Two halves, and both had to go:

| | file:line | what it did |
|---|---|---|
| read | `_week_profiles:595-602` | `d_we = _find_schedule(sun) or _find_schedule(sat)` — **Saturday discarded** whenever Sunday resolved; Holiday (`names[7]`) never read at all; Monday silently stood for all five weekdays |
| read | `_schedule_daytype_profiles` compact branch | `we = we if we is not None else vals` — first of Weekend/Saturday/Sunday wins, the rest dropped |
| write | `_build_compact_fields_2dt:210` | emitted that one profile to `For: Weekends Holidays AllOtherDays` |

So a prototype with a busy Saturday and a quiet Sunday had Saturday overwritten with Sunday, and
T9-13 — specified to carry the intra-day shape through untouched and to be an **exact no-op at
r = 1** — was neither.

## The fix

- `_ALL_DAYTYPES` = Monday..Friday + Saturday + Sunday + Holidays. `_daytypes_for_tokens()` maps
  EnergyPlus `For:` tokens onto them, with `AllDays`/`AllOtherDays` treated as **fill-the-gaps**
  so they can never overwrite a day type an explicit block claimed.
- `_week_profiles` / `_schedule_daytype_profiles` now return `by_daytype` alongside `wd`/`we`.
  **`wd` and `we` keep their exact former meaning** — nothing outside T9-13 shifts, and the r
  values that drive every existing number are untouched. The new key is purely additive.
- `_fill_daytypes()` completes a partial map and **names what it filled** in the provenance.
- `_build_compact_fields_by_daytype()` writes one block per DISTINCT profile, grouping identical
  day types onto one `For:` line — so a genuine two-curve prototype still emits two blocks and the
  schedule does not bloat. Design days ride with the weekday group; the last block carries
  `AllOtherDays` so coverage is total. An incomplete map **raises** rather than filling silently.
- `apply_dhw_volume_scaling(..., proto_by_daytype=)` scales each day type on its own curve by its
  CLASS ratio (weekdays `r_wd`; Saturday/Sunday/Holidays `r_we`). The volume target is unchanged —
  only the shape stops being lost. Omitting the argument reproduces the old behaviour exactly, and
  that path is the named fallback, reported as `t9_13_daytype_FALLBACK`.

## Verified on the real tower, before any simulation

`3rdJ_09G_finding9_verify.py` injects the two cells with the **same call the campaign driver
makes**, then runs the independent schedule-only predictor (`3rdJ_09F_daytype_loss.py`, its own
IDF parser) on the result. At r = 1.000 the answer must be exactly 1.0000:

| prototype | Sat == Sun? | before | after |
|---|---|---|---|
| `RetailStandalone BLDG_SWH_SCH` | no | 0.9234 | **1.0000** |
| `OfficeLarge BLDG_SWH_SCH` | no | 0.9524 | **1.0000** |
| `HotelLarge BLDG_SWH_SCH` | no | 0.9953 | **1.0000** |
| `HotelLarge GuestRoom_SWH_Sch` | YES | 1.0000 | 1.0000 |
| `HotelLarge LAUNDRY_SWH_SCH` | YES | 1.0000 | 1.0000 |
| `HotelLarge LaundryRoom_SWH_Sch_Post2004` | YES | 1.0000 | 1.0000 |

Audit `PASS`, 47 objects, `counts={D1..D6:0, D8:0, D7:0, D9:0}`, `d8_unchecked=[]`,
`daytype_fallback=None`. FINDING 8's six derived hotel/office/retail schedules are intact, and the
`Default_NECB` control still reports `N/A`.

## 🔴 The first gate I wrote for this was vacuous, and the falsification is what caught it

**D8** compares the achieved per-day-type volume ratio against `r(class)/R`, using the numbers the
injector recorded. Re-creating the collapse **in the reader** (`Saturday := Sunday`) on the real
tower left D8 at **0 violations** — because the corrupted Saturday was simultaneously its
reference and its target. A gate whose reference is derived from the same source it audits cannot
fail. That is the **ninth** vacuous-test shape recorded on this project, and it is the one that
generalises: every previous kind was about scope or reachability; this one is about *provenance of
the reference*.

So **D9** was added, modelled on D7: it re-opens the **SAVED IDF** and, for each object, expands
the assigned `MXU_*` schedule and that object's **own prototype** (which the injector never
deletes) and requires `mean(assigned_d)/mean(prototype_d) == r(class)/R` on every day type.
Neither side is a number the injector reported about itself.

**D9 seen failing on the real tower.** Patching the *writer* back to its pre-fix form (strip
`new_by_daytype`, which routes to the documented 2-day-type fallback — byte-for-byte the old
behaviour) and re-injecting:

```
verdict=FAIL  D9 violations=6  objects flagged=6
    Booster Service Water Use 1.33gpm 180F
    F1 Retail_F1_BackSpace Service Water Use 0.3gpm 140F
    F12-F20 Office_Restroom Service Water Use 5.22gpm 140F
    F2 Retail_F2_BackSpace Service Water Use 0.3gpm 140F
    F3-F11 Office_Restroom Service Water Use 5.22gpm 140F
    F38 Hotel_top_Kitchen Service Water Use 2.77gpm 140F
```

Exactly the six pre-registered objects — every prototype with Saturday != Sunday — and **not** the
12 guest rooms, 2 laundries or 27 apartments, whose prototypes have Saturday == Sunday. The
prediction was written into the script before it was run.

**Stated limit, not papered over:** neither D8 nor D9 can catch a defect in
`_schedule_daytype_profiles` itself, since both consult it. The independent check for that is
`3rdJ_09F_daytype_loss.py`, which parses the IDF with its own parser and is run by the verifier and
by the smoke job.

Unit suite additions (group 9, T41–T58): the writer's block grouping, Saturday/Sunday separation,
design-day carriage, total coverage, the raise on an incomplete map, D8 failing on the collapsed
signature, D8 still failing at r != 1, and **T48 — D4 alone does NOT catch it**, which is the test
that justifies D8/D9 existing at all.

## Pre-registered for smoke job 1171448 (written before the run, in the scorer)

Arm G vs arm F, each over its own `Default_NECB`:

- **must move to 1.000**: `F1`/`F2 RETAIL_*_BACKSPACE` 0.923, `F3-F11`/`F12-F20 OFFICE_RESTROOM`
  0.952, `BOOSTER` 0.995, `F38 HOTEL_TOP_KITCHEN` 0.995.
- **must NOT move**: `F30 HOTEL_BOT_LAUNDRY` stays **1.019**, `LAUNDRY` 1.000, 12 guest rooms
  1.000, 27 residential objects unchanged from arm F to within 0.002.
- any other object that moves is counted as a FAIL.

**`F30` is the discriminating one.** The FINDING 8 report attributed its 1.9 % residual to
something other than the day-type collapse, because its prototype has Saturday == Sunday. If F30
comes back at 1.000, that attribution was wrong and it will be recorded as wrong, not adjusted.

**Injector md5 correction, same session:** `1601f10f` -> **`233932d7`**. The residential path has its
own `result` dict, so its `t9_13_daytype_fallback` list was never lifted into the one the provenance
writer reads — a fallback nobody can see is the same failure as no fallback report. Empty on this
tower (all residential prototypes have Sat == Sun), so no number moves; fixed anyway. Smoke job
**1171448 was cancelled 6 minutes in and relaunched as 1171449** rather than shipping a smoke whose
INJ_HASH does not match the injector the campaign will use.

## FINDING 9 smoke — job 1171449 — **10 PASS / 0 FAIL**, CLOSED

`COMPLETED 00:41:48`, exit 0. Arm G `out_G_f9fix/campaign_233932d7` vs arm F
`out_F_f8fix/campaign_456301f5`, each over its own `Default_NECB`. Predictions were hard-coded in
`3rdJ_09G_score_f9.py` and uploaded before the cells ran; none was altered.

| object | arm F | required | arm G | verdict |
|---|---|---|---|---|
| `F1 RETAIL_F1_BACKSPACE` | 0.923 | 1.000 | **1.000** | PASS |
| `F2 RETAIL_F2_BACKSPACE` | 0.923 | 1.000 | **1.000** | PASS |
| `F3-F11 OFFICE_RESTROOM` | 0.952 | 1.000 | **1.000** | PASS |
| `F12-F20 OFFICE_RESTROOM` | 0.952 | 1.000 | **1.000** | PASS |
| `BOOSTER` | 0.995 | 1.000 | **1.000** | PASS |
| `F38 HOTEL_TOP_KITCHEN` | 0.995 | 1.000 | **1.000** | PASS |
| `F30 HOTEL_BOT_LAUNDRY` | 1.019 | **stays 1.019** | **1.019** | PASS |
| `LAUNDRY` | 1.000 | 1.000 | 1.000 | PASS |
| 12 guest rooms | 1.000 | 1.000 | worst dev **0.0000** | PASS |
| 27 residential | — | unchanged | worst \|G−F\| **0.0000** | PASS |
| any other object moving | — | none | **0 moved** | PASS |

Audit: `verdict=PASS n_audited=47 counts={D1..D6:0, D8:0, D7:0, D9:0}`,
`d7_pass=True n_own_derivative=47 n_d7=0 n_d9=0 d9_unchecked=0`. Control cell still `N/A` with D7
holding all 47 objects byte-identical. No `t9_13_daytype_FALLBACK` line in either cell.

**The discriminating prediction held.** `F30 HOTEL_BOT_LAUNDRY` was required to stay at **1.019**,
because its prototype has Saturday == Sunday and FINDING 9 therefore never touched it. It came back
at 1.019 to three decimals. Had it moved to 1.000, the FINDING 8 attribution of that 1.9 % would
have been wrong; it did not, so **F30's residual remains a separate, still-unexplained item** with
peak-flow rescale excluded by measurement and plant-loop coupling the untested candidate. Nothing
about that was adjusted after the fact.

The independent schedule-only predictor — its own IDF parser, the guard that covers what D8 and D9
structurally cannot — now returns **1.0000** for all 18 commercial objects across all 6 prototypes,
including the three with Saturday != Sunday. Residential still spans 0.6706–0.9977 because its `r`
is per household by design.

### What this means for arms A–E

FINDING 9 was present in **every** DHW arm run to date. The correction is a level shift on the DHW
channel wherever `--dhw-model volume_scaled` was used, of the size measured here:
retail **+7.7 %**, office **+4.8 %**, hotel `BLDG_SWH_SCH` objects **+0.5 %**, guest rooms and
laundries unaffected. Arm E's scorecard has not been re-issued — that is a user decision, recorded
in the 2026-08-03 manager prompt, not taken here.

### Status at end of session

- FINDING 7 — fixed, 21/21.
- FINDING 8 — fixed, confirmed at the energy level (9 PASS / 7 FAIL recorded as measured; 3 of the
  7 were objects the fix never touched, 3 were FINDING 9, 1 is F30).
- FINDING 9 — fixed, **10 PASS / 0 FAIL**, gate D9 seen failing on the real tower first.
- **Campaign NOT launched.** Cell count is the user's open call, and FINDING 9 widens it: the fix
  changes DHW in every `volume_scaled` cell, not only the 36 stale 2030 ones.
- Still open, flagged not fixed: F30's 1.9 %; T9-12's `k = 0.60` after the retail rewire; the
  volume identity unverifiable until `WATER USE EQUIPMENT TOTAL VOLUME` is added to the outputs.

Handoff: `improvements/prompts/3rdJ_L3_manager_prompt_2026-08-03.md`.

---

# ARM H — THE POST-FINDING-6/7/8/9 CAMPAIGN. LAUNCHED — job `1171496`, 2026-08-03

## The scope decision — the user's call, made and recorded

Asked as the first action of the session, with the four facts that constrain it. Ruling:
**"lance la campagne 56 cells avec volume_scaled"** — all 56 cells, one arm, `--dhw-model
volume_scaled`. Arm E's scorecard is **re-issued after** this campaign lands, not annotated now.

Why 56 and not the 36 stale 2030-family cells: FINDING 9 changes DHW in **every** cell that runs
`volume_scaled`, not only the 2030 family (retail +7.7 %, office +4.8 %, hotel `BLDG` +0.5 %). The
2030-only re-run was sufficient for FINDINGS 6 and 7 alone; it stopped being sufficient the moment
FINDING 9 was found. `Y2022` and the three historical years are in scope for the DHW reason, not
for the product reason.

## What arm H is

Same two model flags as arm E (`--lighting-model calibrated_v2 --dhw-model volume_scaled`), so
`H − E` isolates the four fixes and nothing else. Everything that differs is upstream of the flags:

| | fix | carrier | md5 |
|---|---|---|---|
| FINDING 6 | office 2030 rebuilt on the matched stock frame | `office_presence_multiplier_2030.csv` | `575d17e5` |
| FINDING 7 | retail 2030 rewired to the calibrated `_C_v2` pool | 3 × `retail_presence_multiplier_2030_*.csv` | `82b425b5` / `11414644` / `700398d0` |
| FINDING 8 | DHW schedule cache-key collision | `commercial_integration.py` | `233932d7` |
| FINDING 9 | per-day-type Saturday/Sunday volume loss | same injector | `233932d7` |

Submit script: `Step8_docs/3rdJ_08D_campaign_speed_armH.sh` (md5 `da7085b9`), array `0-55%20`,
`-t 7-00:00:00`, outroot `campaign/out_H_allfix`. Nothing ran on the login node: `ls`, `scp`,
`sbatch` only.

## Open item 3 CLOSED in the same change — and the reason is a vacuous-gate reason

`Water Use Equipment Total Volume` was never requested as an output, so every volume column in
arms A–E reads `nan`. It is now requested (`DHW_VOLUME_VARIABLE`, `3rdJ_08P_probe_driver.py`) and
written per channel to `dhw_volume_hourly.csv` by `_do_postprocess()`.

The motive is not convenience. The only existing statement of the T9-13 volume identity (0.9647)
comes from `3rdJ_09E_dhw_identity_probe.py`, which computes `Σ Peak_Flow × (5·mean_wd + 2·mean_we)/7`
**by parsing the IDF with our own reader**. Audited quantity and auditing reference are both
products of code we wrote — a defect in the shared schedule reader corrupts both sides together and
the identity still "holds". That is **vacuous-gate kind #9 exactly**, the FINDING 9 D8 lesson, and
it was sitting unnoticed in the one number quoted as proof that T9-13's arithmetic is correct.
EnergyPlus integrates the schedule it was actually handed, so its own reported volume is a
reference our parser cannot corrupt.

Implementation notes:
- `_write_dhw_hourly_csv()` gained `variable`/`col_prefix` keyword arguments so the volume series
  reuses the **same** channel-resolution rules rather than a second copy of them. Defaults
  reproduce the previous behaviour byte-for-byte; the existing call site is untouched.
- The new extraction has its **own** `try/except`, like every sibling extraction. A new reporting
  series must never be able to take down a 56-cell campaign: if the variable is absent, the cell
  still produces every artefact it produced before and the exception lands in the manifest. The
  downside is bounded at the status quo.
- `OUTPUT_SCHEMA_HASH` **`db4e729f` → `93dd5129`**. This is by design — the hash exists to stop a
  reporting-side change from leaving old cells looking "done". It is checked for *uniformity*
  across cells, not against a literal, so the Step-9 gate is unaffected; all 56 arm-H cells share
  one build. `INJ_HASH` does **not** move (`commercial_integration.py` untouched), so the campaign
  directory stays `campaign_233932d7` — the same build the FINDING 9 smoke passed on.

## Guards written into the submit script, and why each one exists

1. **Product md5 literals, checked on every task.** `INPUTS_HASH` only protects a cell against a
   product that changed *under an existing outdir*. A fresh outroot has no prior manifest, so it
   cannot tell a correct product from a stale one — it would run all 56 cells on the
   pre-FINDING-6/7 CSVs and record a self-consistent hash for them. These five literals are the
   only thing between a stale cluster copy and a campaign that looks clean and is wrong. Checked on
   **every** task, not task 0, because a partially completed `scp` would otherwise pass task 0 and
   corrupt the rest.
2. **Compile under `$PY`.** Local Python is 3.13, the cluster env 3.10; a multi-line f-string cost
   a full round trip on 2026-08-02. All three drivers compile inside the job or the job refuses.
3. **T9-13 unit suite as a real gate.** 🔴 `smoke_f9fix.sh` ran it as `$PY ... | tail -3` and then
   reported `$?` — which is **tail's** exit code, always 0. That line could not fail whatever the
   suite did. Carried over unexamined it would have been another gate that cannot fail; here the
   suite's own status is captured and the job refuses on it, on all 56 tasks rather than on task 0,
   because a gate guarding one cell out of 56 does not guard the campaign.

## Status — LAUNCHED, NOT YET VERIFIED

Job `1171496` submitted 2026-08-03. **No cell result has been read yet, and no guard has been
observed firing.** The first thing to check is that the five product-md5 guards and the unit-suite
gate actually passed on task 0 — a green campaign whose guards silently no-op'd would be worth
nothing. Nothing below this line may be quoted until that is confirmed.

## Post-launch correction — two stale claims caught before they reached the handoff — 2026-08-03

Both were caught *after* the arm-H prompt was first written and *before* the session ended. Recorded
because the near-miss is the point.

**1. A tooling defect made me read the wrong 600 lines.** The standing rule is "read the last ~600
lines of the step-9 log before acting." PowerShell `Get-Content <file> | Measure-Object -Line`
reported **3,684** lines; `wc -l` reports **4,837**. `Measure-Object -Line` **counts an empty line
as zero lines**, so it undercounts by exactly the blank-line count (1,153 here; the injector reads
2,748 vs 2,976, i.e. 228 blanks — which also explains why this log's "2,970 lines" for
`commercial_integration.py` never matched a local check). Reading "the last 600" off the PowerShell
figure landed at lines 3,100–3,700 of a 4,737-line file, leaving the **most recent ~1,000 lines
unread** — the entire FINDING 8 correction, the D7/D9 falsification records, and the final arm-E
scorecard. **Never count lines with PowerShell on this project.**

**2. Two superseded numbers were nearly carried into the manager prompt as current.** This log is
append-only, so an early section can be flatly contradicted by a later one:

| claim I nearly shipped | where it comes from | what actually supersedes it |
|---|---|---|
| "arm E: `P1` UNTESTABLE, 2 PASS / 3 FAIL / 1 UNTESTABLE" | the first scoring run | §"P1 IS TESTABLE AFTER ALL" — `P1` **PASSED** (night share 0.0834 → 0.0828, peak hour unmoved at 06:00). Final: **3 PASS / 3 FAIL / 0 UNTESTABLE** |
| "the P4 peak-flow/tank-standby probe is the pre-registered next step" | the P4 section of the arm-E result | job `1171408` **already ran it and REFUTED it** — `Water Use Equipment Heating Energy` ×1.389, the draw energy itself moved. Re-running it would have re-derived a known answer |

Both are fixed in `prompts/3rdJ_L3_manager_prompt_2026-08-03.md`. The rule that caught them is the
one already on the books — *verify every number you inherit* — and what it needed extending to is
numbers inherited **from this log itself**, not only from a predecessor prompt. The prompt now says
so, and says the last statement wins.

**Nothing in the arm-H launch depends on either.** The campaign's flags, guards and products were
verified against the artefacts on disk and against task 0's own log lines, not against this
narrative.

## Pre-registered — the arm-H DHW-volume verification, written BEFORE any cell landed — 2026-08-03

`Step9_docs/3rdJ_09H_dhwvol_verify.py`, authored while the array was still in its first 20 minutes,
so no threshold below has seen data.

The new `dhw_volume_hourly.csv` extraction is deliberately fail-soft (its own `try/except`, so a new
reporting series can never take down a 56-cell campaign). **The cost of that choice is that failure
is silent**: an absent variable, a wrong variable name or an empty join all leave the campaign
looking green. Fail-soft demands a loud external check.

| gate | requirement | what makes it FAIL |
|---|---|---|
| G1 | file exists | extraction raised; manifest carries the reason |
| G2 | 8760 rows | truncated RunPeriod, or a design-day-only join |
| G3 | all 7 `dhwvol_*` columns | channel map changed shape |
| G4 | total annual volume > 0, finite, not all-nan | **the silent-nan mode this script exists for** |
| G5 | no `dhw_volume_hourly_exception`; manifest rows == file rows | postprocess swallowed an error, or manifest and artefact disagree |
| G6 | 0 unresolved `WaterUse:Equipment` | an object fell into `dhwvol_unassigned`, leaving a channel short |
| G7 | **implied ΔT ∈ [20, 80] K per drawing channel** | see below |

**G7 is the reason the script is worth writing.** G1–G6 only prove *something* was written; G7
proves it is a **volume**. With `ΔT = E / (ρ·c·V)`, `ρ = 1000 kg/m³`, `c = 4186 J/(kg·K)`, `E` from
`dhw_hourly.csv` (J) and `V` from the new file (m³), the prototypes draw at 140 °F (60 °C) and
180 °F (82 °C) against 5–20 °C mains, so a genuine volume gives ΔT ≈ 40–70 K. Every realistic
failure mode lands far outside the band:

- reporting the **flow rate** (m³/s) instead of integrated volume → ΔT off by ~3600×
- a units slip to litres → ~1000×
- joining the wrong variable index → arbitrary

A check that merely asked *"is it non-zero"* would pass on all three. That is the difference between
this gate and the one it replaces.

**Stated limit:** G7 bounds the volume against the energy from the *same* simulation, so it cannot
detect an error common to both (e.g. EnergyPlus itself mis-integrating a schedule). What it does
establish is that the new column is the physical quantity it claims to be — which is precisely what
is needed before it can serve as the independent reference for the 0.9647 identity.

---

## Arm H — DHW-volume verification EXECUTED (2026-08-03, first cell landed)

Pre-registered in the section above, **before any cell finished**. Run against the first cell to
land, `Y2022__Tall__MTL` (job 1171496, task 0-7 wave), with
`3rdJ_09H_dhwvol_verify.py`.

### Result: 7 PASS / 0 FAIL — `dhw_volume_hourly.csv` is REAL

| gate | result | measured |
|---|---|---|
| G1 file present | PASS | written by the fail-soft branch |
| G2 8760 rows | PASS | 8760 |
| G3 all 7 `dhwvol_*` columns | PASS | 7 present, none missing |
| G4 total volume > 0, finite, not all-nan | PASS | **37,793.5 m3/yr**, all-nan=False |
| G5 manifest clean + row agreement | PASS | exception=None, manifest 8760 == file 8760 |
| G6 unresolved WaterUse:Equipment | PASS | 0 |
| G7 implied delta-T in [20, 80] K | PASS | see below |

G7, `dT = E / (rho * c * V)` with E from `dhw_hourly.csv` (J) and V from the new file (m3):

| channel | V (m3/yr) | E (J/yr) | implied dT (K) |
|---|---|---|---|
| office | 3,495 | 7.198e11 | 49.19 |
| retail | 273.8 | 5.638e10 | 49.19 |
| hotel | 25,570 | 2.578e12 | **24.08** |
| residential | 8,453 | 1.645e12 | 46.49 |
| residential_common / service_MEP / unassigned | 0 | 0 | no draw |

This closes the silent-nan risk that the fail-soft `try/except` created. The T9-13 volume identity
now has a reference that EnergyPlus produced by integrating the schedule it was actually handed,
not one our own IDF reader re-derived — which was the point of open item 3 (vacuous-gate kind #9).

### The mixing algebra says G7's band is measuring the TARGET temperature

For `WaterUse:Equipment`, `E = rho*c*V_hot*(T_hot - T_cold)` while the reported Total Volume is the
MIXED volume, and `V_hot/V_total = (T_target - T_cold)/(T_hot - T_cold)`. The supply term cancels:

    implied dT  =  T_target - T_cold_mains

All 47 objects carry one of two target schedules — `Mixed Water At Faucet Temp - 140F` (60 C, 45
objects) and `- 180F` (82.2 C, 2 objects: Booster and Laundry). 60 C against Montreal mains gives
~49 K, which is **exactly** office and retail (49.19 both). So G7 is not a loose plausibility band;
it reads back a quantity we can predict from the IDF independently.

### NEW OBSERVATION — the hotel DHW plant saturates at peak draw

Hotel's 24.08 K cannot come from its target temperature: its two distinguishing objects are the
**180 F** ones, which should push it ABOVE 49 K, not to half of it. Splitting the hourly series by
draw magnitude separates the candidate mechanisms cleanly — a structural/attribution error is
draw-independent, a capacity shortfall is not:

| channel | hrs>0 | dT p05 | p25 | p50 | p75 | p95 | std |
|---|---|---|---|---|---|---|---|
| office | 6570 | 42.67 | 44.52 | 49.18 | 53.88 | 55.71 | 4.67 |
| retail | 4950 | 42.68 | 44.53 | 49.18 | 53.88 | 55.71 | 4.67 |
| hotel | 8760 | 16.93 | 22.42 | 48.85 | 55.59 | 59.26 | **16.03** |
| residential | 8760 | 40.44 | 43.23 | 46.79 | 51.21 | 55.46 | 4.72 |

Hotel, binned by its own draw:

| bin | mean V (m3/h) | mean implied dT (K) |
|---|---|---|
| lowest-draw decile | 0.308 | 52.41 |
| median decile | 0.724 | 53.41 |
| peak-draw decile | 8.633 | **18.28** |

Draw-dependent, so not attribution. The other three channels' std of ~4.7 K is just the seasonal
mains swing; hotel's 16.0 K is not that.

**Mechanism, evidenced not assumed.** The six `WaterHeater:Mixed` objects are **hard-sized
literals, not `Autosize`** — `Tank Volume 1.13562` m3 (300 gal) and `Heater Maximum Capacity
87921.32` W, five of those plus one 6-gal 7999.96 W electric booster. Installed capacity for the
**entire tower, all channels** = 5 x 87.92 + 8.00 = **447.6 kW**. The hotel peak-draw decile alone
would need `rho*c*8.6333*52.4/3600` = **526.0 kW** to reach target — **17.5 % more than the whole
building's DHW plant** — and actually received `rho*c*8.6333*18.28/3600` = **183.5 kW**. The
shortfall is arithmetic; it needs no assumption about which heater sits on which loop.

**This cell does NOT implicate T9-13.** All 26 commercial DHW schedules in `Y2022__Tall__MTL` carry
`r1000w1000`, i.e. the volume ratio applied to office/retail/hotel here is exactly 1.000, so peak
flows are the prototype's. The saturation is **inherited from the mixed-tower construction**, not
introduced by the volume-scaling model.

### Vacuity check on T9-13's commercial arm — proposed, and REFUTED

If every commercial object in every cell were `r1000w1000`, T9-13 would change nothing for 3 of the
4 channels and its volume identity would be vacuous where it matters most. Tested on `injected.idf`
(written at injection time, so testable on cells still simulating):

| cell | Office | Retail | Hotel |
|---|---|---|---|
| `Y2022__Tall__MTL` | r1000w1000 | r1000w1000 | r1000w1000 |
| `Y2005__Tall__MTL` | r1030w1049 | r1117w0715 | *absent* |
| `B_opt__Tall__MTL` | r0695w1604 | r0887w0857 | r1203w1203 |

**REFUTED — the commercial arm is live.** Y2022 reads all-1.000 because it is the reference year.
Hotel absent from Y2005 is the documented era exclusion (QC hotel truth starts 2019), not a defect.
Residential was never in doubt: Y2022 alone carries r0885w0939 through r1574w0711 per household.

### PRE-REGISTERED for when `B_opt__Tall__MTL` lands

`B_opt` scales hotel volume by **r1203w1203** (+20 %) against the same 447.6 kW of hard-sized
plant. If the saturation mechanism above is right, the hotel's annual implied dT in `B_opt` must
come out **BELOW Y2022's 24.08 K**, and its peak-draw-decile dT **below 18.28 K**. If instead it
holds at ~24 K or rises, the capacity explanation is wrong and the mechanism must be re-opened.

Written before `B_opt` finished. Consequence if confirmed: hotel DHW **energy under-responds to
volume scaling**, so the T9-13 identity (energy proportional to volume) breaks in the hotel channel
precisely where the scaling is largest — a caveat on arm H's hotel numbers, not a reason to stop
the campaign, since the effect is measurable from artefacts every cell already writes.

---

### Hotel-saturation prediction TESTED on `B_opt__Tall__MTL` (2026-08-03) — **CONFIRMED, both legs**

The prediction was written into the Progress Log and into `3rdJ_09H_dhwvol_sweep.py`'s docstring
**before** `B_opt` finished simulating. It was:

> `B_opt` scales hotel volume by **r1203w1203** (+20 %) against the same 447.6 kW of hard-sized
> plant. If the saturation mechanism is right, hotel annual implied dT must come out **below
> Y2022's 24.08 K** and its peak-draw-decile dT **below 18.28 K**. If it holds at ~24 K or rises,
> the capacity explanation is wrong and must be re-opened.

`B_opt__Tall__MTL` gate result: **7 PASS / 0 FAIL** (G1–G7), total annual volume 43,718.2 m³.

| quantity | Y2022 (r_hotel = 1.000) | B_opt (r_hotel = 1.203) | prediction | outcome |
|---|---|---|---|---|
| hotel annual implied dT | 24.08 K | **22.20 K** | < 24.08 K | **CONFIRMED** |
| hotel peak-decile dT | 18.28 K | **16.36 K** | < 18.28 K | **CONFIRMED** |
| hotel peak-decile draw | 8.633 m³/h | 10.387 m³/h | — | ratio 1.203 (= r exactly) |

The peak-decile draw ratio landing on **1.203 to three decimals** is the independent confirmation
that T9-13 *did* apply the volume scaling it recorded. The plant simply did not follow it.

**The identity splits cleanly by channel.** Comparing the two cells object-for-object:

| channel | V ratio B_opt/Y2022 | E ratio B_opt/Y2022 | dT Y2022 → B_opt | verdict |
|---|---|---|---|---|
| office | 0.796 | 0.796 | 49.19 → 49.18 K | **energy tracks volume exactly** |
| retail | 0.880 | 0.879 | 49.19 → 49.18 K | **energy tracks volume exactly** |
| hotel | 1.203 | 1.109 | 24.08 → 22.20 K | under-responds — 54 % of intended |
| residential | 1.175 | 1.095 | 46.49 → 43.35 K | under-responds — 54 % of intended |

So the T9-13 energy identity `E ∝ V` holds to **three significant figures** in office and retail,
and fails by the same factor (~0.54) in hotel and residential. That is not a coincidence of two
independent bugs: hotel and residential are the two large draws, they share the same six
hard-sized `WaterHeater:Mixed` objects, and both scale *up* in `B_opt` while office and retail
scale *down*. A shared plant that is already at its ceiling absorbs an upward request as a
temperature deficit, not as energy — exactly the mechanism the decile binning evidenced on Y2022.

Hourly spread in `B_opt`, for the record (same shape as Y2022, deeper low tail):

| channel | hrs>0 | dT p05 | p25 | p50 | p75 | p95 | std |
|---|---|---|---|---|---|---|---|
| office | 6570 | 42.65 | 44.50 | 49.17 | 53.86 | 55.71 | 4.675 |
| retail | 4950 | 42.66 | 44.51 | 49.17 | 53.86 | 55.70 | 4.673 |
| hotel | 8760 | 15.04 | 19.69 | 48.47 | 54.75 | 59.23 | **16.691** |
| residential | 8760 | 35.45 | 41.94 | 44.49 | 49.85 | 55.36 | 5.978 |

Hotel by its own draw: lowest decile 0.371 m³/h → 52.45 K; median 0.871 → 53.37 K; peak decile
10.387 → **16.36 K**.

**Consequence — recorded, not repaired.** The plant sizing is inherited from the mixed-tower
construction (`Autosize` was never used; the six heaters are literals). It is *not* a T9-13
defect: T9-13 delivered the volume it promised. But it means **arm H's hotel and residential DHW
energy under-respond to volume scaling by roughly a factor of two**, and any downstream claim of
the form "scaling occupancy by X scales DHW energy by X" is true for office and retail and false
for hotel and residential. This is a caveat to carry into arm H's scorecard and the manuscript —
it is not a reason to stop or re-run the campaign, because the *energy* results are physically
consistent with the plant that is actually in the IDF.

The `3rdJ_09H_dhwvol_sweep.py` step (agg step 3b) will re-run this same test across all 56 cells
with an `r > 1` vs `r == 1` group comparison, so the two-cell result above gets a population check
rather than staying an n=2 anecdote.

### Vacuous-gate #10 — repo-wide sweep DONE, one occurrence, fixed (2026-08-03)

The 2026-08-03 manager prompt carried an action: *"grep the other `.sh` files for `| tail` followed
by `$?` — this pattern was copied around."* Swept every `.sh` under `3J_docs_occ_nTemp/` for a
pipeline (`| tail|head|grep|tee|sort|wc`) whose exit status is read on the next line.

**Exactly one hit**, and it is the already-known one:

```
Step8_docs/smoke_f9fix.sh:47   $PY -u $REPO/eSim_tests/test_t9_13.py | tail -3
Step8_docs/smoke_f9fix.sh:48   echo "  unit suite exit=$?"
```

So the pattern was *not* copied around — the prompt's suspicion is refuted, which is worth recording
because it bounds the blast radius of #10 to a single smoke script. `agg_armH.sh`'s step 3b was
checked specifically: it calls `$PY ... 3rdJ_09H_dhwvol_sweep.py` with **no pipe**, so its
`exit=$?` reads the sweep's own status. Clean.

`smoke_f9fix.sh:47-48` is now fixed rather than left as a museum piece, because the next script
built from it would inherit the defect: the suite's status is captured into `SUITE_RC` before
`tail` runs, and the smoke **aborts** on a non-zero — so the check can now fail, which is the whole
point. The old lines are kept in a comment above the fix as the worked example of kind #10.

### PRE-REGISTRATION — independent test of the T9-13 volume identity (2026-08-03, before running)

Open item 3 was declared closed when `dhw_volume_hourly.csv` was shown to exist and be non-`nan`.
That is only half of what the artefact was requested for. Its stated motive (§3 of the manager
prompt) is anti-vacuity: the **only** existing statement of the T9-13 volume identity — the 0.9647
figure — is produced by `3rdJ_09E_dhw_identity_probe.py`, which computes
`Σ Peak_Flow × (5·mean_wd + 2·mean_we)/7` **with our own IDF reader on both sides of the ratio**.
Audited quantity and auditing reference share a parser: vacuous-gate kind #9, sitting inside the
one number quoted as proof T9-13's arithmetic is right.

EnergyPlus integrates the schedule it was actually handed. Its reported `Water Use Equipment Total
Volume` is therefore a reference our parser cannot corrupt — and until arm H it did not exist.
So the identity can now be tested **absolutely**, not as a ratio of two of our own parses:

    predicted_annual_m3 = Σ_objects Peak_Flow_Rate [m3/s] × (5·mean_wd + 2·mean_we)/7 × 8760 × 3600
    reported_annual_m3  = Σ_channels dhw_volume_hourly.csv

Summing over **all** `WaterUse:Equipment` objects and **all** channel columns deliberately removes
the channel-attribution step, so this tests the volume arithmetic alone and not the aggregator's
zone-prefix rules.

**Pre-registered band, fixed before the script is run:**

| | |
|---|---|
| PASS | `\|predicted/reported − 1\| ≤ 3 %` |
| FAIL | anything larger |

3 % is not a comfort margin, it is the sum of the known approximations in the identity's own
formula: 365 days is 52.14 weeks not 52 (≈ +0.3 % if the odd day is a weekday), `Holiday` and
`SummerDesignDay` day types are not carried by the 5/2 weighting, and Saturday≠Sunday (post
FINDING 9) is averaged into a single weekend mean. Hourly integration itself is exact — schedules
are hourly and `Peak × fraction` is EnergyPlus's own definition — so **there is no legitimate
mechanism for a 10 %, let alone a 40 %, discrepancy.** If one appears, the 0.9647 identity
statement is wrong and everything resting on it is re-opened.

Run on both downloaded cells: `Y2022__Tall__MTL` (r = 1.000 everywhere, the reference year) and
`B_opt__Tall__MTL` (r away from 1 in every channel). A parser that is right only where nothing is
scaled would be a poor reference.

### RESULT — independent volume-identity test: **pre-registered gate FAILED**, cause located (2026-08-03)

`Step9_docs/3rdJ_09H_volume_identity_indep.py`, run on the two downloaded cells.

| cell | reported (E+) | predicted (09E reader) | ratio | verdict |
|---|---|---|---|---|
| `Y2022__Tall__MTL` | 37,793.5 m³ | 23,853.4 m³ | 0.6311 | **FAIL** (−36.89 %) |
| `B_opt__Tall__MTL` | 43,718.2 m³ | 26,880.0 m³ | 0.6148 | **FAIL** (−38.52 %) |

The band was 3 %. This is off by more than a factor of ten beyond it, in the same direction in both
cells. **The FAIL is recorded and stands.** What follows is diagnosis, not repair.

**It is not T9-13's arithmetic. It is our reader.** `3rdJ_09E_dhw_identity_probe.py`'s
`compact_profiles()` resolves the `For:` field with a first-substring-match chain:

```python
if "WEEKEND" in up or "SATURDAY" in up or "SUNDAY" in up:   cur = "we"
elif "ALLDAY" in up or "ALLOTHERDAY" in up or "ALL DAY" in up: cur = "all"
else:                                                        cur = "wd"
```

The hotel laundry schedules are written as a **single `For:` field naming seven day types**:

```
Schedule:Compact,
    MXU_Hotel_DHWv2_HOTELLARGE_LAUNDRY_SWH_SCH_r1000w1000_Y2022__Tall__MTL,
    Fraction,
    Through: 12/31,
    For: Weekdays Saturday Sunday Holidays SummerDesignDay WinterDesignDay AllOtherDays,
    ... 0.0 until 17:00, then 1.0 to 24:00 ...
```

`"SATURDAY" in up` matches first, so the entire field collapses onto the **weekend** bucket and the
weekday profile is never written — it stays `0.0`. The reader then reports
`mean = (5×0.0000 + 2×0.2917)/7 = 0.0833` for a schedule whose true annual mean is `7/24 = 0.2917`.
**A factor of 3.5, on the single largest DHW draw in the tower.**

A second, milder face of the same bug: `For: Saturday` followed by `For: Sunday Holidays
AllOtherDays` (office and retail). The second block also matches the weekend test and **overwrites**
Saturday, so post-FINDING-9 Sat ≠ Sun weekends are read as Sunday everywhere.

**Corrected reader** — resolves a `For:` field into the *full set* of day types it names, keeps
Saturday and Sunday apart, treats `AllOtherDays` as "every day type not yet assigned in this
`Through` period", and weights by the real 2022 calendar (260 weekdays / 53 Saturdays / 52 Sundays)
rather than 5/2:

| cell | reported | predicted (corrected) | ratio | verdict |
|---|---|---|---|---|
| `Y2022__Tall__MTL` | 37,793.5 m³ | 37,797.4 m³ | **1.0001** | PASS (+0.01 %) |
| `B_opt__Tall__MTL` | 43,718.2 m³ | 43,724.0 m³ | **1.0001** | PASS (+0.01 %) |

Closure to **0.01 %** on both cells, and on `B_opt` the r values are away from 1.0 in every channel.
So **the T9-13 volume identity is now confirmed absolutely against EnergyPlus's own integration**,
for the first time, with no shared parser between the audited quantity and the reference. That was
the entire purpose of requesting `Water Use Equipment Total Volume` — it delivered, and the thing it
caught was our instrument.

**Scope of the damage — checked, not assumed.** `09E.volume_table()` filters on
`RESID_TOKENS = ("APARTMENT", "DWELL", "HIGHRISE", "RESI")`, so it never reads a laundry or a
restroom object. Per-channel closure under the 09E reader:

| channel | predicted (09E) | reported | ratio |
|---|---|---|---|
| residential (27 objects) | 8,453.8 m³ | 8,453.3 m³ | **1.00006** |
| office (2) | 3,335.8 | 3,495.3 | 1.048 |
| retail (2) | 253.0 | 273.8 | 1.082 |
| hotel (16) | 11,810.5 | 25,571.2 | 2.165 |

Residential reproduces EnergyPlus to **five significant figures** under the defective reader,
because residential schedules do not use the multi-day-type `For:` form. **The published 0.9647
residential identity figure is therefore unaffected** and needs no restatement. What is unsafe is
using 09E's reader on *commercial* objects — which nothing had done until this script did it.

**Actions.** 09E is left byte-identical: its result is in the historical record and silently
re-running history is worse than an annotated defect. The corrected reader lives in the new script,
which prints **both** so the miss stays visible next to the fix. Anything that quotes a *commercial*
DHW volume derived from 09E must be re-derived; nothing currently does.

**New vacuous-gate observation (not a new kind — kind #9 working as advertised).** 09E's ratio form
divides two numbers from the same reader, so the 3.5× under-read cancels exactly and the ratio looks
right. This is the first time on this project that a kind-#9 gate has been *caught by construction*
rather than by accident: the external reference was requested specifically because the gate shared a
parser with its target, and it found a real defect on first contact.

### FALSIFIER — the corrected reader has been SEEN FAILING (2026-08-03)

`+0.01 %` agreement on two independent cells is close enough to be suspicious. A gate that agrees
that well has to be shown capable of disagreeing, or the number is worth nothing — this is the
project's standing rule and it applies to a result that flatters us just as much as to one that
doesn't.

Method: perturb the thing the reader reads — one `WaterUse:Equipment` `Peak_Flow_Rate` in a copy of
`Y2022__Tall__MTL`'s IDF — while leaving EnergyPlus's reported volume untouched. The gate must then
FAIL by the amount the perturbation implies. Three factors, all **pre-registered before running**:

| perturbation | predicted before running | measured | verdict | pre-registered verdict |
|---|---|---|---|---|
| `Laundry 30.6gpm` × 1.50 | ≈ +23.5 % | **+23.50 %** | FAIL | FAIL |
| × 1.05 | ≈ +2.3 % | **+2.36 %** | PASS | PASS (inside the band) |
| × 1.12 | ≈ +5.6 % | **+5.65 %** | FAIL | FAIL (just outside) |

Three for three, including the two that straddle the 3 % boundary. The gate responds linearly to the
quantity it claims to measure, it fails when it should, and it passes when it should — so the
`+0.01 %` closure is a measurement and not a tautology.

Note that the gate's *other* failure mode was already demonstrated without any perturbation at all:
the same script runs the defective 09E reader beside the corrected one and that reader FAILs on both
cells (−36.9 %, −38.5 %). Both halves of the falsification are therefore in the artefact itself and
re-run on every future invocation, rather than living in this log as a one-off claim.

### Blast-radius sweep for the `For:`-collapse defect — two other sites, **both clean** (2026-08-03)

The defect found in 09E is a *reading* defect, so the first question is whether the same reading
appears anywhere that matters. Grepped the whole repo for the pattern
(`"WEEKEND" in ... or "SATURDAY" in ... or "SUNDAY" in ...`, `compact_profiles`, `build_resolver`).
Three sites total, and the two that are not 09E were read line by line rather than pattern-matched:

**1. `eSim_bem_utils/commercial_integration.py:865-871` — the LIVE injector (md5 `233932d7`, the one
running the 56-cell campaign right now).** Same-looking chain, but it is **not** the same logic and
it is **correct**. The FINDING 9 fix at `:856-864` claims each named day type separately through
`_daytypes_for_tokens(toks)`, and the `wd`/`we` variables at `:865-871` are only fallbacks feeding
`_fill_daytypes`. Traced against the actual laundry field
(`For: Weekdays Saturday Sunday Holidays SummerDesignDay WinterDesignDay AllOtherDays`): line 868
sets `wd = vals`, line 870 sets `we = vals`, and `by_daytype` receives all seven — every path lands
on the same correct profile. **Arm H's IDFs are not affected. No re-run implied.**

**2. `Step9_docs/3rdJ_09F_daytype_loss.py:114` — the independent FINDING-9 guard.** This matters
more than it looks: open item 7 says neither `D8` nor `D9` can catch a defect in
`_schedule_daytype_profiles` because both consult it, and 09F is the *one* check with its own
parser. If 09F carried the collapse, the independent guard would be worthless. It does not. 09F is
**token-based** — it splits the `For:` spec on whitespace and allocates a separate block per named
token (`blocks.setdefault(c, [None]*24)`), then selects with `pick("weekdays", ...)`. A field naming
seven day types produces seven correctly-populated blocks. **Immune by construction, not by luck** —
which is what an independent guard is supposed to be, and the first time that independence has been
demonstrated rather than asserted.

So the defect is confined to `3rdJ_09E_dhw_identity_probe.py`, whose only published output is the
residential-only 0.9647 — already shown unaffected. Nothing needs re-running.

### 🔴 The hotel DHW plant is undersized by construction — quantified (2026-08-03)

With the volume identity closing to 0.01 % at object level, predicted volume can be split by
**target temperature** and compared against the ΔT EnergyPlus actually delivered. Mains temperature
is not assumed: it is *inferred* from the channels that are demonstrably not plant-limited (office
and retail track volume exactly), giving `T_mains = 60.00 − 49.19 = 10.81 °C`.

`Y2022__Tall__MTL`:

| channel | V predicted | V reported | ΔT ideal | ΔT actual | delivered | unmet |
|---|---|---|---|---|---|---|
| office | 3,498.5 m³ | 3,495.3 m³ | 49.19 K | 49.19 K | **100.0 %** | 0.0 GJ |
| retail | 274.2 | 273.8 | 49.19 | 49.19 | **100.0 %** | 0.0 GJ |
| residential | 8,453.3 | 8,453.3 | 49.19 | 46.49 | 94.5 % | 95.5 GJ |
| hotel | 25,571.5 | 25,571.2 | 65.49 | **24.08** | **36.8 %** | **4,432.3 GJ** |

`B_opt__Tall__MTL` (r above 1 in hotel and residential, below 1 in office):

| channel | delivered | unmet |
|---|---|---|
| office | 100.0 % | 0.0 GJ |
| retail | 100.0 % | 0.0 GJ |
| residential | **88.1 %** (was 94.5) | 242.4 GJ |
| hotel | **33.9 %** (was 36.8) | 5,573.8 GJ |

**The arithmetic, with no loop-topology assumption.** Two objects carry the `180 °F` (82.22 °C)
target — `Laundry Service Water Use 30.6gpm 180F` and `Booster 1.33gpm 180F` — and between them
**18,754 m³ of the tower's 37,797 m³, i.e. 49.6 % of all DHW volume in the building.**

```
Laundry, at full flow : 1.9306e-03 m3/s x 1000 x 4186 x (82.22 - 10.81) =  577.1 kW
Installed plant, ALL 6 WaterHeater:Mixed objects, whole tower  =  447.6 kW
```

**The single largest draw demands 129 % of the entire building's installed water-heating capacity,
on its own, for seven hours every day of the year** (the schedule is 0.0 until 17:00, then 1.0 to
midnight). The heaters are hard-sized literals — `Autosize` is never used — so nothing in the model
resizes to meet it.

**What this does and does not mean.**

- It is **not** a T9-13 defect. T9-13 delivers exactly the volume it promises: office and retail
  come out at 100.0 % delivered, and every channel's predicted volume matches EnergyPlus to ≤ 0.1 %.
- It is **not** new to arm H. The plant sizing is inherited from the mixed-tower assembly (ARCH B),
  so **every arm A–H carries it**, and so does any Leg-3 hotel DHW number ever reported.
- It **is** the mechanism behind the saturation observed earlier today, and the `B_opt` column
  proves the coupling is real rather than a hotel-only quirk: scaling residential volume up by
  1.175× pushed residential from 94.5 % → 88.1 % delivered. **The channels compete for one
  undersized plant.** A caveat written as "hotel DHW under-responds" is too narrow — residential
  under-responds too, as soon as it asks for more.
- Consequence for the manuscript: **hotel DHW energy in Leg-3 is not a demand-side result.** It is
  capped by plant capacity for most of its volume, so it cannot be read as "occupancy × intensity",
  and the occupancy-response elasticity measured on it is a *lower bound*, not an estimate.

**Flagged, not fixed.** The obvious remedy — `Autosize` the six `WaterHeater:Mixed` objects, or
size them to the summed peak — would move every hotel and residential DHW number in every arm and
is a re-simulation decision, not an audit decision. It is also not obviously *correct*: a real
mixed-use tower may well have a laundry that runs against a limited plant. **This is the user's
call.** Recorded here with the numbers needed to make it.

### FIX — 09E now REFUSES the field it used to mis-read (2026-08-03)

Earlier today the decision was to leave 09E byte-identical, on the grounds that silently re-running
history is worse than an annotated defect. That reasoning covers *changing the answer*; it does not
cover *leaving a loaded gun on the table*. The reader is still importable and the next person to
point it at a commercial object gets 2/7 of the truth with no warning. So the fix applied is the one
that adds no new answer:

`_for_field_is_ambiguous()` — a `For:` field naming **both** a weekday and a weekend day type is
refused, `compact_profiles()` returns `(None, None)`, and the object surfaces through the existing
`n_unres` / WARNING path with the note
`Compact: REFUSED, multi-day-type For: (use 3rdJ_09H reader)`. 09E now under-reports coverage
loudly instead of over-reporting volume quietly.

Verified on both cells, three pre-registered requirements:

| requirement | result |
|---|---|
| guard fires on the multi-day-type schedules | **2 objects** — `Laundry ... 30.6gpm 180F`, `F30 Hotel_bot_Laundry` |
| guard fires on **no** residential object | 0 of 27 — all 27 still resolve |
| 09E's published residential number is unmoved | annual **8,453.9 m³** vs EnergyPlus **8,453.3** (0.007 %) |

So the 0.9647 residential identity remains exactly as published, and the two objects the guard
removes are the two the corrected reader showed it was reading at 28.6 % of their true volume.

**The recorded FAIL stays reproducible.** With the guard live, 09E would *drop* the laundry objects
rather than under-read them, and `3rdJ_09H`'s "09E reader" column would no longer reproduce
−36.89 %. That number is part of the record, so the as-published chain is now frozen inside
`3rdJ_09H_volume_identity_indep.py` as `_compact_profiles_as_published()`, whose only job is to keep
reproducing the miss beside the fix. Re-run after the change: **−36.89 % / −38.52 %** (09E reader)
and **+0.01 % / +0.01 %** (corrected) — identical to the values recorded before the guard existed.

### The corrected reader was guessing its own calendar — fixed, and the identity is now EXACT (2026-08-03)

Caught while reading the IDF for something else. The cells are named `Y2022`, so the corrected
reader hard-coded the 2022 calendar (Jan 1 = Saturday → 53 Sat / 52 Sun). The `RunPeriod` in these
IDFs is:

```
RunPeriod,
    Run Period 1, 1, 1, 2006, 12, 31, 2006,
    Sunday,       !- Day of Week for Start Day
    No,           !- Use Weather File Holidays and Special Days
    No,           !- Use Weather File Daylight Saving Period
    No,           !- Apply Weekend Holiday Rule
```

**2006 starting Sunday** — which swaps the counts to 52 Saturdays / 53 Sundays. A reader that infers
its calendar from the *cell name* rather than from the RunPeriod is precisely the class of mistake
this script exists to catch in other people's code, so it is now read from the IDF
(`day_counts()`), leap years included, with the source printed on every run.

Two things that were assumptions became verified facts in the process: `Use Weather File Holidays
and Special Days = No`, `Apply Weekend Holiday Rule = No`, and no `RunPeriodControl:SpecialDays`
object — so the `Holiday` day type is **unreachable** and a `For: Holidays` block correctly carries
no weight of its own. That had been asserted in the docstring; it is now checked, and the reader
says so if a `SpecialDays` object ever appears.

Effect on the result:

| cell | reported | predicted (corrected) | before the calendar fix | after |
|---|---|---|---|---|
| `Y2022__Tall__MTL` | 37,793.5 m³ | 37,793.5 m³ | 1.0001 (+0.01 %) | **1.0000 (+0.00 %)** |
| `B_opt__Tall__MTL` | 43,718.2 m³ | 43,718.2 m³ | 1.0001 (+0.01 %) | **1.0000 (+0.00 %)** |

**The T9-13 volume identity now reproduces EnergyPlus exactly, to displayed precision, on both
cells.** The last residual was our calendar, not the model.

Re-verified after the change, so the closure cannot be a coincidence of a looser reader:

- Falsifier, same three pre-registered perturbations: ×1.50 → **+23.49 % FAIL**, ×1.05 →
  **+2.35 % PASS**, ×1.12 → **+5.64 % FAIL**. Three for three, unchanged.
- 09E guard: still fires on exactly the 2 laundry objects, 0 of 27 residential, published
  residential number still 8,453.9 m³ against EnergyPlus's 8,453.3.
- The frozen as-published reader still reproduces the recorded miss at **−36.89 % / −38.52 %**.

### FINDING 9 verified at the OUTPUT level — first time (2026-08-03)

Every FINDING 9 check on file is **schedule-level**: the smoke test (job 1171449) compared IDFs
before and after, `D9` reads the saved IDF, `3rdJ_09F_daytype_loss.py` parses IDFs with an
independent reader. All three ask *"is the right thing written into the IDF?"* None asks *"did
EnergyPlus deliver it?"* Those are different questions, and arm H's volume series makes the second
one answerable for the first time.

`Step9_docs/3rdJ_09H_daytype_volume_verify.py` predicts each channel's mean Saturday and mean Sunday
hourly volume from the IDF, then measures the same two quantities from `dhw_volume_hourly.csv` by
binning the 8760 rows onto the run period's real calendar (2006, starting Sunday → 52 Saturdays,
53 Sundays, read from the `RunPeriod`, not assumed).

Gates pre-registered before the run:

| | |
|---|---|
| **G1** | predicted vs measured within **1 %** on both day types, every channel |
| **G2** | office and retail **must** differ Sat-vs-Sun by more than 1 % |
| **G3** | hotel is **not** required to differ — its prototype laundry is one all-day block, and the smoke's discriminating prediction was exactly that F30 stays put |

G2 and G3 together are what make this non-vacuous: one channel is required to move and another is
required not to. A run that flattened every day type fails G2; a run that invented a weekend
difference everywhere fails G3.

`Y2022__Tall__MTL` (`B_opt__Tall__MTL` identical in structure):

| channel | Sat pred | Sat meas | err | Sun pred | Sun meas | err | Sat/Sun |
|---|---|---|---|---|---|---|---|
| office | 0.2213 | 0.2213 | **+0.00 %** | 0.0879 | 0.0879 | **+0.00 %** | **2.5169** |
| retail | 0.0345 | 0.0345 | **+0.00 %** | 0.0177 | 0.0177 | **+0.00 %** | **1.9518** |
| hotel | 2.9224 | 2.9237 | −0.04 % | 2.9108 | 2.9095 | +0.04 % | 1.0049 |
| residential | 0.9389 | 0.9389 | +0.00 % | 0.9389 | 0.9390 | −0.02 % | 0.9998 |

**G1 PASS, G2 PASS (office 151.7 %, retail 95.2 %), G3 hotel 0.49 % — flat, as required.**
Both cells PASS.

So FINDING 9's fix is not merely written into the IDF: EnergyPlus delivers **2.52× more DHW volume
on Saturday than Sunday in the office channel and 1.95× in retail**, exactly as the schedules
specify, while hotel stays flat to half a per cent.

**Recorded observation — residential is Sat == Sun by construction, and that is not a defect.**
Residential comes out at 0.9998 / 1.0003. Checked rather than inferred: the injected residential
schedules are written as

```
For: Weekdays SummerDesignDay WinterDesignDay,
For: Saturday Sunday Holidays AllOtherDays,
```

i.e. one combined weekend block, because the residential occupancy channel resolves only `r_wd` and
`r_we`. FINDING 9 was a *commercial* day-type defect (`_week_profiles:595`, `sun or sat`) and it
never applied to residential. Worth stating explicitly, because "FINDING 9 restored Saturday ≠
Sunday" reads as a whole-building claim and it is not one. Extending residential to a three-day-type
split would be a **Step-4/Step-7 change**, not an injector change, and nothing in the current
evidence says it is needed.

**One bug in this script, caught by its own G1.** The first run predicted **0.0000** residential
volume: the channel map keyed only on prototype tokens (`MIDRISEAPARTMENT`, …), and the injector
names residential schedules `MXU_Residential_DHWv2_HH<id>_…`, which carries none — so all 27
residential objects went to `unassigned`. G1 failed at −100 % and made it obvious. A test that only
reported the Sat/Sun *ratio* would have shown residential at 0.9998 and passed silently, since the
ratio of two zeros never appeared. **Predicted-vs-measured earns its place over ratio-only exactly
here.**

Added to `agg_armH.sh` as step 3d, so it runs over all 56 cells in-job alongside 3b and 3c.

---

## Progress Log — 2026-08-03 — ARM H CAMPAIGN CLOSED (56/56) + aggregation (jobs 1171496, 1171607)

### What ran

`--dhw-model volume_scaled` (T9-13) on the FINDING-6/7/8/9-corrected injector, md5 `233932d7`.
Campaign array **1171496**, 56 cells, ~4 h wall. Aggregation **1171607**, COMPLETED, exit 0, 29 min.
Output dir `campaign/out_H_allfix/campaign_233932d7`; tables in `campaign/agg_H_allfix`.

### Aggregate — clean

    cells aggregated : 56 / 56
    attribution closes against site energy on every cell (<= 1e-6 relative)
    5 tables: agg_annual, agg_annual_by_channel, agg_diurnal, agg_meta, agg_peak

Site energy spans 27,502 GJ (`Y2010__Tall__CLG`) to 52,887 GJ (`sens_office_cons__SuperTall__MTL`).
Attribution residual is **0.000000 %** on all 56 — not one fallback on cool/hvac/dhw; heating-hour
fallbacks 390–1,111 per cell, unchanged in character from arm E.

### Structural guards (§0–§2d) — all hold

| guard | result |
|---|---|
| injector-hash guard on the campaign dir | `campaign_233932d7` — OK |
| cell count | 56 / 56 |
| P1 `t9_13_audit_pass` | 50 PASS, 2 FAIL, 4 N/A (N/A = the `channels_requested=[]` control) |
| `n_dhw_excluded == 0`, `n_dhw_unresolved == 0` | 56 / 56 both |
| r saturated at `r_max` | 0 |
| D7 (assignment, read back from the saved IDF) | 56 pass, 0 fail, **0 absent** |
| D9 (per-day-type, read back from the saved IDF) | 0 absent, 0 cells with D9>0, **0 unchecked**, **0 two-day-type FALLBACK schedules** |

`n_audited` is constant within every (geometry, channels_requested) group — 0 non-constant groups —
and the values are *not* a universal 47, which is the point of gate 2b:

    SuperTall | office,retail,hotel,residential | 71   (20 cells)
    SuperTall | office,retail,residential       | 47   ( 6 cells)
    SuperTall | []                              |  0   ( 2 cells)
    Tall      | office,retail,hotel,residential | 47   (20 cells)
    Tall      | office,retail,residential       | 31   ( 6 cells)
    Tall      | []                              |  0   ( 2 cells)

### §3b DHW-volume gates G1–G7 — 56/56 on every gate

Hotel saturation test, pre-registered before any cell landed (prediction: cells with `r_hotel > 1`
show LOWER annual hotel dT):

    r_bin   n   dT_hotel_mean  dT_peakdec_mean   r_mean
    r<1     4      25.5610        19.2302        0.9801
    r==1    2      25.5428        19.2680        1.0000
    r>1    34      24.5042        18.1334        1.1084
    delta(r>1 minus r==1) = -1.039 K    corr(r_hotel, dT_hotel) = -0.3395
    VERDICT: CONFIRMED (lower, as predicted; correlation negative as predicted)

### §3c volume identity, all 56 cells — the n=2 result generalises

    09E reader        : 40 FAIL / 16 PASS
    corrected reader  : 56 PASS / 0 FAIL

The 16 cells where the 09E reader passes are exactly `Default_NECB` + `Y2005/2010/2015` — i.e. the
cells whose hotel channel was never injected, so the multi-day-type `For:` field that breaks 09E is
never written. That is a clean mechanistic confirmation: **09E's miss is caused by injection, not by
the cell**. The three worst objects are the same everywhere — the hotel laundry read at 3.500x too
low (mean 0.0833 vs 0.2917, +1194.7 m3/yr) and the two office restroom blocks at 1.118x (+174.4 each).

Per-channel reported volume, fully-injected cell: hotel 28,752.1 m3, residential 9,736.0,
office 3,307.8, retail 240.9.

### §3d FINDING 9 at the OUTPUT level — 40 PASS / **16 FAIL**

Fully-injected cells, predicted vs measured mean hourly volume:

    channel        sat pred  sat meas   err %  sun pred  sun meas   err %   sat/sun
    office           0.4685    0.4685  -0.00    0.1861    0.1861  +0.00    2.5169
    retail           0.0295    0.0295  +0.00    0.0151    0.0151  +0.00    1.9518
    hotel            3.2859    3.2873  -0.04    3.2728    3.2714  +0.04    1.0049
    residential      1.0979    1.0979  +0.00    1.0979    1.0980  -0.01    0.9999

G1 PASS, G2 PASS (office Sat/Sun +151.69 %, retail +95.18 %), G3 hotel flat at 0.49 % as predicted.

**The 16 FAILs, and why they are the reader's fault and not the simulation's.** The failing set is
exactly `Default_NECB` x4 and `Y2005`/`Y2010`/`Y2015` x12 — precisely the cells with a channel that
was never injected (`channels_requested=[]` for Default_NECB; hotel absent pre-2019 because the QC
hotel truth series starts in 2019). Confirmed directly from the saved IDF: in `Y2010__Tall__CLG`,
`Laundry Service Water Use 30.6gpm 180F` points at `HotelLarge LAUNDRY_SWH_SCH`, which is a
`Schedule:Year` -> `Schedule:Week:Daily` -> `Schedule:Day:*` chain, not a `Schedule:Compact`. The
predictor read `Schedule:Compact` only, so it skipped the object and predicted **0.0000** against a
measured 2.9237 m3/h — a −100 % "error" that is entirely ours.

Fixed by extending the predictor (Schedule:Year chain + Schedule:Constant), NOT by touching the 1 %
band. And the more important change: an unreadable schedule is now an **explicit itemised FAIL (G4)**
rather than a silent 0.0. Silently predicting zero for a schedule form the reader does not
understand is exactly how a reader gap got attributed to the simulation.

### A limitation of G2, recorded because it bounds what G2 proves

The office Sat/Sun ratio in the **zero-injection** `Default_NECB` control is **2.5169** — identical
to four decimals to the fully-injected arm-H cells. The ratio is inherited from the DOE prototype
and is structurally invariant under T9-13: Saturday and Sunday both take the same weekend multiplier
`r_we`, which cancels. So G2 does separate "FINDING-9-fixed injector" from "pre-fix injector"
(which collapses Sat onto Sun -> ratio 1) — its stated counterfactual — but it does **not** separate
"injected" from "not injected at all". The gate that does is G1, and G1 is what caught all 16.
This is not a new vacuous-gate kind; it is a bound on an existing gate, written down so nobody
later quotes "office Sat/Sun differs by 151 %" as evidence the injection reached the model.

### Still open from this run

* **2 P1 shape VIOLATIONs**, both the same object: `F38 Resi_bot_S_Apartment_4 Service Water Use
  0.06gpm 140F`, `D2 peak hour 7 -> 0`. Admissible under the pre-registered exception only if the
  schedule is `MXU_Residential_DHWv2_*` with `r_wd = 0.0`. Being read off the saved IDF in job
  1171754 rather than assumed.
* Hotel DHW plant undersizing (577.1 kW demanded vs 447.6 kW installed; hotel delivered fraction
  36.8 % in Y2022) is inherited from ARCH B and is carried by every arm A–H. Unchanged here.
  Autosizing the six `WaterHeater:Mixed` objects is a re-simulation decision and remains the
  user's call.


### Follow-up, same day — both open items closed (jobs 1171754, 1171755)

**A. The 16 day-type FAILs were the predictor, confirmed.** With the Schedule:Year chain reader in
place and nothing else changed — same 1 % band, same cells, same CSVs — job 1171754 returns
**56 / 56 PASS**, `G4` reports **0 unreadable on all 56**, and the re-pre-registered prediction is met
exactly. The two diagnostic cells:

    Y2010__Tall__CLG  (hotel un-injected)     hotel  pred 2.9224  meas 2.9237  -0.04 %   [was 0.0000, -100 %]
    Default_NECB__Tall__CLG (zero injection)  office pred 0.2213  meas 0.2213  +0.00 %   [was 0.0000, -100 %]
                                              retail pred 0.0345  meas 0.0345  +0.00 %
                                              hotel  pred 2.9224  meas 2.9237  -0.04 %
                                              resid  pred 1.0004  meas 1.0004  +0.00 %

The zero-injection control now reproduces to +0.00 % on every channel. Delivered volume was correct
all along; only our prediction of it was blind.

**B. Both P1 VIOLATIONs are admissible under the pre-registered exception.** Read off the saved IDF,
not assumed. Cells `Y2015__SuperTall__CLG` and `Y2015__SuperTall__MTL`, same object and same
household in both:

    F38 Resi_bot_S_Apartment_4 Service Water Use 0.06gpm 140F
      Peak Flow Rate  3.903300198998e-06
      Schedule        MXU_Residential_DHWv2_HH46341_APARTMENTHIGHRISE_APT_DHW_SCH_r0000w0996
                                                                              ^^^^^ r_wd = 0.000

`r_wd = 0.000` is exactly the pre-registered case: a household with zero weekday occupancy has no
weekday peak hour to preserve, so `D2 peak hour 7 -> 0` is the correct outcome, not a shape bug.
The artifact still records `t9_13_audit_verdict=FAIL` on those two cells and that line is left
untouched — the FAIL is *documented-admissible*, not repaired.

Arm H P1 therefore reads **50 PASS / 2 FAIL (both verified admissible) / 4 N/A (the
`channels_requested=[]` control)**.

**G4 falsified before being counted as validation (job 1171755).** G4 passed 56/56 on its first run,
which on its own is worth nothing. Perturbation: disable the Schedule:Year reader only, leaving the
Schedule:Compact path intact — i.e. restore the predictor exactly as it stood when it produced the
16 FAILs. Three predictions written before running, three landed:

    [PASS] P1  G4 FAILs on the zero-injection control with a non-zero itemised count   (got 47)
    [PASS] P2  the old symptom is reproduced -- every channel back to 0.0 predicted
    [PASS] P3  the injected cell is UNAFFECTED, unreadable=0 -- the perturbation is surgical

P3 is the one that matters: without it, P1/P2 could have been produced by any blunt breakage.
G4 can fail, and fails for the stated reason.

**Bottom line for arm H:** 56/56 cells, aggregate closes to 1e-6 on every cell, every structural
guard holds, the volume identity closes under the corrected reader on all 56, FINDING 9 is confirmed
at the output level on all 56 including the un-injected controls, and the only two FAILs in the
whole arm are a single zero-weekday-occupancy household that was pre-registered as admissible.

New files: `Step9_docs/recheck_armH.sh`, `Step9_docs/falsify_g4.py`; `3rdJ_09H_daytype_volume_verify.py`
gained the Schedule:Year/Constant reader and gate G4.


---

## 2026-08-03 — ARM E SCORECARD RE-ISSUE against arm H: PREDICTIONS, RECORDED BEFORE SCORING

User ruling: *"re-issue arm E scorecard against arm H"*. This section is written **before** any arm-H
DHW number has been read. Everything below is derived from **inputs only** — the Step-7 products,
the T9-13 reference table, and the prototype's own daily volumes — all of which predate arm H's
simulation.

### What is being re-issued, and what is not

**Arm E's scorecard is NOT superseded.** It stands at **3 PASS / 3 FAIL / 0 UNTESTABLE**
(P1/P5/P6 PASS, P2/P3/P4 FAIL). Those verdicts were scored against predictions written before arm E
ran, and a later, better-instrumented run does not retroactively repair them. The re-issue answers a
different question: **what do the same six quantities read on the corrected build?**

### The contrast, and its one real confound

`H − C` is the same "T9-13 on/off" contrast as `E − C` (arm C is `--dhw-model none`, i.e. prototype
DHW untouched). But arm H also carries FINDING 6 (office 2030 product) and FINDING 7 (retail 2030
product), which change **occupancy** in the nine 2030-family scenarios = **36 of 56 cells**. The
other five scenarios — `Default_NECB`, `Y2005`, `Y2010`, `Y2015`, `Y2022` (**20 cells**) — are
untouched by F6/F7 and give a clean DHW-only contrast.

This is handled **by declaration, in advance**, per prediction:

* **P2** is *about* office DHW, and F6 is precisely a change to the office `r`. So P2's predicted
  values are **re-derived forward** from the corrected product (below) and scored on the same cells
  as before. This is not re-fitting: the derivation uses only inputs.
* **P3, P4** target hotel and residential, which F6/F7 do not touch. Predictions **unchanged**.
* **P5** bounds *non-DHW* end uses. On the 36 2030-family cells, F6/F7 move lighting and equipment
  directly, so `H − C` there cannot test "T9-13 does not touch non-DHW loads" — the confound is
  structural, not incidental. **P5 is therefore scored on the 20 F6/F7-free cells**, and the full-56
  number is reported beside it as confounded. The restriction is declared here, before the run, and
  is chosen because it isolates the variable P5 is about — **not** because the excluded cells
  failed, which is not yet known.
* **P1, P6** are integrity/shape and are unaffected.

### P2 re-derived — and the derivation validated against its own past first

The arm-E prediction was *"derived from the prototype's own 11.95 wd / 3.71 we daily volumes at 5/2
day weighting and the measured `r`s"*. That model is:

    ΔV/V  =  (5·V_wd·r_wd + 2·V_we·r_we) / (5·V_wd + 2·V_we)  −  1        V_wd = 11.95, V_we = 3.71

**Before using it forward, it was checked backward** against the pre-FINDING-6 `r` values it was
originally applied to. It reproduces all three recorded predictions to ≤ 0.02 pp:

| band | old r_wd / r_we | model | recorded arm-E prediction |
|---|---|---|---|
| B_cons | 0.818140 / 2.492355 | **+0.31 %** | +0.3 % |
| B_central | 0.739882 / 2.079011 | **−11.22 %** | −11.2 % |
| B_opt | 0.663995 / 1.730205 | **−21.82 %** | −21.8 % |

That agreement is what entitles the model to be used forward. The corrected `r` values are taken
from **arm H's own provenance lines** — legitimate as a *prediction* input because `r` is fixed
entirely by the Step-7 product and the reference table, both of which exist before any simulation:

| band | corrected r_wd / r_we | **RE-DERIVED PREDICTION** | arm-E prediction it replaces |
|---|---|---|---|
| B_cons | 0.868615 / 2.603310 | **+6.0 %** | +0.3 % |
| B_central | 0.800255 / 2.116786 | **−5.4 %** | −11.2 % |
| B_opt | 0.695172 / 1.603564 | **−20.4 %** | −21.8 % |

Tolerance stays **±3.0 pp** — unchanged from arm E, and not renegotiated.

🔴 **A qualitative claim dies here, and it should be said plainly.** Arm E's P2 called `B_cons`
*"the sharp one — it must come out flat despite `r_we = 2.493`, because the weekday fall and the
weekend rise nearly cancel"*. That near-cancellation was a property of the **defective** office 2030
product. With the corrected product the weekday fall is smaller (r_wd 0.818 → 0.869) and the weekend
rise larger (2.492 → 2.603), so `B_cons` is now predicted to **rise +6.0 %**, not stay flat. The
elegant "a model that merely scales DHW with occupancy cannot produce that" argument does not
survive the frame correction. Recorded, not quietly dropped.

### P3, P4, P5, P6, P1 — unchanged predictions

* **P3** hotel `B_central` **+12.4 % ± 2.0 pp**. Hotel `r ≈ 1.1244` is untouched by F6/F7 and is
  still present in arm H's provenance. Arm E measured **+15.31 %** (FAIL) — and FINDINGS 8 and 9
  were *both* shown to inflate hotel DHW (the `LAUNDRY` substitution ×3.028 → ×1.000, and the
  Sat≠Sun volume loss). Arm H has both fixed, so **the prediction that arm H lands closer to +12.4 %
  than arm E did is the sharp test of whether those two fixes explain the arm-E miss.**
* **P4** residential `B_central` **+8 % … +18 %** (pool means `r_wd = 1.210`, `r_we = 1.075`).
  Arm E measured **+51.40 %**. Stated in advance: the aggregator attributes the un-prefixed
  `Laundry Service Water Use 30.6gpm 180F` — a **hotel** object — to the **residential** channel, and
  that attribution is *not* changed by any of FINDINGS 6–9. So the residential channel total still
  contains a hotel-`r`-scaled laundry, which the +8…+18 % band never accounted for. **If P4 fails
  again, attribution is the first thing to check, and the band must not be widened for it** — the
  remedy would be an explicit re-specification of what "residential DHW" means.
* **P5** `|Δ| < 0.5 %` on every non-DHW end use with share ≥ 1 % of its channel total, **on the 20
  F6/F7-free cells**.
* **P6** identical 56 cell tags, `max |area_H − area_C| = 0 m²`. Scored first; no delta is quoted if
  it fails.
* **P1** residential night 00–05 share within 0.005 and peak draw hour unchanged, on
  `B_central__Tall__MTL`. Arm D's T9-11 signature was 0.0834 → 0.3286 and 06:00 → 04:00.

### Refutation conditions, stated now

P2 fails if any band lands outside ±3 pp of the re-derived value, or if the ordering
cons > central > opt breaks. P3 fails outside +10.4…+14.4 %. P4 fails outside +8…+18 %. P5 fails on
any material non-DHW end use ≥ 0.5 % among the 20 clean cells. P1 fails on a night-share shift
≥ 0.005 or a moved peak hour. **A miss is recorded, not repaired.**


## 2026-08-03 — ARM E SCORECARD RE-ISSUED AGAINST ARM H: **4 PASS / 2 FAIL** (job 1171763)

Scored by `Step9_docs/3rdJ_09H_score_armH.py` against the predictions recorded in the section above,
before any arm-H DHW number was read.

| | arm E | **arm H** | |
|---|---|---|---|
| P1 shape preservation | PASS | **PASS** | night 00–05 share 0.0834 → 0.0857, peak hour **06:00 unmoved** |
| P2 office DHW | FAIL | **PASS** ← changed | +5.89 / −5.23 / −19.78 % vs re-derived +6.0 / −5.4 / −20.4 |
| P3 hotel DHW | FAIL | **FAIL** | **+5.21 %** vs +12.4 ± 2.0 — now missing LOW (arm E missed high at +15.31) |
| P4 residential DHW | FAIL | **FAIL** | **+7.70 %** vs +8…+18 — misses the floor by **0.30 pp** (arm E: +51.40) |
| P5 non-DHW bound | PASS | **PASS** | 0 of 220 material end uses over 0.5 % on the 20 F6/F7-free cells |
| P6 integrity | PASS | **PASS** | 56 = 56 tags, max \|ΔArea\| = **0.0 m²** over 392 pairs |

**Arm E's 3 PASS / 3 FAIL is NOT superseded.** Those verdicts were scored against predictions written
before arm E ran; a better-instrumented later run produces new numbers, it does not repair an old
verdict.

### P2 — the FINDING 6 fix is confirmed quantitatively, not just directionally

The forward model reproduced its own recorded past to ≤ 0.02 pp on all three bands before being used
(B_cons +0.31 vs +0.3, B_central −11.22 vs −11.2, B_opt −21.82 vs −21.8), and then predicted arm H to
**0.11 / 0.17 / 0.62 pp**. Office DHW spread across the three bundles: arm C **0.004 %** (flat to 3 dp)
→ arm H **27.419 %**, ordering cons > central > opt preserved. Note that arm E's *original* numbers
would have MISSED arm H on two of three bands (+0.3 vs measured +5.89; −11.2 vs −5.23) — the change
is the corrected office 2030 product, exactly as FINDING 6 predicted.

### 🔴 P3 and P4 both miss LOW, and the cause is the same — but my first probe could not prove it

`3rdJ_09H_saturation_probe.py` (job 1171765), within arm H only, across (geometry, city) groups:

    hotel VOLUME elasticity w.r.t. r  =  1.0000   (R2 = 1.000)
    hotel ENERGY elasticity w.r.t. r  =  0.5617

S1 (the control) passes emphatically: **T9-13 delivers exactly the draw it specifies** — volume
tracks `r` to four decimals. Energy does not.

**But that probe's "SATURATION CONFIRMED" verdict is WITHDRAWN — it was under-specified and I should
not have written it.** A constant standby/distribution loss produces an energy elasticity below 1
with no capacity constraint at all, since `E = L + V·ρc·ΔT` gives
`dlnE/dlnV = 1/(1 + L/(V·ρc·ΔT)) < 1`. Over a volume range of only 0.98×…1.20× the two candidates are
near-indistinguishable in shape. **A test that cannot separate its two candidate explanations is not
evidence for either.**

The discriminator is the **marginal** energy per m³, not the average: a fixed loss does not scale with
draw, so under the constant-loss model the marginal cubic metre must still be served at the FULL
target rise. `3rdJ_09H_saturation_discriminate.py` (job 1171767), D1–D4 pre-registered:

    group             n   slope b   intercept a      R2   dT_marg     quad
    SuperTall__CLG   14  0.103672        2469.9  0.9654   24.78 K  -3.0e-06
    SuperTall__MTL   14  0.101874        2536.7  0.9888   24.35 K   4.3e-06
    Tall__CLG        14  0.087781        1805.0  0.9892   20.98 K  -2.3e-06
    Tall__MTL        14  0.085892        1859.5  0.9959   20.53 K   6.0e-07

Target rises actually present in the IDF: **140F → 49.2 K, 180F → 71.4 K** (mains 10.81 °C). The
marginal draw is being served at **22.66 K on average — 46.1 % of the most generous benchmark**, and
below 70 % in every one of the four groups. **D3 SATURATION met; D2 CONSTANT-LOSS not met.**

**D4 corroborates with no fit at all** — average delivered rise falls monotonically as `r` rises:

    r    0.9801  1.0000  1.0143  1.0344  1.0890  1.1244  1.1434  1.2031
    dT   41.50   41.65   41.49   40.69   39.90   39.43   39.17   38.40  K       d(dT)/d(ln r) = -17.56 K

Note the baseline itself: **41.65 K at r = 1.0 against a smallest target of 49.2 K**, and the
volume-weighted target is higher still because the 180F laundry is the largest draw. The hotel plant
is short *before* any occupancy scaling is applied.

**🔴 D1, my own linearity control, FAILED in one group of four** (`SuperTall__CLG`, R² 0.9654 < 0.98).
Recorded, not waved through. Reading it honestly: the quadratic terms are ~1e-6 and of **inconsistent
sign across groups**, so the miss is scatter (other scenarios' thermal coupling), not curvature — but
D1 as written says that group's fit-based number is inadmissible, so **the saturation conclusion
rests on the three groups that pass D1 (dT_marg 20.53 / 20.98 / 24.35 K, all ≤ 50 % of target) and on
D4, which needs no fit.** It still holds; it holds on less than I first claimed.

### What this means for P3 and P4 — a MIS-SPECIFICATION, and the remedy is not a wider band

P3 predicted **+12.4 %** from `r_hotel ≈ 1.1244`, i.e. it predicted a **volume** change and scored it
against an **energy** measurement. On a plant that converts only ~46 % of a marginal cubic metre, those
are not the same quantity. Two separable contributions to the 7.2 pp miss:

1. the prediction used the MTL `r` (1.1244) for a scenario whose four cells average
   **r = 1.1070** across both cities — so the volume-side prediction should have been **+10.70 %**
   (~1.7 pp of the gap is the prediction's own city-averaging);
2. **+10.70 % of volume → +5.21 % of energy** is the plant, an implied local elasticity of **0.50**.

P4 (+7.70 % vs a +8 % floor, a **0.30 pp** miss) is consistent with the same mechanism reaching the
residential channel through the aggregator's attribution of the un-prefixed hotel
`Laundry Service Water Use 30.6gpm 180F` — which is the single most saturation-limited object in the
tower — to **residential**. **This is a candidate, NOT a tested result**: the laundry cannot be split
out of the channel total from the aggregate tables, so it has not been isolated.

**No band was widened and no verdict was repaired.** The honest remedy for P3 is re-specification —
predict the volume (which T9-13 controls and delivers exactly, elasticity 1.0000) or predict energy
through an explicit plant model — and that re-specification is a change of declared gate semantics,
so it is **the user's call**, not mine.

### 🔴 This sharpens the open user decision, and puts a number on it

The hotel DHW plant undersizing is no longer a static observation about installed kW; it is now
measured as an **active distortion of every DHW result in every arm**: 54 % of any increase in hotel
draw does not appear as delivered energy. Any "hotel DHW rises X % under scenario Y" statement in
Steps 8–9 is a plant-capacity statement as much as an occupancy statement. `Autosize`-ing the six
`WaterHeater:Mixed` objects would move every hotel and residential DHW number in every arm — a
re-simulation decision, still the user's.

New files: `Step9_docs/3rdJ_09H_score_armH.py`, `3rdJ_09H_saturation_probe.py`,
`3rdJ_09H_saturation_discriminate.py`. Jobs 1171763, 1171765, 1171767.


## 2026-08-03 — AUTOSIZE IS NOT A FLAG: EnergyPlus refuses it (jobs 1171802, 1171805)

User instruction: *"autosize les 6 WaterHeater:Mixed et relance la campagne"*, together with the
methodological question of whether repeating a 56-cell campaign per iteration is the right loop.

**The campaign was NOT launched, and the probe is why.** `3rdJ_09H_autosize_probe.py` on 3 cells
(`Tall__MTL` at r = 1.0000 / 1.1244 / 1.2031, reusing arm H's own injected IDFs so plant sizing is
the only variable). All three died in **20 seconds**:

    ** Fatal ** SizeTankForSupplySide: Tank="300GAL NATURAL GAS WATER HEATER - 300KBTU/HR
                0.804 THERM EFF", requested sizing for max capacity but entered Recovery Time is zero.

The six `WaterHeater:Sizing` objects are `Design Mode = PeakDraw`, `Time Storage Can Meet Peak Draw
= 0.538503 h`, **`Time for Tank Recovery = 0`**. Under `PeakDraw` that last field is what sizes the
BURNER. Setting `Heater Maximum Capacity` to `Autosize` against a zero recovery time is not a silent
no-op — EnergyPlus refuses to start. **A recovery time has to be chosen, and that is a design
decision, not a mechanical fix.**

The probe's guard did its job on the way in: the edit asserts exactly 6 replacements of each field
and refuses otherwise, so a partial edit could not have masqueraded as a run.

### What the plant is actually asked for (job 1171805, from arm H's own hourly volumes)

| cell | peak m³/h | kW @ 49.2 K | kW @ 71.4 K | vs 447.6 kW installed |
|---|---|---|---|---|
| `Y2022__Tall__MTL` | 10.8173 | 618.6 | 897.7 | **1.38× – 2.01×** |
| `B_opt__Tall__MTL` | 12.6319 | 722.3 | 1048.2 | **1.61× – 2.34×** |

**The peak and the 99th percentile are identical in both cells** — the tower sits at that draw for at
least 88 h/yr, so this is not one freak hour and sizing to it is not over-conservative. Hotel is
**80.1 % / 82.5 %** of the tower peak-hour draw; residential 14.8 / 14.4 %, office 4.6 / 2.7 %,
retail 0.5 / 0.4 %.

### 🔴 A methodological trap in the obvious fix, recorded before anyone falls into it

Per-cell `Autosize` would give each cell a plant matched to **its own** demand — so `B_opt` (r = 1.20)
would receive a larger boiler than `B_cons` (r = 0.98). The 56-cell grid is designed so that cells
differ **only** in occupancy; sizing the plant per scenario breaks exactly that, and "DHW rises with
occupancy" would partly become "we gave it a bigger boiler". **If the plant is resized, it must be
resized ONCE, from the grid maximum, and applied identically to all 56 cells.**

### On the method question — why this probe replaced a campaign

Cost of the answer: **20 seconds × 3 cells**. Cost of finding it by launching arm I: ~4 h and 56
result directories. And the record supports the general rule — of everything the last three campaigns
surfaced, the 16 day-type FAILs, the −36.9 % identity FAIL and FINDING 9 were all defects in **our
readers and writers**, and the plant saturation was extracted from arm H's **existing** files with no
new simulation at all. The loop that works is: **instrument (output variables are free) → probe 2–4
cells for anything that is a property of the building rather than the scenario grid → run 56 once,
when the specification is frozen.**

New files: `Step9_docs/3rdJ_09H_autosize_probe.py`, `autosize_probe.sh`, `3rdJ_09H_peak_demand.py`.


---

## 2026-08-03 — Uniform plant resize, K = 3.0: the 3-cell probe (job 1171807)

**User decision, 2026-08-03:** uniform hard-size to the grid maximum. The plant becomes a *constant*
across the 56 cells, so the occupancy lever stays clean — the trap recorded above is avoided by
construction, not by care.

### The number, measured not assumed (job 1171806, all 56 cells of arm H)

| quantity | value |
|---|---|
| grid-max peak hourly draw | 15.8878 m³/h |
| at the 180 °F target rise (71.4 K) | **1318.4 kW** ← the conservative bound |
| at the 140 °F target rise (49.2 K) | 908.5 kW |
| installed | **447.6 kW** (5 × 87,921.3 + 7,999.96) |
| ratio | 2.95 → **K = 3.0**, ~2 % headroom |

### Why the intervention is energy-neutral by construction

Only `Heater Maximum Capacity` is scaled, on all six `WaterHeater:Mixed`. Three IDF facts checked
*before* choosing this edit, each of which would otherwise have made a larger burner inflate energy
on its own:

* **`Part Load Factor Curve Name` is EMPTY** → thermal efficiency is a flat 0.803984 regardless of
  distance from full load. Oversizing carries no efficiency penalty.
* **`Off/On Cycle Parasitic Fuel Consumption Rate` = 8,146.58 W is a CONSTANT**, not capacity-scaled.
  Six of them = 48.9 kW = **1,542 GJ/yr**, which is most of the ~1,860 GJ fixed intercept the
  saturation discriminator independently measured on `Tall__MTL`. That is a cross-validation of the
  earlier decomposition: the intercept really was a fixed loss, and the depressed marginal ΔT really
  was a separate saturation effect.
* **`Tank Volume` untouched** → the 11.2595 W/K loss coefficient acts on the same storage, so
  standby losses are identical. The edit refuses to run unless the `Tank Volume` fields survive it.

So the burner can only ever *meet more of the load*; it cannot manufacture energy by being larger.

### Result — 3 cells, `Tall__MTL`, 19 min each, all exit 0

| cell | r | installed | ΔT arm H → resized | gain | energy |
|---|---|---|---|---|---|
| `Y2022__Tall__MTL` | 1.0000 | 447.6 → 1342.8 kW | 31.62 → **42.41 K** | +10.79 K | +34.14 % |
| `B_central__Tall__MTL` | 1.1244 | 447.6 → 1342.8 kW | 29.93 → **40.61 K** | +10.68 K | +35.70 % |
| `B_opt__Tall__MTL` | 1.2031 | 447.6 → 1342.8 kW | 28.88 → **39.43 K** | +10.55 K | +36.52 % |

*(tower-wide, all 47 `WaterUse:Equipment` objects)*

**[PASS] R1 — CONTROL.** DHW volume moved **+0.0000 %** in all three cells. Draw is schedule-driven
and a burner resize must not touch it; it did not. Without this the ΔT gains below would be
uninterpretable, since a volume change would move ΔT = E/(V·ρc) by itself.

**[PASS] R2 — delivered rise moves up in every cell**, by +10.6 to +10.8 K, with energy up 34–37 %.
That is not new demand: R1 fixes the volume, so every one of those joules is **load the old plant was
silently failing to serve**. The 447.6 kW burner was dropping roughly a third of the tower's DHW
energy on the floor, and nothing in the arm-H outputs said so.

### 🔴 An honest miss inside a PASS — R2's ordering sub-clause FAILS

R2 as pre-registered had two clauses. Quoting the pre-registration verbatim:

> R2  Tower-wide implied delivered rise goes UP in every cell, **and goes up MORE in the cells that
> were more constrained** (… so the ordering of the GAINS must be the reverse of the arm-H levels).

The first clause passes. **The second fails.** The most-constrained cell (`B_opt`, lowest arm-H ΔT at
28.88 K) gains the **least** (+10.55 K); the least-constrained (`Y2022`, 31.62 K) gains the **most**
(+10.79 K). The ordering is *with* the arm-H levels, not reversed.

**The coded gate only tested `dTr > dTh`, so it printed PASS.** This is a fresh instance of a known
family — *the gate whose printed verdict is narrower than the prediction it claims to test* — and it
is recorded, not repaired. The band is not widened and the PASS is not re-labelled; the sub-clause is
marked FAILED and carried.

Why it plausibly fails (hypothesis, **not** verified, and not used to excuse anything): the gain is
bounded by the *unserved* fraction, and at K = 3.0 the burner is no longer binding in any of the
three cells, so all three converge toward their own target rise. Cells with a higher target-weighted
mix then show a larger absolute gain regardless of how constrained they were. If that is right the
ordering clause was mis-specified — it assumed the resize would still be partially binding. **A
mis-specified clause is re-specified in writing, never quietly dropped**, and that re-specification
has not been done.

### R3 is NOT answerable from this output — scope mismatch caught before quoting

The probe prints **tower-wide** totals. R3's ≥ 0.90 threshold was written against the **hotel-scoped**
elasticity (arm H: 0.5617, job 1171767). The two are not the same estimator: the tower includes four
channels that do not vary with hotel `r`, which dilutes the elasticity toward zero. Tower-wide these
runs give 0.314 → 0.409 — **an uninformative number that must not be reported as R3.**

Job **1171812** re-scopes both sides to hotel, and does it by *importing* the campaign driver's
`_write_dhw_hourly_csv` rather than re-deriving the channel map, so the quantity the whole verdict
rests on has exactly one source of truth in the repo.

An **R0 control was added ahead of R3**: the recomputed arm-H hotel elasticity must reproduce 0.5617
to within ±0.02. If it does not, this script's estimator is not the one the 0.90 threshold was
written against and R3's number means nothing — so **R3 is not quoted until R0 passes.**

New files: `Step9_docs/3rdJ_09H_plant_resize_probe.py`, `resize_probe.sh`,
`Step9_docs/3rdJ_09H_resize_elasticity.py`, `resize_elasticity.sh`.

**Status: no campaign launched.** R3 decides whether K = 3.0 is sufficient; if it misses, K is
revisited *before* arm I, not after.

---

## 2026-08-03 — R3 hotel-scoped: **FAIL at K = 3.0** (jobs 1171812 crash, 1171835 result)

The 3-cell resize probe (1171807) printed TOWER-WIDE totals; R3's 0.90 threshold and the 0.5617
baseline are HOTEL-scoped. Tower-wide those runs give 0.314 → 0.409, and that number was explicitly
**refused** as an R3 answer rather than quoted with a caveat. `3rdJ_09H_resize_elasticity.py`
re-scopes both arms through the campaign driver's own channel resolver (imported, not re-derived,
so the quantity the verdict rests on has one source of truth).

### The first run crashed, and the crash was luck — a silent-default defect

Job 1171812 died in LAPACK: `SVD did not converge in Linear Least Squares`. Cause: `hotel_r()`
guessed three provenance filenames (`provenance.txt`, `provenance.json`, `inject_provenance.txt`);
the real one is **`injected.idf.provenance.txt`**. Finding none, it returned its documented
"safe" default `r = 1.0` — for **all three cells**. The regressor had zero variance, so the fit
was undefined and numpy refused.

**The refusal was accidental, not designed.** Had two cells matched the pattern and one not, the
default would have silently produced a plausible wrong elasticity, and nothing in the output would
have looked abnormal. The defect is not the wrong filename; it is that **the fallback value was
indistinguishable from a legitimately measured one**. `r = 1.0` is a real, expected value in this
grid (`Y2022`), so "unread" and "read as 1.0" collapsed into the same number.

Add to the vacuous-gate taxonomy, adjacent to the silence entry:
**the default that cannot be distinguished from a measurement.** A fallback that returns a value
inside the legal range of the quantity converts a read failure into a data point.

Both fixed in `3rdJ_09H_resize_elasticity.py`:
* `hotel_r()` has **no default any more** — an unreadable r is a `SystemExit`, and disagreement
  between the four hotel schedules is also a refusal. r is parsed from the injector's own record,
  the derived schedule name token `..._r{r_wd*1000:04d}w{r_we*1000:04d}_...`.
* A guard in `main()` refuses when `len(set(r)) < 2`, in the script's own terms, before any fit.
  An elasticity w.r.t. a constant regressor is not a weak estimate, it is undefined; that belongs
  in a pre-fit check, not in a linear-algebra backend's error message.

Recovered r from provenance: `Y2022` **1.000**, `B_central` **1.124**, `B_opt` **1.203** (the token
carries 3 decimals; the campaign spec's 1.1244 / 1.2031 round to these, a ~0.2 % effect on the
slope and immaterial against the 0.44-vs-0.90 gap).

### Result, job 1171835

| cell | r | arm H V (m³) | arm H E (GJ) | arm H ΔT | resized E (GJ) | resized ΔT |
|---|---|---|---|---|---|---|
| `Y2022__Tall__MTL`     | 1.000 | 25,571.2 | 2,578.0 | 24.10 K | 4,189.2 | 39.15 K |
| `B_central__Tall__MTL` | 1.124 | 28,752.1 | 2,749.4 | 22.85 K | 4,407.5 | 36.64 K |
| `B_opt__Tall__MTL`     | 1.203 | 30,764.7 | 2,858.6 | 22.21 K | 4,544.9 | 35.31 K |

```
hotel ENERGY elasticity   arm H 0.5582 (R2 1.000)   resized 0.4403 (R2 1.000)
hotel VOLUME elasticity   arm H 1.0007              resized 1.0007
marginal delivered rise   arm H  12.91 K            resized  16.38 K   (target 49.2 K)

[PASS] R0   arm-H hotel elasticity reproduces the probe's 0.5617: got 0.5582 (|d|=0.0035, tol 0.02)
[PASS] R3v  hotel VOLUME elasticity ~1.0 in both arms (1.0007 / 1.0007)
[FAIL] R3   resized hotel ENERGY elasticity >= 0.90: got 0.4403
[PASS] R4   marginal delivered rise moves up: 12.91 -> 16.38 K (33.3 % of target)
```

**R0 PASS is what licenses quoting R3 at all.** Recomputed hotel-scoped arm H = 0.5582 against the
saturation probe's 0.5617, |d| = 0.0035 inside the 0.02 tolerance. Same estimator, so the 0.90
threshold transfers.

**R3v PASS, and it is exact rather than approximate.** Hotel volumes stand in ratios
28,752.1 / 25,571.2 = 1.1244 and 30,764.7 / 25,571.2 = 1.2031 — the r values themselves. The draw
is schedule-driven and provably cannot see the burner, so any ΔT movement is plant-side.

### 🔴 R3 FAILS, and it fails in the wrong direction

Not "insufficiently improved" — **worse**. 0.5582 → 0.4403 under 3× the burner. Because volume
elasticity is exactly 1.0, the decomposition
`elasticity_E = elasticity_V + elasticity_ΔT` is clean:

| arm | elasticity_V | elasticity_ΔT | elasticity_E |
|---|---|---|---|
| arm H (447.6 kW)  | 1.0007 | **−0.443** | 0.5582 |
| K = 3.0 (1,342.8 kW) | 1.0007 | **−0.559** | 0.4403 |

Tripling capacity made the temperature sag with occupancy **stronger**. Under the capacity-mediation
hypothesis that number had to shrink toward zero. Corroborating: K = 3.0 installs 1,342.8 kW against
the measured grid-max peak requirement of 908.5 kW at the 49.2 K target — already non-binding at the
worst hour of 8760 — yet delivered ΔT sits at 35–39 K, not 49.2 K.

**This is positive evidence against burner capacity being the binding constraint**, not merely a
failure to reach a threshold. The threshold is NOT widened and no 56-cell campaign launches at
K = 3.0.

### R4's PASS is not a pass — it is unresolved

R4 was pre-registered as: the marginal rise *"rises from arm H's 22.66 K toward the 49.2 K target"*.
The coded gate tests `mR > mH` against the **recomputed** baseline (12.91 K), not the written one
(22.66 K, job 1171767, never re-scoped). Against the number actually in the pre-registration,
16.38 K < 22.66 K would **fail**. The verdict flips on which baseline is used, and R4 has no
R0-style control to settle it — R0 exists precisely because that scope question was anticipated
for R3 and not for R4.

**R4 is recorded as UNRESOLVED, not PASS.** Third narrow-verdict instance in one day, after R2's
ordering sub-clause and the silent-default above.

### Next: pre-registered K sweep, K ∈ {6, 10}, same 3 cells (6 runs)

A larger K is proposed *because the user asked for it*, but the evidence above says it is a coin
flip, so the sweep is specified to make **either** outcome a result:

* **K1  CONTROL** — hotel volume unchanged (≤ 0.1 %) at every K, as R1. If volume moves, the edit
  is not surgical and nothing downstream is readable.
* **K2  DECISIVE** — hotel energy elasticity rises **monotonically** with K and reaches ≥ 0.90 at
  K = 10. Measured so far: K=1 → 0.5582, K=3 → 0.4403 (already non-monotone), so K2 is predicted to
  fail; it is written down anyway because a prediction only counts if it was made before the run.
* **K3  DISCRIMINATOR** — delivered ΔT at r = 1.0 (`Y2022`) as a function of K. If capacity-limited,
  ΔT → 49.2 K: pre-register **ΔT(K=10) ≥ 47 K**. If **ΔT(K=10) < 42 K**, burner capacity is
  REFUTED as the binding constraint and **no K fixes R3** — the search moves to tank volume,
  `Use Side Effectiveness`, or plant-loop flow.
* **K4** — the sag |elasticity_ΔT| shrinks with K. It grew from 0.443 to 0.559 between K=1 and K=3;
  continued growth or flatness at K=6,10 is further positive evidence against the capacity story.

K3 is the one that carries information regardless of which way it lands, which is why it is the
discriminator and not K2.

---

## 2026-08-03 — K sweep: **R3 PASSES at K = 10**, capacity confirmed as the binding constraint (jobs 1171837 array, 1171843)

Log: `/speed-scratch/o_iseri/step8_4split/campaign/logs/kelast_1171843.out` (per-cell EnergyPlus in
`ksweep_1171837_%a.out`). Same three `Tall__MTL` cells, same estimator, same 0.90 threshold. Nothing
was widened.

### The four points

Installed = 447.6 kW x K on six `WaterHeater:Mixed` burners; nothing else touched (R1/K1 volume
control holds at every K — hotel volume is identical to arm H in all three cells at all four K).

| K | installed kW | hotel E-elasticity | R2 | dT(Y2022) | dT(B_central) | dT(B_opt) | marginal rise |
|---|---|---|---|---|---|---|---|
| 1 (arm H) |   447.6 | 0.5582 | 1.000 | 24.10 K | 22.85 K | 22.21 K | 12.91 K |
| 3         | 1,342.8 | 0.4403 | 1.000 | 39.15 K | 36.64 K | 35.31 K | 16.38 K |
| 6         | 2,685.6 | 0.3005 | 1.000 | 61.11 K | 56.27 K | 53.70 K | 17.22 K |
| **10**    | **4,476.0** | **1.0013** | 1.000 | **65.50 K** | **65.51 K** | **65.51 K** | **65.55 K** |

Hotel VOLUME elasticity is 1.0007 in every arm at every K, so R3v holds throughout and the energy
elasticity is readable as a plant-mediation measurement, exactly as pre-registered.

R0 was re-derived independently inside each K block and PASSED both times (0.5582 vs the probe's
0.5617, |d| = 0.0035, tol 0.02). That is what licenses quoting R3 at K = 6 and K = 10 against the
0.90 threshold — the estimator is demonstrably the one the threshold was written against.

### K3, the discriminator: **PASS**, and it was the right thing to have pre-registered

Written before the run: *"pre-register dT(K=10) >= 47 K. If dT(K=10) < 42 K, burner capacity is
REFUTED as the binding constraint and NO K fixes R3."* Measured: **65.50 K**. Capacity is confirmed.

At K = 10 the delivered rise is **65.50 / 65.51 / 65.51 K** — identical across three cells whose draw
volumes differ by 20 %. That is the signature of a plant that is no longer the binding constraint:
delivered temperature has gone constant, so hotel DHW energy is a pure linear function of hotel draw
volume, and the elasticity is 1.0013 by consequence rather than by tuning. This is precisely the
condition the user's "uniform hard-size to grid max" decision was meant to create: the plant is a
constant across the grid and the occupancy lever is clean.

65.51 K is the model's own unconstrained mains-to-setpoint rise. It is NOT the 49.2 K (140 F) figure
the sizing calc used as its target — see the correction below.

### K2 and K4 **FAIL as written**. Recorded, not repaired.

- **K2 FAIL.** K2 was a conjunction: *"elasticity rises MONOTONICALLY with K and reaches >= 0.90 at
  K = 10."* The second clause passes (1.0013). The first fails outright: 0.5582 -> 0.4403 -> 0.3005
  -> 1.0013. The elasticity falls for three consecutive K and then snaps up. K2 as written is a FAIL,
  and it is logged as a FAIL even though the outcome it was protecting (R3 >= 0.90) was achieved.
  It had been pre-registered as PREDICTED TO FAIL; it failed for the predicted reason.
- **K4 FAIL.** *"the sag |elasticity_dT| shrinks with K."* Decomposed, elasticity_dT = elasticity_E
  minus elasticity_V: **-0.4425 (K=1) -> -0.5604 (K=3) -> -0.7002 (K=6) -> +0.0006 (K=10)**. The sag
  grew by 58 % before collapsing to zero. Non-monotone, so K4 fails as written.

**This is the fourth narrow-verdict instance in two days** (after R2's ordering sub-clause, the
silent-default reader, and R4's baseline mismatch). The pattern is now explicit enough to name: *a
gate written as a conjunction of a trend clause and a threshold clause reports one verdict for two
independent claims.* Both K2 and K4 should have been split into `K2a` monotonicity / `K2b`
threshold. The remedy is re-specification of the clause, not absorption of the failure into the
passing half.

### Why the elasticity dips before it snaps — and what that does to the K = 3 conclusion

At K = 3 and K = 6 the burner is bigger but **all three cells are still saturating**; the extra
capacity is absorbed preferentially by the cell with the smallest draw (`Y2022`, r = 1.0), because it
runs out of load first and can convert the whole increment into delivered temperature. Its energy
therefore rises fastest in relative terms, which flattens the E-vs-r slope and *lowers* the measured
elasticity. Only when capacity clears the largest cell's demand does delivered temperature go
constant and the elasticity jump to 1.0. **The elasticity is non-monotone in K by construction: it
must dip before it snaps.**

This retro-explains the K = 3 result and **corrects the reading logged earlier today**. The previous
section recorded the wrong-direction move (0.5582 -> 0.4403, sag growing) as *"positive evidence
against burner capacity being the binding constraint."* That inference was wrong. It was a partial-
relief artifact of crossing saturation, not a refutation. The earlier entry is left standing as
written — a miss is recorded, not repaired — and this paragraph is its correction.

The methodological point worth keeping: **a monotonicity prediction on a quantity that crosses a
saturation boundary is not a well-formed prediction.** K2 and K4 were both of that kind, which is why
both failed while the underlying hypothesis they were probing turned out to be true. Do not read a
non-monotone trend clause as evidence about the mechanism.

### Two corrections to the sizing calculation, both material

1. **The peak-draw sizing calc understated the requirement by ~3.4x.** It concluded K = 3.0 from a
   grid-max hourly-mean draw of 15.8878 m3/h at a 71.4 K rise = 1,318.4 kW. Full un-saturation in
   fact required 4,476 kW. The calc was computed on **hourly means**, which cannot see the sub-hourly
   timestep peak or the tank-recovery dynamics that actually set the burner duty. Any future sizing
   argument on this plant must be made on the simulation timestep, not on hourly aggregates.
2. **The 49.2 K "target" is not the model's setpoint.** It was an assumed 140 F rise. The model's
   unconstrained rise is 65.51 K. That is why R4 at K = 10 reports 133.2 % of target: the
   denominator is wrong, not the numerator. **R4's target constant `TARGET_K = 49.2` in
   `3rdJ_09H_resize_elasticity.py:45` is hereby flagged as mis-specified** and must be re-derived
   from the IDF setpoint before R4 is quoted anywhere. This is a second, independent defect in R4, on
   top of the baseline-scope mismatch logged this morning — R4 is now UNRESOLVED on two counts.

### Magnitude consequence, and why the campaign is still not launched

Hotel DHW energy at K = 10 rises **2,578 -> 7,008 GJ on `Y2022__Tall__MTL` (x2.72)**, and similarly
on the other two cells. The resize is *efficiency*-neutral by the flat-PLF / constant-parasitic
argument (verified: `Part Load Factor Curve Name` empty, parasitics constant, tank volume untouched),
but it is emphatically **not magnitude-neutral** — meeting more of the load is the entire point. The
tower EUI will move substantially and will need re-validation against the hotel EUI band.

**Blocking issue before any 56-cell launch: the three swept cells are not representative of the
grid.** All three are `Tall__MTL`, and `Y2022__Tall__MTL` is the **3rd-LOWEST** peak-draw cell of the
56 (10.8173 m3/h). The grid extremes, from job 1171806:

| | cell | peak draw m3/h |
|---|---|---|
| grid MAX | `sens_hotel_opt__SuperTall__MTL` | 15.8878 |
| grid MIN | `B_cons__Tall__CLG` | 10.6444 |
| swept trio | `*__Tall__MTL` | 10.82 - 11.9 |

The grid maximum is **1.47x** the cell K = 10 was verified on. K = 10 un-saturating the low end is no
evidence that it un-saturates the high end, and if it does not, the plant is not a constant across
the grid and the whole point of the uniform hard-size is lost. **56-cell campaign remains BLOCKED**
pending the headroom check below.

### Headroom check — PRE-REGISTERED before running (submitted 2026-08-03)

K = 10 applied to the two grid EXTREME cells, `sens_hotel_opt__SuperTall__MTL` (max) and
`B_cons__Tall__CLG` (min). Scripts: `Step9_docs/headroom_check.sh` (array 0-1) and
`Step9_docs/headroom_elast.sh` (dependent).

- **H1 CONTROL** — hotel volume unchanged from arm H (<= 0.1 %) in both cells, as K1/R1. If volume
  moves, the edit is not surgical and nothing below is readable.
- **H2 DECISIVE** — hotel-scoped delivered dT at K = 10 reaches the same unconstrained constant in
  BOTH extremes: **>= 65.0 K**, and the two cells agree with each other to within **0.5 K**. If the
  grid-max cell lands below 65.0 K, K = 10 does NOT un-saturate the grid, the 56-cell campaign stays
  blocked, and K must be raised and re-tested. Agreement between the extremes is the actual claim —
  a uniform plant is only a valid control if it delivers the same temperature everywhere.
- **H3 FALSIFIER, so that H2 is not vacuous** — the UNRESIZED arm-H dT in these same two cells must
  be **< 40 K**. If arm H already delivered ~65.5 K at the grid max, H2 could not possibly fail there
  and would be measuring nothing. H3 is what establishes that H2 has something to detect. Expected
  ~22 K by analogy with the trio, but it is measured here, not assumed.
- **H4 INFO** — record each extreme cell's measured peak requirement against the 4,476 kW installed.

**The elasticity block printed by `3rdJ_09H_resize_elasticity.py` on this pair is N/A BY
CONSTRUCTION and must not be quoted.** The two cells differ in building height (SuperTall vs Tall),
climate (MTL vs CLG) and scenario, so a 2-point E-vs-r fit across them confounds occupancy with
geometry. R0 is *expected to FAIL* in this run for exactly that reason — it was calibrated on the
`Tall__MTL` trio — and that failure is the script correctly refusing to let R3 be read. Only the
per-cell `dT` lines are in scope for H1-H4.

---

## 2026-08-03 — headroom check attempt 1 REFUSED: **`SuperTall` has 11 heaters, not 6** (job 1171855)

The headroom check was submitted as array 1171855 (K = 10 on the two grid extremes). Task 1
(`B_cons__Tall__CLG`, the grid MIN) ran normally. **Task 0, the grid-MAX cell
`sens_hotel_opt__SuperTall__MTL`, refused in 2 seconds:**

    REFUSING: expected 6 Heater Maximum Capacity fields, rewrote 11

**The guard was right and my constant was wrong.** `3rdJ_09H_plant_resize_probe.py` hard-coded
`N_HEATERS = 6`, measured on the `Tall` geometry. `SuperTall` carries **11** `WaterHeater:Mixed`
objects. The probe refused rather than half-editing the plant and running anyway, which is the
outcome the guard was written for.

### What this invalidates

🔴 **"installed = 447.6 kW" is a `Tall`-geometry number and was never a grid-wide constant.** It
appears throughout the sizing work — in the K-sweep tables, in the `resize_probe` docstring, in the
"installed 4,476 kW at K = 10 vs a 1,318 kW peak requirement" comparison. **Every one of those
statements is now scoped to `Tall` cells.** The K-sweep result itself is unaffected: all three swept
cells are `Tall__MTL`, so the comparison was internally consistent; what is wrong is the extrapolation
to the other 28 `SuperTall` cells of the grid, which was never measured.

The probe also *labelled* its output lines `arm H (447.6 kW)` / `resized (447.6*K kW)`. On a
`SuperTall` cell that label would have been wrong by roughly a factor of two **while looking
authoritative** — a fabricated number printed beside a measured one.

### Fix

`N_HEATERS = 6` is replaced by a **per-IDF measured count**. The guard is reformulated from *"exactly
six fields were rewritten"* to *"every `Heater Maximum Capacity` field the IDF declares was
rewritten"*, with the count taken from the file under edit before the substitution:

    declared = len(pat.findall(txt))
    txt, cnt = pat.subn(sub, txt)
    if cnt != declared: raise SystemExit(...)

**A guard whose reference encodes an assumption about the stock cannot detect that the assumption is
wrong.** That is the same shape as vacuous-gate #9 (the gate whose reference comes from the same
source it audits) with the source displaced one step further — into the author's head. The old form
would have passed silently on any future `Tall` cell and refused loudly on every `SuperTall` one,
which is a lucky failure mode, not a designed one.

The installed base is now **printed and machine-readable** (`PLANT_BASE kW_base=... kW_resized=...
n_heaters=...`), and both summary labels carry the cell's own measured capacity instead of 447.6.

### Does this break the user's "uniform hard-size" decision?

**No, and the reason is worth stating explicitly.** `K` is a multiplier of each cell's own installed
base, so cells of different **geometry** do not land on the same absolute kW. The user's decision was
that the **occupancy** axis must not buy capacity — "`B_opt` (r = 1.20) must not get a larger boiler
than `B_cons` (r = 0.98)". Within any geometry group every scenario gets an identical plant, so that
requirement holds exactly. Geometry is a design axis that already differs in floors, area and zone
count; it is not the lever the 56-cell grid exists to measure.

And once the plant is **non-binding** the question dissolves: delivered ΔT goes constant (65.51 K on
the `Tall` trio) and capacity drops out of the energy answer entirely. Whether the SuperTall plant is
non-binding at K = 10 is precisely what gate **H2** tests — so the right response is to run the
check, not to redesign the intervention.

### 🔴 A second defect, in this project's own harness — vacuous-gate #10, again

`headroom_check.sh` ended with

    $PY -u ... 3rdJ_09H_plant_resize_probe.py ...
    echo "  probe exit=$?  : $(date)"

`echo` is the last command, so **the job exits with `echo`'s status — always 0.** Task 1171855_0
died on the refusal above and SLURM reported it **COMPLETED in 2 s**, and the `--dependency=afterok`
dependent job (1171857) was duly released to run against output that did not exist.

This is **vacuous-gate #10 — the gate that reads the wrong process's exit code — for the second time
on this project**, after `smoke_f9fix.sh:47`. The earlier repo-wide sweep found exactly one
occurrence and concluded the pattern had not been copied around; that conclusion was correct **for
the code that existed at the time**, and the pattern was then reintroduced by hand in new scripts
written the same week. **A sweep certifies a snapshot, not a habit.** The lesson to carry: this
failure is not found by grepping once, it is prevented by never making a bare `echo` the last line of
a job script.

Fixed in `headroom_check.sh` and `resize_sweep.sh` (`RC=$?; echo ...; exit $RC`). The K sweep was not
misled — all six of its tasks genuinely ran — but its harness was unsound while it ran.

### State

- 1171857 **cancelled** (it would have run against a missing SQL).
- **1171858** — headroom check re-submitted, `--array=0`, grid-max cell only, fixed probe.
- **1171859** — dependent hotel-scoped ΔT, `--dependency=afterok:1171858,afterany:1171855`, so it
  waits for both the re-run and the still-running min-side task.
- `1171855_1` (`B_cons__Tall__CLG`) is left to finish. Its output is valid: on a 6-heater cell the
  old and new probe produce a byte-identical IDF edit — same regex, same K — and only the printed
  labels differ.
- **H1–H4 are unchanged.** The pre-registration was written before any of this and is not revised;
  a refused run is not a failed gate, it is no measurement at all.

---

## 2026-08-04 — headroom check: both simulations landed, **H2 NOT YET SCORABLE** (jobs 1171858_0 / 1171855_1)

Both EnergyPlus runs of the headroom check completed. The dependent scorer **1171859 has NOT run** —
it is `PENDING (AssocGrpCpuLimit)`: the account's CPU allocation is fully consumed by a ~100-task
array (`1171864`) belonging to another workload on the same account. Its dependencies are satisfied;
it is queued on resources only.

### What the two probes measured

| cell | geometry | heaters | installed | arm H dT | K = 10 dT | gain |
|---|---|---|---|---|---|---|
| `sens_hotel_opt__SuperTall__MTL` (grid **MAX** draw) | SuperTall | **11** | 887.2 → 8,872.1 kW | 33.83 K | **57.39 K** | +23.56 K |
| `B_cons__Tall__CLG` (grid **MIN** draw) | Tall | 6 | 447.6 → 4,476.0 kW | 31.87 K | **59.91 K** | +28.05 K |

Volume in both cells: **+0.0000 %**. Energy +69.63 % / +88.03 %.

### Scoring

- **H1 CONTROL — PASS (provisional).** Volume identical to 8 significant figures in both cells; the
  edit is surgical. Marked provisional only because H1 is written hotel-scoped and this is the
  tower-wide read; the hotel-scoped line comes from 1171859.
- **H3 FALSIFIER — PASS.** Unresized arm-H dT is 33.83 K and 31.87 K, both < 40 K. H2 therefore had
  something to detect in both cells: neither was sitting at the ceiling before the resize.
- **H4 INFO — RECORDED.** Installed base is **not** a grid constant: 447.6 kW on `Tall` (6 heaters),
  **887.2 kW** on `SuperTall` (11). At K = 10, 4,476.0 kW and 8,872.1 kW respectively.
- **H2 DECISIVE — NOT SCORED.** It is specified on *hotel-scoped* delivered dT and that number is
  produced by 1171859, which has not run.

### 🔴 Why the tower-wide numbers must NOT be substituted for H2

The obvious temptation is to score H2 off the table above: 57.39 K and 59.91 K are both below the
65.0 K threshold and 2.5 K apart, so H2 would "fail". **That is a different quantity.** Pulling the
K-sweep logs for the same script shows the scope gap directly — at K = 10 the `Tall__MTL` trio reads

    Y2022      60.24 K        B_central  60.36 K        B_opt      60.68 K      (tower-wide, probe)
    Y2022      65.50 K        B_central  65.51 K        B_opt      65.51 K      (hotel-scoped, elast)

The 65.50/65.51/65.51 figures that H2's threshold was built on are **hotel-scoped**; the probe's
`implied dT` is **tower-wide DHW across all four channels**. Scoring a 65.0 K hotel threshold against
a tower-wide 57.39 K compares two different measurements and would have produced a confident FAIL out
of a units mismatch. Recorded because this project's failure mode is precisely the confident
cross-scope read.

### What the tower-wide series does say, and it is not nothing

Tower-wide dT on the `Tall__MTL` trio, K = 6 → K = 10: **57.26 → 60.24**, **54.04 → 60.36**,
**52.37 → 60.68**. Still climbing 3–8 K. Hotel-scoped, the same three cells are already pinned at
65.50/65.51/65.51 — three identical digits across cells whose draw differs 20 %, which is the
signature of an unconstrained plant.

The two readings are consistent under one explanation: **the hotel channel is un-saturated at K = 10
on `Tall__MTL`, and some non-hotel channel is not.** The tower-wide average keeps rising because a
residential / office / retail heater is still binding.

### 🔴 A scope question this exposes, and it is the user's call

`resize_idf()` rewrites **every** `WaterHeater:Mixed` in the IDF — all four channels, not just the
hotel's. The finding that started this thread was specifically *"hotel DHW plant undersized in every
arm"*, and the minimal intervention matching it would be a hotel-only resize. The current all-channel
form means a resized campaign would also move residential, office and retail DHW energy, so it is not
a hotel-side correction sitting on top of an otherwise-unchanged arm H — it is a new arm for every
channel. The evidence above suggests those other channels genuinely *are* saturated too, so the
change would be large rather than cosmetic.

Both readings are defensible; they answer different questions. **Not resolved here, and not resolved
by fiat.** Flagged for the user alongside the P3 re-specification and the hotel EUI band, since it
has the same character: it decides what the deliverable claims, not merely how it is computed.

### State

- **1171859 queued**, not lost. H2 is scored the moment it lands; nothing else is blocked on it.
- **The 56-cell campaign is NOT submitted.** It stays held until H2 is scored on its own scope, and
  now additionally until the all-channel-vs-hotel-only scope question is answered.
- H1–H4 are **not** revised. The pre-registration stands as written; the un-scorable clause is
  recorded as un-scorable rather than re-aimed at the number that happened to be available.

---

## 2026-08-04 02:25 — **H2 FAILS**: K = 10 does not un-saturate the grid maximum (job 1171859)

`1171859` landed. The hotel-scoped lines:

    sens_hotel_opt__SuperTall__MTL  r=1.2030 | armH V=34940.2  E=3704.2 GJ  dT=25.34 K
                                             | resized V=34940.2  E=9292.5 GJ  dT=63.56 K
    B_cons__Tall__CLG               r=0.9800 | armH V=25061.8  E=2536.5 GJ  dT=24.19 K
                                             | resized V=25061.8  E=6868.7 GJ  dT=65.50 K

### Scorecard for the headroom check

| gate | verdict | evidence |
|---|---|---|
| **H1** CONTROL | **PASS** | hotel volume identical to 6 s.f. in both cells (34940.2 → 34940.2, 25061.8 → 25061.8). No longer provisional — this is the hotel-scoped read. |
| **H2** DECISIVE | 🔴 **FAIL** | grid-MAX reaches **63.56 K**, below the 65.0 K threshold; and the two extremes are **1.94 K** apart, against a 0.5 K tolerance. **Both clauses fail, and both fail on the same cell.** |
| **H3** FALSIFIER | **PASS** | unresized arm-H dT is 25.34 K and 24.19 K, both far below 40 K. H2 had ~40 K of room to move and moved +38.22 / +41.31 K. **H2 was not vacuous — it could have passed, and did not.** |
| **H4** INFO | recorded | installed base 887.2 kW (`SuperTall`, 11 heaters) vs 447.6 kW (`Tall`, 6). Not a grid constant. |

**The pre-registration is followed as written: the 56-cell campaign stays blocked, K is raised, and
the grid-max cell is re-probed.** The threshold was not moved to accommodate a 1.94 K miss.

### The elasticity block in the same log is N/A, as pre-declared

`R0 FAIL` (1.8470 against the probe's 0.5617) and `R3v FAIL` (volume elasticity 1.6208, not ~1.0) are
the *expected* outcome and were written down as expected before the run: the two cells differ in
height, climate and scenario, so a 2-point E-vs-r fit regresses occupancy against geometry. The
script's own trailer says it — *"R0 FAILED. The estimator here is NOT the one the 0.90 threshold was
written against, so R3 above is not the pre-registered test."* **`R3 PASS (1.4742)` and
`R4 PASS (119.2 % of target)` in that log must not be quoted for anything.** They are arithmetic on a
confounded fit. Recorded here because the log prints them as PASS in the same block as the real
gates, and a later reader grepping for `[PASS]` would collect them.

### How close is it, and why that is not a reason to wave it through

The grid-max cell is at **97 %** of the ceiling: 63.56 K against 65.50 K, after a +38.22 K move. It is
tempting to call 1.94 K noise. It is not noise — the min-side cell landed on **65.50 K**, matching the
`Tall__MTL` trio's 65.50/65.51/65.51 to the second decimal across four cells that differ in draw by
20 %. That is a hard ceiling reproduced five times. A cell sitting 1.94 K under a ceiling that
everything else hits exactly is not scattering around it; it is still being held down.

The physical reading: what remains is an **intermittent** binding — a small number of peak hours whose
demand is still refused. An annual mean hides that almost completely, which is exactly why the
residual looks small while the mechanism is fully intact.

### K escalation submitted — jobs 1172028 (array 0-2) and 1172031

Pre-registration, three separately-numbered gates plus a control (the conjunction habit that produced
vacuous-gate #13 is deliberately avoided — each gate carries one claim):

- **H5 CONTROL** — hotel volume unchanged (≤ 0.1 %) in every task.
- **H6 DECISIVE** — grid-max cell at **K = 20** reaches ≥ 65.0 K **and** within 0.5 K of 65.50 K.
  If K = 20 still falls short, the constraint in that cell is **not** burner capacity and no K fixes
  it — the search moves to `Tank Volume`, `Use Side Effectiveness`, or plant-loop flow.
- **H7 SATURATION** — grid-max `dT(K=40) − dT(K=20) < 0.5 K`. This is the claim that a ceiling
  *exists*, separately from where it is. If dT still climbs at 40× capacity, `implied dT` is not
  tracking a delivered temperature approaching a setpoint and the whole "un-saturate the plant"
  framing is wrong. **H7 can fail while H6 passes, and that would be the most informative outcome.**
- **H8 POSITIVE CONTROL, and it is what stops H7 being vacuous** — the grid-MIN cell, already on the
  ceiling at K = 10, is re-run at K = 20; its gain must be < 0.5 K. If *it* also keeps climbing, then
  "< 0.5 K gain" is not a property of saturation and H7 would have measured the instrument rather
  than the plant.

Without H8, *"dT stopped moving"* and *"dT moves slowly at large K for every cell"* are the same
observation. That is the class of defect this project keeps re-finding, so the control is in the run.

**This probe is unaffected by the open all-channel-vs-hotel-only question (§0.11):** the gates are
read hotel-scoped, and the hotel's own heaters receive the same multiplier under either resolution.
So it is worth running while that decision is still with the user.

---

## 2026-08-04 03:25 — K escalation: **H6 FAILS, H7 PASSES** — burner capacity is REFUTED as the remaining constraint (jobs 1172028 / 1172031)

Hotel-scoped, from `hd2elast_1172031.out`:

| task | cell | K | ΔT |
|---|---|---|---|
| 0 | `sens_hotel_opt__SuperTall__MTL` (grid MAX) | 20 | **63.55 K** |
| 1 | `sens_hotel_opt__SuperTall__MTL` (grid MAX) | 40 | **63.55 K** |
| 2 | `B_cons__Tall__CLG` (grid MIN, control) | 20 | **65.50 K** |

against K = 10: grid-MAX **63.56 K**, grid-MIN **65.50 K**.

### Scorecard

| gate | verdict | evidence |
|---|---|---|
| **H5** CONTROL | **PASS** | hotel volume 34940.2 / 34940.2 / 25061.8 — identical to arm H in all three tasks |
| **H6** DECISIVE | 🔴 **FAIL** | grid-MAX at K = 20 is **63.55 K** — below 65.0 K, and 1.95 K from 65.50 K. It did not rise from K = 10; it fell 0.01 K. |
| **H7** SATURATION | **PASS** | `dT(K=40) − dT(K=20) = 0.00 K` — dead flat |
| **H8** POSITIVE CONTROL | **PASS** | grid-MIN gain K = 10 → K = 20 is **0.00 K**; a cell known to be on the ceiling is flat, so flatness discriminates and H7 is not vacuous |

**This is the combination pre-registered as "the most informative outcome": H6 fails while H7 passes.**

### What it means, stated precisely

Across a **4× capacity range** — K = 10, 20, 40, i.e. 8,872 → 35,489 kW installed on a cell whose
hotel draw is 34,940 m³/yr — the delivered rise does not move by one hundredth of a kelvin. **Burner
capacity is not binding in the grid-maximum cell, and was not binding at K = 10 either.** No K fixes
the 1.95 K gap, because the gap is not a capacity gap.

Per H6's own pre-registration, that sends the search to `Tank Volume`, `Use Side Effectiveness` or
plant-loop flow. But there is a second candidate H6 did not name, and on present evidence it is the
more likely one: **63.55 K may simply BE that cell's unconstrained ceiling.** `implied dT` is
`E / (V·ρc)` — a *volume-weighted average* of the per-use temperature rises in the hotel channel. If
the `SuperTall` hotel channel carries a different mix of hot-water end-uses than `Tall` — a larger
share of a lower-target use such as `HOTEL_BOT_LAUNDRY` — then its weighted ceiling is legitimately
lower, and there is no defect at all.

### 🔴 Which means H2's and H6's second clause was mis-specified — and this is NOT a licence to widen

Both gates required the two extremes to agree **with each other** within 0.5 K, on the premise that
*"a uniform plant is a valid control only if it delivers the same temperature everywhere."* That
premise assumes a **single grid-wide ceiling**. H7 and H8 together falsify it: each cell has a stable
ceiling, and the two ceilings differ by 1.95 K for a reason that 4× capacity cannot touch.

**H2 and H6 stand as FAILED. They are not re-scored, not re-aimed, and not widened.** What changes is
what may be *inferred* from them: they were built on a premise now shown to be false, so their FAIL
is evidence about the premise, not about the plant. That distinction is the whole content of this
entry — a gate that fails because its reference was wrong has still failed, and the honest record is
"failed, and here is why the reference was wrong", never "passes once the reference is corrected".

The same defect is already sitting in the campaign pre-registration: **`C3` requires hotel ΔT constant
to within 0.5 K across all 56 cells, explicitly "across geometry groups".** On this evidence C3 would
fail for a non-plant reason. It must be re-specified **before** the campaign runs, and re-specified
on an independent measurement rather than on the convenience of passing — see the next entry.

### What is now established about the original question

**K = 10 does un-saturate the plant.** That was what the headroom check existed to determine, and
three independent readings agree: the grid-MIN cell sits on the same 65.50 K as the whole `Tall__MTL`
trio; the grid-MAX cell is invariant to a 4× capacity increase; and neither cell's volume moved.
The plant is non-binding everywhere at K = 10, which is *stronger* than "the plant is a constant" —
a non-binding plant drops out of the answer entirely.

What is **not** established is the cause of the 1.95 K inter-cell spread. Until it is, the campaign
stays blocked, because C3 cannot be re-specified on a guess.

### Still N/A, as pre-declared

`R0 FAIL` / `R3v FAIL` / `R3 PASS 1.4737` / `R4 PASS 119.1 %` in the same log are the expected N/A
block — here the "pairs" are not even distinct cells, two of them being the same cell at two K, so
the `r` axis has a repeated point. Do not quote any of them.

---

## 2026-08-04 03:57 — decomposition: **H9 PASS, H10 PASS, H11 PASS.** The 1.95 K gap is a use-MIX effect. **The plant question is CLOSED** (job 1172033)

`3rdJ_09H_hotel_dT_decompose.py` on the two cells, both read at a K where the plant is provably
non-binding (grid-MAX K = 40, grid-MIN K = 20).

### The hotel channel has exactly two target temperatures, and every use hits its own exactly

| use class | target schedule | grid-MAX ΔT | grid-MIN ΔT | Δ |
|---|---|---|---|---|
| `LAUNDRY` | Mixed Water At Faucet Temp – **180F** | 71.43 K | 71.43 K | **0.00** |
| `BOOSTER` | Mixed Water At Faucet Temp – **180F** | 71.34 K | 71.34 K | **0.00** |
| 9 shared faucet types (`*GPM140F`) | Mixed Water At Faucet Temp – **140F** | 49.17–49.23 K | 49.17–49.23 K | **0.00** every one |

**Not one object is short of its own design rise, in either cell, to two decimal places.** Mechanism
(B) THROTTLE is dead: there is no tank-volume, use-side-effectiveness or plant-loop-flow constraint
left to find.

### The gap is the 180 F volume share, and it reproduces to the second decimal by hand

| cell | 180 F volume (laundry + booster) | share | 140 F share | weighted ΔT |
|---|---|---|---|---|
| grid-**MAX** `sens_hotel_opt__SuperTall__MTL` | 22,563.3 m³ | **64.57 %** | 35.43 % | **63.55 K** |
| grid-**MIN** `B_cons__Tall__CLG` | 18,380.8 m³ | **73.34 %** | 26.66 % | **65.50 K** |

    (0.7334 - 0.6457) x (71.40 - 49.19)  =  0.0877 x 22.21  =  1.95 K

**That is the observed gap exactly.** This hand-check is deliberately computed by a different route
than the script's own reconstruction — two 180 F/140 F shares and two design rises, no per-type
table, no reweighting — so it is not the script agreeing with itself.

### Scorecard

| gate | verdict | evidence |
|---|---|---|
| **H11** CONTROL | **PASS** | the duplicated channel map reproduces the driver's hotel volume to **0.00000 %** in both cells (34,940.2 and 25,061.8 m³). The second source of truth is byte-identical to the first. |
| **H9** PARTS | **PASS** | all 11 shared types agree to 0.00 K |
| **H10** WHOLE | **PASS** | MIN's per-type rises re-weighted by MAX's volume shares = **63.55 K** against a measured 63.55 K, `\|d\| = 0.00 K` |

**Mechanism (A) MIX is established. It required both H9 and H10 and got both.**

#### The one caveat in H10, stated rather than buried

11.95 % of the grid-MAX volume (5 faucet types: `0.17/0.18/0.67/1.58/1.67 GPM140F`) has no
counterpart in the grid-MIN cell and therefore borrowed its **own** rise in the reconstruction — that
share cannot, by itself, be evidence for the mix story. It does not weaken the conclusion, and the
reason is checkable: every one of those five is a **140 F faucet measuring 49.17–49.22 K**, i.e. the
same value the nine *shared* faucet types measure. Substituting the shared-faucet 49.19 K for all
five moves the reconstruction by under 0.01 K. The hand-check above already does exactly that — it
uses only two design rises — and lands on 1.95 K.

### 🔴 What this closes, and what it re-opens

**CLOSED — the plant.** `K = 10` un-saturates the DHW plant across the whole grid. Every hotel use
delivers its full design rise; four times the capacity changes nothing (H7); the cell believed to be
on its ceiling is flat (H8); and the two cells' ceilings differ only because their use mix differs
(H9/H10). **There is no plant defect left, and no reason to raise K further.**

**RE-OPENED — `TARGET_K = 49.2`, and this finally explains it.** `3rdJ_09H_resize_elasticity.py:45`
carries `TARGET_K = 49.2`, long flagged as a wrong denominator without knowing what the right one
was. It is now identified precisely: **49.2 K is the 140 F FAUCET design rise** — the measured faucet
types come in at 49.17–49.23 K, so the constant is not invented, it is simply *scoped to one use
class*. The hotel channel's aggregate rise is **63.55–65.50 K**, because the 180 F laundry and
booster carry 65–73 % of the volume at 71.4 K.

Consequences, both material:

1. **R4's "133.2 % / 119.2 % of target" is an aggregate over a faucet-only denominator.** Every
   quotation of R4 anywhere in this log is wrong by that factor and must not be repeated. The correct
   denominator is either **per-use** (49.19 K for 140 F, 71.40 K for 180 F) or **per-cell aggregate**
   (63.55 K for the grid max, 65.50 K elsewhere measured) — never a single grid-wide 49.2.
2. **The original hotel finding was UNDERSTATED, not overstated.** The standing entry reads *"marginal
   m³ served at 22.66 K vs a 49.2 K target"*. The real aggregate target is ~65 K, so arm H was
   serving its marginal cubic metre at roughly **35 %** of the delivered rise, not 46 %. The finding
   that started this whole thread is stronger than it was written, not weaker. (22.66 K is a marginal
   OLS slope and ~65 K an average, so this is a direction, not a new coefficient — the re-derivation
   is owed before the number is quoted.)

### 🔴 `C3` must be re-specified — here is the successor, and why it is not a widening

Campaign gate `C3` as written requires *"hotel delivered ΔT constant across all 56 cells to within
0.5 K … it must hold ACROSS geometry groups"*. That is now known to be **false by construction**: the
180 F share is a property of the tower's use mix, and it varies with geometry. C3 would fail in every
run for a reason that has nothing to do with the plant.

**C3 as written stands recorded as mis-specified. H2 and H6 stand recorded as FAILED.** Neither is
re-scored. The successor gate tests the claim C3 was *trying* to make, against the quantity that is
actually invariant:

> **C3′ DECISIVE** — in all 56 cells, **every hotel WaterUse:Equipment type delivers its own design
> rise**: 140 F types within 0.5 K of 49.19 K, 180 F types within 0.5 K of 71.40 K. Additionally the
> per-cell aggregate must equal the 180 F/140 F volume-share reconstruction within 0.5 K, so that a
> cell whose aggregate drifts for a *third* reason is still caught.

This is **stricter than C3, not looser**: C3 checked one aggregate per cell, C3′ checks every object
in every cell *and* the aggregate. It also has a defined failure mode — any object short of its
design rise is a throttle — where C3 had one it could not distinguish from a mix difference. The
justification comes from an independent measurement (H9/H10/H11 + the hand-check), not from the
convenience of passing, which is the standard this project holds a re-specification to.

### Campaign status — still HELD, and now for exactly one reason

The plant blocker is gone. **The remaining blocker is the open question in §0.11, which is the
user's call: does the resize apply to the hotel's heaters only, or to all four channels?**
`resize_idf()` currently rewrites every `WaterHeater:Mixed` in the IDF. Launching 56 cells under the
wrong resolution produces 56 runs that answer the wrong question. That decision is not the manager's
to take, so the campaign is not submitted.

---

## 2026-08-04 — **§0.11 ANSWERED: ALL-CHANNEL RESIZE.** The campaign's last decision blocker is gone

**User decision, verbatim: "je voudrais continuer avec 'all-channel resize'".**

`resize_idf()` stays exactly as written — it rewrites **every** `WaterHeater:Mixed` in the IDF, all
four channels. **No code change implements this decision.** What changes is what the campaign
*claims*, and therefore what it is obliged to *report*.

### 🔴 The claim this commits the deliverable to

The resized campaign is **not** a hotel-side correction sitting on top of an otherwise-unchanged
arm H. It is a **new arm for residential, office, retail AND hotel simultaneously.** Every comparison
of a resized cell against arm H moves four channels at once, and every such comparison must say so in
writing. §0.10 already gives direct evidence the non-hotel channels are saturated too — tower-wide ΔT
on the `Tall__MTL` trio was still climbing 3–8 K from K = 6 → 10 (57.26 → 60.24, 54.04 → 60.36,
52.37 → 60.68) at a K where the hotel-scoped reading was already pinned to three identical digits
across cells whose draw differs 20 %. So the non-hotel movement is expected to be **large, not
cosmetic**, and the write-up does not get to treat it as a rounding detail.

### Three consequences carried into `resize_campaign.sh`, none optional

1. 🔴 **`C1` widens from hotel-only to all four channels.** As pre-registered it checks *hotel* volume
   unchanged ≤ 0.1 %. Under an all-channel resize, residential/office/retail draw is equally exposed
   to an accidental change and nothing would catch it. A gate that cannot fail for three quarters of
   what the intervention touches is the same defect this log has now recorded thirteen times.
   **This is a strengthening of C1, not a re-aim of it** — the original clause survives verbatim as
   the hotel sub-case, and three more channels are added to it.
2. 🔴 **`C6 INFO` is added: per-channel resized − arm H DHW energy and volume, all four channels, all
   56 cells.** It is **INFO and not a gate**, deliberately: there is no pre-registered expectation for
   how far residential/office/retail *should* move, so the honest position is to measure it, not to
   score it against a threshold invented after seeing it. **It must not be promoted to a gate later
   on the strength of what it happens to show** — that is precisely how a gate becomes unfalsifiable.
3. 🔴 **The magnitude warning is now tower-wide.** Hotel DHW alone went 2,578 → 7,008 GJ (×2.72) on
   `Y2022__Tall__MTL`. With three further channels un-saturating, **tower EUI moves further than that
   figure implies**, and the still-open hotel EUI band is no longer the only band this has to be
   re-validated against.

### What the decision does NOT settle

K stays at **10** — evidenced by the sweep (R3 = 1.0013, K3 PASS) and shown non-binding by H7/H8, not
by this decision. The hotel EUI band, the P3 re-specification and the Leg-2 corrigendum remain parked
with the user. `H2`, `H6` and `C3`-as-written stay recorded as FAILED / mis-specified; none is
re-scored, and this decision does not touch them.

### Campaign status — the hold is now purely mechanical

For the first time since the resize thread opened, **nothing about the campaign is waiting on a
judgement call.** What remains is three script edits — `C3` → `C3′`, `C1` widened, `C6 INFO` added —
and one discipline requirement: **the pre-registration block in the script header must be re-read
against the code it claims to describe before submission.** A pre-registration that no longer matches
what the script evaluates is not a pre-registration, and this campaign is about to change three of
its five clauses at once.

---

## 2026-08-04 — 56-cell RESIZED campaign SUBMITTED (jobs 1172037 + 1172045), all-channel, K = 10

**State change: the campaign is no longer held.** The plant thread closed with H7/H8/H9/H10/H11
(the 1.94 K that failed H2 is use-mix, not throttling), and the user answered the open scope
question on 2026-08-04: **all-channel resize**. What remained was script work, done here.

### Jobs

| job | what | log |
|---|---|---|
| `1172037` | 56-cell resized campaign, `--array=0-55%20`, K = 10 | `logs/resizecamp_1172037_*.out` |
| `1172045` | scorecard, `--dependency=afterany:1172037` | `logs/resizescore_1172045.out` |

`afterany`, not `afterok`, and deliberately: if a cell dies the scorer must still run and name the
missing cells. A scorer that silently never runs leaves 56 verdicts absent with nothing to explain
them — the quietest failure mode available.

### What changed in the code, and why each change is a strengthening

**1. `3rdJ_09H_resize_campaign_cell.py` — each cell now writes `hotel_dT_by_type.csv`.**
This is the evidence `C3a` is scored on, produced *in the run* rather than reconstructed later by a
second job re-opening 56 `eplusout.sql` files. The per-type reduction is **imported** from
`3rdJ_09H_hotel_dT_decompose.py` — the module H9/H10/H11 were scored with (job 1172033) — so there
is no third copy of the channel-resolution rules. It carries H11's own self-check per cell: the
per-type hotel volume must reproduce the driver's `dhwvol_hotel` column to 0.01 % or the cell
**refuses**. Design temperature is read from the *target temperature schedule name*
(`Mixed Water At Faucet Temp - 140F` / `- 180F`), which is the causal input, and an object whose
schedule carries no readable `F` is reported as `None` and itemised — never defaulted to 140,
because 140 is a legitimate measured value and a default colliding with a real value is
vacuous-gate #12.

**2. `C1` → `C1′`: widened from hotel-only to all four channels.** The resize rewrites every
`WaterHeater:Mixed`, so residential/office/retail draw is equally exposed to an accidental change.
A hotel-only control could not fail for three quarters of what the intervention touches. Channels
with zero draw in both arms are reported `no-draw`, never counted as agreement.

**3. `C2` → `C2′`: re-specified, because as written it was unscoreable.** The original read
"`INJ_HASH` identical to arm H in all 56 manifests, and area delta 0 m²". Two defects, both found
by trying to code it:
- the resized manifest is a **copy** of arm H's, so comparing its `INJ_HASH` with arm H's compares
  a value with itself — **vacuous-gate #9 exactly**, a gate whose reference comes from the source
  it audits;
- **no area key exists anywhere in the manifest** (checked against
  `out_H_allfix/campaign_233932d7/B_cons__Tall__CLG/manifest.json`, 2026-08-04 — `grep -i area`
  returns nothing). The clause referred to a quantity the artefact does not carry.

`C2′` tests the thing that can actually differ: `injected_resized.idf` differs from arm H's
`injected.idf` **only** on `!- Heater Maximum Capacity` lines — exactly `PLANT_N_HEATERS` of them,
each scaled by exactly K — plus the appended `Output:Variable` block. It subsumes the area claim: a
geometry change would appear as a differing line.

**4. `C3` → `C3a` + `C3b`: re-specified and SPLIT.** `C3` ("hotel ΔT constant across all 56 cells
within 0.5 K, across geometry groups") is false by construction — the 180 F volume share is a
use-mix property that varies with geometry (64.57 % vs 73.34 % between the measured grid extremes)
— so it would have failed every run for a non-plant reason.

- `C3a` DECISIVE — every hotel use-type delivers its own design rise: 140 F within 0.5 K of
  49.19 K, 180 F within 0.5 K of 71.40 K. Reference = the H9/H10 measurement (job 1172033:
  49.17–49.23 K and 71.34–71.43 K, both grid extremes, both cities). **Failure mode defined:** any
  object short of its design rise is a throttle. Stricter than `C3`, which checked one aggregate
  per cell and could not tell a throttle from a mix difference.
- `C3b` CONTROL — the per-type table must reconcile with the driver's own hotel channel: volume to
  0.01 % of `dhwvol_hotel`, energy to 0.01 % of `dhw_hotel`.

🔴 **Why the split, and an admission about the pre-registration as it stood this morning.** The
handoff's `C3′` bundled the per-type clause with "the per-cell aggregate equals its own 180 F/140 F
volume-share reconstruction within 0.5 K". **That second clause is arithmetically implied by the
first and cannot fail once it passes** — a weighted mean of values each within 0.5 K of their design
rise is necessarily within 0.5 K of the weighted design mean. It would have printed a PASS that
carried no information, in a gate advertised as "stricter than C3, with a defined failure mode".
It is now **printed as a derived quantity and not scored**; `C3b` is the independent check it was
reaching for. Bundling a measurement clause with a reconciliation clause under one verdict is
vacuous-gate #13, recorded yesterday on `K2`/`K4` and repeated here in the very re-specification
written to avoid it.

**5. `C4c` added, a discriminator control on `C4`.** Arm H's own per-group elasticity must be below
0.90 in every group where `C4` passes; a group already at ≥ 0.90 before the resize is a group where
`C4`'s pass discriminates nothing. Arm H measured 0.5582 on `Tall__MTL`, so it is expected to pass
— expected is not measured.

**6. `C6 INFO` added** — per-channel resized − arm H DHW energy and volume, four channels, 56 cells,
plus `C6_per_channel_delta.csv`. INFO and it stays INFO: no expectation was pre-registered for the
non-hotel channels, and a number scored against an expectation invented after seeing it is not a
test. `C5 INFO` is now all-fuel site energy shift, whole tower (the Leg-2 precedent); floor area is
unchanged by construction (`C2′`), so the % shift *is* the EUI shift.

### Order of work, so the pre-registration is one

`3rdJ_09H_resize_campaign_score.py` and `resize_campaign_score.sh` were **written before the
campaign was submitted**, and the gate texts in the scorer's docstring and in
`resize_campaign.sh`'s header were reconciled against each other first. A pre-registration that
does not match the code that evaluates it is not a pre-registration.

Every gate itemises what it could not read: incomplete cells are listed and excluded, unreadable
channels are counted separately from violations, unparseable design targets are named. A reader
returning 0.0 for input it cannot parse blames the simulation for its own gap — that cost 16
spurious FAILs in job 1171607.

### What is NOT re-scored

`H2` and `H6` stand **FAILED**. `C3` stands **mis-specified**. None is re-aimed, none is widened.
What changed is what may be *inferred* from them, which is written up in the 2026-08-04 sections
above.

### Expected reading order when 1172045 lands

`C3a` first. `C4` is only meaningful if `C3a` holds — an elasticity of 1.0 in a group whose plant is
still binding is a coincidence, not a clean lever. Then `C1′`/`C2′`/`C3b`/`C4c` as the controls that
license reading either, then `C5`/`C6` as INFO.

🔴 **Every comparison in this campaign moves four channels at once.** It is not a hotel-side
correction on top of an otherwise-unchanged arm H; it is a **new arm** for residential, office,
retail and hotel. Anything written up from it must say so.

---

### 2026-08-04 — 56-cell RESIZED campaign SCORED: 6/6 PASS (job 1172110), and the undersizing was not hotel-only

**Campaign landed 56/56 COMPLETED, zero FAILED/CANCELLED/TIMEOUT/NODE_FAIL** (array `1172037`, per-cell
wall 20–60 min, long pole `_45` at 1:00:15). Scorer `1172110`, exit 0, 56/56 cells scored.

```
  SCORECARD  C1' PASS   C2' PASS   C3a PASS   C3b PASS   C4 PASS   C4c PASS
```

| gate | verdict | measured |
|---|---|---|
| C1′ control — DHW volume unchanged (≤ 0.1 %), all four channels | PASS | 56 × 4, 0 violations, 0 unreadable |
| C2′ control — resized IDF differs from arm H ONLY on `Heater Maximum Capacity` | PASS | 56 cells, 0 violations |
| **C3a DECISIVE** — every hotel use-type delivers its design rise (49.19 / 71.40 K, tol 0.5 K) | PASS | 56 cells, 0 type violations, 0 unreadable targets |
| C3b control — per-type table reconciles with the driver's hotel channel (≤ 0.01 %) | PASS | 0 violations |
| **C4 DECISIVE** — hotel DHW energy elasticity ≥ 0.90 per (geometry, city) group | PASS | 1.0013 / 1.0014 / 1.0014 / 1.0015, R² 1.000 |
| C4c control — no group already ≥ 0.90 in arm H | PASS | arm H 0.6470 / 0.6431 / 0.5830 / 0.5779 |

Derived, NOT scored (implied by C3a): worst |aggregate − mix reconstruction| = 0.0324 K on `B_opt__Tall__MTL`.

**The 22.66 K marginal-rise defect is closed.** Arm H delivered its marginal hotel m³ at 22.66 K against a
49.2 K target; under `K = 10` every hotel use-type in every cell delivers its design rise, and C4c confirms
the elasticity moved from 0.58–0.65 to ~1.00 rather than having been there already.

#### TWO CAVEATS ON C4 — it is a confirmation, not a second independent measurement

1. **C4 is only weakly independent of C3a.** Once every use-type delivers its design rise, and volume scales
   exactly with r (C1′ shows volume identical across arms; the draw is schedule-driven and cannot see the
   burner), then E = V·ρc·ΔT_design ∝ r follows arithmetically. C3a's 0.5 K tolerance on a 49.19 K target is
   ~1 %, which over a log-r span of ~0.18 leaves room for roughly ±0.06 of slope — so C4 *could* have landed
   0.94–1.06 with C3a still passing. The window where C3a passes and C4 fails is real but narrow. C4 earns
   its DECISIVE label from C4c (it discriminates resized from arm H), not from being orthogonal to C3a.
2. **`n_r` = 4–5 distinct r values per group, not 14.** Each group holds 14 cells, but only 4–5 distinct
   hotel r: `sens_office_*` and `sens_retail_*` vary office/retail and inherit their base scenario's hotel r,
   and 4 cells sit at exactly r = 1.0. R² = 1.000 is across 4–5 distinct x with replication, not 14 free
   points. The `n_r` column was added to the C4 table precisely so this is visible rather than hidden behind
   an n = 14 label.

#### C6 INFO — the plant undersizing was NOT hotel-only

| channel | ΔE min % | ΔE median % | ΔE max % | ΔV max % |
|---|---|---|---|---|
| hotel | +134.70 | **+170.79** | +194.99 | 0.0000 |
| residential | +4.39 | **+11.30** | +13.91 | 0.0000 |
| office | −0.04 | −0.03 | −0.01 | 0.0000 |
| retail | −0.04 | −0.00 | −0.00 | 0.0000 |

Full table → `out_R_resize/K10/C6_per_channel_delta.csv`. Volume is flat to 4 decimals in every channel, so
all of this is delivered-energy recovery, not extra draw.

**NEW FINDING: residential DHW was plant-limited too, by 4–14 %.** That was not part of the hotel 22.66 K
diagnosis and had not been predicted. Office and retail were never binding (≈ 0 %, and the tiny negative sign
is cycling noise at the 0.04 % level, not a real reduction). C6 stays INFO and must not be scored: no
expectation for the non-hotel channels was pre-registered, and a number scored against an expectation
invented after seeing it is not a test.

#### C5 INFO — whole-tower all-fuel site energy vs arm H

min **+10.95 %** (`Default_NECB__SuperTall__MTL`) · median **+18.93 %** · max **+24.69 %** (`B_opt__Tall__CLG`).

Floor area is unchanged by construction (C2′), so the % shift IS the EUI shift. A ~19 % median whole-tower
move makes the resized arm a materially different building, which reinforces the scope warning already on
file: 🔴 **every comparison in this campaign moves four channels at once.** It is a new arm for residential,
office, retail and hotel — not a hotel-side correction on top of an otherwise-unchanged arm H. Anything
written up from it must say so. It also bears on the still-open hotel EUI band decision.

#### READER FIX — two refusals before the scorecard, NO gate touched

The scorer was submitted with the campaign as an `afterany` dependent, so the gate code was frozen before any
result existed. It then refused twice at C4, both times correctly, on the hotel `r` reader:

- **Job `1172045`** — `REFUSING: no hotel r token in Default_NECB__SuperTall__CLG` . Those cells were never
  DHW-injected (`channels_requested=[]`, `n_dhw_applied=0`), so they carry no
  `MXU_Hotel_DHWv2_..._r####w####` token. The reader had no case for them.
- **Job `1172108`** — first fix asserted **whole-cell** untreatedness, which then refused on
  `Y2005__SuperTall__CLG`: hotel absent from `channels_requested`, but `n_dhw_applied=47` for the other three
  channels. A cell that injected 47 DHW schedules is plainly not untreated. **The scope was wrong, not the
  strictness.**

Rather than patch one refusal per job cycle, job **`1172109`** (pure grep, no python) censused the hotel-DHW
state of all 56 cells. The population is exactly bimodal, `n_dhw_unresolved=0` throughout, no third state:

```
40  hotel injected        4 MXU schedules + one `t9_13 hotel` line -> r from the token
16  hotel never injected  hotel absent from channels_requested, present in fallback_channels
    = 4 Default_NECB__*   (nothing injected at all, n_dhw_applied=0)
    + 12 Y2005/Y2010/Y2015__*  (hotel-era exclusion, QC hotel truth starts 2019;
                                other three channels injected, n_dhw_applied=47 or 31)
```

Those 16 run the untouched NECB hotel schedule, which **is** the `baseline_series` that every other cell's r
is measured against — identical `reference_occ_mean` hotel wd=0.357275 we=0.368193 in the treated and
untreated provenances alike. So r = 1.0 there is a fact read off the file, and they are each group's anchor
point (4 per group), not cells to drop.

Because **1.0 is also a perfectly legitimate measured r**, a silent 1.0 fallback would be indistinguishable
from a real one — the fallback-that-is-also-a-value failure (vacuous-gate kind #12). The never-injected state
is therefore asserted POSITIVELY on six hotel-specific conditions — crucially `hotel NOT in
channels_requested` **AND** `hotel IS in fallback_channels`, which is what separates a deliberate
non-injection from an injection that ran and produced nothing — and every cell taking that path is **NAMED**
on the scorecard. Anything neither tokened nor fully asserted still hard-refuses.

**No gate, threshold, tolerance or grouping was touched.** C1′/C2′/C3a/C3b do not call the r reader and had
already PASSED under the original code, byte-identical across all three scorer runs. Adding the 16 anchor
points does change C4's fit, which is why it is written into the script header rather than left as a silent
reader repair.

Files changed: `Step9_docs/3rdJ_09H_resize_elasticity.py` (`hotel_r_with_source`, `hotel_r` now a thin
wrapper), `Step9_docs/3rdJ_09H_resize_campaign_score.py` (C4 names every non-token r source, new `n_r`
column, header note), new `Step9_docs/resize_hotel_r_census.sh`.

Jobs: `1172037` (array 0-55%20, 56/56 COMPLETED) · `1172045` FAILED 1:0 (reader) · `1172108` FAILED 1:0
(reader, wrong scope) · `1172109` census COMPLETED · **`1172110` COMPLETED 0:0, the scorecard above.**

---

### 2026-08-04 (late morning) — four user decisions taken; §8E aggregation of the resized arm LAUNCHED (job 1172148)

**Decisions, put to the user after the 6/6 scorecard landed:**

1. **Which arm is the deliverable → DECIDE AFTER SEEING R's STEP-9 GATES.** Deliberately deferred.
   Arm H carries all Step-8/9 analysis and a known physical plant defect; arm R fixes it but is a new
   arm for four channels moving the tower ~19 %. The user declined to choose on the resize scorecard
   alone. 🔴 **Neither arm may be written up as primary until R's own `S9-EUI-*` / `G8*` /
   `S9-LONG-*` results exist.**
2. **What runs next → §8E aggregation + Step-9 re-score on R.** Aggregation launched (below). The
   **re-score was deliberately NOT launched**: it scores gates, so its falsifiable predictions must be
   written into this log *before* it runs. That is the next session's first task.
3. **Hotel EUI band → find and read the CanmetENERGY study first.** R2's `[140,220]`/`[160,240]` may
   not be adopted until the *Commercial Archetypes Performance Study* (2020) settles whether the NECB
   2017 hotel archetype is full- or limited-service. Not in `deepResearch/`. Until then
   `S9-EUI-hotel` stays on R1 `[240,300]` and stays FAIL — **adopting R2 first would be choosing the
   band that rescues the gate.**
4. **P3 re-specification → predict VOLUME.** Score what T9-13 actually delivers (volume, elasticity
   1.0000) rather than energy through a saturated plant. Band not widened; the re-spec must be
   written down before it is scored.

Still open with the user: **Decision 5**, the Leg-2 office-EUI corrigendum.

#### §8E aggregation of the resized arm — job `1172148`, `Step9_docs/agg_armR.sh` → `agg_R_resize`

🔴 **Verified by `ls` before writing anything: there was no `agg_R_*`.** Every other arm has one
(`agg_A_t99`, `agg_B_lm3`, `agg_C_lm3v2`, `agg_D_full`, `agg_E_dhwvol`, `agg_H_allfix`); the resized
arm had never been through §8E, so **no Step-9 gate had ever been scored on it.** The 6/6 scorecard
read cells directly and touched no Step-9 gate.

Three deliberate departures from `agg_armE.sh`, all in the script header:

- **No `campaign_<hash>/` level.** `out_R_resize/K10/<cell>/` directly — each cell is a post-process
  of arm H, not a fresh injection. Arm E's hash guard cannot apply; §1 asserts the arm-H tree
  (`campaign_233932d7`) the cells were built *from*, which is the provenance that matters.
- **No T9-13 audit sweep.** Every `injected.idf.provenance.txt` in the resized tree is **copied from
  arm H** — the resize does not re-inject. Re-running the P1 shape sweep here would re-measure arm H
  and report it as a property of arm R: **vacuous-gate #9**, the gate whose reference comes from the
  source it audits. Arm H's sweep already passed and stands on its own record.
- **`--idf-name`, new in `3rdJ_08E_aggregate_4split.py`.** Default `injected.idf`, so all six earlier
  arms aggregate byte-identically; the resized cells write `injected_resized.idf` and `injected.idf`
  does not exist there. Cells missing the named IDF now `[FAIL]` by name instead of raising.
  🔴 **Deliberately NOT solved with a symlink named `injected.idf`:** in every other arm that name
  means "arm H's injected IDF", so a later reader diffing `injected.idf` across arms would silently
  compare a resized IDF against an unresized one and read the burner-capacity change as an injection
  difference. A flag says what is happening; a same-named symlink hides it.

The job pre-checks all 56 cells for `injected_resized.idf`, `manifest.json`, `hourly_meters.csv`,
`channel_hourly.csv`, `dhw_hourly.csv` and `run/eplusout.sql`, and FATALs on any shortfall rather
than aggregating a partial arm — a missing input would otherwise drop cells silently.

**Handoff for the next session: `improvements/prompts/3rdJ_L3_manager_prompt_2026-08-05.md`**
(296 lines, self-contained). Predecessor `..._2026-08-04_progress.md` retains the full resize thread
(§§0.1–0.17, the K sweep, H1–H11, and why `H2`/`H6`/`C3` stand failed).

---

## §0.18 — arm R §8E aggregation: run LOCALLY, not on Speed (2026-08-04)

**Status: DONE. 56/56 cells, attribution residual 0.000000 % on every cell, exit 0.**
No Step-9 gate has been scored on these tables yet — see §0.18.6.

### 0.18.1 Why the cluster was abandoned

`agg_armR.sh` was submitted twice and never started:

| job | request | outcome |
|---|---|---|
| 1172148 | `--cpus-per-task=4` | cancelled — waiting on four simultaneous free slots |
| 1172151 | `--cpus-per-task=1` | cancelled — still never started |

I had claimed 1172151 would "backfill the moment a single `qc1983nu` task ends." **That was wrong**, and
`squeue -t PENDING` with priorities is what falsified it:

- `1172111_[32-75]` — 44 pending tasks, **priority 9362**
- `1172112_[0-75]` — 76 pending tasks, **priority 9362**
- ours (1172151) — **priority 9356**

120 higher-priority tasks queue ahead of us, each with a 7-day walltime, against an account cap of
`cpu=32`. Every freed slot goes to one of them; there is no backfill window. Also corrected: `qc1983nu`
is **the user's own** account (`UserId=o_iseri(30315)`, `Account=chachemv`), not a foreign job — so it
is not a queue accident that will clear on its own.

**User's call: stop proposing Speed workarounds; compute locally.** Recorded here because it changes
the provenance of an arm-level deliverable, which is not a thing a reader should have to infer.

### 0.18.2 Proving the local run is the same computation — not assuming it

A local run is only admissible if the code is the same code. Both files were pulled from the cluster
repo and `diff -q`'d against the working tree:

| file | result |
|---|---|
| `3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/3rdJ_08E_aggregate_4split.py` | **identical** |
| `eSim_bem_utils/commercial_integration.py` (supplies `classify_tag2`) | **identical** |

🔴 **One provenance difference remains and is NOT waved away: the interpreter.**
The cluster env is **Python 3.10.20**; this run executed under **Python 3.13.5** (pandas 2.3.3,
numpy 2.3.5, eppy 0.5.63), EnergyPlus IDD `C:\EnergyPlusV24-2-0\Energy+.idd` (24.2.0, same version as
the cluster's). Arm R's tables are therefore the only §8E output in this project produced off-cluster.
Note also that the standing rule *"a local `py_compile` is not a valid syntax check for cluster code"*
does not bite here for the opposite reason than usual — local 3.13 **is** the runtime, so compiling
locally checks the thing that actually ran.

### 0.18.3 Moving the inputs down: 336 files, 11.63 GB

§8E reads six files per cell (`injected_resized.idf`, `manifest.json`, `hourly_meters.csv`,
`channel_hourly.csv`, `dhw_hourly.csv`, `run/eplusout.sql` — the last ~161 MB each).
56 × 6 = **336 files, 11.63 GB** (this corrects an earlier 9.2 GB estimate).

Transfer script: `scratchpad/fetch_armR.sh`, 8 parallel `scp` streams. No `rsync` locally, and `tar` is
forbidden on the login node, so a tar-pipe was not available. Made **idempotent** by comparing each
local file's byte size to a manifest captured in **one** remote `ls` — a per-file remote `stat` would
have been 336 ssh handshakes — so an interrupted transfer resumes instead of restarting.

Two failures worth recording, both silent-in-principle:

1. **Fabricated cell names.** `awk -F/ '{print $1}'` was applied to the whole manifest line
   `<size> <path>`, not to field 2, yielding cell names like `10212105 B_opt__SuperTall__MTL`. The
   symptom was "82 cells started, 0 sql landed" — i.e. it looked like *progress*. Fixed to
   `awk '{print $2}' | awk -F/ '{print $1}'`, with the failure written into the script as a comment so
   the next reader does not re-derive it.
2. **`TaskStop` does not kill a process tree on Windows.** Stopping the first run left its `xargs` and
   `scp` descendants alive, still creating bogus directories and competing with the relaunch (73 dirs,
   65 space-named, 15 live `scp`). Cleared with a `Win32_Process` command-line match → 36 processes
   killed, **survivors verified 0**. The 83 space-named dirs were confirmed to contain **0 files**
   before `rm -rf`, so the 10 already-valid cells were preserved.

Final verification: **336/336 files present, every byte count equal to the remote manifest, 0
`SCPFAIL`.** An earlier verification pass flagged 3 `eplusout.sql` as short — they were still in
flight and matched on recheck; recorded because a size check that is run too early *looks* like
corruption.

### 0.18.4 `--jobs`, new in `3rdJ_08E_aggregate_4split.py`

Added so the 56 cells use the local box's 20 cores. Constraints it was written to respect:

- **Default `--jobs 1` is the pre-2026-08-04 sequential loop, byte-for-byte.** All six previously
  aggregated arms therefore still reproduce exactly.
- Results are collected with `ProcessPoolExecutor.map`, which **preserves submission order**, so even
  the output *row order* is unchanged. `--jobs` changes no arithmetic.
- `build_diurnal` / `build_peak` were moved **into** the worker rather than left in `main`. Each cell's
  raw `aggregate_cell` result carries several 8760-row frames (`chan`, `hourly`, `cal`,
  `hourly_channel_total`) that would otherwise be pickled back across the process boundary for nothing;
  the worker now returns three small frames plus meta.

### 0.18.5 Result

```
PYTHONPATH=<repo> python -u 3rdJ_08E_aggregate_4split.py \
    --campaign-dir <local>/_local_armR_cache/K10 \
    --outdir       <local>/_local_armR_cache/agg_R_resize \
    --idf-name injected_resized.idf --jobs 10 \
    --eplus-idd C:\EnergyPlusV24-2-0\Energy+.idd
```

| table | rows (excl. header) |
|---|---|
| `agg_annual.csv` | 4088 |
| `agg_annual_by_channel.csv` | 392 = 56 × 7 (6 channels + `core_exterior`) |
| `agg_diurnal.csv` | 129024 |
| `agg_peak.csv` | 2072 |
| `agg_meta.csv` | 56 |

`cells aggregated : 56 / 56`; **attribution closes against site energy on every cell (≤ 1e-6
relative)** — the printed residual is `0.000000 %` for all 56, matching arm H.

**`--idf-name` was load-bearing, not cosmetic:** `ls K10/*/injected.idf` returns **0**. Had the flag
not been added, the default would have failed outright — which is the desired behaviour, and the
reason the alternative (a symlink named `injected.idf`) was rejected in §0.17: a symlink would have
made a resized IDF answer to the name every other arm uses for an unresized one.

### 0.18.6 🔴 What has NOT been done

**No Step-9 gate has been scored on arm R.** The aggregation was deliberately run *without* the
re-score, because the re-score scores gates and **the falsifiable predictions must be written into this
log first** — scoring first and recording predictions afterwards is how a gate becomes unfalsifiable
(the failure mode catalogued repeatedly in this project). The predictions are the next writing task.

One observation is already visible in the tables and is recorded here **as an observation, not a
verdict**: `B_central__SuperTall__CLG` hotel EUI = **216.2 kWh/m²·CFA**, still below the `S9-EUI-hotel`
R1 band `[240, 300]`. That band is itself pending — the CanmetENERGY *Commercial Archetypes Performance
Study* (2020) has not been located and read, and until it is, `S9-EUI-hotel` stays on R1 and stays
**FAIL**. The band is not to be widened to absorb this number.

---

## §0.19 — Step-9 re-score on arm R: PREDICTIONS, WRITTEN BEFORE THE SCORER IS RUN (2026-08-04)

Nothing in this section was written after seeing an arm-R gate result. The re-score command is at
§0.19.7 and had not been executed when §§0.19.1–0.19.6 were committed.

### 0.19.1 What is being tested

Arm R differs from arm H in **exactly one thing**: `Heater Maximum Capacity` on the tower's six
`WaterHeater:Mixed` objects (K = 10). That is not an assumption here — it is the C2' control already
recorded in §0.17: *"resized IDF differs from arm H ONLY on `Heater Maximum Capacity` — 56 cells, 0
violations."* Every difference the scorer reports must therefore trace to DHW. A difference that
cannot be routed through DHW **falsifies the resize's provenance**, not the gate.

Both arms are scored by the **same instrument on the same machine**:
`3rdJ_09_activityDrivenLoads_4split.py` (unmodified; `--agg-dir` is its only relevant input), run
locally on `agg_H_allfix` and `agg_R_resize`. Arm H's tables were pulled from Speed for this purpose;
arm H's numbers below are **measurements**, arm R's are **predictions**.

### 0.19.2 Arm H reference — measured, from `agg_H_allfix`

| channel | dhw share of own energy | median EUI | SuperTall / Tall | in band |
|---|---|---|---|---|
| hotel | **36.94 %** | 182.39 | 158.24 / 205.15 | 28/56 in `[180,300]`, **0/56 in `[240,300]`** |
| residential | **48.88 %** | 123.45 | — | no band |
| office | **14.39 %** | 81.63 | — | 0/56 in `[100,200]` |
| retail | **7.34 %** | 89.91 | — | 55/56 in `[80,155]` |
| residential_common | **0.00 %** | 53.48 | — | no band |
| service_MEP | **0.00 %** | 59.49 | — | no band |

Whole-tower DHW = **26.98 %** of site energy, and it is **99.0 % NaturalGas** (591.1 of 596.9 TJ).
That fuel split is load-bearing for P6 below.

### 0.19.3 🔴 The scorer's hotel band is STALE relative to user decision (3)

`BENCH["hotel"]` in the Step-9 scorer is `lo=180, hi=300` (file dated 2026-07-31). R1's verdict, taken
2026-08-03, is that **the applicable band is `[240,300]`, not `[180,300]`** — the 180 floor is a
limited-service figure and this tower is not that building. Decision (3) then froze `S9-EUI-hotel` on
R1 `[240,300]` pending the CanmetENERGY study.

**The scorer will therefore report the hotel gate against a band the standing decision has already
superseded.** This is recorded rather than fixed: editing `BENCH` now would be moving a band on the
same day its result is read, which is the banned move regardless of which direction it moves. So:

- the scorer's hotel line is to be read as **"the pre-R1 band"** and is not the governing verdict;
- the **R1 verdict is computed separately** (P5) and is the one that governs;
- the band is **not widened, narrowed, or re-sourced** by this run.

### 0.19.4 🔴 Disclosure — what I have already seen of arm R

Predictions are only worth writing if the writer could still be wrong. Two arm-R quantities are
already in my context from the §0.18 aggregation and its schema check:

1. **All 56 `site_energy_GJ`** (printed per cell by the aggregation). **No prediction is made about
   site energy** — I could not be wrong about it, so it is not evidence.
2. **One hotel EUI**: `B_central__SuperTall__CLG` = **216.22** vs arm H's **154.10** (+40.31 %).
   P3's hotel range and the hotel counts in P4/P5 are informed by this single cell. Everything else —
   all other channel EUIs, every count, every peak, every diurnal and longitudinal statistic, and
   **every gate status in both arms** — is unseen.

### 0.19.5 Predictions

Mechanism: a channel's EUI can only rise by `dhw_share × (f_dhw − 1)`, where `f_dhw` is how much more
DHW energy the unsaturated plant delivers. Share is measured (§0.19.2); `f_dhw` is what the resize
buys.

**P1 — CONTROL, the sharpest falsifier.** `residential_common` and `service_MEP` have **0.00 %** DHW.
Their median EUI must move by **< 2 %** R vs H. This gate discriminates by *end use*, not magnitude:
if it fails with the change concentrated in `pumps`/`fans`, the mechanism is SWH-loop plant energy
attributed to `service_MEP` — legitimate coupling, report it; if it fails in `interior_equipment` or
`interior_lighting`, the resize touched something it must not have and the arm is not a clean
one-variable contrast.

**P2 — ORDERING.** `ΔEUI%(hotel) > ΔEUI%(residential) > ΔEUI%(office) > ΔEUI%(retail)`.
Residential carries the *larger* DHW share (48.88 % vs 36.94 %) yet is predicted to move *less*,
because hotel is the channel that was saturated (§0.17: marginal m³ served at 22.66 K against a
49.2 K target). So P2 is a claim about **saturation, not share** — if it fails by residential
overtaking hotel, share won and the "hotel was the saturated one" story is wrong.

**P3 — MAGNITUDES** (median over 56 cells, R vs H):

| channel | predicted ΔEUI | basis |
|---|---|---|
| hotel | **+18 % … +45 %** | one seen cell at +40.31 %; Tall was less saturated than SuperTall |
| residential | **+3 % … +9 %** | 48.88 % × the +11.3 % residential DHW rise of §0.17 ≈ +5.5 % |
| office | **0 % … +6 %** | 14.39 % share, saturation unknown |
| retail | **0 % … +4 %** | 7.34 % share |

**P4 — GATE FLIPS under the scorer's (pre-R1) band.**

- `S9-EUI-hotel`: **FAIL → PASS**, in-band **≥ 50/56** (H = 28/56). Mechanism: SuperTall median
  158.24 rises through the 180 floor; Tall (205.15) was already inside.
- `S9-EUI-office`: **stays FAIL, 0/56.** H's *maximum* is 90.33; at the top of P3's office range that
  is 95.7, still under the 100 floor. This is the prediction that says the resize does not rescue
  office — and it is cheap to falsify: one office cell ≥ 100 kills it.
- `S9-EUI-retail`: **stays PASS**, in-band **56/56** (H = 55/56; the one miss is the 79.87 minimum,
  just under the 80 floor, and any positive move carries it in).

**P5 — 🔴 THE VERDICT THAT ACTUALLY GOVERNS.** Against R1's `[240,300]`, hotel in-band is
**≤ 30/56** and `S9-EUI-hotel` **remains FAIL**. Arithmetic: Tall 205.15 × 1.18–1.45 = 242–297 (in
band), SuperTall 158.24 × 1.18–1.45 = 187–229 (still out). So the resize is predicted to fix the
*Tall* half only. **The DHW undersizing defect being closed does not close the hotel EUI gate.**

**P6 — LEVERS AND PEAKS UNTOUCHED.** `G8o`/`G8r`/`G8h` stay **PASS** with the same non-degeneracy and
monotonicity; the coincidence factor moves **< 0.02** absolute (H = 0.966). Burner capacity is not an
occupancy lever, and DHW is 99.0 % gas, so the electric peak has almost no route to move.

**P7 — SCORECARD DELTA.** R's scorecard equals H's with **exactly one status change**: hotel EUI
FAIL → PASS (under the scorer's stale band). PASS +1, FAIL −1, every other gate identical in status.
Any *second* status change is a finding to chase, not a rounding difference.

### 0.19.6 How this section can be wrong

P1 failing in `interior_*` would mean arm R is not a one-variable contrast — that outranks every other
result here and would suspend P2–P7. P2 failing means the saturation story is wrong and the effect is
just DHW share. P4-office failing means office EUI is recoverable by plant sizing, which contradicts
§0.17's decomposition (~15 of office's 22 kWh/m² shortfall is the standalone-prototype band). P5
failing in the *optimistic* direction would be the only result that could retire the hotel gate — and
it may not be obtained by touching the band.

### 0.19.7 Command

    python -u 3rdJ_09_activityDrivenLoads_4split.py --agg-dir <...>/agg_H_allfix --outdir outputs_step9_H
    python -u 3rdJ_09_activityDrivenLoads_4split.py --agg-dir <...>/agg_R_resize  --outdir outputs_step9_R

Same binary, same interpreter (local Python 3.13.5 — see §0.18.2), arms differing only in `--agg-dir`.

---

## §0.20 — Step-9 re-score on arm R: RESULT vs the §0.19 predictions (2026-08-04)

**Both arms score 17 PASS / 0 WARN / 3 FAIL / 10 INFO. Across all 30 gates there is NOT ONE status
change.** The three FAILs are the same three in both arms: `S9-EUI-office`, `S9-EUI-retail`,
`S9-EUI-hotel`.

**Prediction scorecard: 5 PASS / 8 FAIL** (13 sub-claims). The failures are the informative part.

### 0.20.1 🔴🔴 HEADLINE — the hotel gate count is IDENTICAL and it means the opposite of what it looks like

`S9-EUI-hotel` reads **28/56 in arm H and 28/56 in arm R**. It is a *completely different 28*.

| | arm H | arm R |
|---|---|---|
| hotel median, SuperTall | 158.24 (below the 180 floor) | **216.25** (inside) |
| hotel median, Tall | 205.15 (inside) | **323.43** (above the 300 ceiling) |
| cells above the 300 ceiling | 0 | **28** |
| in band `[180,300]` | 28/56 | 28/56 |

The 28 SuperTall cells came **up** into the band; the 28 Tall cells went **out the top**. The count is
stable because the two halves swapped, not because nothing happened. Reading the unchanged 28/56 as
"the resize did nothing to hotel" would be exactly backwards: hotel DHW delivered energy rose
**+124.09 %**.

**New vacuous-reading class — provisionally #12** (verify numbering against the catalogue): *the gate
whose count is stable while its membership turns over completely.* Every previous class concerned a
gate that could not fail; this one is a gate that failed identically for opposite reasons on either
side of a change. The defence is to report **which** cells pass, not how many — and here the geometry
split (`SuperTall`/`Tall`) was already the known bimodality, so the check was available and simply
not asked for.

### 0.20.2 P1 CONTROL — PASS, and it is the result that licenses everything else

Predicted: the two channels with **0.00 %** DHW move **< 2 %**. Measured:

- `residential_common` **+0.0007 %**, `service_MEP` **+0.0015 %**
- tower-wide, **every non-DHW end use** moves within **±0.005 %**: cooling −0.000, interior_lighting
  +0.000, interior_equipment +0.000, fans +0.001, heating +0.002, heat_recovery +0.002, pumps +0.005

So arm R really is a one-variable contrast: **only DHW moved.** The alternative failure mode named in
§0.19.5 (movement landing in `interior_*`) did not occur, and the pump/fan coupling that would have
been the *legitimate* failure is present only at the 0.005 % level.

### 0.20.3 Mechanism — the undersizing was very nearly hotel-only

DHW delivered energy, 56 cells pooled, R vs H:

| channel | dhw share (arm H) | H → R | Δ |
|---|---|---|---|
| **hotel** | 36.94 % | 276.5 → **619.6 TJ** | **+124.09 %** |
| residential | 48.88 % | 227.5 → 241.0 TJ | **+5.94 %** |
| office | 14.39 % | 87.7 → 86.5 TJ | **−1.42 %** |
| retail | 7.34 % | 5.2 → 5.1 TJ | **−0.75 %** |
| tower | 26.98 % | 596.9 → **952.3 TJ** | **+59.53 %** |

🔴 **This contradicts §0.17 and must be reconciled, not quietly dropped.** §0.17 concluded *"undersizing
was NOT hotel-only — residential DHW +11.3 % too, tower all-fuel +18.9 % median, so this is a NEW ARM
for all 4 channels."* On the aggregated arm, residential DHW is **+5.94 %**, and office and retail move
**negatively** — they were never saturated, despite office carrying a 14.39 % DHW share. The two
numbers may be measuring different things (§0.17 read cells directly, possibly volume served rather
than delivered energy). **Which is right is an open item**; what is now on file is that the aggregated
arm does not support "all 4 channels".

### 0.20.4 Prediction scorecard

| # | claim | verdict | measured |
|---|---|---|---|
| **P1** | zero-DHW channels move < 2 % | **PASS** | +0.0007 % / +0.0015 % |
| **P2** | hotel > residential > office > retail | **FAIL** | hotel +47.16 > residential +3.55 > retail −0.05 > **office −0.17** |
| **P3a** | hotel ΔEUI +18…+45 % | **FAIL** | **+47.16 %** (overshoot) |
| **P3b** | residential ΔEUI +3…+9 % | **PASS** | +3.55 % |
| **P3c** | office ΔEUI 0…+6 % | **FAIL** | **−0.17 %** (wrong sign) |
| **P3d** | retail ΔEUI 0…+4 % | **FAIL** | **−0.05 %** (wrong sign) |
| **P4a** | `S9-EUI-hotel` FAIL→PASS, ≥ 50/56 | **FAIL** | stays FAIL, **28/56** |
| **P4b** | `S9-EUI-office` stays FAIL 0/56 | **PASS** | FAIL, 0/56, max 90.2 |
| **P4c** | `S9-EUI-retail` stays PASS 56/56 | **FAIL** | **baseline mis-stated** — retail was already FAIL in H (55/56); R is **54/56**, worse |
| **P5** | R1 `[240,300]`: ≤ 30/56, stays FAIL | **PASS, wrong reason** | 0/56 → **2/56**, stays FAIL |
| **P6a** | `G8o`/`G8r`/`G8h` stay PASS | **PASS** | all three PASS in both arms |
| **P6b** | coincidence moves < 0.02 absolute | **FAIL** | 0.967 → **0.937** (−0.030); range 0.952–0.979 → **0.818–0.967** |
| **P7** | exactly one status change | **FAIL** | **zero** status changes across all 30 gates |

**P5 passed for the wrong reason and is recorded as such.** The predicted arithmetic was "Tall lands
inside `[240,300]`, SuperTall stays below" — reality is that Tall *overshot past 300* (323.43) and
SuperTall stopped at 216.25, below the 240 floor. Both halves are out of the R1 band, for opposite
reasons. The verdict I predicted is right; the mechanism I gave for it is wrong.

**P4c is my error, not a model result.** §0.19 asserted retail "stays PASS"; arm H's retail gate was
already **FAIL** at 55/56. The baseline was mis-stated in the prediction section. Recorded as a miss.

### 0.20.5 What this settles and what it opens

**Settles:** closing the DHW undersizing does **not** close the hotel EUI gate, under either band. Under
the scorer's pre-R1 `[180,300]` the count is unchanged (28/56, inverted membership); under R1's
`[240,300]` — the band user decision (3) put it on — it goes 0/56 → **2/56** and stays **FAIL**. No band
was touched, widened, or re-sourced.

**Opens — 🔴 K = 10 now looks like an over-correction.** Arm R's Tall hotel median is **323.43**, above
the 300 ceiling of the band it was supposed to reach, and 28/56 cells now exceed it. Arm H under-served
hotel DHW; arm R over-serves it. Neither arm puts hotel in band, and "which arm is the deliverable"
(user decision 1, deferred pending exactly this scorecard) now has a third possible answer: **neither,
until the hotel draw itself is examined.** The resize fixed the plant; the remaining gap is in the
draw or in the band.

**Also open:** the §0.17 reconciliation in §0.20.3; and P6b — the coincidence factor fell 0.030 with its
range widening to 0.818–0.967, which is a real change to the mixed-use diversity number the manuscript
quotes, driven by a hotel gas peak that more than doubled. `S9-COINC` still PASSes, so the gate did not
catch it; the number moved anyway and should be re-quoted from whichever arm becomes the deliverable.

Outputs: `outputs_step9_H/` and `outputs_step9_R/` (each: `step9_gates.json`, four CSVs, five figures,
`step9_report.html`), both produced by the unmodified scorer under local Python 3.13.5.

---

# §0.21 — OPEN QUESTIONS AND PROBLEMS: state of play for external review (2026-08-04)

**This section is written to be read COLD, by a reviewer with no access to the rest of this log or to
the project's history.** It states what the project is, what has been run, what is blocking, and what
I believe the blockage actually is. It is deliberately self-critical: the question it was written to
answer is *"two weeks and ~10 re-simulations later, are we on the right path?"*

## 0.21.1 What the project is, in one paragraph

3J Leg-3 builds a four-channel mixed-use high-rise energy model (office / retail / hotel /
residential) in EnergyPlus 24.2.0. The scientific contribution is **occupancy**: Canadian General
Social Survey (GSS) time-use diaries are converted into per-channel occupancy schedules and injected
into the building model, replacing the code-standard (NECB 2020) schedules. The claim under test is
that behaviour-derived occupancy changes building energy in ways a rescaled code schedule cannot
reproduce. Step 9 is the validation layer: **30 gates** scored on the aggregated simulation output.
A campaign is **56 cells** = 14 scenarios × 2 geometries (`Tall`, `SuperTall`) × 2 cities
(`CLG` = Calgary, `MTL` = Montréal).

## 0.21.2 The record: 8 simulated arms, and what each one moved

Every arm is a full 56-cell EnergyPlus campaign. Per-channel EUI in kWh/m²·yr, CFA basis, median of
56 cells.

| arm | what changed | office | retail | hotel | gate outcome |
|---|---|---|---|---|---|
| `cf69d508` pre-fix | baseline | 71.08 | 75.43 | 178.29 | 3 FAIL |
| **A** `out_A_t99` | T9-9: restore the plug/light standby floor the injector destroyed | 80.03 | 84.05 | 180.94 | 3 FAIL |
| **B** `out_B_lm3` | T9-10: lighting zone-coincidence, office `n=3` | 82.69 | frozen — **rejected on mechanism** | 179.72 | 3 FAIL |
| **C** `out_C_lm3v2` | T9-12: retail lighting re-spec, `k=0.60` | — | 90.05 | — | 3 FAIL |
| **D** `out_D_full` | T9-11: DHW per-capita | — | — | — | **arm REFUTED and withdrawn** |
| **E** `out_E_dhwvol` | T9-13: DHW volume scaling | — | — | — | 4P/2F vs H |
| **H** `out_H_allfix` | FINDINGS 7/8/9 fixed (injector, cache-key collision) | 81.63 | 89.91 | 182.39 | 3 FAIL |
| **R** `out_R_resize` | DHW burner capacity ×10 (undersizing fix) | 81.52 | 89.87 | 271.40 | 3 FAIL |

Net over eight arms: office **71.08 → 81.52**, retail **75.43 → 89.87**, hotel **178.29 → 271.40**.
The same three gates — `S9-EUI-office`, `S9-EUI-retail`, `S9-EUI-hotel` — have been FAIL throughout.
The other 27 gates have been stable and passing.

**Real defects were found and fixed along the way, and they were worth finding** (an injector writing
one occupancy schedule over PEOPLE+LIGHTS+EQUIPMENT and destroying the 22 % plug standby floor; a
cache-key collision; a Leg-2 EUI inflated 1.706× by a `ReportName` filter bug; DHW plant undersizing).
That work is sound. **The question is whether it was ever going to move the three gates — and the
controls say no.**

## 0.21.3 🔴🔴 THE CENTRAL PROBLEM: none of the three blocking gates is an occupancy problem

This is the assessment. It rests on one control that has been available since 2026-07-31 and was not
acted on: the **`Default_NECB` cell — a cell with NO GSS injection at all, running pure NECB code
schedules, identical geometry / envelope / climate / plant.**

### office — the band is unreachable, and our contribution is not the reason

| | arm H | arm R |
|---|---|---|
| `Default_NECB` (NO injection, NECB's own schedules) | **85.45** | **85.34** |
| `B_central` (GSS injected) | 81.27 | 81.09 |
| band floor | **100** | **100** |
| `Default_NECB` cells in band | **0/4** | **0/4** |

**The code's own reference implementation fails this band by 15 %.** A band that the uninjected NECB
building cannot reach is not measuring our occupancy model — it is measuring a mismatch between the
band and the building. Injection then moves office *down* by ~4 kWh/m² (81 vs 85), so the best case
available from any correction to the occupancy model is roughly the uninjected 85 — **still 15 %
below the floor.** The median needs **+22.7 %** to reach 100.

Across eight arms office moved +14.7 %. It needs +22.7 % more, and its own no-injection control sits
below the floor. **More arms cannot close this.**

### retail — the gate fails on 0.06 % and 0.23 %

Arm R retail: **54/56 cells in band `[80,155]`**. The two misses:

| cell | EUI | short of the 80.00 floor by |
|---|---|---|
| `B_cons__SuperTall__CLG` | 79.82 | 0.18 = **0.23 %** |
| `sens_retail_cons__SuperTall__CLG` | 79.96 | 0.04 = **0.06 %** |

The gate is FAIL because it requires **56/56**. `Default_NECB` retail is **4/4 in band**. This is a
**gate-threshold artefact**, not a modelling failure — and note it is *not* a licence to widen the
band; it is a question about whether "all 56 cells" is the right rule (see Q3).

### hotel — the plant, not the occupancy

Arm R raised hotel EUI +47 % by changing **burner capacity only**. The `Default_NECB` (uninjected)
hotel moved with it: **178.03 → 260.87**. A change that moves the *uninjected control* by the same
mechanism is a plant effect with no occupancy content. And it over-shot: `Tall` hotel is now
**323.43**, above the band's 300 ceiling, while `SuperTall` is 216.25, below R1's 240 floor. Both
halves are out, in opposite directions. See §0.20 for the full scorecard.

### Conclusion I draw

**Of the three blocking gates: one is a band-applicability problem (office, proven by the uninjected
control), one is a gate-threshold problem (retail, 0.06–0.23 % misses under an all-56 rule), one is a
plant-and-band problem (hotel).** None is an occupancy-modelling problem — and occupancy is what the
paper is about. Arms C, E, H and R were, in hindsight, attempts to fix through the occupancy channel
three failures that the controls locate outside it. **That is the wrong loop, and I stayed in it.**

The unblocking action was already decided and never executed: **user decision #2, taken 2026-08-02 —
"office EUI gate → re-derive a band valid for a *stacked channel*, sourced independently from
literature BEFORE looking at our number."** Four more arms were run instead. The same decision applies
to hotel (decision #3, the CanmetENERGY study, still not located and read).

## 0.21.4 Open questions

Each is stated as: what is known / what is missing / what would settle it.

**Q1 — Is a per-channel EUI band from a STANDALONE prototype applicable to a channel stacked inside a
mixed-use tower?**
*Known:* every band in use (`office [100,200]`, `retail [80,155]`, `hotel [180,300]`) comes from
standalone prototype buildings (NECB2020 / 90.1-2019 DOE-PNNL, and dr_L3-02/03). The uninjected NECB
control fails the office band by 15 %. A stacked channel has less envelope exposure, shares a
centrally-sized plant, and has different infiltration and internal-gain neighbours.
*Missing:* a band derived for, or validated on, stacked channels.
*Settles it:* decision #2's independent literature re-derivation — done **before** looking at our
numbers, and written down before scoring. If no such band exists, the honest outcome is that
`S9-EUI-*` cannot be a PASS/FAIL gate at all and must become INFO with the measurement published.
*Note:* a prior attempt to explain the deficit by envelope exposure was **measured and refuted**
(exposure rank came out the wrong way round, 56/56 cells). So "stacked ⇒ lower EUI" is a hypothesis
that has already failed once by the obvious mechanism; it needs a better one or a different band.

**Q2 — Is the office deficit real, or is the office channel itself mis-specified?**
*Known:* office is the outlier — retail and hotel sit near or inside their bands, office is ~~19 %~~
**14.55 %** below its floor even uninjected. A separate audit (B-11) found **retail zones are
25.0 m²/person, identical to office**, while the documentation claims ~3.7 m²/person — a 6.8× gap —
and that the "0.95 NECB retail peak" in our docs is actually the **office** peak. If channel occupant
densities are wrong, per-channel EUI is wrong at the source.
*Missing:* an audit of office (and retail) occupant density, lighting power density and equipment
power density against NECB 2020 tables, independent of anything we have injected.
*Settles it:* that audit. It is cheap — it reads the IDF, no simulation.

> **🔴 CORRECTION 2026-08-04 — the figure above was wrong, and it was wrong in the direction that
> matters.** `19 %` is the **injected** `B_central` shortfall (81.27 vs a floor of 100 = 18.73 %). The
> **uninjected** `Default_NECB` office is **85.45**, i.e. **14.55 % below the floor**, needing
> **+17.0 %**. `§0.21.3` states this correctly at 15 %; only this paragraph carried the injected number
> under the uninjected label — and the whole argument of `§0.21.3` is that the *uninjected control* is
> the evidence, so this was the one place it could not be misquoted. Raised by the backward audit,
> 2026-08-04.

> **🔴 Q2 IS NOW ANSWERED — 2026-08-04 — and the answer runs against this question's premise.**
> The occupant-density third was parsed 2026-08-03; the lighting and equipment thirds were parsed
> 2026-08-04, read-only, from both source towers. Result:
>
> | internal-gain spec | office | retail | hotel | apartment | per-space-type? |
> |---|---|---|---|---|---|
> | occupant density | `0.040015` | `0.040015` | `0.040015` | `0.040015` | ❌ blanket |
> | occupancy schedule | `NECB-A-Occupancy` | same | same | same | ❌ blanket |
> | **lighting W/m²** | `6.566` | `4.090/9.042/9.500` | 7 distinct | 4 distinct | ✅ **yes** |
> | **lighting schedule** | `OfficeLarge …` | `RetailStandalone …` | `HotelLarge …` | `ApartmentHighRise …` | ✅ **yes** |
> | **equipment W/m²** | `7.5028` | `7.5028` | `7.5028` | `7.5028` | ❌ blanket |
> | equipment schedule | `NECB-A-Electric-Equipment` | same | same | same | ❌ blanket |
>
> **Two of the four internal-gain specifications are parameterised per space type; two are one blanket
> value — and the blanket two are occupancy and plug load, the two this project's claim runs through.**
> All three blanket values are *office* quantities (25.0 m²/person; 7.5028 W/m²; a 0.9-peak occupancy
> curve dipping to 0.5 at midday — a lunch trough). **So office is the one channel these constants are
> plausibly right for**, and retail / hotel / residential are the channels wearing office's clothes.
>
> **Correcting them moves retail, hotel and residential EUI. It cannot move office.** Q2 therefore
> resolves **NO — the office deficit is not an occupant- or power-density mis-specification** — and
> `§0.21.3`'s band-applicability conclusion is *strengthened*: office's 14.55 % uninjected shortfall
> has now survived the cheapest available alternative explanation, which `§0.21.6` ranked first. What
> remains is **Q1**.
>
> *Still outstanding:* whether `7.5028 W/m²` and `0.040015 person/m²` are the correct **office**
> values. That needs the NECB 2020 / 90.1-2019 tables opened — backward-audit item **5e**.
> New backward-audit finding **B-12** (blanket plug density) records the equipment half; its likely
> error sign is **opposite** to B-11's, so the two partially cancel. See
> `improvements/investigation/3rdJ_L3_backward_audit_2026-08-03.md`.
>
> 🔴 **One consequence for a blocking gate.** `S9-EUI-retail` FAILs on two `SuperTall__CLG` cells short
> of the 80.00 floor by **0.23 %** and **0.06 %**. B-11 and B-12 move retail internal gains by order
> **6.8×**, not 0.2 % — occupant gains up, outdoor air up 2.08× (DCV is `No`, so OA rides the *design*
> density), plug load plausibly down. Three effects, two signs, in a heating-dominated climate: the net
> is not derivable. Audit item **5c** (one pre-registered sensitivity cell) is the measurement.
> **It must be read as exposure, never as an attempt to make retail pass** — and one specification
> diagnostic cell is not the ninth arm `§0.21.6` warns against.

**Q3 — Is "all 56 cells in band" the right gate rule?**
*Known:* retail FAILs at 54/56 on misses of 0.06 % and 0.23 %. Office FAILs at 0/56. The rule cannot
distinguish "the model is wrong" from "two cells grazed a threshold".
*Missing:* a stated rule for what fraction constitutes agreement, **written before it is applied**.
*Settles it:* pre-registering the rule. 🔴 **Constraint: this must not be chosen by looking at which
threshold makes retail pass.** If the rule is decided now, it is decided knowing the answer — so the
defensible move is to publish both (54/56 in band; 2 cells short by <0.25 %) and let the reader judge.

**Q4 — Which arm is the deliverable?** *(user decision 1, deferred since 2026-08-04 pending the arm-R
scorecard, which now exists — §0.20)*
*Known:* arm H under-serves hotel DHW; arm R over-serves it (Tall 323 vs a 300 ceiling). Neither puts
hotel in band. Every other gate is identical between them.
*Missing:* whether the correct burner capacity is between H's and R's — i.e. whether `K` should be
calibrated rather than set to 10.
*Settles it:* the existing K-sweep data may already answer it without new simulation. **Check the sweep
before running anything.**

**Q5 — Is the hotel DHW *draw* right, independent of plant capacity?**
*Known:* with an unsaturated plant, hotel DHW delivered energy is **+124 %** vs arm H, pushing hotel
EUI above its ceiling. Hotel is 63 % of prototype DHW volume, and laundry alone is 75 % of hotel
design flow.
*Missing:* validation of the hotel draw (L/person/day) against a published hotel benchmark.
*Settles it:* one literature figure, no simulation.

**Q6 — §0.17 vs §0.20 contradiction on who was undersized.**
*Known:* §0.17 concluded the undersizing affected all four channels ("residential DHW +11.3 %, tower
all-fuel +18.9 %"). The aggregated arm gives hotel **+124.09 %**, residential **+5.94 %**, office
**−1.42 %**, retail **−0.75 %** — very nearly hotel-only, with office *falling* despite a 14.39 % DHW
share.
*Missing:* whether §0.17 measured volume served rather than delivered energy.
*Settles it:* re-deriving §0.17's number from the same tables. No simulation.

**Q7 — The scorer's hotel band is stale.**
`BENCH["hotel"]` in `3rdJ_09_activityDrivenLoads_4split.py` is `[180,300]`; R1's verdict and user
decision #3 put the gate on `[240,300]`. The code has not been updated. 🔴 **It was deliberately not
edited on the day its result was read** — changing a band while looking at the number it judges is the
banned move in either direction. It must be fixed and re-run **before** any hotel result is quoted.

~~**Q8 — Backward-audit item B-3, still open.** The residential occupancy model uses `HHSIZE × any-present`
with **zero intra-household diversity**, and this reaches the **already-submitted 2J paper**. It is the
only high-severity backward-audit finding still needing compute. It has been open since 2026-08-03.~~

> **🔴 CORRECTION 2026-08-04 — this fused two different findings under one number, and got the cost
> backwards.** The content above is **B-1**; **B-3** is a different finding entirely. Struck and split
> into Q8a / Q8b below. As originally written — and as carried into `READER_GUIDE §1.4` with the answer
> *"needs simulation? yes — the only one"* — it told a cold reviewer that the finding touching the
> **submitted** 2J manuscript is blocked on cluster time. It is not.

**Q8a — Backward-audit item B-1, still open.** The residential occupancy model uses
`People(t) = HHSIZE × 1[any member present at t]`, and every co-resident carries an identical presence
vector, so **intra-household presence diversity is exactly zero**. This reaches the
**already-submitted 2J paper**, where it bites hardest (1.98 persons/HH there vs 1.27 in Leg-3).
*Needs simulation:* **no.** Report R1 retired step 2 of its falsifier — under perfect synchrony
`any-present × N` is *identical* to sum-of-members, so the inflation ratio is 1.0 by construction —
leaving **step 1 only**: one script, minutes, checking whether co-resident `hom30` vectors are
identical. GSS samples one person per household, so the diversity cannot be recovered, only
manufactured; **the fix is a limitations paragraph describing *perfectly synchronised household
presence*, an attested simplification — not a model change.** Open since 2026-08-03.

**Q8b — Backward-audit item B-3, still open.** `RW1`/`RW2` — the two gates built to catch a dead retail
head — read **teacher-forced numbers from `step4_training_log.csv`**, not the shipped pool; `RW8` and
`REG-1/2` are proxies for the same reason. This touches **Leg-3 Step 4 only** and does **not** reach
the 2J paper. *Needs simulation:* **yes** — and it is the **only** backward-audit item that does: one
04E re-run persisting retail probabilities, ~40 minutes on one GPU. Open since 2026-08-03.

## 0.21.5 Problems with the instrument, not the model

1. **`S9-EUI-*` gates are being used as if they validate the occupancy model. They do not.** They
   compare an absolute EUI level against an external band. Occupancy affects *shape* and, at the
   margin, level. Every gate that actually tests the scientific claim — `S9-INJECTION` (occupancy
   flips midday-dominant → evening-dominant), `G8o`/`G8r`/`G8h` (levers non-degenerate and monotonic),
   `S9-COINC` (0.937–0.967, channels do not peak together), `S9-D20` (energy-vs-occupancy lag: office
   0.26 h, residential 10.56 h) — **passes, and has passed in every arm.**
2. **A gate count can be stable while its membership completely turns over** — `S9-EUI-hotel` read
   28/56 in both arms H and R, a *different* 28 (§0.20.1). Counts alone are not a safe summary.
3. **Eight arms, one moving target.** No arm was launched with a pre-registered numeric prediction for
   the gate it was meant to fix until arm E. Predictions were added late (§0.19 is the first full
   pre-registered set) — which is why the earlier arms could not distinguish "the fix worked" from
   "something moved".

## 0.21.6 What I would stop doing, and what I would do instead

**Stop:** running campaign arms to move `S9-EUI-*`. Eight arms have moved office by +14.7 % against a
required +22.7 %, and its own uninjected control is below the floor. There is no reason to expect a
ninth to differ.

**Do instead — all of it is desk work, no simulation:**
1. Q2's IDF audit of occupant / lighting / equipment power density per channel vs NECB 2020 (cheapest,
   and it could invalidate or explain the office deficit outright).
2. Decision #2's independent band re-derivation for stacked channels; decision #3's CanmetENERGY
   study for hotel. Both were taken and neither executed.
3. Q6 and Q4 from existing tables and the existing K-sweep.
4. If Q1 concludes no valid stacked-channel band exists: **convert `S9-EUI-*` to INFO, publish the
   measurement, and state the limitation.** That is the honest outcome and it does not weaken the
   paper — the paper's claims rest on shape, lever response, diversity and lag, all of which pass.
   🔴 It must be reached by the band being shown inapplicable, **never** by widening it to absorb a
   FAIL.

## 0.21.7 What is NOT in doubt

So the reviewer can calibrate: attribution closes to ≤ 1e-6 on every cell of every arm; 56/56 cells
complete; the injector's provenance is hash-tracked; arm R was verified as a strict one-variable
contrast (every non-DHW end use moved < 0.005 %); and 27 of 30 gates pass consistently, including all
four that test the paper's actual claim. **The pipeline is sound. The dispute is entirely about three
absolute-level EUI bands and whether they apply to this building.**
