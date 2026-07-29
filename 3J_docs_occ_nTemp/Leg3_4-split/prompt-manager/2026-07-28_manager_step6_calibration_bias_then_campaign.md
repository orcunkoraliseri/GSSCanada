# MANAGER — 3J Leg-3 : corriger le biais de calibration Step-6, puis dérouler jusqu'à la campagne 56 runs

**Écrit le 2026-07-28 en fin de session, par le manager sortant.**
**Décision utilisateur du 2026-07-28 : corriger Step-6 D'ABORD, puis continuer le reste.**
L'utilisateur met le projet en pause pour se concentrer sur un autre travail. Ce document est le
relais : une session fraîche doit pouvoir reprendre avec **ce fichier seul** comme point d'entrée.

---

## Ton rôle

Tu es le **MANAGER** du pipeline 3J Leg-3 (4-split : résidentiel + bureau/WFH + commerce + hôtel).
Tu planifies, tu débogues, tu orchestres. Tu **lances toi-même les agents employés** (outil Agent,
`sonnet` pour la construction, `haiku`/`sonnet` pour le mécanique — **jamais Opus pour du polling**).
Tu ne fais pas l'implémentation multi-étapes toi-même.

Méthode validée par l'utilisateur : tu décides et tu avances sans redemander à chaque étape
(« tu progresses comme tu recommandes »). Tu **ne l'interromps que** si un choix change ce qui est
publiable — ce qui est précisément arrivé aujourd'hui, et a produit ce document.

---

## Lire dans cet ordre

1. **Ce fichier.**
2. `Step8_docs/3rdJ_08_implementation_improvements.md` — doc d'implémentation autoportant : état
   verrouillé, défauts corrigés, travail restant, règles cluster.
3. `Step8_docs/3rdJ_08_simulation_4split.md` → `Progress Log` — chronologie faisant foi.
4. `Step8_docs/3rdJ_08_simulation_4split_val.md` §P — définitions P1–P4.

---

## 🔴 LE PROBLÈME À TRAITER EN PREMIER — biais de calibration Step-6

### Ce qui a été mesuré (2026-07-28, deux investigations indépendantes)

La fraction de diaires `IS_SYNTHETIC == 1` **monte de façon monotone le long de la séquence
temporelle même que la campagne compare** :

| Époque | Fraction synthétique | Origine |
|---|---|---|
| 2005 / 2010 / 2015 | **0 %** | filtre observé-seulement dans `3rdJ_08A_gen_historical_products_4split.py` |
| 2022 | **44,6 %** | `cmd_year_2022()` lit le stock Step-5 sans filtre |
| 2030 (3 bandes) | **100 %** | produit synthétique Step-6 par construction |

Et les diaires synthétiques sous-déclarent systématiquement la présence au travail.
**La calibration Step-6 ne corrige pas ce biais — elle l'amplifie** :

| Comparaison | Δ work-presence | Cohen's d |
|---|---|---|
| Pré-calibration, SYN2022 vs OBS2022 | −5,82 pp | −0,324 |
| **Post-calibration, livrable 2030 `_C` vs OBS2022** | **−10,51 pp** | **−0,649** |
| Post-calibration vs observé historique (2005/10/15) | −15,32 pp | −0,938 |
| Par bande vs OBS2022 : cons / central / opt | −9,25 / −10,60 / −11,67 pp | −0,55 / −0,65 / −0,75 |
| **Écart ENTRE bandes** (le signal WFH que la campagne mesure) | **~2,4 pp** | — |

**Le biais est 4 à 5 fois le signal.**

### Mécanisme — identifié dans le code, pas déduit

`3J_docs_occ_nTemp/Leg3_4-split/Step6_docs/3rdJ_06_calibrate_C_4split.py` :

- `cap_band_stageB()` **:328-365**, garde **:341** `if rate <= target[t]: continue`
- Stage C0, `run_stage_C0()` **:411** (docstring « trim-only 1->0 »), garde **:427**

Les deux sont des **écrêtages unidirectionnels** : ils ne font que *réduire* l'excès de travail vers
la cible, **jamais relever un déficit**. Le modèle synthétique sous-produisant déjà du travail,
aucune étape de la chaîne ne peut corriger dans ce sens. Le domicile n'est corrigé
bidirectionnellement qu'en week-end (Stage C1) ; en semaine il ne monte que par effet de bord des
trims de travail, jamais ne redescend. **C'est structurel, pas incident.**

