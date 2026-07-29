# Prompt DIRECTEUR — 3J Leg-3 Step 8 (probes PASSÉES, défaut produit retail à trancher)
**Date : 2026-07-28**

---

## Ton rôle

Tu es le **manager** du pipeline 3J Leg-3 (4-split : résidentiel + bureau/WFH + commerce + hôtel).
Tu **planifies, débogues, et orchestres** ; tu **n'exécutes pas** toi-même les tâches lourdes.
Des **employés (Sonnet/Haiku)** exécutent chaque handoff et journalisent dans le Progress Log du
doc concerné. Tu possèdes la liste de tâches et la mémoire.

**Note de méthode (validée par l'utilisateur le 2026-07-28) :** pas besoin d'écrire un prompt
employé à coller à la main — tu peux **lancer les agents toi-même** (Agent tool, modèle `sonnet`
pour la construction, `haiku`/`sonnet` pour le mécanique, jamais Opus pour du polling). Tu écris
la spec, l'agent exécute, tu relis avant soumission.

Lis d'abord `CLAUDE.md` (racine repo) — règles cluster ABSOLUES, workflow deux-agents, règle de coût.
Puis la mémoire : `MEMORY.md` → `project_3j_leg3_step8_status.md` (le plus à jour),
`project_3j_leg3_step7_status.md`.

---

## Où on en est (état verrouillé au 2026-07-28)

### Fait et fermé

- **Steps 1–7 : DONE.** Architecture **B** (tour mixte unique, 4 canaux par Tag-2). Ne jamais
  revenir au cadrage A (UBEM par archétype, rejeté).
- **8B : DONE.** Les 4 IDF v24.2 (Tall/SuperTall × MTL/CLG) vérifiés sur
  `/speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/outputs_step8/office_idfs_v242/`.
  Réutilisés, pas re-transitionnés. Chaque paire MTL/CLG diffère de **36 octets** exactement →
  géométrie identique, tag climat seul, donc les deltas EUI isolent le climat.
- **AUDIT-W : 9P/1W/0F** (jobs `1169582` puis `1169584`). Recensement Tag-2 Tall =
  30 résid / 33 bureau / 9 commerce / 25 hôtel / 63 service_MEP = **164**. W2, W3, W6, W7 PASS.
  Le WARN unique = 4 Spaces plénum sans Tag-2, sans charges → accepté-documenté.
- **BUG-W7 corrigé** dans `eSim_bem_utils/commercial_integration.py` : il écrivait
  `Interpolate_to_Timestep` sur LIGHTS/ELECTRICEQUIPMENT (champ de `Schedule:Day:Interval`),
  → 26 fausses WARN « injection failed » par run. Le câblage était bon (l'assignation précède le
  throw) mais le bruit aurait masqué un vrai échec sur 56 runs, et le code était fragile à l'ordre.
  **Nouvelle gate W7** ajoutée : avant elle, le câblage LIGHTS/EQUIP commercial n'était sous
  **aucune** gate (W2 et W3 ne regardent que PEOPLE).
- **PROBES §P : 23P / 0W / 2F** (job `1169679`). Détail complet dans le Progress Log du runbook.
  - PASS : office (Δpeople 16,5 / 128,1), hotel (1,95 / 27,9), retail-vs-baseline (117,1),
    P3a hash, P3b complétude ×14, les 3 gates P4.
  - **Zéro fuite inter-canaux** : dans chaque paire, tout canal non varié donne Δ = 0,0 exactement.
    L'injection est proprement cloisonnée par Tag-2 — bonne nouvelle pour l'attribution §8.
  - Résidentiel = INFO, **NON EXERCÉ**.

### Les 2 FAIL — un seul défaut, en amont, dans Step 7

`retail_presence_multiplier_2030_{cons,central,opt}.csv` ont des colonnes **`multiplier`
identiques deux à deux (Δ = 0)**. Elles ne diffèrent que dans `at_retail_fraction` — colonne
diagnostique que personne ne lit. Or `load_retail_series()` ne consomme **que** `multiplier`.
Conséquence : **les trois bandes retail 2030 sont un seul et même scénario** côté BEM ; l'axe
retail de la campagne a 2 états distincts (2022, « 2030 »), pas 4. Hotel (Δ 0,059–0,126) et office
(Δ 0,115–0,149) sont sains.

**Cause structurelle** — `Step7_docs/3rdJ_07_aug_to_bem_4split.py::_retail_rows_from_slotarray` :
```
421  peak  = float(arr_clock48.max())
422  shape = arr_clock48 / peak          # normalisation par son PROPRE pic
423  multiplier_raw = 0.95 * shape
```
`arr_clock48` est le tableau **déjà leviéré par la bande**. La ligne 422 le divise par son propre
maximum → tout rééchelonnage de *niveau* s'annule exactement. `build_retail_product_2030()` (L456)
appelle ça à l'identique pour les trois bandes, donc elles s'effondrent ensemble.

**Ce que ça aurait coûté sans les probes :** l'axe de sensibilité retail aurait rendu des résultats
identiques pour central et opt, avec des EUI parfaitement plausibles, en silence. C'est le symptôme
byte-identité de Leg-2 reproduit ailleurs — précisément ce que §7 a été écrit pour attraper.

---

## 🔴 DÉCISION EN ATTENTE (bloquante, posée à l'utilisateur, sans réponse à ce jour)

**Comment corriger le `multiplier` retail ?** Ça change des valeurs de produit Step-7 déjà
publiées → escaladé, **jamais appliqué unilatéralement**.

- **(a) — RECOMMANDÉ.** Normaliser par un **pic de référence fixe** au lieu du pic propre à chaque
  bande. Référence = pic de `central` ⇒ central reste bit-identique, cons/opt s'échelonnent
  relativement. Préserve la sémantique de forme existante, minimalement invasif.
- **(b)** Garder l'auto-normalisation puis multiplier par les constantes de bande
  (retail 0,90 / 0,97 / 1,05 selon la définition des bundles Step-7). Marche, mais empile un second
  concept de mise à l'échelle sur le premier.

Après correction : regénérer les **trois** bandes, puis **RE-SIMULER** les cellules 1 et 3
(≈38 min chacune) — un simple `--postprocess-only` **ne suffit pas**, l'horaire lui-même change —
puis relancer le scorecard.

**Deuxième question posée, sans réponse :** faut-il vérifier le résidentiel colonne par colonne ?
Ses 4 fichiers scénarios diffèrent en taille + md5, mais **une normalisation destructrice de niveau
dans ce chemin serait rigoureusement invisible à ce test**. Même famille de piège.

---

## Décisions verrouillées ce jour (ne pas rouvrir)

- **OD-8R-L3 — règle d'effondrement résidentielle.** Un **ménage distinct par `Space` résidentiel**,
  tiré à **graine 42**, **filtre condo/appartement** (via `DTYPE`/`CONDO`), **`Number_of_People` =
  `HHSIZE`**. Amende OD-8I-L3 qui disait « no per-household sampling in the towers ».
  *Rationale :* déterministe + préserve la diversité inter-ménages qui est tout l'intérêt de piloter
  un BEM par une enquête temps-usage ; la moyenne aurait aplati le pic résidentiel coïncident, et la
  forme de charge **est** la contribution (§1).
  ⚠️ Les valeurs exactes de `DTYPE`/`CONDO` constituant « condo/appartement » doivent être **lues
  dans la donnée**, pas devinées, et écrites dans le docstring du script.
  ⚠️ Appariement du nombre de chambres au mix du prototype : **non adopté**. Ce serait une nouvelle OD.
  **Spécifiée mais PAS implémentée.**

---

## Le travail restant (ordonné)

1. **Trancher (a) vs (b)** → regénérer les 3 bandes retail → re-simuler cellules 1+3 → re-scorecard.
   **P1 retail et P2 restent FAIL jusque-là. Ne pas assouplir les seuils.**
1b. **Vérif résidentielle colonne par colonne** (le trou signalé ci-dessus).
2. **Injecteur résidentiel** (OD-8R-L3) **+ son propre audit de câblage** avant toute simulation.
   On assure le câblage au niveau IDF **d'abord**, on ne le déduit jamais de l'énergie après coup —
   leçon Leg-2. Puis la branche résidentielle de P1 devient exerçable.
   ⚠️ **2J Bug A** s'applique : résidentiel = REPLACE, Spaces multi-zones → carrier **par zone**,
   sinon équipement/éclairage du bâtiment s'effondre à ~1/N. Lignée `integration.py`
   md5 `6a92268be1f8dc3301df3bec80d6dd2e`. Le fix est **énergétiquement neutre sur les agrégats
   annuels** — ne jamais prétendre qu'il « restaure » de l'énergie.
3. **Sous-étape 8A** : produits historiques 2005/2010/2015 — **n'existent pas**. Idem les
   **6 jeux de sensibilité one-at-a-time**. Sur 14 scénarios de la matrice, **4 seulement existent
   sur disque** (2022, 2030_cons/central/opt) — et les 3 bandes 2030 retail sont en fait 1 seule.
4. **CAMPAGNE** 56 runs : 2 bâtiments × 2 villes × 14 scénarios, `--array=0-55`, `-t 7-00:00:00`,
   déterministe. **Bloquée** tant que 1–3 ne sont pas fermés.
5. **Mineur, à régler avant campagne** : l'EPW Calgary sur disque est taggé `_6B` alors que §3 du
   runbook dit 7A. Sans effet sur les probes (MTL seul).

---

## Infrastructure en place (vérifiée, ne pas re-dériver)

- **Arbre cluster** : `/speed-scratch/o_iseri/step8_4split/{upload,logs,audit_w,probes}`.
  Sorties probes : `probes/campaign_5670f602/<tag>/` pour les tags `baseline_necb`, `B_central`,
  `var_office`, `var_retail`, `var_hotel`, `cycle_2022`, `fallback_retail`.
- **Harnais probes** (`Step8_docs/`) : `3rdJ_08P_probe_driver.py`, `3rdJ_08P_probes.sh`,
  `3rdJ_08P_postprocess.sh`, `3rdJ_08P_probe_gates.py`, `3rdJ_08P_gates.sh`.
  Le driver a un mode **`--postprocess-only`** qui re-dérive les CSV depuis un `eplusout.sql`
  existant — **40 s au lieu de 38 min** quand seul le post-traitement est en cause.
- **Empreinte** : chemin de sortie = `campaign_<md5(commercial_integration.py)[:8]>/`. Garde
  stale-output **structurelle**. Le md5 du driver est en plus consigné dans le manifeste : `INJ_HASH`
  n'empreinte que l'injecteur, donc un correctif de post-traitement ne doit pas (et ne doit pas
  pouvoir) invalider le chemin de sortie de la simulation.
- **Mesure par canal** : `Output:Variable` horaires par zone (occupants, éclairage, équipement),
  regroupés via `classify_tag2()` → `channel_hourly.csv`. Les meters EnergyPlus sont au niveau
  bâtiment et ne diraient pas *quel* canal a bougé.
- **Couverture meters** : `WaterSystems:Electricity` imposé (2J Bug B — l'ECS 100 % électrique
  pesait ~80 % de l'électricité MidRise et était invisible ; sur un hôtel c'est pire).
- **Moteur** : SIF `/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif`, exe interne
  `/EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64/energyplus`, wrapper singularity
  `--bind /speed-scratch --bind /nfs/speed-scratch` (les deux binds obligatoires — python résout
  le symlink `/nfs`, leçon Cycle-7). Wrappers **jamais dans `/tmp`** (noexec).
- **EPW MTL** : `/speed-scratch/o_iseri/step8_2split/upload/BEM_Setup/WeatherFile/CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw`
- **Python cluster** : `/speed-scratch/o_iseri/envs/step4/bin/python` (3.10, eppy + pandas OK).
- **IDD** : `/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/Energy+.idd`.

### Pièges rencontrés, à ne pas re-découvrir

- **EnergyPlus met `ReportDataDictionary.KeyValue` en MAJUSCULES** pour les variables de zone
  (`BASEMENT_CORRIDOR ZN`), alors que l'IDF porte la casse mixte (`Basement_Corridor ZN`). Un
  `.map()` sans normalisation rend NaN à 100 % et le `dropna` vide la table en silence. Corrigé,
  mais c'est un piège générique.
- **`classify_tag2()` est exact-match sensible à la casse** (`.strip()`, pas de `.upper()`).
- Le shell login Speed est **tcsh** : jamais `2>/dev/null` ni `2>&1` dans une commande ssh
  (« Ambiguous output redirect »).
- **`py -3 -m py_compile`** en PowerShell pour compile-check ; `python` nu échoue sous Git Bash
  (alias Windows Store).
- Le docstring de `commercial_integration.py` (~L32-34) prétend qu'aucun prototype IDF mixte
  n'existe dans le repo — **c'est périmé**, le recensement a mesuré le contraire. Un agent s'y est
  déjà laissé prendre.
- `assert_wiring()` (L429) annonce W2+W3 dans son docstring mais ne code que W2 ; W3 vit dans le
  script d'audit. **Décision manager toujours ouverte** : le remonter dans le module ou le laisser
  côté validateur.

---

## Règles cluster ABSOLUES (Speed HPC — verbatim CLAUDE.md, jamais assouplies)

- 🔴 **JAMAIS** de `srun` bloquant/interactif ni AUCUN python/calcul sur le login node
  (`speed-submit2`) — signalé 3× déjà, prochain = suspension de compte. **TOUJOURS `sbatch`
  fire-and-forget.**
- 🔴 **AUCUN `python`/`python3` nu** sur le login node (même one-liner) ; tout ce qui importe
  pandas/numpy/torch/eppy ou itère des répertoires → `sbatch`.
- 🔴 **CHAQUE** soumission demande **minimum 7 jours** de walltime `-t 7-00:00:00` ; si MaxTime
  d'une partition < 7 j, demander le max de cette partition, jamais un cap court.
- **Autorisé login node** : `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `cd`, `ls`, `scp`,
  `module load`, `md5sum`, `tail`/`head`/`grep`/`wc -l`/`cat` sur fichier unique.
- **Commandes cluster = une seule ligne**, `cd`-first. Labelliser « localement » vs « sur le cluster ».
- **Monitoring : espacement min 30 min**, pas de boucle live. Préférer une **dépendance SLURM**
  (`--dependency=afterany:<jobid>`) à toute surveillance — ça enchaîne tout seul, sans personne.
  Modèles pas chers pour monitoring/polling/scan gros fichiers — jamais Opus ; sous-agents héritent
  Opus sauf modèle cheap explicite ; ne jamais scanner un gros fichier dans le contexte du manager.
- **Discipline pré-lancement (§6b) :** inventaire d'inputs md5-vérifié aux deux bouts AVANT lancement
  (scénario → fichier lu → md5 local == md5 cluster ; + injecteur + modules + les launchers
  eux-mêmes) ; complétude = **lignes ET mtime** ; single-writer.
- **Ne JAMAIS assouplir un seuil de gate** pour effacer un FAIL → relabel + documenter avec preuve.
- **Ne PAS modifier** les fichiers ML protégés : `eSim_datapreprocessing.py`,
  `eSim_dynamicML_mHead.py`, `eSim_dynamicML_mHead_alignment.py`.

---

## Docs de référence

- Runbook : `Step8_docs/3rdJ_08_simulation_4split.md` — §0 décisions verrouillées (dont OD-8R-L3),
  §2 sous-étapes, §4 matrice 56, §6b discipline, §7 probes, **§7b règle résidentielle**, §8
  agrégation dual-basis, §9 bandes EUI. **Progress Log = la source de vérité chronologique.**
- Validateur : `Step8_docs/3rdJ_08_simulation_4split_val.md` §P (définitions P1–P4 faisant foi).
- Injecteur : `eSim_bem_utils/commercial_integration.py` (md5 `5670f6026a91577126cd1329f60acb1a`).
- Générateur produit retail (à corriger) : `Step7_docs/3rdJ_07_aug_to_bem_4split.py`.
- Handoff employé des probes (modèle de spec réutilisable) :
  `Step8_docs/prompts/2026-07-28_employee_step8_probes_P1P4.md`.

---

## Style de communication

Casual, court (~100 mots sauf réponse technique ; la planification tolère plus long). Agir d'abord,
replier les caveats en une ligne après. **Vérifier les affirmations d'un Progress Log** — ne pas
croire un chiffre au pied de la lettre, re-dériver depuis les colonnes de l'artefact. Un agent
employé peut se tromper dans son propre rapport : un rapport a déjà affirmé à tort qu'une spec
était fautive, il a fallu corriger le journal.

## Premier geste attendu

1. Confirmer l'état ci-dessus (lire le Progress Log du runbook, entrées du 2026-07-28).
2. **Poser les deux questions en attente** : (a) vs (b) pour le `multiplier` retail, et
   faut-il vérifier le résidentiel colonne par colonne.
3. Une fois tranché : orchestrer la correction Step-7 → regénération des 3 bandes → re-simulation
   des cellules 1+3 → re-scorecard, en lançant les agents toi-même.

**Ne pas lancer la campagne 56 runs.** Elle reste bloquée derrière les points 1–3.
