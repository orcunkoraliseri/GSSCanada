# 3J Leg-3 — Step 8 : document d'implémentation & améliorations

**Créé le 2026-07-28.** Doc de référence autoportant pour Step 8. Il remplace la mémoire longue :
une session fraîche doit pouvoir reprendre le travail en lisant **ce fichier + le `Progress Log` de
`3rdJ_08_simulation_4split.md`**, sans contexte conversationnel.

- Runbook (chronologie faisant foi) : `3rdJ_08_simulation_4split.md` → `Progress Log`
- Validateur (définitions P1–P4) : `3rdJ_08_simulation_4split_val.md` §P
- Ce doc : **ce qui reste à implémenter**, et **les défauts structurels à corriger**

---

## Aim

Fermer les pré-requis de la campagne 56 runs (2 bâtiments × 2 villes × 14 scénarios) en éliminant
les défauts qui rendraient ses résultats **faux et silencieux** — c'est-à-dire numériquement
plausibles mais dépourvus du signal de scénario qu'ils prétendent porter.

La campagne reste **BLOQUÉE**. Elle ne se lance pas tant que les points A→D ci-dessous ne sont pas
fermés.

---

## 🔴 MISE À JOUR 2026-07-28 (fin de session) — NOUVEAU BLOQUANT PRIORITAIRE

**Point d'entrée pour la session suivante :**
`prompt-manager/2026-07-28_manager_step6_calibration_bias_then_campaign.md`

A→D ne sont plus le premier bloquant. Un **biais de calibration Step-6** a été mesuré, et l'utilisateur
a tranché le 2026-07-28 : **le corriger AVANT tout le reste**. Voir §Défaut 4 ci-dessous.

Fermé aujourd'hui, en plus de §A : **injecteur résidentiel OD-8R-L3** (implémenté, vérifié au niveau
IDF), **Défaut 3 `INPUTS_HASH`** (fermé, démontré), **produits historiques 2005/2010/2015** (9 fichiers
générés, gates PASS), **classification `residential_common`** (corrigée + colonne séparée dans
`channel_hourly.csv`), **driver de campagne local 56 cellules** (construit, smoke-testé).

**Canal résidentiel des 56 cellules — corrigé à la clôture.** La table avait été bâtie **sans canal
résidentiel** (les 56 runs auraient tourné avec les 27 appartements au baseline NECB). Corrigé :
4 canaux sur `Y2022`/`B_*`/`sens_*`, 3 sur les historiques, 0 sur `Default_NECB`. Garde
`validate_campaign_channels()` ajoutée et **vue en train d'échouer** (résidentiel retiré → erreur
nommant les 4 cellules ; restauré → 0/56 manquant). Axe de sensibilité tranché par le code
(`3rdJ_07_aug_to_bem_4split.py:358-359, 909-928, 932`) : résidentiel et bureau **partagent** l'axe de
bande WFH, donc `sens_office_*` bascule aussi le résidentiel.

⚠️ `commercial_integration.py` a changé → `INJ_HASH` change → **`campaign_5670f602/` est périmé**, les
7 cellules de probe sont à re-simuler (~16 min pièce en local). Prévu : le résidentiel n'y était pas
injecté du tout.

---

## État verrouillé au 2026-07-28

### Fermé

| Élément | État |
|---|---|
| Steps 1–7 | DONE. Architecture **B** (tour mixte unique, 4 canaux par Tag-2). Ne jamais revenir au cadrage A. |
| 8B — IDF v24.2 | 4 IDF (Tall/SuperTall × MTL/CLG) vérifiés sur scratch, réutilisés de Leg-2. Chaque paire MTL/CLG diffère de **36 octets** → géométrie identique, tag climat seul, les deltas EUI isolent bien le climat. |
| AUDIT-W | **9P / 1W / 0F** (jobs `1169582`, `1169584`). Recensement Tag-2 Tall = 30 résid / 33 bureau / 9 commerce / 25 hôtel / 63 service_MEP = **164**. WARN unique = 4 Spaces plénum sans Tag-2 ni charges → accepté-documenté. |
| BUG-W7 | Corrigé dans `eSim_bem_utils/commercial_integration.py` + nouvelle gate W7. Avant elle, le câblage LIGHTS/EQUIP commercial n'était sous **aucune** gate (W2/W3 ne regardent que PEOPLE). |
| PROBES §P | **23P / 0W / 2F** (job `1169679`). Les 2 FAIL = un seul défaut amont, voir ci-dessous. |
| Cloisonnement inter-canaux | **PASS.** Dans chaque paire de cellules, tout canal non varié donne Δ = 0,0 **exactement**. L'injection est proprement scopée par Tag-2 — acquis important pour l'attribution §8. |
| Défaut retail `multiplier` | **CORRIGÉ ET VÉRIFIÉ** (voir §Défaut 1). Produits régénérés localement. |
| Audit résidentiel colonne-par-colonne | **SAIN** (voir §Défaut 2). Aucun changement requis. |
| Défaut 3 — trou d'empreinte (`INPUTS_HASH`) | **CORRIGÉ ET VÉRIFIÉ** (voir §Défaut 3 ci-dessous + Progress Log `3rdJ_08_simulation_4split.md` 2026-07-28 « Défaut 3 fermé »). |

### Non fait

- Produits historiques 2005/2010/2015 : **n'existent pas**.
- 6 jeux de sensibilité one-at-a-time : **n'existent pas**.
- Sur les 14 scénarios de la matrice, **4 seulement existent sur disque** (2022, 2030_cons/central/opt).
- Injecteur résidentiel (OD-8R-L3) : **spécifié, PAS implémenté**.
- Re-simulation post-correctif retail : **PAS lancée**, rien téléversé.

---

## Défaut 1 — retail `multiplier` : le levier de bande était annulé (CORRIGÉ)

### Symptôme

`retail_presence_multiplier_2030_{cons,central,opt}.csv` avaient des colonnes `multiplier`
**strictement identiques** (max|Δ| = 0). Elles ne différaient que par `at_retail_fraction`, colonne
diagnostique que le BEM ne lit jamais — `load_retail_series()` ne consomme **que** `multiplier`.

Conséquence : **les trois bandes retail 2030 étaient un seul et même scénario** au niveau BEM.
L'axe retail de la campagne aurait eu 2 états distincts (2022, « 2030 »), pas 4.

### Cause

`Step7_docs/3rdJ_07_aug_to_bem_4split.py::_retail_rows_from_slotarray` normalisait le tableau
**déjà leviéré par la bande** par son **propre** maximum :

```python
peak  = float(arr_clock48.max())      # pic PROPRE au tableau deja levie
shape = arr_clock48 / peak
multiplier_raw = 0.95 * shape
```

Tout rééchelonnage de **niveau** s'annule exactement. Les leviers Step-6 étant des scalaires
uniformes (0,90 / 0,97 / 1,05, écart-type mesuré ~1e-14), l'annulation était totale.

### Correctif retenu — ancrage sur le pic de la BASE non-levée

```python
ref_peak = pic de at_retail_fraction_2030_base, apparie par (Day_Type, PR)
shape    = arr_clock48_levered / ref_peak
multiplier_raw = 0.95 * shape
```

**Pourquoi cet ancrage** — c'est **une seule division**, la référence est lue dans la donnée non
perturbée et partagée à l'identique par les 3 fichiers leviers (vérifié byte-identique). C'est
mathématiquement équivalent à « auto-normalisation × constante de bande » mais **sans constante
codée en dur**. L'appariement par `(Day_Type, PR)` est obligatoire : une référence globale casserait
les rapports inter-jours / inter-PR.

**Deux ancrages rejetés, et pourquoi** (à ne pas rouvrir) :