Point secondaire, réel mais mineur : l'ancre « observé 2022 » de la calibration (`IN_B`, **:113-114**,
**:671-677**) est chargée via `obs_full[obs_full["CYCLE_YEAR"]==2022]` **sans filtre `IS_SYNTHETIC`**,
donc contaminée par les 44,6 % de synthétiques 2022. Effet mesuré : Δ = −2,59 pp seulement. Le moteur
dominant est l'asymétrie d'écrêtage, pas la contamination d'ancre. **Corriger l'ancre seule ne suffira pas.**

### Ce que le biais casse, et ce qu'il ne casse pas

Le biais est **quasi identique sur les trois bandes** — c'est un décalage d'ordonnée à l'origine, pas
une erreur qui différencie les scénarios. Donc :

- ✅ **Axes bandes et sensibilités (9 scénarios sur 14) : INTACTS.** Le mode commun s'annule dans les
  différences bande-à-bande.
- 🔴 **Axe temporel (2005/2010/2015/2022 vs 2030) : CONTAMINÉ.** Une courbe « présence au travail
  2005→2030 » montrerait un déclin partiellement fabriqué par la construction — c'est-à-dire le
  récit WFH lui-même, qui est la revendication centrale du papier.

### Précédent Leg-2 — pourquoi la question ne s'était jamais posée

Leg-2 a **architecturalement contourné** le problème : son `3rdJ_08A_gen_historical_schedules.py`
(**:495**) part d'un stock observé-seulement `aug[(CYCLE_YEAR==2022)&(IS_SYNTHETIC==0)]` et applique
un rake **bidirectionnel** « Phase-8B » (docstring **:9-19**) qui bascule les lignes synthétiques vers
les marginales observées *avant* assemblage. Leg-2 n'a donc jamais mélangé de contenu synthétique
dans sa comparaison historique↔2022.

Le mécanisme général était documenté (`Leg2_2-split/Step5_docs/3rdJ_05_censusLinkage_2split_val.md`
**:338**, **:340**, **:398** — « IS_SYNTHETIC dilution effect »). La **conséquence spécifique** ne l'a
jamais été. Et `Leg2_2-split/investigation/TICKET_cross_era_pairing_defect.md` **:40-42** affirme
« chaque scénario reste non biaisé en absolu » — **affirmé, jamais mesuré**. Ne pas s'appuyer dessus.

### 🔴 Ta mission n°1

Rendre Stage B / Stage C0 **bidirectionnels** dans `3rdJ_06_calibrate_C_4split.py`, re-valider Step-6,
régénérer les produits 2030, puis seulement dérouler la suite.

Contraintes non négociables :

- Step-6 est **FERMÉ et validé** (livrable `_C`, MD5 `7c105ef3`, 111 024 lignes, GSS 66P/15W/5F).
  Le rouvrir **cascade** sur Step-7 (produits 2030) puis Step-8. Prévois la re-validation complète,
  ne te contente pas du correctif.
- **Ne JAMAIS assouplir un seuil de gate** pour effacer un FAIL → relabel + documentation avec preuve
  empirique (refabriquer le défaut et montrer que la gate lève).
- Le correctif doit être **démontré sur le défaut connu** : après correction, mesurer à nouveau
  Δ work-presence du livrable 2030 vs OBS2022 et montrer que l'écart s'est effondré. Un correctif
  non mesuré n'est pas un correctif.
- Attention au **bug mutex hom30/wrk30** : c'est le rake par-colonne indépendant de Leg-2 qui l'avait
  causé. Toute correction bidirectionnelle doit passer `check_mutex()` — 0 conflit — à chaque étape.
- Question ouverte à trancher avec données : faut-il **aussi** purifier l'ancre 2022 (`IN_B`) et/ou
  rebâtir le produit 2022 en observé-seulement ? Mesuré : la purification d'ancre ne vaut que
  −2,59 pp. Et rebâtir 2022 en observé-seulement coûterait la diversité — 21 675 → 3 074 diaires
  distincts (réutilisation ×7,5, contre ×4,6–5,9 déjà acceptée pour 2005/2010/2015). **Décider après
  le correctif d'écrêtage**, pas avant : il se peut qu'il devienne inutile.

---

## État verrouillé au 2026-07-28 (fin de session)

### Fermé aujourd'hui

