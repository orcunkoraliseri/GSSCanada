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
| V8 | L'exclusion hôtel des époques n'est **pas** motivée par « les données commencent en 2011 ». La vraie raison écrite dans le générateur : **la vérité-terrain QC commence en 2019** ; une courbe hôtel 2015 serait AB-seul → **confusion province × canal** dans tout le bras historique | `Step8_docs/3rdJ_08A_gen_historical_products_4split.py:12-20`, renvoyant à `3rdJ_06_hotel_sarima_4split.py:24-29` |
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

### T9-1 — Rétrograder `S9-EUI-{c}` en INFO, sans toucher `BENCH`

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

### T9-2 — Gate `S9-EUI-TOWER` (conditionnelle à T9-4)

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
   `3rdJ_08A_gen_historical_products_4split.py:12-20` et `3rdJ_06_hotel_sarima_4split.py:24-29`.
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

*(à compléter à l'exécution — une entrée datée par tâche, avec les nombres re-dérivés, pas
recopiés)*