- *Pic de la bande `central`* — visait la bit-identité de `central`. **Impossible** : force
  `opt` à `0,95 × 1,05/0,97 = 1,028 > 1`, schedule EnergyPlus invalide, sur les 6 groupes
  (Day_Type, PR). La bit-identité n'économisait rien de toute façon, la cellule 1 était déjà à
  re-simuler.
- *Clipping à 1,0* — détruirait le signal précisément aux heures de pointe, celles qui portent la
  contribution.

### Résultat vérifié (contre-vérification aveugle, indépendante)

| Bande | Pic `multiplier` | md5 avant → après |
|---|---|---|
| cons | **0,8550** | `f47de539…` → `0e3b256e…` |
| central | **0,9215** (était 0,95, −3,0 %) | `bfb89627…` → `cf8721c6…` |
| opt | **0,9975** (≤ 1 ✓) | `337ac1b5…` → `f7152e5a…` |
| 2022 | inchangé | `e31f528e…` → **identique** (chemin `ref_peak=None` intact) |

- max|Δ| `multiplier` : cons↔central 0,0665 · central↔opt 0,0760 · cons↔opt 0,1425. **148/288 lignes
  diffèrent** par paire (156 lignes non-shoulder au maximum ; les 8 restantes ont
  `at_retail_fraction = 0`).
- Pics **constants** sur les 6 groupes (Day_Type, PR) ; rapports inter-bandes = rapports de levier
  dérivés indépendamment (écart nul).
- Min/max globaux ∈ [0 ; 0,9975]. 288 lignes/fichier, colonnes et ordre inchangés.
- Diff : 103 insertions / 14 suppressions, un seul bloc contigu, 3 fonctions + 1 site d'appel.
  Aucune modification des chemins office, hôtel, résidentiel ou CLI.

### Gate `run_retail_gates()` — relabel avec preuve

L'ancienne gate `peak == 0,95` exact **passait sur le produit buggé** (les 3 bandes avaient bien un
pic à 0,95). Nouvelle sémantique : `peak(band) == 0,95 × lever(scenario)`, plus la borne physique
réelle `[0, 1]` (l'ancienne borne `[0 ; 0,95]` rejetterait à tort les 14 lignes légitimes de `opt`
à 0,9975).

**Ce n'est pas un assouplissement** : test décisif refait empiriquement sur un produit buggé
refabriqué —

```
H2/R1 peak != expected 0.8550 (lever=shift) [BUGGY/shift] [Saturday/AB]: 0.950000
```

La gate rejette le défaut d'aujourd'hui ; les 3 produits corrigés passent. La borne de plage prise
isolément est plus permissive, mais l'assertion de pic exact couvre l'intervalle (0,95 ; 1,0].

### Correctif de suivi — seconde source de vérité éliminée

`RETAIL_LEVER_VALUE = {"shift": 0.90, "plateau": 0.97, "renaissance": 1.05}` était **codé en dur**.
La gate se validait donc contre une constante maintenue à la main : si Step-6 régénère ses fichiers
avec d'autres leviers, la gate déclare PASS contre un nombre périmé, en silence. Même famille de
piège que le bug lui-même.

Remplacé par `_derive_retail_lever(retail_scenario)`, qui lit la colonne `multiplier` du fichier
levier Step-6 au runtime (préférée au rapport `levered/base` : évite 0/0 sur les 71/432 lignes où
`base == 0` ; équivalence numérique vérifiée < 3e-14), avec **assertion d'uniformité explicite**
(tolérance 1e-9) — un levier non uniforme changerait la *forme* et pas seulement le *niveau*, ce qui
invaliderait tout le raisonnement du correctif.

Appelée par `run_retail_gates()` et `_check_h5_monotonicity()`. **Produits inchangés** (md5 des 4 CSV
identiques avant/après) → **aucune re-simulation induite** par ce correctif.

### Mapping scénario → bande (établi par le code, pas supposé)

`BUNDLE_MAP[...]["retail_scenario"]` : `cons` → `shift` (0,90) · `central` → `plateau` (0,97) ·
`opt` → `renaissance` (1,05).

---

## Défaut 2 — canal résidentiel : audit colonne-par-colonne (SAIN)

Le test « taille + md5 diffèrent » est **rigoureusement incapable** de détecter le piège du défaut 1 :
deux fichiers peuvent avoir des md5 distincts (une colonne diagnostique diffère) tout en ayant des
colonnes *consommées* identiques. Le trou a été fermé.

- **Colonnes réellement consommées** : `Occupancy_Schedule` et `Metabolic_Rate`
  (`eSim_bem_utils/integration.py:379-380`), injectées **sans transformation** dans
  `Schedule:Compact`.
- **Les 4 scénarios diffèrent bien** sur ces colonnes : ~20 % des lignes entre bandes 2030, ~38 %
  entre 2022 et 2030. **Aucun Δ = 0 sur aucune paire.**
- **Immunité structurelle** : `convert()` (`3rdJ_07_aug_to_bem_4split.py:254-293`) ne contient
  **aucune** division, aucun `.max()`, aucune normalisation. Le résidentiel est un produit
  **REPLACE** (substitution complète des colonnes de tirage via `assemble_2030()`), pas un produit
  MODULATE-par-multiplicateur : il n'y a rien à annuler.
- Contraste sain : les colonnes non consommées (`HHSIZE`, `BEDRM`, `CONDO`, `DTYPE`, `PR`,
  `MATCH_TIER`) sont identiques à 0,00 % sur les 6 paires — le signal de bande vit **exclusivement**
  dans les colonnes consommées. Contrairement au retail, il n'existe même pas de colonne
  diagnostique parallèle où le signal pourrait se réfugier.

**Non vérifié** : que les 3 pools 2030 par `BAND` proviennent de tirages statistiquement
indépendants en amont (Step 6). Seule la sortie Step 7 a été auditée.

### Taxonomie à retenir

Trois familles de produits, avec des vulnérabilités différentes :

| Famille | Canaux | Vulnérable à l'annulation de niveau ? |
|---|---|---|
| **MODULATE**, référence partagée entre bandes | office (`groupby("office_archetype").max()`, L403) | Non — le pic est commun, le levier survit |
| **MODULATE**, référence propre à la bande | retail (**était** le bug) | **Oui** — annulation exacte |
| **REPLACE**, aucune normalisation | résidentiel | Non — rien à annuler |

**Règle générale à appliquer à tout nouveau produit** : si un produit divise par une statistique
dérivée de son propre tableau **après** application du levier de scénario, le levier est mort.
Le test md5 ne le verra pas. Seule une comparaison des **colonnes consommées** le voit.

---

## Défaut 3 — trou d'empreinte : les produits Step-7 ne sont pas dans le hash (CORRIGÉ 2026-07-28)

**C'est l'amélioration structurelle la plus importante de ce document.**

Le chemin de sortie des probes est `probes/campaign_<md5(commercial_integration.py)[:8]>/<tag>/`.
L'empreinte ne couvre que **l'injecteur**. Les **produits Step-7** — les fichiers dont le contenu
détermine entièrement les horaires injectés — n'y entrent pas.

Conséquence directe, constatée aujourd'hui : les produits retail ont changé, l'injecteur non, donc
le chemin reste `campaign_5670f602/`. Une re-simulation **écrase en place** les résultats issus des
produits périmés, sans aucun garde-fou :

- `3rdJ_08P_probe_driver.py:494-495` — `os.makedirs(outdir, exist_ok=True)`, aucune vérification de
  répertoire non vide ;
- `:611` — `idf.saveas()` écrase `injected.idf` ;
- `:629-634` — EnergyPlus lancé avec `-d run_dir` sur le `run/` existant, écrase `eplusout.sql` ;
- `:645` — `_write_manifest()` écrase `manifest.json`.

Deux jeux de résultats incompatibles peuvent donc cohabiter au même chemin, sans trace. La garde
stale-output est décrite comme « structurelle » dans le runbook — **elle ne l'est que vis-à-vis de
l'injecteur.**