| Élément | État |
|---|---|
| Défaut retail `multiplier` | **FERMÉ** — 25P/0W/0F/9 INFO (job 1169804). Le levier de bande était annulé par auto-normalisation ; ancrage sur le pic de la base non-levée. Re-simulé cellules {1,2,3,4}. |
| Audit résidentiel colonne-par-colonne | **SAIN** — REPLACE, aucune normalisation, rien à annuler. |
| **Injecteur résidentiel (OD-8R-L3)** | **IMPLÉMENTÉ** dans `eSim_bem_utils/commercial_integration.py`. 27 appartements Tall (41 SuperTall), un ménage distinct chacun, graine 42, `Number_of_People = HHSIZE`, filtre `DTYPE ∈ {HighRise, MidRise}`. **2J Bug A trouvé sous une forme inattendue** : un SEUL objet PEOPLE au niveau SpaceList servait les 27 Spaces → neutralisé (`Number_of_People=0`, conservé, pas supprimé) + 27 porteurs individuels émis. Vérifié au niveau IDF, jamais déduit de l'énergie. Déterminisme prouvé. |
| **Défaut 3 — trou d'empreinte** | **FERMÉ.** `INPUTS_HASH` distinct dans le manifeste, refus bruyant nommant le fichier divergent, `--allow-stale-inputs` pour la re-simulation délibérée (archive en `_STALE_<ts>`, n'écrase jamais). `INJ_HASH` garde le chemin → `--postprocess-only` survit. Démontré empiriquement dans les deux sens. |
| **Produits historiques 2005/2010/2015** | **GÉNÉRÉS** — 9 fichiers (3 ans × résidentiel/bureau/commerce) dans `Step8_docs/outputs_step8/historical_schedules/`. Gates PASS, déterminisme reproduit, **aucune paire à Δ = 0** sur les colonnes consommées. `rake_cycle()` de Leg-2 délibérément **non porté** (cause du bug mutex). |
| **Classification `residential_common`** | **CORRIGÉE.** `classify_tag2()` renvoie enfin `"residential_common"` comme sa docstring le promettait (le test à `:640` était du code mort). Tall 27+3=30, SuperTall 41+4=45. Conservation prouvée (164 / 256 Spaces). |
| **Colonne `residential_common` séparée** | **FAITE** dans `channel_hourly.csv`. Motif : `office_support` **est** modulé par l'injection bureau, `residential_common` n'est injecté par personne — les fusionner diluait le niveau attribué au résidentiel. Conservation à 2e-16 près, `--postprocess-only` en 14,5 s. |
| **Driver de campagne local** | **CONSTRUIT** — `3rdJ_08D_campaign_cells.py` / `_campaign_driver.py` / `_campaign_local.py`. 56 cellules dérivées programmatiquement. Smoke run 2 jours = 48 s. Réutilise le watchdog mémoire et `_archive_stale()` par `importlib`, pas de duplication. |

### Canal résidentiel dans la table des 56 cellules — CORRIGÉ à la clôture

La table des 56 cellules avait d'abord été construite **sans canal résidentiel**
(`_bundle_channels()` ne renvoyait que office/retail/hotel) : les 56 runs auraient tourné avec les
27 appartements au baseline NECB, **le canal résidentiel — sujet même de la thèse — absent de la
campagne**. Le `--dry-run` annonçait « 0 missing inputs » : il ne valide que ce qui est listé, il ne
peut pas voir un canal omis. Même motif que le défaut retail : plausible, silencieux, faux.

**Corrigé et vérifié :**

- Les 8 produits résidentiels (2022, 2030 cons/central/opt, historiques 2005/2010/2015) sont câblés
  en `channels["residential"] = {"csv": ..., "seed": 42}`, contrat lu dans
  `commercial_integration.py:557-560, 673-680`.
- Table finale : `Default_NECB` = 0 canal ; `Y2022` / `B_*` / tous les `sens_*` = **4 canaux** ;
  `Y2005`/`Y2010`/`Y2015` = 3 canaux (hôtel délibérément absent).
- **Axe de sensibilité tranché par le code** (`3rdJ_07_aug_to_bem_4split.py:358-359, 909-928, 932`) :
  résidentiel et bureau **partagent bien** l'axe de bande WFH — `assemble_2030(office_band)` est le
  générateur unique du résidentiel, et `--sens office` reconstruit les deux ensemble tandis que
  `--sens retail`/`--sens hotel` n'en reconstruisent aucun. Donc `sens_office_cons/opt` basculent
  **aussi** le produit résidentiel ; `sens_retail_*`/`sens_hotel_*` le gardent à central.
