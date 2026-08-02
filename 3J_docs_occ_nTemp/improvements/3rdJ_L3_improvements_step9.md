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