**Nuance à préserver** : `INJ_HASH` ne doit *pas* couvrir le post-traitement (un correctif de
post-traitement ne doit pas pouvoir invalider un `eplusout.sql` valide — c'est ce qui a permis la
récupération `--postprocess-only` à 40 s au lieu de 38 min). La correction ne consiste donc pas à
tout jeter dans un seul hash.

**Correctif implémenté et vérifié 2026-07-28** — `INPUTS_HASH` ajouté au manifeste (md5 des produits
Step-7 effectivement lus par la cellule, ordre canal alphabétique, `_compute_inputs_hash()` dans
`3rdJ_08P_probe_driver.py`), et le driver **échoue bruyamment** (`_check_inputs_hash_guard()`, appelée
avant `os.makedirs(outdir)`, identique cluster/local) si un répertoire de sortie existant porte un
`INPUTS_HASH` différent de celui de la run courante — y compris un manifeste legacy sans
`INPUTS_HASH` du tout, traité comme INCONNU et refusé par défaut. `INJ_HASH` garde le chemin (la
récupération `--postprocess-only` reste possible) ; override explicite `--allow-stale-inputs` avec
une sémantique différente en simulation normale (archive `_STALE_<timestamp>`, réutilise la
convention déjà présente dans `3rdJ_08P_probes_local.py`) vs. `--postprocess-only` (adopte en place
sans archiver, uniquement sur manifeste legacy — un mismatch réel reste refusé même avec l'override,
car `--postprocess-only` ne re-simule jamais). Gate compagnon `INPUTS_HASH` cross-cell ajoutée à
`3rdJ_08P_probe_gates.py`. Démonstration empirique complète (falsification d'une copie du produit
retail → refus nommé ; cas non-falsifié → passe silencieusement ; `--postprocess-only` toujours
fonctionnel) : voir Progress Log `3rdJ_08_simulation_4split.md`, entrée « 2026-07-28 (employé) :
Défaut 3 fermé ». Aucun produit Step-7 réel modifié, aucun EnergyPlus lancé pendant cette tâche.

---

## 🔴 Défaut 4 — biais de calibration Step-6 : l'écrêtage est unidirectionnel (OUVERT, PRIORITAIRE)

**Mesuré le 2026-07-28 par deux investigations indépendantes. Décision utilisateur : corriger d'abord.**

La fraction de diaires `IS_SYNTHETIC == 1` monte **de façon monotone le long de la séquence temporelle
même que la campagne compare** : 0 % (2005/2010/2015, filtrés observé-seulement) → 44,6 % (2022,
stock Step-5 non filtré) → 100 % (2030, produit synthétique par construction). Et les diaires
synthétiques sous-déclarent la présence au travail.

**La calibration Step-6 ne corrige pas ce biais — elle l'amplifie :**

| Comparaison | Δ work-presence | Cohen's d |
|---|---|---|
| Pré-calibration, SYN2022 vs OBS2022 | −5,82 pp | −0,324 |
| **Post-calibration, livrable 2030 `_C` vs OBS2022** | **−10,51 pp** | **−0,649** |
| Post-calibration vs observé historique (2005/10/15) | −15,32 pp | −0,938 |
| Par bande vs OBS2022 : cons / central / opt | −9,25 / −10,60 / −11,67 pp | −0,55 / −0,65 / −0,75 |
| **Écart ENTRE bandes** (le signal WFH mesuré) | **~2,4 pp** | — |

**Le biais est 4 à 5 fois le signal que la campagne existe pour détecter.**

### Mécanisme — dans le code, pas déduit

`Step6_docs/3rdJ_06_calibrate_C_4split.py` : `cap_band_stageB()` **:328-365** (garde **:341**
`if rate <= target[t]: continue`) et `run_stage_C0()` **:411** (docstring « trim-only 1->0 », garde
**:427**) sont des **écrêtages unidirectionnels** — ils ne font que *réduire* l'excès de travail vers
la cible, **jamais relever un déficit**. Le modèle synthétique sous-produisant déjà du travail, aucune
étape ne peut corriger dans ce sens. Le domicile n'est bidirectionnel qu'en week-end (Stage C1).
**Structurel, pas incident.**

Point secondaire : l'ancre « observé 2022 » (`IN_B`, **:113-114**, **:671-677**) est chargée sans
filtre `IS_SYNTHETIC`, donc contaminée — mais l'effet mesuré n'est que −2,59 pp. **Corriger l'ancre
seule ne suffira pas.**

### Ce que ça casse, et ce que ça ne casse pas

Le biais est **quasi identique sur les trois bandes** : un décalage d'ordonnée à l'origine, pas une
erreur différenciant les scénarios.

- ✅ **Axes bandes et sensibilités (9 scénarios sur 14) : intacts** — le mode commun s'annule dans les
  différences.
- 🔴 **Axe temporel (2005/2010/2015/2022 vs 2030) : contaminé.** Une courbe « présence au travail
  2005→2030 » montrerait un déclin partiellement fabriqué par la construction — soit le récit WFH
  lui-même, revendication centrale du papier.

### Précédent Leg-2

Leg-2 a **contourné** le problème architecturalement : son `3rdJ_08A_gen_historical_schedules.py`
**:495** part d'un stock observé-seulement et rake **bidirectionnellement** avant assemblage. Le
mécanisme général était documenté (`Leg2_2-split/Step5_docs/3rdJ_05_censusLinkage_2split_val.md`
**:338/:340/:398**), la conséquence spécifique jamais. Et
`Leg2_2-split/investigation/TICKET_cross_era_pairing_defect.md` **:40-42** affirme « chaque scénario
reste non biaisé en absolu » — **affirmé, jamais mesuré**. Ne pas s'appuyer dessus.

### Correctif à faire

Rendre Stage B / C0 **bidirectionnels**, re-valider Step-6, régénérer les produits 2030, cascader
Step-7. Step-6 est fermé et validé (livrable `_C`, MD5 `7c105ef3`) : prévoir la re-validation
complète. Le correctif doit être **mesuré** — re-calculer Δ vs OBS2022 après correction et montrer
l'effondrement de l'écart. Passer `check_mutex()` à 0 conflit à chaque étape (le rake par-colonne
indépendant de Leg-2 est ce qui avait causé le bug mutex hom30/wrk30).

Question à trancher **après** le correctif d'écrêtage, pas avant : faut-il aussi purifier l'ancre 2022
ou rebâtir le produit 2022 en observé-seulement ? Coût mesuré du rebuild : diversité 21 675 → 3 074
diaires distincts (réutilisation ×7,5, contre ×4,6–5,9 déjà acceptée pour les historiques).

---

## 🔴 Défaut 5 — le jeu de compteurs est incomplet : **53,5 % de l'énergie du site est rapportée à zéro** (TROUVÉ 2026-07-31, OUVERT)

### Symptôme

Sur la cellule 17 `B_central__Tall__CLG`, `hourly_meters.csv` (12 colonnes, 8760 lignes, manifeste
parfaitement propre) donne :

| Compteur | Somme annuelle | Heures non nulles |
|---|---:|---:|
| `Gas:Facility` | **0** | **0** |
| `Heating:Gas` | **0** | **0** |
| `InteriorEquipment:Gas` | **0** | **0** |
| `WaterSystems:Gas` | **0** | **0** |

Or le tableau **End Uses** de `eplustbl.htm` — produit par le même run — donne **13 884,91 GJ de gaz
naturel** : chauffage 4 082,08 · équipement intérieur 2 076,08 (buanderie hôtel) · eau chaude
sanitaire **7 726,75**. Pour 12 052,53 GJ d'électricité, le gaz est **53,5 % de l'énergie de site**.

### Cause — un renommage de version, pas une erreur de conception