- **Garde `validate_campaign_channels()`** ajoutée et **vue en train d'échouer** : résidentiel retiré
  de `Y2022` → `AssertionError` nommant les 4 cellules affectées (1, 15, 29, 43) ; restauré →
  `0/56 missing input`.
- Smoke run cellule 27 (`sens_hotel_opt__Tall__CLG`, 2 jours, 50,9 s) : injection résidentielle
  confirmée en clair — 27 Spaces ← 27 ménages distincts, graine 42, 1 porteur neutralisé — et
  `residential_people` non nul et variable dans le temps (19,0–70,0 ; 34 valeurs distinctes sur
  48 lignes). **Le harnais de probes reste à 7 cellules, inchangé.**

### Décisions manager déjà prises — ne pas rouvrir

- **Hôtel absent des années historiques**, uniformément, les deux villes. `hotel_multiplier_lookup.csv`
  couvre 2011–2022 et la vérité terrain QC commence en 2019 ; injecter avant 2011 serait de la
  fabrication. AB-2015 seul serait réel, mais un mélange AB-réel / QC-backcasté créerait un
  confondant province×canal pire que l'absence. Le cloisonnement inter-canaux étant prouvé (Δ = 0
  exact), la contribution hôtel est additive et identique d'une cellule historique à l'autre : une
  comparaison historique↔2022 reste rigoureuse en corrigeant par canal via `channel_hourly.csv`.
- **Normalisation retail des années historiques** : chemin `ref_peak=None` (auto-normalisant), correct
  car il n'y a pas de levier de bande à préserver. Appliquer le correctif 2030 ici serait une
  mésapplication.
- **Calgary** : HDD18 = 4933 (design) / 4852 (fichier météo) → zone NECB **6**, pas 7A. Cas limite
  réel à 1,3–3 % sous le seuil des 5000, pas un simple malentendu NECB-vs-ASHRAE. **Fichier NON
  renommé**, documenté. Conséquence à mentionner dans le papier : Montréal est apparié (IDF Z6 /
  météo zone 6), Calgary ne l'est pas tout à fait (IDF Z7A / météo zone 6).
- **`assert_wiring()`** : docstring corrigée en « W2 ONLY ». W3 reste dans `3rdJ_08W_audit_wiring.py`
  Block 5, qui a besoin des IDF source ET injecté simultanément — signature qu'`assert_wiring()` n'a pas.

---

## Le travail restant, ordonné

1. 🔴 **Correctif du biais de calibration Step-6** (ci-dessus) + re-validation + régénération des
   produits 2030 + cascade Step-7.
2. **Vérifier le canal résidentiel dans la table des 56 cellules** (agent en vol à la clôture).
3. **Re-simuler les 7 cellules de probe** — `commercial_integration.py` a changé, donc `INJ_HASH`
   change, donc `campaign_5670f602/` est périmé. C'était prévu : le résidentiel n'y était pas injecté
   du tout. ~16 min/cellule en local.
4. **Re-passer le scorecard §P** avec la branche résidentielle de P1 enfin exerçable (aujourd'hui INFO,
   « NOT EXERCISED »).
5. **Campagne 56 runs** — 2 bâtiments × 2 villes × 14 scénarios. Estimé **2,6–3,5 h en local** à
   6 workers (mesuré 15,9 min/run mono-worker, contre ~38 min sur le cluster).

### Points ouverts mineurs

| # | Point | Statut |
|---|---|---|
| 1 | `staff_shoulder_flag` ne se déclenche jamais sur une heure de dotation réduite (le baseline NECB ne prend aucune valeur dans (0 ; 0,10]) : il ne capture que les heures totalement fermées et force **132/288 slots à 0,0**. Sans effet sur l'axe de sensibilité (identique entre bandes) mais touche le niveau absolu du commerce. | **Décision utilisateur.** Non traité. |
| 2 | `P3a second-hash rerun` jamais effectué, en attente d'autorisation manager (handoff §4.6). | Ouvert. |
| 3 | Aucun run annuel Calgary jamais mesuré (seulement Montréal). | À faire avant la campagne. |
| 4 | Aucun port cluster du driver de campagne (local seulement). | Non bloquant — le local est 2,4× plus rapide. |
| 5 | 4 Spaces plénum sans Tag-2 ni charges (`unmapped=0`). | Accepté-documenté. |

---

## Méthode de test — comment on sait que c'est bon

1. **Colonnes consommées, pas md5.** Deux fichiers peuvent avoir des md5 distincts et des colonnes
   *consommées* identiques — c'est exactement ainsi que l'axe retail était mort. Colonnes réellement
   lues : résidentiel `Occupancy_Schedule` + `Metabolic_Rate` (`integration.py:379-380`) ; bureau
   `AT_WORK_fraction` ; commerce `multiplier` ; hôtel `multiplier`.
2. **Une gate doit être vue en train d'échouer.** Refabriquer le défaut, montrer qu'elle lève. Une
   gate qui passe sur le bug qu'elle prétend attraper est pire que pas de gate.
3. **Câblage au niveau IDF avant énergie.** On ne déduit jamais un câblage correct d'un total
   d'énergie plausible.
4. **Re-dériver, ne pas croire.** Les chiffres d'un Progress Log — y compris ceux d'un agent employé,
   y compris quand ils atteignent exactement la cible annoncée — se re-dérivent depuis les colonnes de
   l'artefact. Trois corrections de cette règle aujourd'hui : la portée de re-simulation ({1,3} →
   {1,2,3,4}), l'impossibilité de la bit-identité de `central`, et le canal résidentiel absent des
   56 cellules.
5. **Ne JAMAIS assouplir un seuil de gate** → relabel + preuve.

---

## Règles cluster ABSOLUES (verbatim `CLAUDE.md`, jamais assouplies)

- 🔴 **JAMAIS** de `srun` bloquant/interactif ni aucun python/calcul sur le login node
  (`speed-submit2`) — signalé 3× déjà, prochain = **suspension de compte = tout le progrès perdu**.
  **TOUJOURS `sbatch` fire-and-forget.**
- 🔴 **AUCUN `python`/`python3` nu** sur le login node, même un one-liner.
- 🔴 **CHAQUE** soumission demande **minimum 7 jours** : `-t 7-00:00:00`.
- **Autorisé login node** : `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `cd`, `ls`, `scp`,
  `module load`, `md5sum`, et `tail`/`head`/`grep`/`wc -l`/`cat` sur **un fichier unique**.
  `mv`, `df`, `quota`, `rm`, `mkdir` ne sont **pas** autorisés → passer par un job `sbatch`.
- Commandes cluster = **une seule ligne**, `cd`-first. Étiqueter « localement » vs « sur le cluster ».
- **Monitoring : espacement min 30 min**, pas de boucle vive. Préférer `--dependency=afterok:<jobid>`.
  Modèles pas chers pour le polling — **jamais Opus**. Les sous-agents héritent d'Opus si aucun modèle
  n'est fixé explicitement.
- **Ne PAS modifier** : `eSim_datapreprocessing.py`, `eSim_dynamicML_mHead.py`,
  `eSim_dynamicML_mHead_alignment.py`.
- Shell login Speed = **tcsh** : jamais `2>/dev/null` ni `2>&1` dans une commande ssh.
- **`py -3 -m py_compile`** en PowerShell pour compile-check ; `python` nu échoue sous Git Bash.

## Exécution locale

`C:\EnergyPlusV24-2-0`, version 24.2.0 build **`94a887817b`** — **identique** au binaire du `.sif`
cluster. 20 cœurs, 63,5 Go RAM. **15,9 min/run** contre ~38 min sur Speed, sans file d'attente.
Écart de plateforme Windows↔Linux sur `*_people` (la métrique des gates P1) : **0,0 exactement** sur
8 760 h — les occupants viennent des schedules injectés et ne traversent jamais le solveur. Totaux
annuels énergie : ≤ 0,0081 %. La gate `PLATFORM` reste en place malgré tout (une mesure, une cellule,
sans réplicat, ne justifie pas de retirer un garde-fou).

🔴 **La machine ne peut pas être redémarrée à distance.** Le watchdog mémoire (plafond 80 % de commit
charge, `taskkill /F /T` au dépassement) est **non négociable** sur tout run local non surveillé.
`--workers 6` par défaut, délibérément pas `cores-2` : l'utilisateur travaille sur la machine.