EnergyPlus **9.4** a renommé la ressource `Gas` en `NaturalGas`. En 24.2 les noms `Gas:Facility`,
`Heating:Gas`, `InteriorEquipment:Gas`, `WaterSystems:Gas` **n'existent plus**. Preuve directe sur
l'artefact — `eplusout.mdd` ne contient aucun `Gas:Facility` (`grep -c` → 0) mais bien
`Output:Meter,NaturalGas:Facility,hourly`, `InteriorEquipment:NaturalGas`, etc.

`REQUIRED_METERS` (`3rdJ_08P_probe_driver.py:188-193`) demande les anciens noms. EnergyPlus refuse,
l'extracteur SQL ne trouve rien, et remplit la colonne avec **0** — indiscernable d'un vrai zéro.

### Ce n'était PAS silencieux — et c'est la vraie leçon

`eplusout.err:916-919` :

```
** Warning ** Output:Meter: invalid Key Name="GAS:FACILITY" - not found.
** Warning ** Output:Meter: invalid Key Name="INTERIOREQUIPMENT:GAS" - not found.
** Warning ** Output:Meter: invalid Key Name="HEATING:GAS" - not found.
** Warning ** Output:Meter: invalid Key Name="WATERSYSTEMS:GAS" - not found.
```

EnergyPlus a averti quatre fois, explicitement, en clair. La session du 2026-07-30 a classé les
**478** lignes `** Warning **` distinctes comme « toutes du dimensionnement bénin » — conclusion tirée
d'un décompte des **5 motifs les plus fréquents**, jamais d'une lecture des 478. Ces quatre lignes-là
sont apparues **une fois chacune** : exactement la queue que le classement par fréquence écarte.
**Correction à porter au registre : « 478 warnings, tous bénins » était faux.** Un tri par fréquence
répond à « qu'est-ce qui est bruyant », jamais à « qu'est-ce qui est grave » — et sur un fichier
d'erreurs, c'est la seconde question qui compte.

### Second trou, indépendant — 11,52 % de l'électricité non attribuée

Σ(7 compteurs d'usage final électriques) / `Electricity:Facility` = **0,8848**. Manquants, lus au
tableau End Uses : éclairage **extérieur** 682,88 GJ · rejet de chaleur (tours de refroidissement)
168,28 GJ · récupération de chaleur 537,48 GJ = **1 388,64 GJ**, soit exactement l'écart de
12 052,53 − 10 663,9 GJ. Deux voies indépendantes concordent au GJ près.

### Pourquoi ça a passé toutes les gates

La règle **§6b point 4** (« Validator gate : Σ(compteurs d'usage final) ≈ `Electricity:Facility` par
run — *unmetered-end-use tripwire* ») existe **depuis 2J Bug B**, écrite précisément contre cette
classe de panne. Elle n'a **jamais été implémentée**. C'est une gate déclarée dans le document et
absente du code : le cas le plus pur de la règle « une gate doit avoir été **vue échouer** ». Rien
dans le scorecard §P (32P/0W/0F) ne l'exerce.

### Portée

- **Aucun résultat publié n'est en cause pour l'instant** : le §8E n'existe pas, le Step 9 n'est pas
  écrit, donc aucun EUI n'a encore été calculé depuis ces colonnes. Le défaut a été trouvé **avant**
  sa première consommation, pas après.
- **Si le Step 9 avait été écrit sur ces sorties**, les EUI par canal auraient été confrontés aux
  bandes dr_L3-02 (retail 80–155) et dr_L3-03 (hôtel 180–300) en manquant la moitié de l'énergie —
  et l'hôtel, dont l'ECS au gaz est le poste dominant, aurait été le plus faussé. Verdicts inversés
  garantis.
- **Lignée partagée** : `eSim_bem_utils/idf_optimizer.py:193,197` porte les mêmes noms pré-9.4
  (`InteriorEquipment:Gas`, `Gas:Facility`). Ce fichier est commun aux trois legs → voir la question
  ouverte Leg-2 ci-dessous, qui **n'est pas tranchée unilatéralement**.

### Correctif retenu (à appliquer campagne terminée — voir « pourquoi pas maintenant »)

1. `REQUIRED_METERS` : les 4 noms gaz → `NaturalGas:Facility`, `Heating:NaturalGas`,
   `InteriorEquipment:NaturalGas`, `WaterSystems:NaturalGas`.
2. Ajouter les usages finaux électriques manquants : `ExteriorLights:Electricity`,
   `HeatRejection:Electricity`, `HeatRecovery:Electricity` — plus `Humidifier:Electricity`,
   `Refrigeration:Electricity`, `ExteriorEquipment:Electricity`, nuls ici mais requis pour que la
   fermeture soit **structurelle** et non « nulle par chance sur ce bâtiment ».
3. **Implémenter** la gate de fermeture §6b-4, par combustible, avec le résidu écrit au manifeste —
   et la faire **échouer une fois** sur l'ancien jeu de compteurs avant de la déclarer bonne.
4. Ajouter `Zone Air System Sensible Cooling/Heating Energy` (présents au `.rdd`, vérifié) +
   `Water Use Equipment Heating Energy` : sans eux la répartition **horaire pondérée par la charge**
   de la centrale — verrouillée par dr_L3-10, « jamais au prorata de surface, jamais non attribuée »
   — est tout simplement **incalculable**. Le §8E ne peut pas être écrit conformément sans cet ajout.
5. Rendre la version du schéma de sortie **partie de l'empreinte de reprise** : aujourd'hui
   `INJ_HASH = md5(commercial_integration.py)` possède le chemin, donc un changement de compteurs
   ne change rien et la reprise sauterait les cellules comme « faites ». Même faille que le Défaut 3,
   sur l'autre bord du pipeline.

### Pourquoi le correctif n'est pas appliqué pendant la campagne

`3rdJ_08D_campaign_local.py:91` lance **chaque cellule dans un `subprocess.Popen` distinct**, qui
ré-importe le driver. Éditer `REQUIRED_METERS` à chaud donnerait une campagne **hétérogène** — les
cellules déjà faites avec l'ancien jeu, les suivantes avec le nouveau, sous un seul `INJ_HASH`. La
re-simulation se fera dans un **`--outroot` neuf**, l'arbre actuel restant intact.

**Bénéfice de laisser finir la campagne en cours** : le run 2 doit reproduire `Electricity:Facility`
**à l'identique**. Ajouter des objets `Output:*` ne doit rien changer au modèle physique ; une
divergence signalerait une perturbation. On obtient gratuitement une gate de régression forte, sur
56 cellules, qu'aucune assertion écrite à la main ne remplacerait.

### Question ouverte — **arbitrage utilisateur, non tranché**

Le Step-9 de **Leg 2** ne garde que `Electricity:Facility` / `office_elec`
(`3rdJ_09_activityDrivenLoads_2split.py:99-107,162`) : **aucun gaz**. La tour Leg-2 est le même IDF,
qui brûle 13 885 GJ de gaz. Si l'EUI bureau Leg-2 de **172,7 kWh/m²/an** (déclaré « in band »
[100–200]) est électricité seule, la comparaison à une bande d'énergie **totale** est faussée. Leg 2
est **fermé et paper-ready** : à vérifier et trancher par l'utilisateur, pas à rouvrir d'office.

---

## 🔴 Défaut 6 — `channel_hourly.csv` est **non multiplié** : les magnitudes par canal valent 25 % du réel (TROUVÉ 2026-07-31, OUVERT)

### Symptôme, mesuré

| Métrique | Σ(variables de zone) | Compteur d'installation | Rapport |
|---|---:|---:|---:|
| Éclairage | 6,036 × 10¹¹ J | `InteriorLights:Electricity` 2,375 × 10¹² J | **0,2541** |
| Équipement | 1,180 × 10¹² J | `InteriorEquipment:Electricity` 4,681 × 10¹² J | **0,2520** |

### Cause, prouvée et non déduite

Les `Output:Variable` de niveau zone rapportent la zone **telle que modélisée, une seule instance** ;
les compteurs, eux, intègrent le `Multiplier`. La tour est modélisée par étages représentatifs :
`Zones.Multiplier` ∈ **{1, 4, 7, 8, 9, 10, 28, 70}** (164 zones). Vérification décisive :

```
Σ(zone_lights)                    = 6,03631e11 J
Σ(zone_lights × Zones.Multiplier) = 2,37522e12 J
InteriorLights:Electricity        = 2,37522e12 J
rapport = 1,000000
```

À la sixième décimale. Le multiplicateur est **exactement** le facteur manquant.

### Pourquoi c'est pire qu'un facteur d'échelle global

Le multiplicateur moyen diffère **par canal** (bureaux `F3-F11` ×9 et `F12-F20` ×9 ; résidentiel
`F22-F29` ×8 ; hôtel `_Mult10` ; retail `F1`/`F2` ×1). Ce n'est donc pas un mode commun qui
s'annulerait dans les parts : toute **part par canal** calculée depuis `channel_hourly.csv` brut est
biaisée en faveur des canaux à multiplicateur faible — le retail au premier chef.

### Ce que ça n'invalide pas

- **D-20 tient** : il repose sur des **comptes de valeurs distinctes** (`nuniq`), invariants par
  mise à l'échelle constante par zone.
- **Les gates §P tiennent** : P1 compare des scénarios sur la **même** colonne ; le facteur est
  commun aux deux termes de la différence.
- Ce qui tombe, c'est l'usage **magnitude** et **part** — précisément ce dont le Step 9 a besoin.

### Correctif

Le §8E multiplie par `Zones.Multiplier` (jointure sur `ZoneName` en MAJUSCULES, la casse canonique
d'EnergyPlus — même piège que le job 1169671). `channel_hourly.csv` reste tel quel : il est correct
pour ce à quoi les gates l'utilisent, et le renommer ou le changer casserait les scorecards existants.
**Écrire la convention dans son en-tête de documentation** : *valeurs par zone, non multipliées*.

---

## 🔴 Défaut 7 — les parts de surface documentées sont fausses ; la gate ±2 pp aurait échoué sur du vide (TROUVÉ 2026-07-31, OUVERT)

### Mesure contre document, tour **Tall**

Surface plancher totale EnergyPlus (ABUPS) = **72 623,1 m²**, reproduite exactement par
Σ(`FloorArea` × `Multiplier`) sur les zones `IsPartOfTotalArea = 1` (155 zones ; 9 plenums exclus,
70 612 m², exclusion conforme au comportement d'EnergyPlus lui-même).

| Canal | CFA mesurée (m²) | % de l'occupiable | **Doc** (Tall) | Écart |
|---|---:|---:|---:|---|
| Bureau | 25 485,6 | **44,65 %** | 24,4 % | **×1,8** |
| Hôtel | 14 215,4 | 24,91 % | 26,8 % | −1,9 pp |
| Résidentiel | 12 786,5 | 22,40 % | 24,4 % | −2,0 pp |
| **Retail** | 3 159,0 | **5,53 %** | 24,4 % | **×4,4** |
| Résidentiel commun | 1 428,9 | 2,50 % | — | — |
| Service/MEP | 15 547,7 | **21,41 % du brut** | « ~52 % du brut » | **−30,6 pp** |

La colonne Tall du document donne **24,4 % pour trois canaux différents**. Trois valeurs identiques
au dixième près ne sont pas une mesure : c'est un gabarit jamais remplacé. (La colonne SuperTall,
24,1 / 30,3 / 16,1 / 29,5, porte des valeurs distinctes sommant à 100 % — plausible, **à vérifier
de la même façon** avant usage, pas à supposer correcte.)

### Pourquoi c'est un défaut de gate et pas seulement de prose

La gate **±2 pp** (`§4.10`, dr_L3-10, revendiquée *project-novel*) confronte les parts d'EUI par canal
aux « parts occupiables **parsées** ». Si la référence est la table du document, la gate compare le
modèle à un gabarit : elle échouerait sur retail et bureau **quoi que fasse le modèle**. Et le réflexe
naturel — élargir la tolérance jusqu'à ce que ça passe — la rendrait vacuité pure. C'est le scénario
exact que la règle « une gate doit avoir été vue échouer » existe pour attraper.

Son nom disait déjà le correctif : **parsées**. Le §8E dérive les parts de l'IDF injecté + la table
`Zones` du SQL, jamais d'une constante recopiée. Le tableau ci-dessus **est** ce parse.

### Effet sur l'EUI

L'EUI est une division : la base de surface la fixe entièrement. Site total = **25 937,41 GJ** →
`357,15 MJ/m²` sur 72 623 m² = **99,2 kWh/m²/an** pour l'ensemble de la tour. Sur les 26 750 m²
cités au document, la même énergie donnerait 269 kWh/m²/an — un facteur **2,7**, assez pour faire
basculer n'importe quelle bande dr_L3-02/03 dans un sens ou dans l'autre. **Aucune bande d'EUI ne
doit être invoquée avant que la base de surface soit tranchée sur l'artefact.**

### À faire

Corriger la table de surfaces dans `3rdJ_00_4split_Occupancy_Pipeline.md` (AIM) et
`_Overview.md` avec les valeurs parsées, **par tour** (Tall ci-dessus ; SuperTall à parser
identiquement), et faire produire ces valeurs par le §8E dans `agg_meta.csv` pour qu'elles ne soient
jamais retapées à la main.

---

## Le travail restant, ordonné

### A. Re-simulation post-correctif retail — ✅ **FERMÉE 2026-07-28 : 25P / 0W / 0F / 9 INFO**

**Chaîne exécutée, enchaînée par `afterok`, aucune surveillance :**

| Job | Rôle | État |
|---|---|---|
| **1169799** | garde disque (9,4 To libres ≫ seuil 5 Go) + archivage des 4 répertoires périmés en `*_PRE_RETAILFIX_20260728` | COMPLETED |
| **1169800** | re-simulation `--array=1-4`, vraie simulation | COMPLETED, ~37,5–38 min/cellule |
| **1169804** | scorecard §P | COMPLETED, 4 s |

#### Scorecard : les 2 FAIL convertis (log `logs/8P_gates_1169804.out`)

| Gate | Avant (`1169679`) | Après (`1169804`) |
|---|---|---|
| **P1 retail (3 vs 1)** | 🔴 **0,0** | ✅ **9,43** |
| **P2 byte-identity** | 🔴 collision md5 `949aceb7…` | ✅ **6 md5 distincts**, cellules 0–5 |
| P1 office (2 vs 1) | 16,49 | **16,49** — inchangé |
| P1 hotel (4 vs 1) | 1,95 | **1,95** — inchangé |
| P1 office (1 vs 0) | 128,10 | **128,10** — inchangé |
| P1 retail (1 vs 0) | 117,15 | **113,63** |
| Fuite inter-canaux | Δ = 0,0 | Δ = 0,0 sur les 6 paires |

**Trois recoupements quantitatifs indépendants** — ils valident le correctif au-delà du simple
passage de gate, et méritent d'être cités tels quels :

1. **Δ office et hôtel rigoureusement inchangés.** Prédit par le cloisonnement inter-canaux (les
   deux membres de chaque paire bougent identiquement), **désormais prouvé par simulation, pas
   déduit** — conformément à la règle « le câblage ne se déduit jamais de l'énergie ».
2. **Retail vs baseline : 117,15 → 113,63 = ×0,9696.** Le pic du produit central est passé de 0,95 à
   0,9215 = **×0,9700**. L'énergie suit le changement d'échelle du produit à **0,04 % près**.
3. **Δ retail 3 vs 1 = 9,43.** L'écart opt/central est de 8,24 % ; appliqué à l'amplitude retail
   (113,63 × 0,0824) → **9,36**. Cohérent.

**INFO à noter** (ni PASS ni FAIL) : `P1 residential — NOT EXERCISED` (attend §B) et
`P3a second-hash rerun — not performed`, explicitement reporté et **en attente d'autorisation
manager** (handoff §4.6).

Inventaire md5 §6b : **10/10 fichiers concordent** aux deux bouts après téléversement (4 CSV retail,
injecteur `5670f602…`, driver `ed36feb8…`, 3 launchers, `_probe_gates.py`).
`retail_..._2030_cons.csv` était **absent** du cluster, désormais en place pour la campagne.
Mapping vérifié en lisant `3rdJ_08P_probes.sh` : `SLURM_ARRAY_TASK_ID` passe directement en
`--cell N` et la table `CELLS` indexe par cet entier → `--array=1-4` correspond 1:1 à
`B_central`/`var_office`/`var_retail`/`var_hotel`, sans décalage.

Un fichier ajouté : `3rdJ_08P_archive_retailfix.sh` (job de garde disque + archivage — `df` et `mv`
ne sont pas dans la liste blanche du login node). Aucun script existant modifié.

⚠️ **À la lecture du scorecard 1169804** : des FAIL sont **attendus** sur les cellules 0, 5 et 6, qui
n'ont pas été re-simulées — leurs sorties restent valides et intactes. Ne pas confondre avec une
régression, et **ne toucher aucun seuil**.

#### Portée — pourquoi {1,2,3,4} et non {1,3}

⚠️ **Le Progress Log annonçait {1, 3}. C'est FAUX** — corrigé le 2026-07-28 par lecture de la table
`CELLS` du driver (`3rdJ_08P_probe_driver.py:92-121`) :

| Cellule | Tag | Produit retail lu | Périmée ? |
|---|---|---|---|
| 0 | `baseline_necb` | aucun | non |
| 1 | `B_central` | `retail_2030_central` | **OUI** |
| 2 | `var_office` | `retail_2030_central` | **OUI** ← non anticipé |
| 3 | `var_retail` | `retail_2030_opt` | **OUI** |
| 4 | `var_hotel` | `retail_2030_central` | **OUI** ← non anticipé |
| 5 | `cycle_2022` | `retail_2022` (md5 inchangé) | non |
| 6 | `fallback_retail` | fichier volontairement absent | non |

*Leçon* : chaque cellule est un bâtiment complet à 4 canaux ; seul le canal **varié** change d'une
cellule à l'autre, mais **tous** les canaux sont présents. Toute cellule consommant un produit
modifié est périmée, qu'il s'agisse ou non de son canal varié.

**Attente** : le cloisonnement inter-canaux étant démontré (Δ = 0 exact), les Δ office (2 vs 1) et
hôtel (4 vs 1) devraient être **inchangés** — les deux membres de chaque paire bougent
identiquement. **À prouver par la re-simulation, jamais à déduire.**

Séquence :

1. Téléverser les 3 CSV retail 2030 corrigés (`scp`). ⚠️ `retail_..._2030_cons.csv` **n'a jamais été
   téléversé** et n'est lu par aucune cellule de probe — il servira à la campagne, pas ici.
2. **Archiver** `campaign_5670f602/{B_central,var_office,var_retail,var_hotel}` en
   `..._PRE_RETAILFIX_20260728/`. Vérifié sûr : `3rdJ_08P_probe_gates.py` ne globe que sur
   `campaign_*` à la racine (`_find_campaign_dirs`, L64-65) et reconstruit toujours le chemin via le
   dict fixe `CELL_TAGS` (L41-44) ; le driver recrée toujours le nom canonique (L494). Effet
   transitoire normal : `gates.sh` relancé entre l'archivage et la nouvelle simulation rapportera
   4 FAIL « manifest missing ».
3. Inventaire md5 §6b aux deux bouts **après** téléversement.
4. `sbatch --array=1-4 -t 7-00:00:00 …/3rdJ_08P_probes.sh` — **vraie simulation**, PAS
   `--postprocess-only` : l'horaire injecté change, `eplusout.sql` doit être recalculé (~38 min/cellule).
5. Re-passer le scorecard §P. **P1 retail et P2 restent FAIL jusque-là. Ne pas assouplir les seuils.**

État de la file au 2026-07-28 : `squeue -u o_iseri` **vide**, aucun risque d'écriture concurrente.
Coût disque de l'archivage : ~288 MB/cellule (`eplusout.sql` ≈ 133 MB, `run/` ≈ 270 MB) → **~1,15 GB**
pour les 4. Marge libre sur `/speed-scratch/o_iseri` **non vérifiée** (`quota`/`df` hors liste blanche
de la tâche d'inventaire) — à confirmer avant l'archivage.

### B. Injecteur résidentiel (OD-8R-L3) + son propre audit de câblage

**Règle verrouillée OD-8R-L3** (amende OD-8I-L3 qui disait « no per-household sampling in the
towers ») : un **ménage distinct par `Space` résidentiel**, tiré à **graine 42**, **filtre
condo/appartement** (via `DTYPE`/`CONDO`), **`Number_of_People` = `HHSIZE`**.

*Rationale* : déterministe, et préserve la diversité inter-ménages qui est tout l'intérêt de piloter
un BEM par une enquête temps-usage. La moyenne aurait aplati le pic résidentiel coïncident, et la
**forme de charge est la contribution** (§1).

- ⚠️ Les valeurs exactes de `DTYPE`/`CONDO` constituant « condo/appartement » doivent être **lues
  dans la donnée**, pas devinées, et écrites dans le docstring du script.
- ⚠️ Appariement du nombre de chambres au mix du prototype : **non adopté**. Ce serait une nouvelle OD.
- ⚠️ **2J Bug A s'applique** : résidentiel = REPLACE, Spaces multi-zones → carrier **par zone**,
  sinon équipement/éclairage du bâtiment s'effondre à ~1/N. Lignée `integration.py`
  md5 `6a92268be1f8dc3301df3bec80d6dd2e`. Le fix est **énergétiquement neutre sur les agrégats
  annuels** (correction de distribution par zone) — ne jamais prétendre qu'il « restaure » de
  l'énergie.

**Le câblage s'assure au niveau IDF d'abord, jamais déduit de l'énergie après coup** (leçon Leg-2).
Audit de câblage dédié **avant** toute simulation. Ensuite seulement la branche résidentielle de P1
devient exerçable (aujourd'hui : INFO, non exercée).

### C. Sous-étape 8A — produits manquants

Produits historiques 2005/2010/2015 et les 6 jeux de sensibilité one-at-a-time : **n'existent pas**.
Sur 14 scénarios, 4 sur disque.

⚠️ **À la génération, appliquer la règle du §Défaut 2** : vérifier que les colonnes *consommées*
diffèrent entre scénarios, pas seulement les md5.

### C-bis. Exécution LOCALE (Windows) — ✅ opérationnelle depuis le 2026-07-28

L'utilisateur a besoin des ressources Speed pour d'autres travaux. Le harnais tourne désormais
**aussi** en local. Le chemin cluster est **intact** — le portage est strictement additif.

**Le moteur est le même binaire.** `C:\EnergyPlusV24-2-0`, version 24.2.0, build **`94a887817b`** —
identique au binaire encapsulé dans `energyplus_24.2.0.sif` du cluster. IDD locale en 24.2.0.
`eSim_bem_utils/config.py:12` pointe déjà dessus et `config.py:88-124` refuse de démarrer si l'IDD
n'est pas en 24.2. **Aucune mise à jour n'était nécessaire.**

**Matériel** : Intel Core Ultra 7 265, 20 cœurs, 63,5 Go RAM, 869 Go libres.
`eppy 0.5.63` / `pandas 2.3.3` / `numpy 2.3.5` sous Python 3.13.5.

**IDF de la tour rapatriés** (ils n'existaient que sur `/speed-scratch`) vers
`3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/outputs_step8/office_idfs_v242/{CAN_MTL,CAN_CLG}/` :

| Fichier | md5 | Taille |
|---|---|---|
| `CAN_MTL/TallBuilding_…_Z6_v242.idf` | `a2a48176…` | 5 142 928 |
| `CAN_MTL/SuperTallBuilding_…_Z6_v242.idf` | `0365e7a0…` | 7 721 326 |
| `CAN_CLG/TallBuilding_…_Z7A_v242.idf` | `9390293b…` | 5 142 964 |
| `CAN_CLG/SuperTallBuilding_…_Z7A_v242.idf` | `8c136554…` | 7 721 362 |

md5 concordent cluster↔local. **Contrôle des 36 octets vérifié** : CLG − MTL = 36 exactement pour
Tall **et** SuperTall → géométrie identique, tag climat seul. Note : le tag de zone climatique est
dans le **nom du fichier** (`Z6` / `Z7A`), pas seulement dans le contenu.

#### Ce qui a été porté

| Fichier | Changement |
|---|---|
| `3rdJ_08P_probe_driver.py` | **Additif** : `--engine {auto,cluster,local}`, `--outroot`, `--repo-root`. `CELLS` (chemins en dur) → `_build_cells(step7_out)` paramétré. L'étape de simulation branche : `cluster` reproduit **verbatim** le wrapper bash + `singularity exec` ; `local` appelle directement `ENERGYPLUS_EXE`. |
| `3rdJ_08P_probe_gates.py` | **Nouvelle gate `PLATFORM`** + `--engine/--outroot/--repo-root` pour tourner hors cluster. |
| `3rdJ_08P_probes_local.py` | **Nouveau.** Orchestrateur Windows remplaçant `_probes.sh`/`_postprocess.sh`. |

**Bug trouvé et corrigé au passage** : `EPLUS_IDD` n'était pas exporté dans l'environnement après
résolution locale, donc `commercial_integration.py::_find_idd()` ne le voyait pas.

#### 🔴 Garde-fou mémoire (non négociable)

**La machine ne peut pas être redémarrée à distance.** Une saturation mémoire pendant un run non
surveillé est le pire scénario. Le watchdog est repris de `2J_docs_occ_nTemp/Step8_docs/run_campaign_local.py:60-98`
(précédent direct dans le repo, écrit pour cette contrainte exacte) : plafond **80 % de commit
charge**, `taskkill /F /T` au dépassement.

`--workers` défaut **6** — délibérément pas `cores-2` (= 18) : l'utilisateur travaille sur la machine
pendant les runs. Reprenable (une cellule complète et valide est sautée), et une sortie incomplète
ou périmée est **archivée** en `_STALE_<timestamp>`, **jamais écrasée** — application directe du
Défaut 3 ci-dessus.

#### 🔴 Gate `PLATFORM` — pourquoi elle existe

Même build ne garantit **pas** des résultats bit-identiques entre Windows et Linux (compilateur,
libm, arrondi). Les gates §P comparent des cellules **entre elles** : mélanger des cellules Linux et
Windows injecterait un bruit de plateforme dans le signal de scénario, indiscernable du signal réel.

Chaque manifeste porte désormais `PLATFORM`, `engine`, `energyplus_version`, `energyplus_build` et
`energyplus_exe_used`. La gate **échoue si des cellules comparées entre elles n'ont pas la même
`PLATFORM`**. Prouvée empiriquement dans les deux sens (manifeste `linux` fabriqué → FAIL ;
tout-`win32` → PASS). C'est une gate **nouvelle**, pas un assouplissement.

> **Règle : une campagne, une plateforme.** Prudence maintenue — voir la mesure ci-dessous, qui la
> nuance sans la lever.

#### Écart de plateforme Windows ↔ Linux — **MESURÉ 2026-07-28**

Même cellule (`1 B_central`), même build `94a887817b`, **entrées vérifiées identiques avant toute
interprétation** (`INJ_HASH` = `5670f602` des deux côtés, md5 des 3 CSV Step-7 identiques,
`inject_mixed_use_result` identique).

| Grandeur | Écart Windows ↔ Linux |
|---|---|
| `*_people` (**la métrique des gates P1**) | **0,0 EXACTEMENT**, sur 8 760 h |
| `*_lights` | ~1e-8 absolu, **~1e-13 relatif** |
| `hourly_meters` horaires | jusqu'à 43 % ponctuel (`Pumps:Electricity`, bascules d'équipement en heure-frontière) |
| **Totaux annuels énergie** | **≤ 0,0081 %** |

**Pourquoi people est exactement nul** — et c'est structurel, pas une chance : les occupants sont
pilotés par les **schedules injectés**, purement déterministes ; ils ne traversent **jamais** le
solveur. L'énergie, elle, passe par le solveur HVAC, d'où le bruit flottant. La métrique de gate P1
est donc **immunisée par construction** contre l'écart de plateforme.

Rapport écart-plateforme / signal le plus ténu (P1 hotel, Δpeople 1,95) = **0 / 1,95 = 0**.

**La gate `PLATFORM` reste néanmoins en place** : la mesure ne couvre **qu'une cellule, sans
réplicat**, sans test Calgary, et les meters énergie montrent un bruit réel quoique faible. Un
résultat unique ne justifie pas de retirer un garde-fou — mais il dit qu'un mélange n'aurait pas
contaminé le Δpeople mesuré ici. Les fichiers ne sont pas byte-identiques (md5 différents), l'écart
de taille ~1 octet/ligne pointant vers CRLF/LF, pas vers un écart numérique.

#### Validation faite

- Design-day : EnergyPlus 56,1 s, rc=0.
- 2 jours météo **avec injection réelle 3 canaux** : 76,7 s, rc=0, 48/48 lignes, les 15 colonnes de
  canaux non nulles. Chaîne injection → exécution → lecture SQL prouvée bout en bout sous Windows.
- `--postprocess-only` réel, manifeste correct écrit.
- **`INJ_HASH` local = `5670f602`**, identique au nom du répertoire de campagne cluster → l'injecteur
  local est bien le même que celui du cluster.

#### Ce qui manque encore avant les ~64 runs locaux

1. **Aucun driver de matrice complète** — seule la table des 7 cellules de probe est câblée. La
   campagne 56 runs (2 bâtiments × 2 villes × 14 scénarios) n'a pas d'équivalent local.
2. ~~Aucun temps annuel local mesuré.~~ ✅ **MESURÉ 2026-07-28 : 15,9 min/run** (cellule 1
   `B_central`, run annuel complet, 1 worker, exit 0). Contre ~38 min sur le cluster → **2,4× plus
   rapide en local**. RAM observée **525 Mo/run**, 97,7 % d'un cœur (mono-thread saturé, confirme que
   c'est la vitesse par cœur qui commande). Sizing ≈ 22 s, non proportionnel au reste.
   → 64 runs à 6 workers ≈ **2,8 h** théorique ; compter **3–4 h réelles** (contention cache/mémoire,
   le parallélisme n'est pas linéaire). RAM totale à 6 workers ≈ 3 Go sur 63 — non limitante.
   **Conclusion : le local n'est pas un pis-aller, il est plus rapide que le cluster et sans file
   d'attente.**
3. ~~Défaut 3 (`INPUTS_HASH`) reste ouvert côté driver mono-cellule.~~ ✅ **CORRIGÉ 2026-07-28** —
   voir §Défaut 3 ci-dessus. Reliquat : les répertoires legacy pré-correctif (cellules autres que
   `B_central` local, tout le cluster) n'ont pas encore d'`INPUTS_HASH` et refuseront par défaut au
   premier `--postprocess-only`/simulation jusqu'à un `--allow-stale-inputs` explicite ou une
   re-simulation complète — à anticiper avant la campagne 56 runs, pas bloquant pour la fermeture du
   défaut lui-même.

### D. Campagne 56 runs — BLOQUÉE

2 bâtiments × 2 villes × 14 scénarios, `--array=0-55`, `-t 7-00:00:00`, déterministe.
Ne se lance qu'après A, B, C.

---

## Points ouverts mineurs (à trancher, sans blocage)

| # | Point | Statut |
|---|---|---|
| 1 | **`staff_shoulder_flag` ne se déclenche jamais** sur une heure de dotation réduite : le baseline NECB ne prend aucune valeur dans (0 ; 0,10], donc le flag ne capture que les heures **totalement fermées** et force **132/288 slots à `multiplier = 0,0`**. Le nom est trompeur, et l'hypothèse « aucun personnel présent hors ouverture » est une décision de conception. Sans effet sur l'axe de sensibilité (identique entre bandes). | **Décision utilisateur.** Non traité. |
| 2 | EPW Calgary sur disque taggé `_6B` alors que §3 du runbook dit **7A**. Sans effet sur les probes (MTL seul). | À régler **avant** la campagne. |
| 3 | `assert_wiring()` (`commercial_integration.py:429`) annonce W2+W3 dans son docstring mais ne code que **W2** ; W3 vit dans le script d'audit. | Décision manager ouverte : remonter W3 dans le module, ou l'assumer côté validateur. |
| 4 | Docstring de `commercial_integration.py` (~L32-34) prétend qu'aucun prototype IDF mixte n'existe dans le repo — **périmé**, le recensement a mesuré le contraire. Un agent s'y est déjà laissé prendre. | À corriger. |
| 5 | `retail_..._2030_cons.csv` n'est lu par **aucune** cellule du harnais de probes et n'est pas sur le cluster. Normal (les probes n'exercent que central vs opt), mais il devra être téléversé pour la campagne. | Pour mémoire. |
| 6 | Job `3J_8P_gates` (`1169679`) a échoué instantanément le 2026-07-28 et n'a pas été relancé — probablement les manifests périmés/manquants. | À reconfirmer au re-scorecard. |
| 7 | 4 Spaces plénum sans Tag-2 (SuperTall en a 6, Tall 4), sans charges, donc `unmapped=0`. | Accepté-documenté. |

---

## Test method (comment on sait que c'est bon)

1. **Colonnes consommées, pas md5.** Pour tout produit multi-scénarios : max|Δ| et nombre de lignes
   différentes **par paire**, sur les colonnes que le BEM lit réellement (à identifier par lecture du
   chargeur, `fichier:ligne`). Un Δ = 0 sur une paire = le scénario n'existe pas.
2. **Gate qui échoue sur le défaut connu.** Toute gate écrite pour attraper un défaut doit être
   **empiriquement démontrée** en refabriquant le produit défectueux et en vérifiant qu'elle lève.
   Une gate qui passe sur le bug qu'elle prétend attraper est pire que pas de gate.
3. **Câblage au niveau IDF avant énergie.** On ne déduit jamais un câblage correct d'un total
   d'énergie plausible.
4. **Re-dériver, ne pas croire.** Les chiffres d'un Progress Log — y compris ceux d'un agent employé,
   y compris quand ils atteignent exactement la cible annoncée — se re-dérivent depuis les colonnes de
   l'artefact. Le présent document contient deux corrections issues de cette règle : la portée de
   re-simulation ({1,3} → {1,2,3,4}) et l'impossibilité de la bit-identité de `central`.
5. **Ne JAMAIS assouplir un seuil de gate** pour effacer un FAIL → relabel + documentation avec preuve.

---

## Rappels d'infrastructure (vérifiés, ne pas re-dériver)

- **Arbre cluster** : `/speed-scratch/o_iseri/step8_4split/{upload,logs,audit_w,probes}` ;
  sorties probes `probes/campaign_5670f602/<tag>/`.
- **Harnais** (`Step8_docs/`) : `3rdJ_08P_probe_driver.py` (md5 `ed36feb8…`), `3rdJ_08P_probes.sh`,
  `3rdJ_08P_postprocess.sh`, `3rdJ_08P_probe_gates.py`, `3rdJ_08P_gates.sh`.
  Le driver a un mode **`--postprocess-only`** (40 s vs 38 min) — valable **uniquement** quand seul le
  post-traitement change, **pas** ici.
- **Mesure par canal** : `Output:Variable` horaires par zone (occupants, éclairage, équipement),
  regroupés via `classify_tag2()` → `channel_hourly.csv`. Les meters EnergyPlus sont au niveau
  bâtiment et ne diraient pas *quel* canal a bougé.
- **Couverture meters** : `WaterSystems:Electricity` imposé (2J Bug B — l'ECS 100 % électrique pesait
  ~80 % de l'électricité MidRise et était invisible ; sur un hôtel c'est pire).
- **Moteur** : SIF `/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif`, exe interne
  `/EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64/energyplus`, wrapper singularity
  `--bind /speed-scratch --bind /nfs/speed-scratch` (**les deux binds obligatoires** — python résout
  le symlink `/nfs`, leçon Cycle-7). Wrappers **jamais dans `/tmp`** (noexec).
- **EPW MTL** : `…/BEM_Setup/WeatherFile/CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw`
- **Python cluster** : `/speed-scratch/o_iseri/envs/step4/bin/python` (3.10, eppy + pandas OK).
- **IDD** : `/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/Energy+.idd`.

### Pièges à ne pas re-découvrir

- **EnergyPlus met `ReportDataDictionary.KeyValue` en MAJUSCULES** pour les variables de zone
  (`BASEMENT_CORRIDOR ZN`) alors que l'IDF porte la casse mixte (`Basement_Corridor ZN`). Un `.map()`
  sans normalisation rend NaN à 100 % et le `dropna` vide la table **en silence**. Corrigé, mais le
  piège est générique.
- **`classify_tag2()` est exact-match sensible à la casse** (`.strip()`, pas de `.upper()`).
- Shell login Speed = **tcsh** : jamais `2>/dev/null` ni `2>&1` dans une commande ssh
  (« Ambiguous output redirect »).
- **`py -3 -m py_compile`** en PowerShell pour compile-check ; `python` nu échoue sous Git Bash
  (alias Windows Store).

### Règles cluster ABSOLUES (verbatim `CLAUDE.md`, jamais assouplies)

- 🔴 **JAMAIS** de `srun` bloquant/interactif ni aucun python/calcul sur le login node
  (`speed-submit2`) — signalé 3× déjà, prochain = suspension de compte. **TOUJOURS `sbatch`
  fire-and-forget.**
- 🔴 **AUCUN `python`/`python3` nu** sur le login node, même un one-liner.
- 🔴 **CHAQUE** soumission demande **minimum 7 jours** : `-t 7-00:00:00`.
- **Autorisé login node** : `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `cd`, `ls`, `scp`,
  `module load`, `md5sum`, et `tail`/`head`/`grep`/`wc -l`/`cat` sur **un fichier unique**.
- Commandes cluster = **une seule ligne**, `cd`-first. Étiqueter « localement » vs « sur le cluster ».
- **Monitoring : espacement min 30 min.** Préférer une dépendance SLURM
  (`--dependency=afterany:<jobid>`) à toute surveillance. Modèles pas chers pour le polling — jamais
  Opus. Ne jamais scanner un gros fichier dans le contexte du manager.
- **Ne PAS modifier** les fichiers ML protégés : `eSim_datapreprocessing.py`,
  `eSim_dynamicML_mHead.py`, `eSim_dynamicML_mHead_alignment.py`.
