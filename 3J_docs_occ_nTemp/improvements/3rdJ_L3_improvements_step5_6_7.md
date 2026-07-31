# 3J Leg-3 — Améliorations Steps 5 / 6 / 7 : document d'implémentation

**Créé le 2026-07-30.** Doc de référence autoportant. Il couvre **deux lots de travail** :

1. **Lot A — le biais de calibration Step-6** (bloquant, décidé par l'utilisateur le 2026-07-28) :
   rendre Stage B / Stage C0 bidirectionnels, re-valider Step-6, régénérer les produits 2030,
   cascader Step-7.
2. **Lot B — les améliorations de validation relevées par l'utilisateur le 2026-07-30** en relisant
   les rapports HTML de validation des Steps 5, 6 et 7 (10 points, ci-dessous).

Docs frères, à lire pour le contexte cluster / campagne :

- `Leg3_4-split/prompt-manager/2026-07-28_manager_step6_calibration_bias_then_campaign.md` — relais manager
- `Leg3_4-split/Step8_docs/3rdJ_08_implementation_improvements.md` — état verrouillé Step-8, règles cluster
- `Leg3_4-split/Step8_docs/3rdJ_08_simulation_4split.md` → `Progress Log` — chronologie faisant foi

---

## Aim

Éliminer les défauts qui rendraient les résultats **faux et silencieux** — numériquement plausibles
mais dépourvus du signal qu'ils prétendent porter — avant la campagne 56 runs, et rendre les
rapports de validation **lisibles et vérifiables** par un lecteur qui n'a pas écrit le code.

La campagne 56 runs reste **BLOQUÉE** jusqu'à la fermeture du Lot A.

---

## Règle de méthode (vaut pour tout ce document)

1. **Colonnes consommées, pas md5.** Colonnes réellement lues en aval : résidentiel
   `Occupancy_Schedule` + `Metabolic_Rate` ; bureau `AT_WORK_fraction` ; commerce `multiplier` ;
   hôtel `multiplier`.
2. **Une gate doit être vue en train d'échouer** — refabriquer le défaut, montrer qu'elle lève.
3. **Câblage au niveau IDF avant énergie** — jamais déduire un câblage correct d'un total plausible.
4. **Re-dériver, ne pas croire** — y compris les chiffres d'un Progress Log, y compris quand ils
   atteignent exactement la cible annoncée.
5. **Ne JAMAIS assouplir un seuil de gate** pour effacer un FAIL → relabel + preuve empirique.

---

## Registre des décisions — 2026-07-30

Chaque décision prise ce jour, avec la **preuve** qui la fonde, l'**option écartée**, et surtout
**ce qui la renverserait**. Une décision dont on ne sait pas dire ce qui l'invaliderait n'est pas une
décision, c'est une préférence.

### D-1 — Métrique de référence du Stage B : ancre **2022 seul**, **32 slots non-BIZ**

- **Preuve.** `run_stage_B():455` tire sa cible de `obs22` (`CYCLE_YEAR==2022`) et `:461-462` n'opère
  que sur `DDAY_STRATA==1 & LFTAG==1` ; `cap_band_stageB()` saute `BIZ_SET` en `:399-400`. La
  métrique doit coïncider avec l'ère de la cible **et** le périmètre du stage.
- **Écarté.** L'ancre tous-cycles (2005-2022, n = 14 237) : elle répond à « 2030 ressemble-t-il à la
  moyenne sur vingt ans ? », pas à « 2030 reproduit-il 2022 ? ». Écartée après que je l'ai moi-même
  utilisée à tort. Écarté aussi `all48` seul : c'est un mélange, prouvé par
  (32 × −0,92 + 16 × −4,05)/48 = −1,963 = le chiffre observé.
- **Renversé si** : on démontre que la cible du Stage B n'est plus tirée de 2022 seul, ou que le
  périmètre `BIZ_SET` change. Les deux sont des changements de code, donc détectables.
- **Réserve assumée.** Grader contre l'ancre qui a servi de cible est une mesure de **convergence**,
  pas d'exactitude. C'est légitime pour juger le correctif, et insuffisant pour juger le pipeline —
  d'où D-9.

### D-2 — Ancre week-end : **mise en commun samedi + dimanche**

- **Preuve.** SE samedi ±1,40 pp contre un biais retiré de 1,37 pp ; dimanche ±1,57 pp contre
  0,33 pp. Règle pré-enregistrée en §A.7 déclenchée. Pooling justifié par les données et pas
  seulement par commodité : 0,0716 vs 0,0778, écart 0,62 pp contre des SE de ~1,5 pp — indiscernables.
- **Écarté.** Cible purifiée par jour (échange un biais connu contre un bruit plus grand) ; cible
  semaine ajustée (introduit une hypothèse de report semaine→week-end non mesurée).
- **Résultat mesuré après application.** Samedi +1,03 → +0,22 pp ; dimanche +0,02 → −0,33 pp.
- **Renversé si** : un apport de diaires week-end réels fait tomber la SE par jour nettement sous le
  biais, ou si samedi et dimanche deviennent statistiquement distinguables.

### D-3 — R.1 / R.2 : re-spécification **bande-consciente**, tolérances inchangées

- **Preuve.** Pic de `shape` = levier exactement (0,900000 / 0,970000 / 1,050000) ; pic de
  `multiplier` = 0,95 × levier ; écart R.2 monotone en |levier − 1|. 2022 intact.
- **Ce n'est pas un assouplissement** : les gates gagnent en pouvoir (ils épinglent la survie du
  levier), les tolérances restent 1e-6 / 1e-4, et sur 2022 les tests se réduisent verbatim aux
  anciens.
- **Renversé si** : la normalisation cesse d'ancrer sur `at_retail_fraction_2030_base`.

### D-4 — R.7 : **lire l'artefact livré**, pas le dictionnaire de constantes

- **Preuve.** `:655` affecte depuis `RETAIL_LEVER_VALUE`, `:657` compare à `RETAIL_LEVER_VALUE` :
  tautologie `x == x`, le CSV n'est testé que par `exists()`.
- **Séparation voulue et rétablie** : R.1 = produit vs fichier de levier brut (cohérence interne),
  R.7 = produit vs constantes de design 0,90/0,97/1,05. Elles tombent sous des corruptions
  différentes — c'est la raison d'être des deux.
- **Leçon de méthode.** J'avais autorisé R.1 à rester indépendant du dict *parce que R.7 épinglait la
  valeur*. R.7 n'épinglait rien : déléguer la rigueur à un gate non audité peut laisser une propriété
  contrôlée par personne.

### D-5 — R.4 : statistique **facteur de charge** (moyenne/pic), pas ratio de pics

- **Preuve.** Ratio de pics = 1,000 systématique, y compris en 2022 (`QC=0,9500 AB=0,9500`) : la
  normalisation force l'égalité des pics par construction. La différence dominicale QC/AB vit dans la
  **forme**.
- **Pourquoi cette statistique.** Un rapport de deux quantités à la même échelle annule le facteur
  d'échelle : elle survit à toute renormalisation par groupe.
- **Résultat.** QC < AB dans les 4 produits ; 2030 Δ −0,0334 identique d'une bande à l'autre, donc
  bien invariant au levier. Cohérent physiquement (horaires dominicaux restreints au Québec →
  activité concentrée → facteur de charge plus bas).
- **Ce qu'elle ne détecte pas**, et qu'il faut donc laisser à d'autres gates : la position du pic
  (R.3) et le niveau (R.1/R.7).

### D-6 — M.2, bandeau PR, `4.secondary.retail` : **relabel + preuve, jamais le seuil**

- **M.2** : pic commerce QC-2022 à 16 h = comportement bimodal réel (0,950 contre 0,770 à 13 h) ; de
  plus QC est la région à correspondance **exacte** tandis qu'AB passe par un proxy Prairies — donc
  l'échantillon douteux est celui qui **passe**. WARN documenté, fenêtre inchangée (11-15 h), toute
  autre violation échoue toujours. La doc a été alignée sur le code, jamais l'inverse.
- **PR 83,3 %** : `PR=6` (territoires) n'a aucun donneur GSS — 24 lignes sur 30 273, rattrapées en
  Tier-3. **Mauvaise attribution** au bug Leg-2, pas mauvais seuil : bandeau reformulé, FAIL et seuil
  conservés, aucune exemption PR=6 ajoutée.
- **`4.secondary.retail`** : `js_divergence()` renormalise à somme = 1 avant comparaison, donc mesure
  une distorsion de forme ; à erreur absolue constante 0,005, le JS varie d'un facteur ~637 entre 2 %
  et 50 % de densité. Le commerce est ~42× plus creux que le domicile. **Aucun correctif pipeline** :
  le tableau était trompeur, pas faux.

### D-7 — W2 (Step 5) et W.* (Step 7) : `N/A` / PENDING assumés, pas des PASS

- **W2** : la strate hors-population-active est vide (`LFTAG ∈ {1,2}`), le taux retombe sur 0,0, le
  test est trivialement vrai → `N/A`. Cause amont non refermée sur une supposition :
  `eSim_dynamicML_mHead_alignment.py::data_alignment()` n'harmonise jamais `LFTAG`, le domaine vient
  d'encore plus haut — **intentionnalité non confirmable** depuis ce script.
- **W.1–W.6** : PENDING honnête (l'audit de câblage exige l'IDF v242), vérifié comme tombant en WARN
  et ne gonflant aucun compte de PASS. Laissés tels quels, mais explicitement étiquetés.

### D-8 — F.1 (branche 2030) : **remplacer**, priorité maximale de l'audit

- **Preuve.** `:949-961` : dictionnaire de chaînes en prose du 2026-07-23 → `_rec("pass", …)`
  inconditionnel → publié `CONFIRMED (build-session evidence)`. Aucun calcul à l'exécution.
- **Pourquoi c'est le plus grave.** Il certifie la **séparabilité des canaux**, socle du factoriel
  3×3×3 (~9 simulations par canal au lieu de 27 reconstructions). C'est le gate qui devrait attraper
  une violation de séparabilité, et il ne le peut pas.
- **Remède retenu.** Contrôle d'exécution : (a) structurel — les fichiers commerce/hôtel ne portent
  aucune colonne `BAND` ; (b) MD5 croisés entre bandes hors-axe. Preuves de session gardées **en
  commentaire** pour la provenance, jamais comme valeur de retour.

#### ✅ Exécuté le 2026-07-30 — et ce qu'il faut dire honnêtement du remplaçant

Le nouveau F.1 (`val.py:1019-1045`) calcule bien quelque chose à l'exécution, et il a été **vu
échouer** sur deux perturbations en mémoire (fausse colonne `BAND`, `s_t` corrompu). La tautologie
est morte. Mais **il prouve moins que ce qu'il remplace**, et il faut l'écrire :

| | Affirmation certifiée |
|---|---|
| Ancien F.1 (vide) | « rebâtir l'axe bureau laisse les fichiers commerce/hôtel **octet-pour-octet identiques** » |
| Nouveau F.1 (réel) | « aucune colonne `BAND` n'est atteignable par commerce/hôtel » + « le `s_t` hôtel est identique entre les 3 bundles » |

Le nouveau est une **condition nécessaire** de la séparabilité, pas une preuve. Une fuite par
*valeurs* — sans colonne `BAND` — passerait encore. La preuve forte reste la reconstruction
hors-diagonale (`--sens office` puis comparaison MD5 des fichiers commerce/hôtel), aujourd'hui
adossée à une observation manuelle du 2026-07-23 rétrogradée en commentaire de provenance.

**Décision.** Ne pas laisser cet écart ouvert : la ligne 2 (cascade Step-7) régénère de toute façon
les produits 2030 depuis le livrable promu `5aa74f44`. Elle **doit** donc inclure un build
`--sens office` hors-diagonale et la comparaison MD5 correspondante — la preuve forte coûte alors
presque rien, et la séparabilité cesse de reposer sur un souvenir de session. Reporté en ligne 2 de
l'ordre d'exécution, pas en dette.

**Note honnête sur le décompte.** Les rapports 2030 passent de « 53 PASS dont 5 vides » à
**51 de 52 réellement exercés** (seul `G.4` reste vide, laissé faute de statistique de substitution
non devinée — D-10). Le compte affiché baisse de 53 à 52 : ce n'est pas une régression, c'est ce
que coûte d'arrêter de compter des gates qui ne pouvaient pas échouer.

### D-9 — Biais génératif du décodeur : **hors périmètre calibration**, priorité relevée

- **Preuve, triangulée trois fois indépendamment.** Gate 4.1 : +8,91 / −10,99 pp en semaine.
  Taux de positifs (B.2.2) : domicile +5,16 pp, travail −6,74 pp. Slots BIZ16 (Lot A) : −4,05 pp,
  **identiques au bit** avant/après calibration.
- **Pourquoi la calibration ne peut pas le traiter.** `calibrate_C_4split.py` ne lit jamais
  `reconstructed_2022_diaries_4split.csv` ; et Stage B saute `BIZ_SET` par construction.
- **Correction de ma propre estimation** : −4,05 pp sur l'ancre 2022, et non les −13,02 pp que ma
  lecture tous-cycles avait produits. Ordre de grandeur trois fois plus petit, conclusion inchangée :
  c'est la composante dominante de l'écart `all48`.

### D-12 — Étendre le pooling week-end au canal **domicile** (Stage C1) — correction d'une incohérence de D-2

- **Déclencheur.** La re-validation de `_C_v2` fait passer les trois gates `5.2` (WD < WE domicile,
  une par bande) de FAIL à PASS : GSS 66P/15W/5F → **69P/15W/2F**. Excellent résultat — mais le
  mécanisme rapporté (« le pooling week-end ») est **faux**, et je l'ai tracé.
- **Mécanisme réel, mesuré.** C'est la **purification d'ancre sur le canal domicile, via le seul
  samedi** :

| Strate | domicile, pool contaminé | domicile, réel seul | décalage |
|---|---|---|---|
| Semaine | 70,04 % | 70,31 % | +0,26 pp |
| **Samedi** | 72,65 % | **81,19 %** (n = 103) | **+8,54 pp** |
| Dimanche | 77,13 % | 76,71 % (n = 105) | −0,42 pp |

- **La purification elle-même est solide** : +8,54 pp contre une SE domicile-samedi de **1,71 pp**,
  soit **5 σ**. Le pool contaminé était réellement biaisé, pas bruité.
- **Mais la cible purifiée *par jour* affirme quelque chose que les données ne soutiennent pas.**
  Domicile réel : samedi 81,19 ± 1,71 ; dimanche 76,71 ± 2,12 ; différence +4,48 pp, SE_diff 2,72,
  **z = +1,65** — non significatif. Et le sens compte : les cibles purifiées rendent le **samedi plus
  casanier que le dimanche**, ce qui inverse à la fois l'ordre du pool contaminé (72,65 < 77,13) et
  l'attente ordinaire. On inscrirait une inversion samedi/dimanche dans le livrable sur la foi d'un
  z = 1,65 mesuré sur une centaine de diaires.
- **Mon incohérence, corrigée.** J'avais poolé samedi+dimanche pour C0 (travail) exactement sur ce
  raisonnement, puis laissé C1 (domicile) par jour — alors que c'est le domicile qui porte le gros
  décalage. C'était arbitraire.
- **Décision.** Pooler aussi le domicile en C1 : cible 78,93 % sur n = 208, SE **1,37 pp** (contre
  1,71 / 2,12 par jour).
- **Attente pré-enregistrée** : la moyenne week-end est quasi inchangée — (81,19 + 76,71)/2 = 78,95
  contre 78,93 poolé — donc le pooling ne fait que **redistribuer entre samedi et dimanche**. Le gate
  5.2 (WD vs WE agrégé) **doit rester PASS** dans les trois bandes. S'il repasse FAIL, autre chose
  s'est produit et il faut le comprendre avant tout le reste.
- **Ce n'est pas cosmétique** : les horaires résidentiels sont émis **par Day_Type**, donc une
  inversion samedi/dimanche se propage dans les horaires bâtiment du samedi et du dimanche, puis dans
  l'énergie.

### D-11 — Promotion de `_C_v2` en livrable canonique : **critère PRÉ-ENREGISTRÉ**

> Écrit le 2026-07-30 **avant** que la re-validation Step-6 sur `_C_v2` ne rende son résultat.
> Motif : un critère écrit après coup s'ajuste à ce qui revient. C'est précisément le défaut qui a
> produit le « FAIL → PASS » flatteur du Lot A, et le reproduire ici serait impardonnable.

`_C_v2` (MD5 `36159935`, 111 024 lignes) **remplace** le canonique `_C` (`7c105ef3`) si et seulement
si les quatre conditions suivantes sont réunies :

1. **Aucun gate ne passe de PASS à FAIL.** Un nouveau FAIL n'est pas rédhibitoire en soi — il peut
   être le correctif exposant enfin quelque chose — mais il **suspend la promotion** jusqu'à ce que
   son mécanisme soit établi et écrit. Pas de promotion sur un FAIL non expliqué.
2. **Les 5 FAIL connus et acceptés-documentés restent les mêmes cinq**, avec le même mécanisme. S'ils
   changent de nature, l'acceptation antérieure ne les couvre plus et doit être re-instruite.
3. **L'amplitude inter-bandes reste ≥ 4,0 pp** (semaine-employés ; 4,82 avant, 4,48 après correctif).
   C'est le **signal même de la campagne** : un livrable mieux calibré mais dont l'axe WFH s'est
   aplati serait un recul déguisé en progrès.
4. **Le mutex tient à 0 conflit** à chaque stage et l'assert final passe.

**Si une condition manque** : `_C_v2` reste un livrable candidat, le canonique `7c105ef3` reste en
place, et la campagne reste bloquée. **Aucune promotion par défaut, aucune promotion pour avancer.**

#### Évaluation du 2026-07-30 sur le build `36159935` — **PROMOTION SUSPENDUE**

| Condition | Verdict | Preuve |
|---|---|---|
| 1 — aucun PASS → FAIL | ✅ | 0 nouveau FAIL, 0 nouveau WARN ; 3 gates bougent, tous FAIL → PASS |
| 2 — les 5 FAIL connus inchangés **de nature** | ✅ *(lecture d'intention)* | 3 des 5 (`5.2` ×3, classe WD ≥ WE) sont **résolus** ; les 2 restants (`4.1.home/work`) sont des constantes du job de backcast, structurellement indépendantes du livrable testé. Le critère visait à empêcher qu'un FAIL accepté ne **mute** en un autre défaut sous la même étiquette ; une résolution n'est pas une mutation. Écrit ici plutôt que réinterprété en silence. |
| 3 — amplitude inter-bandes ≥ 4,0 pp | ✅ | **4,48 pp** (contre 4,82 avant), re-dérivée par le manager |
| 4 — mutex 0 conflit | ✅ | 0 à chaque stage, assert final à 0 |

**Les quatre conditions sont remplies — et la promotion est néanmoins suspendue**, pour un motif
extérieur à la grille : **D-12**. Promouvoir maintenant canoniserait une inversion samedi/dimanche du
domicile que les données ne soutiennent pas (z = 1,65). La grille D-11 vérifie qu'un livrable ne
**régresse** pas ; elle ne vérifie pas qu'il n'inscrit pas une hypothèse non étayée. C'est une
lacune de mon critère pré-enregistré, pas une raison de l'assouplir : je la note ici et la promotion
attend le build post-D-12.

**Leçon à reporter sur les futures grilles** : ajouter une cinquième condition — *le livrable
n'affirme aucune structure que les données ne distinguent pas statistiquement*. Elle est ajoutée
comme **condition 5** ci-dessous et appliquée dès cette évaluation.

#### Évaluation du 2026-07-30 sur le build post-D-12 `5aa74f44` — ✅ **PROMOTION ACCORDÉE**

Le build `36159935` évalué ci-dessus est **abandonné** (jamais promu). Le candidat est désormais
`_C_v2` reconstruit après D-12, MD5 **`5aa74f44cd09a7afa9fa5418864956ed`**, 111 024 lignes.

| Condition | Verdict | Preuve — **re-dérivée par le manager sur l'artefact**, pas reprise du rapport |
|---|---|---|
| 1 — aucun PASS → FAIL | ✅ | Validateur Step-6 relancé par le manager sur `5aa74f44` : GSS **69P/15W/2F** (contre 66P/15W/5F pour `7c105ef3`). Aucun gate ne recule. |
| 2 — les 5 FAIL connus inchangés **de nature** | ✅ | Les 2 FAIL GSS restants extraits du rapport : **`4.1.home`** (MAD 0,0996 / niveau 8,91 pp) et **`4.1.work`** (MAD 0,1132 / niveau 10,99 pp). Ce sont les constantes du backcast 2022, transcrites du job 1133427 — elles ne lisent **pas** le livrable 2030. Les 3 autres (`5.2` ×3) sont **résolus**. |
| 3 — amplitude inter-bandes ≥ 4,0 pp | ✅ | **4,48 pp** {cons 21,03 / hybrid 18,18 / fullyhybrid 16,55}. L'axe WFH ne s'est pas aplati. |
| 4 — mutex 0 conflit | ✅ | **Vérifié par le manager sur les 5 329 152 cellules du livrable** : `H&W=0, H&R=0, W&R=0`. Pas repris de l'employé. |
| **5 — n'affirme aucune structure non distinguée** *(nouveau)* | ✅ | Écart samedi−dimanche du domicile dans le livrable : **−0,02 pp**. L'inversion à z = 1,65 est éteinte. |

**Contrôle pré-enregistré (D-12) — tenu.** J'avais écrit d'avance que le gate `5.2` devait **rester
PASS** dans les trois bandes, le pooling ne faisant que redistribuer entre samedi et dimanche.
Résultat mesuré :

| Bande | `7c105ef3` (avant) | `5aa74f44` (après) |
|---|---|---|
| conservative | WD 74,98 / WE 73,71 → **NON** | WD 74,93 / WE 76,85 → **OUI** |
| hybrid | WD 76,92 / WE 75,92 → **NON** | WD 76,86 / WE 78,90 → **OUI** |
| fullyhybrid | WD 78,15 / WE 77,82 → **NON** | WD 78,10 / WE 80,63 → **OUI** |

**Métrique de référence D-1 inchangée par D-12** : −0,92 pp (non-BIZ32, ancre 2022), identique au
build pré-D-12 — attendu, le Stage C1 ne touche jamais le travail en semaine. Le correctif Stage B
et le correctif week-end sont donc **orthogonaux**, ce qui est la propriété qu'on voulait.

**Ce que la promotion ne dit pas.** `BIZ16` reste à **−4,05 pp**, strictement inchangé par les deux
correctifs. C'est D-9, le biais génératif du décodeur, hors périmètre de la calibration. Promouvoir
`_C_v2` signifie « mieux calibré sur ce que la calibration contrôle », **pas** « Step 6 est exact ».

**Point non tranché, et qui doit l'être avant la promotion** : la métrique de référence D-1 est une
mesure de **convergence** (le livrable est gradé contre l'ancre qui a servi de cible). Elle valide le
correctif ; elle ne valide pas l'exactitude du pipeline, qui reste plombée par D-9. La promotion de
`_C_v2` ne doit donc **pas** être lue comme « Step 6 est exact » — seulement comme « Step 6 est
mieux calibré qu'avant sur ce que la calibration contrôle ».

### D-13 — Mécanique de la promotion : **repointer, jamais écraser**

- **Contrainte permanente de l'utilisateur** : ne jamais écraser le livrable Step-6 validé `_C`
  (`7c105ef3`). Une promotion par renommage (`_C_v2` → `_C`) la violerait, et détruirait la
  provenance du build sur lequel tous les rapports du 2026-07-23 ont été écrits.
- **Décision.** `7c105ef3` **reste sur disque, intact, sous son nom**. On déplace le *pointeur*, pas
  le fichier. Deux constantes changent, dans deux fichiers :
  - `3rdJ_07_aug_to_bem_4split.py:85-101` — `D2030` → `..._C_v2.csv`, `D2030_EXPECTED_MD5` →
    `5aa74f44`, plus `D2030_PREDECESSOR_MD5 = 7c105ef3` conservé explicitement.
  - `3rdJ_07_bemIntegration_4split_val.py:46-52` — les mêmes.
- **Rollback** = repointer ces deux constantes. Rien n'est perdu, rien n'est à reconstruire.
- **Durcissement 1 — l'allowlist H6.** Le gate H6 testait `"_C" in path.stem` : un test de
  sous-chaîne qui aurait accepté `..._C_scratch`, `..._C_tmp`, n'importe quel intermédiaire
  à demi construit portant `_C` quelque part. C'est **exactement la classe de gate qui ne peut pas
  vraiment échouer** qu'on est en train de nettoyer (§B.3.6). La promotion l'a donc **resserré** en
  un ensemble explicite (`D2030_ALLOWED_STEMS`), pas élargi.
- **Durcissement 2 — le verrou de lockstep.** `D2030_EXPECTED_MD5` était **déclaré dans le
  validateur et jamais lu** : une empreinte épinglée qui n'épinglait rien. Nouveau
  `assert_d2030_lockstep()` (`val.py:54-86`), appelé avant tout chargement, qui attrape deux
  pannes : (1) le fichier sur disque n'est pas le build épinglé ; (2) **le générateur et le
  validateur sont épinglés sur des builds différents** — c'est-à-dire un rapport qui certifierait
  un fichier dont les produits ne sont pas issus. C'est la forme même du défaut de rapport périmé
  (§B.3.0). Échec dur, pas ligne FAIL : si c'est faux, tout ce qui suit parle du mauvais fichier.
- **Preuve que le verrou peut échouer** (règle : un gate non vu échouer n'est pas un gate) —
  trois cas exécutés le 2026-07-30 :

| Cas | Attendu | Obtenu |
|---|---|---|
| nominal | pas de levée | `[LOCKSTEP PASS] ... 5aa74f44 matches generator + validator pins` |
| validateur épinglé sur le prédécesseur `7c105ef3` | `AssertionError` | ✅ `LOCKSTEP VIOLATION: generator pins 5aa74f44…, validator pins 7c105ef3…` |
| source générateur épinglée ailleurs | `AssertionError` | ✅ `LOCKSTEP VIOLATION: generator pins 01234567…` |

### D-14 — Séparabilité : **la preuve est structurelle**, et le test MD5 que j'avais commandé était vide

- **Mon erreur, d'abord.** J'ai fait exécuter en ligne 2 un test « hors-diagonale » : rebâtir avec
  `--sens office` puis vérifier que les fichiers commerce/hôtel restent identiques au bit. L'employé
  l'a exécuté honnêtement et a rapporté **identique partout, y compris sur l'axe visé**.
- **C'est précisément ce qui rend le test vide.** Si *rien* ne change nulle part, « hors-axe
  identique » est vrai trivialement, et le test ne distingue plus « inchangé parce que séparable »
  de « inchangé parce que rien n'a été rebâti ». Lecture du code (`:931-947`) : `--sens office` pose
  `retail_states, hotel_states = []` — les canaux hors-axe ne sont **jamais écrits**. Le test mesurait
  une propriété de *périmètre d'écriture*, pas de séparabilité. J'ai commandé un gate vide en
  auditant les gates vides.
- **La vraie preuve, et elle est plus forte.** Elle se lit dans les signatures :

| Constructeur | Signature | Références à `BAND` / `office` dans le corps |
|---|---|---|
| `build_retail_product_2030` | `(retail_scenario)` | **0** |
| `build_hotel_product` | `(monthly_rate_df, scenario_label)` | **0** |
| `build_office_multiplier` | `(df, band_label, lookup_df)` | 3 *(normal : c'est le canal porteur de l'axe)* |

  Le produit commerce est une **fonction pure de `retail_scenario`** : il n'existe aucun paramètre
  par lequel la bande bureau pourrait entrer. Idem hôtel, appelé `(rates, f"2030/{blabel}")` où
  `rates` vient de `hotel_multiplier_2030.csv`, indépendant du bureau. Ce n'est pas une corroboration
  empirique, c'est une **impossibilité de construction** — plus fort qu'un MD5, et non falsifiable
  par un run particulier.
- **Corroboration empirique quand même utile** : le rebuild depuis le livrable promu `5aa74f44`
  change le résidentiel (3 fichiers) **et** le bureau, et laisse les **6 fichiers commerce/hôtel 2030
  et les 4 fichiers 2022 identiques au bit**. Le livrable 2030 a changé ; commerce et hôtel ne l'ont
  pas vu. C'est le test que j'aurais dû commander d'emblée, et il est passé.
- **Conséquence** : le factoriel 3×3×3 (27 cellules analytiques depuis ~9 simulations par canal)
  tient sur une base structurelle, plus sur un souvenir de session du 2026-07-23.

### D-15 — `E.3` : la non-monotonicité `Office_Sales` **préexiste** et se tient sur l'axe de la campagne

- **Le fait.** Unique FAIL des trois rapports 2030. Fenêtre du gate (semaine, 9 h–17 h) :

| Archétype | conservative | hybrid | fullyhybrid | monotone |
|---|---|---|---|---|
| Office_Knowledge | 0,4571 | 0,4051 | 0,3509 | ✅ |
| Office_Public | 0,4725 | 0,3980 | 0,3681 | ✅ |
| **Office_Sales** | **0,4483** | **0,4630** | 0,3366 | ❌ **inversion −1,47 pp** |

- **Ce n'est pas un artefact de fenêtre.** Sur les 24 h de semaine : cons 0,2086 contre hybrid
  0,2113 — l'inversion tient. Par heure, elle est présente de 10 h à 15 h et **culmine à 17 h**
  (cons 0,1443 / hybrid 0,2214 / fully 0,1517, soit **+7,7 pp**). À 17 h, `conservative` est la bande
  la **plus basse des trois** — c'est une anomalie de *timing de départ*, pas de niveau.
- **Ce n'est pas nous.** Rapport archivé d'avant la cascade : cons 0,4472 / hyb 0,4616 — déjà FAIL,
  même forme. La re-calibration Step-6 déplace les valeurs de ~0,1 pp et ne touche pas le
  phénomène. **Ni causé ni corrigé par les correctifs de calibration** — même classe que D-9.
- **Pourquoi ça compte quand même** : `Office_Sales` est un des trois archétypes de l'axe bureau, et
  l'axe bureau est un des trois axes du factoriel. La non-monotonicité **ne casse ni la séparabilité
  ni l'arithmétique** des 27 cellules — elle casse la *lecture* : pour ce seul archétype, « plus de
  télétravail » ne réduit pas monotonement la présence au bureau entre `cons` et `hybrid`.
- **Décision.** Ne pas relâcher le gate — il fait exactement son travail. Investiguer le mécanisme
  **avant d'interpréter** la campagne. La campagne elle-même n'est pas bloquée par ce défaut
  (2,6–3,5 h en local, ré-exécutable), mais publier une lecture de l'axe bureau sans l'avoir compris
  le serait.

#### D-15 — RÉSOLU le 2026-07-30 : bruit d'échantillonnage, **et l'axe reste lisible pour Sales**

Diagnostic livré, puis **re-dérivé intégralement par le manager** depuis les artefacts
(`scratchpad/verify_d15_sales.py`, `verify_d15_addendum.py`). Tous les chiffres de l'employé se
confirment au centième près. Deux points lui échappent, dont **une erreur que j'avais moi-même
écrite ci-dessus**.

**Le mécanisme, vérifié à la source.** `office_archetype_lookup.csv` fait correspondre **NOCS 6 →
`Office_Sales` seul** (contre {1,2} pour Knowledge, {3,4,5} pour Public) : pas de catégorie
fourre-tout, juste le seau le plus étroit. D'où **n = 201** en semaine contre 1 928 et 1 994 — un
facteur 10. Et le contenu du diaire de chaque ligne vient du donor-swap Step-6
(`3rdJ_06_longitudinalForecasting_4split.py:1915-2025`), stratifié sur **emploi + classe WFH +
AGEGRP uniquement** — vérifié ligne à ligne : **`NOCS` n'entre jamais dans l'appariement**, par
conception documentée (« TELEWORK conditioning is NOT a learnable lever »). L'étiquette
d'archétype est donc apposée **après** l'affectation du diaire : les trois archétypes sont trois
sous-échantillons d'**une seule distribution aveugle à la profession**.

**Corroboration indépendante du mécanisme** (angle non utilisé par l'employé) : si l'injection est
aveugle à la profession, les trois archétypes doivent partager la **même pente de bande**. Test de
tendance (bandes codées 0/1/2, fenêtre du gate) :

| Archétype | n | cons − hyb | hyb − fully | cons − fully | **pente / bande** | z(pente) |
|---|---|---|---|---|---|---|
| Office_Knowledge | 1 928 | +5,21 (z=+3,68) | +5,42 (z=+3,85) | +10,62 (z=+7,58) | **−5,31 pp** | −7,55 |
| Office_Public | 1 994 | +7,45 (z=+5,36) | +3,00 (z=+2,16) | +10,45 (z=+7,50) | **−5,22 pp** | −7,52 |
| **Office_Sales** | **201** | **−1,46 (z=−0,33)** ❌ | +12,63 (z=+2,91) | +11,17 (z=+2,59) | **−5,58 pp** | **−2,56** |

Les trois pentes sont **statistiquement indiscernables** (−5,31 / −5,22 / −5,58). C'est exactement
ce que prédit l'injection aveugle à la profession, et ça ferme le mécanisme.

**La nuance que le rapport sous-estime.** L'employé conclut « Sales n'a pas l'échantillon pour
résoudre l'effet ». C'est trop faible. Sales **résout l'effet de bout en bout** : `cons − fully`
z = +2,59, tendance z = −2,56, tous deux significatifs. Ce qui n'est pas résolvable à n = 201, c'est
le **seul pas adjacent** `cons`/`hybrid`. Conséquence pour la campagne : **l'axe bureau est
interprétable pour les trois archétypes**, y compris Sales, avec une amplitude commune d'environ
−5,4 pp par bande. Seul l'ordonnancement fin de deux bandes voisines est hors de portée.

**🔴 Correction d'une affirmation écrite plus haut dans ce même D-15.** J'avais écrit que
l'excursion à 17 h était « une anomalie de *timing de départ*, pas de niveau ». **C'est faux.** À
17 h, la population bureau **agrégée** est plate : 0,1667 / 0,1689 / 0,1692 — il n'existe aucun
signal de bande à cette heure-là, pour personne. Et les **trois** archétypes y sont non monotones,
Knowledge et Public compris. Le +7,7 pp de Sales est une excursion de petit échantillon sur une
heure sans signal, pas une anomalie de départ. Ce qui sauve Knowledge et Public dans `E.3`, c'est la
moyenne sur la fenêtre 9 h–17 h avec un n dix fois plus grand — pas une meilleure tenue horaire.

**Ce que ça apprend au passage** (utile au manuscrit) : le levier de bande bureau déplace le
**niveau du plateau** diurne, pas la **forme** de l'horaire — la rampe de fin de journée est
insensible à la bande. À retenir pour l'interprétation énergétique de l'axe bureau.

**Contrôle que le manager a ajouté** : l'employé teste en **non apparié**. Si les trois bandes
contenaient les mêmes personnes, le test correct serait **apparié** et le verdict pouvait basculer.
Vérifié : SE appariée 4,36 pp contre 4,40 pp non appariée — l'appariement n'apporte rien (le
donor-swap re-tire le diaire entier, la corrélation intra-personne est nulle). **Le verdict tient
sous les deux tests.**

**Verdict : bruit d'échantillonnage indiscernable de zéro** (|z| = 0,33 sur le pas incriminé), ni
défaut de modélisation, ni effet de composition réel. **Aucun script, lookup ou seuil n'a été
modifié.**

**Disposition.** `E.3` reste **FAIL accepté-documenté**, au même titre que les autres FAIL acceptés
de ce document — **le seuil n'est pas relâché** (règle permanente). Le défaut réel n'est pas la
valeur : c'est que **`E.3` chaîne des comparaisons adjacentes sans tenir compte de la puissance**,
donc il échouera à chaque re-tirage sur l'archétype à n = 201, quel que soit l'état du pipeline. Un
gate correct testerait la **tendance** (que les trois archétypes passent, Sales à z = −2,56) ou
porterait une tolérance fonction du SE. **Non appliqué** : c'est une révision de définition de gate,
elle demande sa propre instruction et ne doit pas être glissée dans une cascade de calibration.

### D-16 — Le motif de la re-simulation des probes était faux (rectifié)

Écrit en ligne 10 depuis le début : « `INJ_HASH` a changé, `campaign_5670f602/` périmé ». **Les deux
moitiés sont fausses, et la conclusion reste juste** — mauvaise raison, bonne action. Rectifié avant
de lancer quoi que ce soit.

- **`INJ_HASH` ne dépend pas de Step-7.** `INJ_HASH = md5(commercial_integration.py)[:8]` et il
  **possède le chemin de sortie** (`3rdJ_08P_probe_driver.py:35-48`). Une reconstruction de produits
  Step-7 ne le déplace pas — c'est le « trou d'empreinte » (Défaut 3) déjà fermé le 28/07 par un
  **`INPUTS_HASH` séparé**, md5 des CSV Step-7 réellement lus par la cellule. Ce qui a bougé
  aujourd'hui, c'est `INPUTS_HASH`, pas `INJ_HASH`.
- **`INJ_HASH` a bien changé — mais pour une autre raison, et avant nous.** `5670f602 → cf69d508`,
  provoqué le 28/07 par le correctif `classify_tag2()` résidentiel/résidentiel-commun d'une session
  concurrente (`3rdJ_08_simulation_4split.md:1675-1679`). C'est un changement de **câblage**, pas de
  produit.
- **Conséquence réelle, plus forte que celle que j'avais écrite.** Le scorecard §P clos à
  **25P/0W/0F** le 28/07 a été produit **sur le cluster** avec l'injecteur `5670f602`. Il est
  périmé pour **deux** motifs indépendants : injecteur différent (`cf69d508`) *et* produits Step-7
  différents (`_C_v2`). Une seule des deux raisons aurait suffi ; je n'avais noté ni l'une ni
  l'autre correctement.
- **Ce qui change concrètement** : les résultats cluster vivent sous `campaign_5670f602/`, la
  re-simulation sous `campaign_cf69d508/` — **les chemins se séparent d'eux-mêmes**, aucun risque
  d'écrasement, et l'arborescence enregistre la divergence. Le seul répertoire présent sous
  `cf69d508` était déjà archivé en `_STALE_20260728_205116`. Dry-run : **7 cellules à faire, 0
  sautée**. Pas besoin de `--allow-stale-inputs` — le garde ne se déclenche pas sur un répertoire
  neuf.

**Ce que ça coûte de ne pas vérifier un motif** : rien ici, par chance. Mais un motif faux se
propage — s'il avait dit « seul `INPUTS_HASH` a bougé », on aurait pu croire le câblage inchangé et
sauter la re-validation du canal résidentiel, précisément celui que `classify_tag2()` touche.

### 🔴 D-19 — `inject_residential()` n'avait jamais tourné, et le smoke test enregistré donnait une fausse assurance

Trouvé en poursuivant un simple `INFO` du scorecard : `P1 residential -- NOT EXERCISED`.

**Ce que le harnais de probes fait, et pourquoi ce n'est pas un défaut.** Le résidentiel est **hors
périmètre par conception** côté probes (`3rdJ_08P_probe_driver.py:12-14` : « residential is OUT […]
the injector already skips residential Tag-2 unconditionally »). D'où
`Injected PEOPLE: office=6 retail=0 hotel=3` dans **toutes** les cellules de probe : conforme, pas
cassé. **Les probes ne peuvent donc structurellement pas valider le canal résidentiel** — le sujet
même de la recherche.

**Ce qui rendait la situation dangereuse.** Côté campagne, `3rdJ_08D_campaign_cells.py:14-20` note
que le résidentiel « was never wired in, so every cell would have run with the 27 residential
apartment Spaces at NECB baseline, **silently omitting the entire subject of the research** » — puis
l'implémente. Mais le **smoke test consigné au Progress Log** (`n_spaces` office 6 / retail 3 /
hotel 3, 28/07 20:41) **précède** ce câblage (`_campaign_cells.py`, 20:51). Un lecteur du journal y
lit « chaîne complète prouvée de bout en bout » — la phrase est exacte à la date où elle a été
écrite, et **fausse pour le code d'aujourd'hui**. C'est la version « artefact » du problème des
gates vides : une preuve valide qui survit à ce qu'elle prouvait.

**Vérification faite avant de lancer quoi que ce soit de long** (smoke campagne, 0,8 min) :

| Contrôle | Résultat |
|---|---|
| Canaux demandés | `['office', 'retail', 'hotel', 'residential']` — les 4 |
| `residential.n_spaces` | **27** |
| `n_households_drawn` | **27** — soit **un ménage distinct par Space**, conforme à OD-8R-L3 (graine 42) |
| Horaires créés | **54** = 27 × (`MXU_Residential_Occ_HH*` + `MXU_Residential_Met_HH*`) |
| `n_carriers_neutralized` | 1 — le correctif « 2J Bug A » (porteur par zone) est actif |
| `fallback` / `ambiguous` | `[]` / `[]` |

**§B (injecteur résidentiel OD-8R-L3) est CLOS** — et la doc Step-8 qui le dit « spécifié, non
implémenté », ainsi que la mémoire de projet, étaient périmées. **La campagne n'est plus bloquée par
§B.**

**Leçon à garder** : un run de fumée n'atteste que du code au moment où il tourne. Quand le câblage
change après coup, la preuve consignée devient un piège — d'autant plus efficace qu'elle est
authentique. Ici, l'écart entre les deux était de **dix minutes**.

### D-18 — `P4 banner` : un gate qui échouait sur sa propre résolution de fichier

Le scorecard §P relancé le 30/07 sort **31P / 0W / 1F**. L'unique FAIL :
`P4 banner -- no SLURM log matched 8P_probe_*_6.out`.

**Ce n'était pas le comportement testé qui échouait.** Le gate vérifie que la bannière de repli
`!!! FALLBACK` est *imprimée bruyamment* dans le log d'exécution — un second témoin, indépendant du
manifeste, que le canal commerce est bien retombé sur la base NECB. Vérifié dans le log local
(`_logs/fallback_retail.log:173,177,179`) : la bannière **est** présente, avec
`Injected PEOPLE: office=6 retail=0 hotel=3; fallback=['retail']`. Le gate globait en dur le nom de
fichier **SLURM**, qui n'existe que sur le cluster ; l'orchestrateur Windows écrit `<tag>.log`.
Même classe que le gate `PLATFORM` ajouté pendant le portage — **un trou de portage, pas un défaut
de pipeline**.

**Correctif : le glob seulement.** `log_pattern = "8P_probe_*_6.out" if engine == "cluster" else f"{CELL_TAGS[6]}.log"`.
L'assertion (`"!!! FALLBACK"` doit apparaître dans le log) est **inchangée** — donc **aucun seuil
n'est assoupli**, seule change la question « quel fichier lire ». La distinction est la même que
celle appliquée à R.1/R.2 et R.7 : réparer ce qu'un gate *regarde* est légitime, déplacer ce qu'il
*exige* ne l'est pas.

**Vu passer ET vu échouer** (règle permanente — un gate seulement vu passer est un gate non testé) :

| Épreuve | Résultat |
|---|---|
| Log réel (bannière présente) | ✅ PASS — `banner found in _logs/fallback_retail.log` |
| Log privé de sa seule ligne bannière | 🔴 **FAIL** — `'!!! FALLBACK' banner NOT found` |
| Log restauré | md5 `63f582aa…` **identique à l'original** (aller-retour vérifié) |

**Scorecard final : 32P / 0W / 0F / 10 INFO** — contre 25P/0W/0F sur le cluster le 28/07. Les 7
points de plus ne sont pas de la complaisance : 6 gates `INPUTS_HASH` (le correctif du Défaut 3)
sont désormais réellement exercés, plus ce P4 réparé.

### D-17 — L'échelle de composition de l'axe époque est un **choix de construction**, pas une propriété de la donnée

Contrôle pré-campagne exigé par le §C de `3rdJ_08_implementation_improvements.md` (« vérifier que les
colonnes *consommées* diffèrent entre scénarios, pas seulement les md5 » — la leçon du Défaut 1).
Exécuté le 30/07 sur les produits historiques 2005/2010/2015.

**Résultat du §C : l'axe époque est VIVANT.** Colonnes réellement lues par l'injecteur —
`AT_WORK_fraction` pour le bureau (`commercial_integration.py:315-316`), `multiplier` pour le
commerce (`:330`) et l'hôtel (`:345-346`) — et non `multiplier` pour le bureau, contrairement à ce
qu'on pourrait supposer :

| Canal | Colonne consommée | Paires d'époques testées | Lignes différentes | max\|Δ\| |
|---|---|---|---|---|
| Bureau | `AT_WORK_fraction` | 6/6 | 143–144 / 144 | 0,052–0,092 |
| Commerce | `multiplier` | 6/6 | 154–156 / 288 | 0,458–0,758 |

(Le commerce ne bouge que sur ~la moitié des créneaux : les 132/288 forcés à `0,0` par
`staff_shoulder_flag` sont constants par construction — point ouvert n° 1, cohérent.)

**Résidentiel — même contrôle, même verdict.** Profil moyen sur les 48 bins `Day_Type × Hour`,
colonne consommée `Occupancy_Schedule` : **48/48 bins diffèrent** sur les 6 paires d'époques,
max\|Δ\| **0,046–0,095**. Les 4 époques ont la même taille (1 109 520 lignes, 23 115 ménages) et des
moyennes annuelles quasi identiques (0,6833 / 0,6784 / 0,6824 / 0,6833) : **le signal d'époque est
dans la forme, pas dans le niveau** — exactement le principe du §1 (« la forme de charge est la
contribution »). Un contrôle sur les totaux annuels aurait conclu à un axe mort. **Les trois canaux
de l'axe époque sont vivants.**

**Les produits historiques ne sont PAS périmés.** `3rdJ_08A_gen_historical_products_4split.py:359`
lit `step7.AUG` — la trame **observée Step-5**, filtrée par `CYCLE_YEAR` — et **jamais** le livrable
Step-6 calibré. La correction `_C_v2` ne les atteint donc pas : aucune régénération requise.

**Le raffinement.** Le Défaut 4 décrit une échelle `0 % → 44,6 % → 100 %` de diaires synthétiques le
long de l'axe époque. C'est exact — et j'ai mesuré d'où vient chaque barreau. Dans la **trame
elle-même**, la part synthétique est **plate** sur les quatre cycles :

| CYCLE_YEAR | lignes | synthétiques | part |
|---|---|---|---|
| 2005 | 9 488 | 4 304 | **45,4 %** |
| 2010 | 7 040 | 3 077 | **43,7 %** |
| 2015 | 7 414 | 3 302 | **44,5 %** |
| 2022 | 5 560 | 2 473 | **44,5 %** |

Le `0 %` des époques 2005/2010/2015 **n'est pas dans la donnée** : il vient du filtre
`IS_SYNTHETIC == 0` appliqué délibérément en `:228` (choix documenté — l'étape `rake_cycle()` de
Leg-2, qui récupérait aussi les lignes synthétiques, n'a **pas** été portée). Or le produit **2022**
de Step-7 est construit **sans ce filtre**. Donc :

🔴 **À l'intérieur même du bras historique de la campagne, les époques ne sont pas construites de la
même façon** : 2005/2010/2015 sur des pools 100 % observés, 2022 sur un stock à 44,5 % synthétique.
Ce n'est pas un écart de donnée, c'est un écart de **filtre**. Le seul barreau irréductible est
2030 (100 % synthétique par construction — c'est une prévision).

**Décision : ne rien changer maintenant, et ne pas laisser passer non plus.** Harmoniser (filtrer
2022 comme les autres) rendrait le bras historique homogène en composition, mais **invaliderait** le
produit 2022, son rapport Step-7 fraîchement régénéré et la cellule de probe `cycle_2022`. C'est un
arbitrage de méthode, pas une correction de bug : il revient à l'utilisateur, pas à une cascade
technique. Inscrit en ligne 12bis. **La campagne peut tourner sans** — cette échelle affecte la
*lecture* de l'axe époque, exactement comme D-15 affecte celle de l'axe bureau.

### D-20 — Le canal résidentiel pilote **les personnes seulement** ; les trois canaux commerciaux pilotent aussi éclairage et prises

Trouvé en vérifiant la cellule Calgary — non pas dans le manifeste, qui est propre, mais dans les
**colonnes du produit horaire**. Le nombre de valeurs distinctes sur l'année trahit le câblage :

| Canal | `_people` | `_lights` | `_equip` | Lecture |
|---|---|---|---|---|
| office | 46 | 3593 | **46** | equip suit exactement l'occupation |
| retail | 37 | 2651 | **37** | idem, à l'unité près |
| hotel | 192 | 4058 | 156 | idem |
| **residential** | **33** | **12** | **5** | **ne suit pas** — niveaux NECB de base |

L'égalité `nuniq(people) == nuniq(equip)` sur office et retail est la signature d'un canal
MODULATE ; le résidentiel ne l'a pas. Confirmé à la source : `inject_residential()` n'émet que des
objets PEOPLE, et son dict de retour n'a même pas de clés `n_lights` / `n_equip`
(`commercial_integration.py:588`) — là où les trois canaux commerciaux en ont.

**Ce n'est pas un défaut.** C'est `OD-7D`, verrouillé et documenté dans le docstring : *« LIGHTS/
ELECTRICEQUIPMENT for residential Spaces are NOT touched — no Step-9 equipment/lighting columns
exist in the Step-7 residential product; deferred »*. Prémisse vérifiée sur l'artefact : le produit
résidentiel est à **13 colonnes**, `Occupancy_Schedule` et `Metabolic_Rate` en tout et pour tout.
Et vérifié aussi sur Leg-2 — **schéma identique**, donc pas une régression entre jambes ; le chiffre
« 17 colonnes » qui traîne dans les notes est de lignée 2J et ne s'applique pas au 3J.

**Décision : ne rien changer, et l'inscrire comme réserve de manuscrit.** La conséquence est une
**asymétrie de voies**, pas une erreur : l'occupation commerciale atteint l'énergie par trois
chemins (métabolique → CVC, éclairage, prises), l'occupation résidentielle par **un seul**
(métabolique → CVC). Toute comparaison inter-canaux de la *sensibilité énergétique à l'occupation*
est donc structurellement défavorable au résidentiel — qui est le sujet de la thèse. À énoncer
explicitement avant de comparer les canaux entre eux ; les comparaisons **intra-canal** (bandes,
villes, époques) ne sont pas touchées, l'asymétrie y est en mode commun.

### D-14 — RENFORCÉE le 2026-07-30 : la séparabilité est aussi prouvée empiriquement

D-14 concluait à une preuve **structurelle** (signature + zéro référence à `BAND`) après l'échec du
test vide. Il restait une faille que la structure seule ne ferme pas : un **état global** (une frame
mise en cache au niveau module, dérivée du livrable 2030) contournerait la signature.

Les mtimes la ferment. Les 6 produits commerce/hôtel 2030 ont été **réellement réécrits** par la
cascade (`19:17–19:18`, pas sautés) à partir d'un livrable résidentiel **modifié** — et ressortent
**identiques au md5** de leurs sauvegardes pré-cascade :

| Produit 2030 | md5 après cascade | md5 pré-cascade |
|---|---|---|
| `hotel_..._central` / `_cons` / `_opt` | `4b3d3a46` / `d6e834ba` / `e0ab6c86` | identiques |
| `retail_..._central` / `_cons` / `_opt` | `cf8721c6` / `0e3b256e` / `f7152e5a` | identiques |

**Les deux preuves portent sur des choses différentes** : la structure exclut une dépendance
*déclarée*, la réécriture exclut une dépendance *cachée*. Ensemble elles fondent le factoriel
3×3×3. C'est ce que le test vide prétendait faire et ne faisait pas.

### D-10 — Triage sans deviner (A.12, B.4, H.5, G.4)

Correction **seulement** là où l'intention du gate est sans ambiguïté dans le code ou la doc
environnante ; sinon, rapport et question ouverte. **Quatre questions ouvertes honnêtes valent mieux
qu'un gate plausible et faux** — c'est exactement le défaut qu'on est en train de réparer, et le
reproduire en le réparant serait absurde.

---

# LOT A — Biais de calibration Step-6 (🔴 bloquant)

## A.1 Le défaut, mesuré

La fraction de diaires `IS_SYNTHETIC == 1` monte de façon monotone **le long de la séquence
temporelle même que la campagne compare** :

| Époque | Fraction synthétique | Origine |
|---|---|---|
| 2005 / 2010 / 2015 | **0 %** | filtre observé-seulement dans `3rdJ_08A_gen_historical_products_4split.py` |
| 2022 | **44,6 %** | `cmd_year_2022()` lit le stock Step-5 sans filtre |
| 2030 (3 bandes) | **100 %** | produit synthétique Step-6 par construction |

Et les diaires synthétiques sous-déclarent la présence au travail. La calibration **ne corrige pas
ce biais, elle l'amplifie** :

| Comparaison | Δ work-presence | Cohen's d |
|---|---|---|
| Pré-calibration, SYN2022 vs OBS2022 | −5,82 pp | −0,324 |
| **Post-calibration, livrable 2030 `_C` vs OBS2022** | **−10,51 pp** | **−0,649** |
| Post-calibration vs observé historique (2005/10/15) | −15,32 pp | −0,938 |
| Par bande vs OBS2022 : cons / central / opt | −9,25 / −10,60 / −11,67 pp | −0,55 / −0,65 / −0,75 |
| **Écart ENTRE bandes** (le signal WFH mesuré par la campagne) | **~2,4 pp** | — |

**Le biais vaut 4 à 5 fois le signal.**

## A.2 Le mécanisme — lu dans le code, pas déduit

`Leg3_4-split/Step6_docs/3rdJ_06_calibrate_C_4split.py` :

| Étage | Fonction | Garde unidirectionnelle |
|---|---|---|
| Stage B (semaine) | `cap_band_stageB()` **:328-365** | **:341** `if rate <= target[t]: continue` |
| Stage C0 (week-end) | `run_stage_C0()` **:409-444** | **:427** `if p_30 <= p_obs + 1e-9: continue` |

Les deux sont des **écrêtages unidirectionnels** : ils ne font que *réduire* l'excès de travail vers
la cible, **jamais relever un déficit**. Le modèle synthétique sous-produisant déjà du travail, aucun
étage de la chaîne ne peut corriger dans ce sens. Le domicile n'est corrigé bidirectionnellement
qu'en week-end (Stage C1) ; en semaine il ne monte que par effet de bord des trims de travail, et ne
redescend jamais. **C'est structurel, pas incident.**

*Confirmé indépendamment par le manager le 2026-07-30 en relisant `:315-444` — les deux gardes sont
bien présentes et strictement `continue`-on-deficit.*

Point secondaire, réel mais mineur : l'ancre « observé 2022 » (`IN_B`, **:113-114**, **:671-677**) est
chargée via `obs_full[obs_full["CYCLE_YEAR"]==2022]` **sans filtre `IS_SYNTHETIC`**, donc contaminée
par les 44,6 % de synthétiques 2022. Effet mesuré : **−2,59 pp seulement**. Le moteur dominant est
l'asymétrie d'écrêtage. **Corriger l'ancre seule ne suffira pas.**

## A.3 Ce que le biais casse, et ce qu'il ne casse pas

Le biais est **quasi identique sur les trois bandes** — c'est un décalage d'ordonnée à l'origine, pas
une erreur qui différencie les scénarios.

- ✅ **Axes bandes et sensibilités (9 scénarios sur 14) : INTACTS.** Le mode commun s'annule dans les
  différences bande-à-bande.
- 🔴 **Axe temporel (2005/2010/2015/2022 vs 2030) : CONTAMINÉ.** Une courbe « présence au travail
  2005→2030 » montrerait un déclin partiellement fabriqué par la construction — c'est-à-dire le récit
  WFH lui-même, revendication centrale du papier.

## A.4 Précédent Leg-2 — pourquoi la question ne s'était jamais posée

Leg-2 a **architecturalement contourné** le problème : `3rdJ_08A_gen_historical_schedules.py`
(**:495**) part d'un stock observé-seulement `aug[(CYCLE_YEAR==2022)&(IS_SYNTHETIC==0)]` et applique
un rake **bidirectionnel** « Phase-8B » (docstring **:9-19**) qui bascule les lignes synthétiques vers
les marginales observées *avant* assemblage. Leg-2 n'a donc jamais mélangé de contenu synthétique dans
sa comparaison historique↔2022.

Le mécanisme général était documenté (`Leg2_2-split/Step5_docs/3rdJ_05_censusLinkage_2split_val.md`
**:338**, **:340**, **:398** — « IS_SYNTHETIC dilution effect »). La **conséquence spécifique** ne l'a
jamais été. Et `Leg2_2-split/investigation/TICKET_cross_era_pairing_defect.md` **:40-42** affirme
« chaque scénario reste non biaisé en absolu » — **affirmé, jamais mesuré. Ne pas s'appuyer dessus.**

## A.5 Le correctif — spécification

Rendre Stage B et Stage C0 **bidirectionnels** : quand `rate < target`, *relever* le déficit au lieu
de `continue`.

Contraintes non négociables :

- **Mutex.** `check_mutex()` / `resolve_and_assert_mutex()` doit renvoyer **0 conflit à chaque étage**.
  C'est le rake par-colonne indépendant de Leg-2 qui avait causé le bug `hom30`/`wrk30` — toute
  opération de lift doit choisir ses lignes candidates en respectant l'ordre de mutex
  **work > retail > home**, et ne jamais poser `wrk30=1` sur un slot où `ret30=1`.
- **Cohérence de bloc.** Le trim existant privilégie les *queues* de bloc de travail (`trail`, puis
  `lead`, puis n'importe qui). Le lift doit être son symétrique : étendre un bloc existant par sa
  queue/tête avant de créer un bloc isolé, sinon on fabrique des motifs de travail non physiques
  (heures de travail orphelines au milieu d'une journée à domicile).
- **Colonne `ACT`.** Le trim remet `ACT` à `SLEEP`/`PASSIVE` selon `NIGHT` (**:362-363**). Le lift doit
  faire l'inverse : poser `WORK_ACT_0IDX` sur les slots relevés, sinon `AT_WORK_fraction` et le canal
  activité divergent.
- **Déterminisme.** Même `rng` (graine 42), même ordre de parcours. Reproductibilité bit-à-bit exigée
  sur deux exécutions.
### Template confirmé — Stage C1 (`run_stage_C1`, `:452-509`)

Stage C1 **est** déjà bidirectionnel : c'est le patron exact à recopier.

| Élément | Ligne | Comportement |
|---|---|---|
| Écart par slot | `:471` | `diff = p_obs - p_30`, **recalculé à frais, jamais mis en cache** |
| Branche UP | `:474-485` | candidats **restreints à l'état OUT** `(hom==0) & (wrk==0) & (ret==0)` → bascule vers HOME |
| Branche DOWN | `:486-496` | candidats `(hom==1) & (wrk==0)` → bascule vers OUT |

### 🔴 L'invariant mutex — la ligne à ne pas franchir

`resolve_and_assert_mutex()` est défini `:168-213` et appelé **après chaque étage** : `:403` (B),
`:446` (C0), `:509` (C1), `:569` (Retail), `:632` (C2), `:701` (GlobalMindwell). Priorité
**work > retail > home** (`:186-198`), avec un `assert` dur à 0 conflit résiduel (`:209-213`).

**Invariant obligatoire pour toute opération de lift : ne recruter les candidats que depuis l'état
OUT** — `(hom==0) & (wrk==0) & (ret==0)` — **avant** de poser un canal à 1. C'est exactement ce que
font déjà les branches UP de C1 et de l'étage Retail.

Si un lift travail Stage B/C0 saute cette restriction, la résolution de priorité *a posteriori*
écrasera silencieusement la comptabilité du lift lui-même — et **reproduira la classe de bug mutex
`hom30`/`wrk30` de Leg-2** (`:44-55`). C'est le piège nº 1 de ce correctif.

## A.6 Preuve exigée — un correctif non mesuré n'est pas un correctif

1. **Avant/après sur le défaut connu** : re-mesurer Δ work-presence du livrable 2030 vs OBS2022 et
   montrer que l'écart **s'est effondré** (cible : |Δ| ramené sous l'écart entre bandes ~2,4 pp, donc
   le signal redevient dominant).
2. **La gate vue en train d'échouer** : refabriquer l'asymétrie (remettre le `continue`) et montrer
   qu'une gate lève.
3. **Mutex 0 conflit** à chaque étage, imprimé.
4. **Déterminisme** : deux runs, md5 identiques.
5. **Re-validation complète Step-6** (le livrable `_C` actuel : MD5 `7c105ef3`, 111 024 lignes,
   GSS 66P/15W/5F) — puis **cascade Step-7** (produits 2030) et **Step-8** (`INPUTS_HASH` change →
   re-simulation).

## A.7 Purification de l'ancre 2022 — REQUALIFIÉE le 2026-07-30

**Ce n'est plus une option « à −2,59 pp ».** La mesure par strate (§B.2.3) change la donne :

| Strate d'`obs22` | % synthétique | Étage qui la consomme |
|---|---|---|
| Semaine | 27,6 % | Stage B |
| **Samedi** | **87,1 %** | **Stage C0** |
| **Dimanche** | **86,7 %** | **Stage C0** |

Le −2,59 pp était l'effet **global**. L'ancre **week-end**, celle que Stage C0 consomme, est
synthétique à **~87 %**. Et la cible de Stage B est déjà dégonflée de 2,6 pp (travail réel-seulement
0,1944 vs pool contaminé 0,1685) **avant que le trim ne tourne**. Contamination et asymétrie
**se composent** : on écrête vers une cible elle-même trop basse.

**Décision : purifier l'ancre fait partie du correctif, pas de la question ouverte.**
Un `& (obs_full["IS_SYNTHETIC"] == 0)` à `calibrate_C_4split.py:675` et `val.py:247`.

**Réserve à chiffrer avant de figer** — purifier le week-end ne laisse que ~103 diaires samedi et
~105 dimanche : **on échange un biais contre de la variance**. Mesurer l'erreur-type de la cible
week-end purifiée ; si elle est du même ordre que le biais qu'on retire, préférer un lissage
(mise en commun samedi+dimanche, ou cible semaine ajustée) plutôt qu'une cible bruitée. **À décider
sur la mesure, pas d'avance.**

#### ✅ Mesure faite le 2026-07-30 — décision : **mise en commun samedi + dimanche**

| Strate | n réel | taux travail réel | SE | biais retiré | SE vs biais |
|---|---|---|---|---|---|
| Samedi | 103 | 0,0716 | **±1,40 pp** | +1,37 pp | SE ≈ biais |
| Dimanche | 105 | 0,0778 | **±1,57 pp** | +0,33 pp | SE ≫ biais |

La règle pré-enregistrée ci-dessus se déclenche : une cible purifiée **par jour** échange un biais
connu contre un bruit de taille égale ou supérieure — ce n'est pas un correctif. La mise en commun
n'est pas qu'un pis-aller de commodité, elle est **justifiée par les données** : samedi 0,0716 vs
dimanche 0,0778, soit 0,62 pp d'écart contre des SE de ~1,5 pp — les deux jours sont statistiquement
indiscernables. n = 208 poolé ramène la SE vers ~1,0 pp en conservant l'essentiel du débiaisage.

### Reste ouvert

Faut-il **rebâtir le produit 2022 en observé-seulement** ?

| Option | Gain | Coût |
|---|---|---|
| Rebâtir 2022 en observé-seulement | supprime la contamination 44,6 % à la source | diversité : 21 675 → 3 074 diaires distincts (réutilisation ×7,5, contre ×4,6–5,9 déjà acceptée pour 2005/2010/2015) |

**Décider après le correctif d'écrêtage + purification d'ancre** : il se peut qu'ils le rendent inutile.

---

# LOT B — Améliorations de validation (relevé utilisateur, 2026-07-30)

> Statut : **investigation en cours** (3 employés lancés le 2026-07-30). Cette section est remplie
> au fur et à mesure. Chaque point reçoit : réponse en une phrase → preuve re-dérivée → action.

## B.1 — Step 5 — INSTRUIT le 2026-07-30

### B.1.1 — `PR: 83,3 %` et le FAIL « Leg-2 PR-remap bug class »

**Réponse (1 phrase).** Le recensement contient une province `PR = 6` (Yukon / TNO / Nunavut) pour
laquelle le pool GSS n'a **aucun donneur** — le GSS n'enquête jamais les territoires — donc
`5 / 6 = 83,3 %` ; ce **n'est pas** le bug Leg-2 que le message annonce, et ce n'est pas non plus lié
à la restriction QC/AB de Leg-3.

**Preuve.**

| Élément | Référence |
|---|---|
| Logique de gate | `3rdJ_05_censusLinkage_4split_val.py:290-306` — diff d'ensembles `cen_dom`/`pool_dom`, `overlap_pct = 100·|cen∩pool| / |cen|`, FAIL si `missing` non vide |
| Impression du FAIL | `:338-340` ; bandeau HTML `:1085-1086` |
| Clés comparées | `PR` recensement (brut, déjà consolidé en régions par StatCan — `MATCH_KEYS`, `3rdJ_05_censusLinkage_4split.py:86`) vs `PR` pool **après** remap `_PROVINCE_TO_REGION` (`:111-119`, appliqué en `val.py:268-273`) |

Re-dérivé depuis les CSV (pas depuis le HTML) :

| Ensemble | Domaine | n |
|---|---|---|
| `PR` recensement (`Aligned_Census_2025.csv`, 30 273 lignes) | {1,2,3,4,5,**6**} | 6 |
| `PR` pool après remap (pool verrouillé, 192 183 lignes) | {1,2,3,4,5} | 5 |
| Recouvrement | census ∩ pool | **5/6 = 83,3 %**, `missing = [6]` |

Cause racine : les codes PR bruts du pool plafonnent à 59 (C.-B.) ; aucune ligne ne porte 60/61/62,
donc rien ne mappe vers la région 6.

**Conséquence réelle : négligeable et gracieuse.** En joignant `Matched_Keys.csv` au `PR` recensement,
les **24 lignes** `PR = 6` (soit **0,08 %** de 30 273) se résolvent toutes en
`MATCH_TIER = 3_Constraints` — le seul palier qui laisse tomber `PR`. Elles reçoivent des donneurs
nationaux proportionnels à la population. Le matching se dégrade, il n'échoue pas.

Déjà documenté : `3rdJ_05_censusLinkage_4split.md:458-465` et
`outputs_step5/investigation/INVESTIGATION_3fails_findings.md` (FAIL 3).

**Action.** Aucun changement de seuil — le FAIL est **délibérément laissé visible plutôt que masqué**
(précédent Leg-2), et la doc recommande explicitement de ne pas exclure `PR = 6` du test de
sous-ensemble juste pour verdir la gate. Un seul geste, **cosmétique et non-assouplissant** : le
bandeau attribue le FAIL à la « Leg-2 PR-remap bug class », ce qui est une **mauvaise attribution** —
reformuler le message pour nommer les deux causes possibles (bug de remap **ou** absence structurelle
de donneurs), sans toucher au seuil.

### B.1.2 — « Section 3 — AT_WORK Consistency » : est-on sûr du résultat ?

**Réponse (1 phrase).** W1 / W3 / W4 sont exacts et reproduits au chiffre près, **mais W2 est une
gate vide** : le domaine `LFTAG` de cet extrait recensement ne contient que {1, 2}, donc le groupe de
comparaison « hors population active » est **vide** et la gate ne peut structurellement jamais
échouer.

**Preuve.** Re-dérivé depuis `3rdJ_25CEN_aug_Full_Schedules.csv` (30 273 lignes) avec les formules du
validateur (`val.py:540-627`) :

| Gate | Rapport | Re-dérivé | Verdict |
|---|---|---|---|
| W1 (écart max intra-`Day_Type`) | 2,05 pp · 0 slot > 3 | 2,05 pp · 0 slot > 3 | exact |
| W2 `employed_max` / `noninlf_max` | 19,97 % / 0,00 % | 19,97 % / 0,00 % | exact mais **vide** |
| W3 (collègues intra-`Day_Type`) | 0,888 pp | 0,888 pp | exact |
| W4 `NonOffice` / `Unknown` | 48,16 % / 5,48 % | 48,16 % / 5,48 % | exact |

Mécanisme de la vacuité (`val.py:577-591`) : le code traite `LFTAG ∈ {1,2}` comme « employé » et
**tout le reste** comme « hors PA ». Or `value_counts` du recensement = `{1: 28 498, 2: 1 765,
99→NaN: 10}` — **aucun code 3 ou 4 n'existe dans cet extrait**. Donc `noninlf_vals` est toujours vide,
`noninlf_rate` retombe silencieusement sur `0.0` (`val.py:583`), et le test `employed_max > 0.0`
est trivialement vrai — que les données soient justes ou complètement cassées.

**C'est exactement le motif « une gate qui passe sur le bug qu'elle prétend attraper ».** Nouvelle
trouvaille : non signalée dans `.md` ni `val.md`.

⚠️ **Cadrage honnête de la portée, à écrire dans le papier** : W1 et W3 sont légitimes (ils comparent
deux sous-ensembles disjoints d'origine de donneur, `IS_SYNTHETIC == 1` vs `== 0` — pas une colonne
contre elle-même), mais ce sont des **contrôles de cohérence interne** du split SYN/OBS du pool porté
à travers le matching. **Aucun des quatre ne valide `AT_WORK` contre une référence externe du marché
du travail.**

**Action.**
1. `3rdJ_05_censusLinkage_4split_val.py:577-591` — passer W2 en **`N/A` quand la strate hors-PA est
   vide** (le validateur a déjà ce motif `N/A` en §5.x/6.x), **ou** la remplacer par un vrai contrôle
   externe. Ne pas la laisser afficher PASS.
2. À tracer : `LFTAG ∈ {1,2}` seulement est-il un **filtre amont volontaire** (extrait recensement
   restreint aux personnes en emploi) ou un effet de bord ? L'employé n'a pas remonté le script
   d'alignement. Si c'est volontaire, W2 n'a simplement pas de sens dans Leg-3 et doit disparaître.

### B.1.3 — Porter les figures F1 et F5 de 2J vers Leg-3

Générateur de référence : `2J_docs_occ_nTemp/outputs_step5/_gen_step5_v2_plots.py`.

**F1 · Per-slot AT_HOME residual** (`:151-179`)

| | |
|---|---|
| x | slot 1–48 (origine 04:00) |
| y | `moyenne(hom30, toutes lignes)·100 − moyenne(hom30, IS_SYNTHETIC==0)·100` |
| séries | une courbe de résidu + points rouges sur les slots dépassant ±3 pp |
| entrées | `IS_SYNTHETIC`, `hom30_001..048` |

Colonnes **présentes à l'identique** dans `3rdJ_25CEN_aug_Full_Schedules.csv` (vérifié sur les
en-têtes).

🔴 **Complication Leg-3** : Leg-3 a **3 canaux liés au GSS** (`hom30` / `wrk30` / `ret30`). Une seule
courbe `hom30` ne raconte plus toute l'histoire — il faut **exécuter la recette 3 fois**, et ancrer
chaque instance sur la gate Leg-3 correspondante, **pas** sur les libellés §2.2/§6.1 de 2J :

| Canal | Gate d'ancrage Leg-3 |
|---|---|
| `hom30` | 2.2 — `val.py:463` |
| `wrk30` | W1 — `val.py:567` |
| `ret30` | R1 — §3r |

**F5 · Per-HH mean AT_HOME & the 5H exclusion** (`:234-250`)

| | |
|---|---|
| x | moyenne AT_HOME par ménage (0–1, 51 bins) |
| y | nombre de ménages |
| forme | histogramme + ligne verticale / bande à **0,30** |
| entrées | `HH_hom30_001..048` du fichier **non-`excl`** `…_Full_Aggregated.csv` (pour montrer la queue **avant** exclusion) |

Colonnes présentes à l'identique dans `3rdJ_25CEN_aug_Full_Aggregated.csv`. **Pas de multiplication
par canal ici** : `HH_wrk30` / `HH_ret30` n'existent pas *par conception* — leur absence est
elle-même assertée par la gate 5.4 (`val.py:936-939`). Le concept est donc AT_HOME-seul dans les deux
legs.

La « 5H exclusion » existe verbatim dans Leg-3 : `run_exclusion()`,
`3rdJ_05_censusLinkage_4split.py:1200-1260`, même seuil `< 0,30` sur la moyenne `HH_hom30` (`:1212`),
explicitement résidentiel-seulement (« office channel is not excluded here », `:1203`).

**Action.** F1 → porter en 3 exemplaires, ancrés après les Sections 2 / 3 / 3r. F5 → quasi
copier-coller contre `Full_Aggregated` / `Full_Aggregated_excl` de Leg-3.

## B.2 — Step 6 — INSTRUIT le 2026-07-30

> 🔴 **L'hypothèse de départ du manager était fausse, et c'est important.** J'avais supposé que
> 4.1 home / 4.1 work seraient la même asymétrie d'écrêtage que le Lot A. **Ce n'est pas le cas** —
> prouvé par les entrées/sorties, pas par raisonnement. Ce sont **deux défauts distincts**, à traiter
> séparément.

### B.2.1 — Pourquoi 4.1.home et 4.1.work sont FAIL

**Réponse (1 phrase).** Le décodeur entraîné **sur-produit AT_HOME et sous-produit AT_WORK** dans sa
reconstruction 2022 non calibrée (+8,91 pp / −10,99 pp en semaine) : c'est un **biais génératif du
modèle**, sur un chemin de code que la calibration Stage B/C0 ne touche jamais.

**Preuve — la séparation est une preuve d'E/S, pas une déduction.**

`3rdJ_06_calibrate_C_4split.py` lit **uniquement** `2030_diaries_*_raw.csv` + `IN_B` (`:657-677`) et
écrit **uniquement** le fichier 2030 `_C`. Il **ne touche jamais**
`reconstructed_2022_diaries_4split.csv`. Ce backcast est produit **une seule fois**, par un décodage
direct sans aucune calibration dans ce chemin.

| Élément | Référence |
|---|---|
| Gate | `3rdJ_06_longitudinalForecasting_4split_val.py:461` (`home_pass = MAD<0,10 ET dHome_pp<=2,0`), `:466` (`work_pass = MAD<0,10 ET dWork_pp<=3,0`) ; boucle `:458-478` |
| Constantes | `BUILD_BACKCAST_GATE_TABLE` `:84-95` — **transcrites** du stdout du job 1133427 (docstring `:442-456`) |
| Calcul sous-jacent | `3rdJ_06_longitudinalForecasting_4split.py`, `run_substage_d_phase_i()` `:1699-1845` ; boucle JS/MAD/level `:1793-1822` |
| `gen_*` | `decode_deliverable()` — T=0,7, nucleus p=0,9, min-dwell (`:1738-1755`) |
| `obs_*` | colonnes brutes `hom30`/`wrk30` de `df_2022 = df[df["CYCLE_YEAR"]==2022]` (`:1727`), où `df` = `augmented_diaries.csv` de Step-4 chargé **sans filtre** (`:2215`) |

| Strate 1 (semaine) | MAD | seuil | level (pp) | seuil | dépassement |
|---|---|---|---|---|---|
| home | 0,0996 | < 0,10 (passe de justesse) | **8,91** | ≤ 2,0 | **+6,91 pp** |
| work | **0,1132** | < 0,10 (**échoue**) | **10,99** | ≤ 3,0 | **+7,99 pp** |

**Mécanisme.** `home` n'échoue que sur la sous-condition de *niveau* — sa **forme** est bonne
(MAD 0,0996, sous le seuil au poil). `work` échoue sur **les deux**, parce qu'il est le canal
complémentaire qui absorbe la même masse d'heures ouvrables mal attribuée. Un seul défaut, deux
symptômes.

**Limite de re-dérivation, honnête.** L'employé reproduit exactement la ligne INFO
`4.secondary.*` (JS/MAD au 4ᵉ décimal) depuis `reconstructed_2022_diaries_4split.csv` vs
`3rdJ_25CEN_aug_Full_Aggregated_excl.csv` — l'arithmétique est donc confirmée. Mais les chiffres
**PRIMARY par strate** ne sont **pas** recalculables localement : le fichier reconstruit n'a pas de
colonne `DDAY_STRATA`, et sa source d'alignement (`seed_3_g3fix/augmented_diaries.csv`, 418 Mo) n'est
pas stagée localement. C'est la limite que le validateur documente lui-même. **Le log brut du job
1133427 n'est pas là non plus** → la table PRIMARY reste des constantes transcrites, croisées
seulement via la reproduction poolée.

**Action.** Hors périmètre du code de calibration : c'est le décodeur qu'il faut réentraîner ou
repondérer. **Ne pas** tenter de « rattraper » ce biais par la calibration — ce serait exactement
l'erreur qui a produit le Lot A. À traiter comme un point séparé, après le Lot A.

### B.2.2 — Les écarts `home level` / `work level` / `retail level`

**Réponse (1 phrase).** Seuls les deux écarts de **semaine** sont réellement grands (§B.2.1) ; le
week-end passe proprement, et **l'écart commerce n'existe pas** — c'est un **artefact de métrique**
sur un canal creux, pas un défaut de pipeline.

| Check | Canal | Strate | Écart (pp) | Verdict |
|---|---|---|---|---|
| 4.1.home | home | Semaine | **8,91** | 🔴 FAIL |
| 4.1.work | work | Semaine | **10,99** | 🔴 FAIL |
| 4.1.retail | retail | Semaine | 0,10 | ✅ PASS |
| 4.2.* | home/work/retail | Samedi | 0,46 / 0,37 / 1,04 | ✅ PASS |
| 4.3.* | home/work/retail | Dimanche | 0,12 / 0,28 / 0,29 | ✅ PASS |
| 4.secondary.* | — | poolé (INFO, non gaté) | JS 0,0012 / 0,0278 / **0,0429** — MAD 0,0681 / 0,0830 / **0,0115** | non gaté |

**Pourquoi le commerce *paraît* mauvais.** Le seul grand chiffre commerce est le `JS = 0,0429`
**poolé et secondaire** — le **plus grand** JS des trois canaux alors qu'il a le **plus petit** MAD
(0,0115). C'est précisément l'**artefact de gonflement du JS sur canal creux** (~2 % de positifs) que
la métrique profil+MAD+level a été adoptée pour éviter — écrit noir sur blanc dans la docstring du
module (`:16-19`) et dans le validateur (`:483-487` : « retail … flagged as the worst case for that
artifact »). **Dans les chiffres qui font foi (4.1/4.2/4.3), le commerce passe partout.**

Trois causes candidates écartées par mesure pour le commerce : l'écrêtage Stage B/C0 (jamais appliqué
au commerce), l'ordre de mutex (le commerce bat le domicile et ne perd que contre le travail, et les
conflits sont rares à ~2 % de prévalence), la contamination d'ancre (moyenne commerce réel-seulement
0,0115 vs pool contaminé 0,0132 → **0,17 pp**, négligeable).

**Action commerce : aucun correctif de pipeline.** Requalifier `4.secondary.retail` en INFO
explicitement étiqueté « JS non fiable sur canal creux — lire le MAD ». Le tableau est trompeur pour
un lecteur, pas faux.

#### ✅ EXÉCUTÉ le 2026-07-30 — mécanisme démontré, pas seulement affirmé

Mécanisme confirmé dans le code : `js_divergence()` (`val.py:118`) **renormalise** les deux profils
48 slots à somme = 1 **avant** de comparer — c'est donc une mesure de distorsion de *forme* relative,
pas d'erreur absolue. Le MAD (`:541-544`) est calculé sur les probabilités brutes, non renormalisées :
c'est lui qui est comparable entre canaux. Bloc confirmé **non gaté** (recherche explicite d'un seuil
attaché à `4.secondary.*` : aucun).

Taux de positifs re-dérivés depuis les données ; **les trois taux de la reconstruction reproduits
exactement par le manager** sur une lecture indépendante :

| Canal | reconstruction | observé 2022 (n = 5 560) | densité moyenne | JS | MAD |
|---|---|---|---|---|---|
| domicile | 76,58 % | 71,42 % | 74,00 % | 0,0012 | 0,0681 |
| travail | 10,11 % | 16,85 % | 13,48 % | 0,0278 | 0,0830 |
| **commerce** | **2,20 %** | **1,32 %** | **1,76 %** | **0,0429** | **0,0115** |

Le commerce est **~42× plus creux** que le domicile. La densité classe commerce < travail < domicile,
le JS classe exactement à l'inverse, et le **MAD ne suit pas du tout la densité** (commerce le plus
petit, travail le plus grand). Démonstration synthétique ajoutée au script et rejouée à chaque
régénération (`_toy_js_density_demo`) : à erreur absolue **constante** de 0,005, le JS vaut 0,0080 à
2 % de densité contre 0,0003 à 10 % — **un facteur ~637 dû à la seule densité**. Verdict `SUPPORTED`,
calculé en code et non codé en dur.

**Portée honnête de la preuve** : la corrélation densité↔JS ne repose que sur 3 points ; c'est la
démonstration synthétique qui porte la charge causale, pas le classement sur les données réelles.

**Nuance relevée à l'œil, à ne pas perdre** : la courbe commerce reconstruite présente un **double
pic** là où l'observé n'a qu'une seule bosse. C'est une vraie anomalie de *forme*, noyée dans le MAD
parce que le commerce est quasi nul la majeure partie de la journée. Le commerce est donc bien
reconstruit **en niveau** — ce que disent 4.1/4.2/4.3 — mais pas parfaitement **en forme**. À
rapprocher de §B.3.6 (R.4, différence dominicale QC/AB, elle aussi une question de forme).

**Résultat** : `4.secondary.{home,work,retail}` portent chacun leur taux de positifs en ligne, plus une
nouvelle ligne INFO `4.secondary.mechanism` avec la démonstration chiffrée. Les JS restent publiés,
rien n'est masqué. Scorecard **inchangé** — GSS 66P/15W/5F, hôtel 17P/3W/2F, seul l'INFO passe de 19
à 20 (la ligne ajoutée). Aucun seuil touché. Rapport `step6_validation_report_v2.html`, canonique
intact.

### 🔴 B.2.3 — Trouvaille non demandée : la contamination d'ancre est bien pire en week-end

L'employé a quantifié `obs22` (chargé en `val.py:242-247`, `calibrate_C_4split.py:675`, `IN_B:113-114`) :

| Strate | Lignes synthétiques | % synthétique |
|---|---|---|
| Global | 2 473 / 5 560 | **44,5 %** |
| Semaine | 1 096 / 3 975 | 27,6 % |
| **Samedi** | 693 / 796 | **87,1 %** |
| **Dimanche** | 684 / 789 | **86,7 %** |

Le chiffre de −2,59 pp du relais manager décrivait l'effet **global**. Par strate, c'est autre chose :
**l'ancre week-end est synthétique à ~87 %**. Or c'est précisément l'ancre que **Stage C0** consomme.

Effet mesuré sur la cible : moyenne travail réel-seulement **0,1944** vs pool contaminé **0,1685** →
la cible de `run_stage_B` (`owe[WRK].mean()`, `:373-374`) est **déjà dégonflée de 2,6 pp avant même
que le trim ne tourne**. Contamination et asymétrie d'écrêtage **se composent** : on écrête vers une
cible elle-même trop basse.

**Conséquence pour le Lot A** — voir §A.7 mis à jour : la purification d'ancre n'est plus une option
« à −2,59 pp », c'est un pré-requis du Stage C0. Avec une réserve à mesurer : purifier le week-end ne
laisse que ~103 diaires samedi et ~105 dimanche → **on échange un biais contre de la variance**, et
il faut le chiffrer avant de trancher.

⚠️ Portée : cette contamination affecte les **cibles de calibration 2030** et les checks
Section 5 / secondary. Elle n'affecte **pas** la table PRIMARY de la Section 4, qui a une autre source
d'observé (`augmented_diaries.csv`).

## B.3 — Step 7 — INSTRUIT le 2026-07-30

### 🔴 B.3.0 — Défaut trouvé en chemin : les 4 rapports HTML Step-7 sont PÉRIMÉS

Non demandé, mais bloquant pour tout le reste de §B.3. Les quatre rapports
(`step7_validation_report_{2022,2030_cons,2030_central,2030_opt}.html`) datent du **2026-07-23
22:28**, donc **d'avant** le correctif du défaut retail `multiplier` du 2026-07-28. Ils affichent
encore le bug : les trois bandes toutes à `0,9500`.

| Fichier | mtime | Pic `multiplier` global |
|---|---|---|
| `retail_presence_multiplier_2030_cons.csv` (courant) | 28 juil. | **0,8550** |
| `…_2030_cons_BAK_2026-07-28.csv` (pré-correctif) | 23 juil. | 0,9500 |
| `…_2030_central.csv` (courant) | 28 juil. | **0,9215** |
| `…_2030_opt.csv` (courant) | 28 juil. | **0,9975** |

Les chiffres du HTML correspondent aux `BAK` pré-correctif, pas aux CSV courants. Donc **R.1/R.4 tels
qu'affichés valident le bug** au lieu du correctif.

**Action : ré-exécuter `3rdJ_07_bemIntegration_4split_val.py` sur les 4 produits** avant de citer quoi
que ce soit de ces rapports. C'est exactement le motif « re-dériver, ne pas croire » — les rapports
montrent un PASS sur des données qui n'existent plus.

⚠️ À vérifier dans la foulée : seul le canal commerce a été re-généré le 28. Les produits bureau /
hôtel / résidentiel datent toujours du 23 — donc *cohérents* avec leurs rapports, mais à re-valider
de toute façon après la cascade du Lot A.

### B.3.1 — `[FAIL] M.2` — pics commerce AB=13 / QC=16

**Réponse (1 phrase).** Ce n'est **ni un bug de roll ni une gate mal spécifiée** : le diaire GSS-2022
observé du Québec pique réellement en fin d'après-midi (16 h), et le FAIL n'apparaît **que dans le
rapport 2022** — les trois rapports 2030 passent.

**Preuve.**

| Élément | Référence |
|---|---|
| Gate M.2 | `3rdJ_07_bemIntegration_4split_val.py:731-742` — test de fenêtre `:735` `11 <= h <= 15` ; test de nuit `:736-737` |
| « post-roll » | roll +4 h diaire GSS→heure horloge : `3rdJ_07_aug_to_bem_4split.py:536,538` (2030, `np.roll(...,8)`) et `:559` (2022, `ret48_clock = np.roll(ret48,8)`) ; convention documentée `:297-298` |
| Mapping slot↔heure | `3rdJ_07_aug_to_bem_4split.py:500-501` — `slot` = index demi-heure 1-48, `Hour = slot_index // 2` |

Re-dérivé depuis `retail_presence_multiplier_2022.csv` (semaine ; n = 5 778 QC, 3 593 AB) :

| PR | Top-1 | Top-2 | Top-3 | Verdict M.2 |
|---|---|---|---|---|
| QC | **H16 → 0,9500** | H17 → 0,9454 | H13 → 0,7701 | FAIL (16 hors `11..15`) |
| AB | **H13 → 0,9500** | — | — | PASS |

Forme QC réellement **bimodale**, l'après-midi l'emporte de peu sur le midi. Et ce n'est pas un
artefact de petit échantillon : **QC utilise la région à correspondance exacte (région 2)**, tandis
qu'AB passe par un proxy Prairies à 3 provinces (région 4) — l'échantillon suspect est celui qui
PASSE, pas celui qui FAIL. Le FAIL est déjà consigné comme connu dans
`3rdJ_07_bemIntegration_4split.md:111`.

Répartition : `2022` → `{'AB':13,'QC':16} … False`. `2030 cons/central/opt` → `{'AB':14,'QC':11} … True`.

**Action.** Ne **pas** élargir la fenêtre pour effacer le FAIL. Deux gestes :

1. **Relabel + preuve** : requalifier en `WARN accepté-documenté` avec la preuve empirique ci-dessus
   (bimodalité QC re-dérivée, région exacte). Le papier mentionne le pic commerce QC en fin
   d'après-midi comme résultat, pas comme défaut.
2. **Corriger un désaccord doc↔code trouvé au passage** : `3rdJ_07_bemIntegration_4split_val.md`
   annonce une tolérance « ±1 slot » (≈ 30 min) alors que le code implémente `11 <= h <= 15`, soit
   **±2 h**. La doc est fausse, pas le code — la doc est plus stricte que ce qui tourne. Aligner la
   doc sur le code (et non l'inverse : changer le code resserrerait une gate a posteriori).
   *Sans effet sur ce FAIL : 16 h est dehors dans les deux lectures.*

### B.3.2 — « Section A — Schema & Structure » : pourquoi le tableau ne dit rien

**Réponse (1 phrase).** Ce n'est pas un tableau de gates mais un **manifeste de comptage** (lignes et
ménages par canal) ; les vraies vérifications A.1–A.11 vivent dans le *Summary Table* plus bas, d'où
l'impression qu'il ne veut rien dire.

**Preuve.** Construit en `3rdJ_07_bemIntegration_4split_val.py:279-288` via `ax.table()` matplotlib —
c'est donc une **image**, pas du HTML sélectionnable. Colonnes = `Item` / `Value`.

| Item | Value | Ce que ça veut dire |
|---|---|---|
| Residential rows | 1 109 520 | N_HH × 2 `Day_Type` × 24 h |
| Unique HH | 23 115 | ménages simulés |
| Retail rows | 288 | 3 `Day_Type` × 2 PR × 48 slots |
| Hotel rows | 2 304 | 2 PR × 12 mois × 2 `Day_Type` × 48 slots |
| Office rows | 144 | archétypes × 2 `Day_Type` × 24 h |

**Figure proposée (remplace le tableau).** Barres **horizontales**, axe x **logarithmique** (le
résidentiel ~1,1 M écrase le commerce à 288) :

- y = canal (Résidentiel / Bureau / Commerce / Hôtel)
- x = nombre de lignes (log)
- couleur de barre = résultat de la gate A.1–A.11 propre à ce canal (vert / rouge)
- annotation sur chaque barre = **la formule** (`N_HH×2×24`, `3×2×48`, …) + badge PASS/FAIL

Source : les valeurs sont **déjà calculées** en `val.py:229-270` (`n`, `self.N_HH`,
`len(self.office)`, `len(self.retail)`, `len(self.hotel)`) — il n'y a qu'à les tracer au lieu de les
tabuler. La formule affichée à côté du compte est ce qui rend le tableau vérifiable d'un coup d'œil.

### B.3.3 — « Section R — Retail Product (NEW) » : que montre-t-elle, est-ce correct ?

**Réponse (1 phrase).** La figure est bien construite et le levier de bande **bouge réellement**
aujourd'hui (pic 0,855 cons < 0,9215 central < 0,9975 opt, soit ~14,3 pp d'amplitude) — **mais le
rapport publié montre encore l'ancien bug** (voir §B.3.0), donc ce que tu as lu à l'écran est faux.

**Contenu de la figure** (`val.py:595-611`), deux sous-graphes :
- gauche : `multiplier` vs `Hour`, **6 séries** = PR × `Day_Type`
- droite : barres du nombre de slots marqués `staff_shoulder_flag`, par `Day_Type`

**Vérification re-dérivée depuis les CSV courants :**

| Contrôle | Résultat |
|---|---|
| (i) Levier de bande vivant | ✅ ~14,3 pp cons→opt (avant correctif : 0,0) |
| (ii) Nuit ≈ 0 | ✅ 0,0017–0,0020 (seuil ≤ 0,01) |
| (iii) Position du pic | ✅ 11 h / 14 h dans la fenêtre pour 2030 ; QC-2022 à 16 h = §B.3.1 |

**Action.** Ré-exécuter le validateur (§B.3.0). ⚠️ **La conclusion « ensuite la section R est bonne
telle quelle » était fausse** — la ré-exécution a fait tomber R.1 et R.2 : voir §B.3.3bis, qui est la
trouvaille la plus importante des trois chantiers.

### 🔴 B.3.3bis — Trouvaille non demandée : les gates R.1 et R.2 encodent le bug d'avant le 2026-07-28

**Réponse (1 phrase).** Le correctif retail du 28 juillet a été appliqué au **générateur** mais jamais
**cascadé au validateur** : R.1 et R.2 continuent d'affirmer l'invariant que le bug fabriquait, et
personne ne l'a vu parce que les rapports n'ont jamais été régénérés depuis (§B.3.0).

**Le mécanisme.** Avant le 28/07, le produit retail se normalisait sur **son propre** pic, ce qui
annulait exactement le levier de bande — d'où un pic figé à 0,95 pour *toutes* les bandes. Le
correctif ancre désormais sur le pic de `at_retail_fraction_2030_base` (non levé, partagé par les
trois fichiers), donc `multiplier = 0,95 × levered / base_peak` et le niveau survit.
`3rdJ_07_aug_to_bem_4split.py:680-698` **spécifie déjà en toutes lettres** le gate de remplacement —
le validateur n'a simplement jamais suivi.

**Re-dérivé par le manager depuis les CSV, avant d'agir** (`shape` et `multiplier`, max par
`Day_Type × PR`, 3 × 2 = 6 cellules par bande) :

| Produit | levier | `shape` pic | `multiplier` pic | `0,95 × levier` | écart R.2 |
|---|---|---|---|---|---|
| 2022 | 1,00 | 1,000000 | 0,950000 | 0,9500 | 9 e-7 ✅ |
| 2030 cons | 0,90 | **0,900000** | **0,855000** | 0,8550 | 0,0094 |
| 2030 central | 0,97 | **0,970000** | **0,921500** | 0,9215 | 0,0030 |
| 2030 opt | 1,05 | **1,050000** | **0,997500** | 0,9975 | 0,0055 |

Le pic de `shape` **est** le levier, au sixième décimal ; le pic de `multiplier` **est** 0,95 × levier.
L'écart R.2 est monotone en |levier − 1| (0,10 → 0,05 → 0,03), signature exacte du mécanisme et non
d'un bruit numérique. Comptage : 6 enregistrements R.1 + 1 R.2 = 7 par bande 2030, + le FAIL
préexistant = **8**. 2022 (sans levier) est intact — c'est la preuve que le défaut est bien
levier-dépendant.

**Décision manager — re-spécifier, pas assouplir.** Les deux gates deviennent conscients de la bande
et **strictement plus forts** : ils épinglent désormais la *survie du levier* dans le produit au lieu
d'épingler une constante que le bug fabriquait. Tolérances **inchangées** (1e-6 / 1e-4) ; sur 2022
les deux tests se réduisent verbatim à ceux d'aujourd'hui.

- **R.1** : levier dérivé à l'exécution par la logique `_derive_retail_lever()` du générateur
  (`aug_to_bem:153`, lit la colonne `multiplier` du fichier de levier Step-6 brut) — **pas** le dict
  figé `RETAIL_LEVER_VALUE` (`val.py:54`), qui reste l'affaire de R.7. Cette indépendance est le
  fond du sujet : un fichier de levier corrompu doit faire tomber R.7 pendant que R.1 passe.
  Assertion : `shape_pic == levier` et `multiplier_pic == 0,95 × levier`.
- **R.2** : ancrer sur le pic non levé — `recon = shape × (at_retail_fraction.max() / levier)`.

**Ce que ça coûte au dossier.** Les « 52P/7W/1F » du Step-7 sont doublement périmés : ils validaient
des CSV d'avant le correctif **avec des gates d'avant le correctif**. Le vrai scorecard Step-7 ne
sera connu qu'après cette re-spécification.

**✅ RÉSOLU le 2026-07-30, vérifié depuis les rapports eux-mêmes** (pas depuis le compte rendu de
l'employé) : R.1 affiche désormais `shape=lever=0,9000, mult=0,95×lever | all OK | PASS`, R.2 PASS.
Scorecards re-lus dans le HTML : 2022 → FAIL 1 → **0** (M.2 relabellisé en WARN portant ses pics) ;
2030 ×3 → **52P / 7W / 1F**, le FAIL survivant étant `Office band monotonicity` (préexistant, sans
rapport avec le commerce). Preuve de faillibilité fournie et rejouée : `multiplier` × 1,01 →
`R.1 mult_peak=0,863550 (exp 0,855000)` FAIL ; un slot de `shape` corrompu de +0,05 → `R.2 diff=0,004418`
FAIL. Le levier est dérivé à l'exécution depuis le CSV Step-6 brut, indépendamment de `RETAIL_LEVER_VALUE`.

### 🔴 B.3.6 — Trouvaille transversale : la classe des **gates qui ne peuvent pas échouer**

**Réponse (1 phrase).** Trois gates découverts le même jour n'ont **aucun pouvoir discriminant** — ils
sont structurellement incapables d'échouer — et chacun gonfle un scorecard qui est ensuite cité
comme preuve de validation.

| Gate | Mécanisme de vacuité | Preuve |
|---|---|---|
| **Step-5 W2** | la strate « hors population active » est vide (`LFTAG ∈ {1,2}` seulement), son taux retombe sur 0,0 et le test est trivialement vrai | §B.1.2 — corrigé en `N/A` |
| **Step-7 R.7** | tautologie littérale : `:655` affecte `all_ret[b] = RETAIL_LEVER_VALUE[…]`, `:657` compare **la même expression** à elle-même ; le CSV n'est jamais lu, seul son `exists()` est testé | lu dans le code par le manager |
| **Step-7 R.4** | compare les **pics** QC vs AB, or la normalisation force tous les pics à être égaux par construction → ratio 1,000 systématique. Le manager a vérifié : dégénéré **aussi en 2022** (`QC=0,9500 AB=0,9500`), donc antérieur au levier | lu dans les 4 rapports |

**Pourquoi c'est grave.** R.4 était censé détecter la différence de régime dominical Québec/Alberta —
une vraie différence réglementaire — mais elle vit dans la **forme**, pas dans le pic, exactement la
dimension que la normalisation annule. Le gate existe, il est vert ou orange, et il ne regarde rien.
De même, quand j'ai autorisé R.1 à rester indépendant de `RETAIL_LEVER_VALUE` « puisque R.7 épingle
la valeur », **R.7 n'épinglait rien** : sur mon instruction, plus aucun gate ne contrôlait le levier.

**Ce que ça implique pour le chiffre « 52P ».** Un scorecard n'est un argument que si chaque unité
comptée pouvait échouer. Tant que l'audit de vacuité n'est pas fait, **52P est un majorant**, pas une
mesure. Audit commandé sur l'intégralité des gates Step-7 (sections A/B/C/D/E/R/H/F/G/M/P/W) :
pour chacun, la statistique peut-elle différer de la valeur affirmée ? Réponse en table
CAN-FAIL / VACUOUS / SUSPECT, **corrections séparées de l'audit** pour ne pas mélanger constat et
remède.

**Règle à retenir pour la suite du projet** : un gate n'est validé que lorsqu'on l'a **vu échouer**
au moins une fois sur une perturbation contrôlée. Cette règle existait déjà pour les correctifs
(§A.6) ; elle doit s'appliquer aussi aux gates eux-mêmes, à leur écriture.

#### Audit de vacuité Step-7 — résultat (2026-07-30)

R.4 et R.7 corrigés et **vus échouer** sur perturbation : R.4 devient un *facteur de charge*
`moyenne/pic` par (dimanche, PR) — invariant à toute remise à l'échelle par groupe, donc il survit à
la normalisation qui annulait l'ancien ratio de pics. QC < AB dans les **quatre** produits
(2030 : Δ −0,0334, identique d'une bande à l'autre, donc bien invariant au levier), ce qui a un sens
physique : les horaires dominicaux restreints du Québec concentrent l'activité sur une fenêtre plus
étroite. R.7 lit désormais le levier réalisé dans le produit livré et le compare aux constantes de
design — la séparation voulue est rétablie (R.1 = produit vs fichier de levier, R.7 = produit vs
0,90/0,97/1,05). Scorecards : 2022 **43P/0F**, 2030 ×3 **53P/6W/1F**.

**Sur l'ensemble des sections A→W : 11 gates VACUOUS, 3 SUSPECT, ~41 CAN-FAIL.**

Les 7 gates `W.*` sont un **PENDING honnête** (audit de câblage impossible tant que l'IDF v242 n'est
pas en main) et tombent en WARN, donc ils ne gonflent aucun compte de PASS — vérifié. Restent **5
faux PASS** : A.12, B.4, H.5, G.4 et la branche 2030 de **F.1**.

**🔴 F.1 est un cas à part, et le plus grave du lot.** Lu en `:949-961` : ce n'est pas un gate creux,
c'est un **dictionnaire de chaînes en prose** décrivant des observations faites à la main le
2026-07-23, passé tel quel à un `self._rec("pass", …)` inconditionnel et publié au tableau de synthèse
comme `CONFIRMED (build-session evidence)`. Il ne calcule **rien** à l'exécution. Une observation
manuelle passée est ainsi blanchie en PASS automatique présent — pire qu'un gate incapable
d'échouer, puisque le lecteur ne peut pas faire la différence avec un vrai contrôle.

Et il certifie la propriété **la plus porteuse de tout le design** : la séparabilité des canaux est
ce qui fait de la campagne un factoriel 3×3×3 coûtant ~9 simulations par canal au lieu de 27
reconstructions. Si la séparabilité venait à être violée, F.1 est le gate qui devrait l'attraper —
et il ne le pourrait pas.

**Arithmétique honnête à retenir** : sur les 53 PASS annoncés, 5 sont vides → **48 réellement
exercés**. C'est 48 qu'il faut citer tant que les cinq ne sont pas réparés.

*Note* : il n'existe **pas** de Section P dans le validateur Step-7 — les probes P1–P4 relèvent du
Step 8. La ligne 11 de l'ordre d'exécution ci-dessous le référençait à tort.

### B.3.4 — « Section F — Channel Consistency » : où est la figure ?

**Réponse (1 phrase).** Il y a bien une balise `<img>` — mais elle contient un **axe vide** avec une
seule légende texte et **aucune donnée tracée**, d'où l'impression qu'elle manque.

**Preuve.** Émetteur `val.py:854-860` : `ax.axis("off")` puis `ax.text(...)` affichant
« F-section: cross-channel insulation + WFH direction check (see console/summary table) ». La section
est bien dans `chart_sections` (`:933`) et rendue en base64 (`:936-940`) — mais elle ne trace rien.
Les nombres de F.1–F.4 (insulation MD5, distinction des fichiers de bundle, direction WFH) ne partent
que dans le *Summary Table*.

**Figure proposée — et les données existent déjà.** F.4 calcule déjà
`home_daytime{cons,central,opt}` et `office_daytime{cons,central,opt}` (moyennes semaine 9 h–17 h,
`val.py:837-844`) sans jamais les tracer. Graphe en **haltères (dumbbell) ou barres groupées** :

- x = bundle (`cons` / `central` / `opt`)
- série 1 = « Occupation domicile (%) » ← `self.res_bundles[*]` `Occupancy_Schedule`
- série 2 = « Bureau AT_WORK (%) » ← `self.office` `AT_WORK_fraction` / `BAND`
- annotation = les flèches Δ **déjà calculées** (`home_rise`, `office_fall`)

Elle montre d'un coup d'œil ce que F.4 affirme en texte : **le domicile monte pendant que le bureau
descend** quand le WFH augmente. C'est la figure qui rend le cloisonnement inter-canaux visible.

---

## Ordre d'exécution retenu — révisé le 2026-07-30 après instruction

| # | Travail | Dépend de | Statut |
|---|---|---|---|
| 1 | 🔴 **Lot A** — Stage B / C0 bidirectionnels **+ purification d'ancre + pooling week-end** + preuve | — | ✅ **CLOS** ; métrique de référence = ancre 2022 / nonBIZ32 : **−1,91 → −0,92 pp, PASS** ; Progress Log vérifié ligne à ligne |
| 1ter | 🔴 **D-12** — étendre le pooling week-end au canal **domicile** (Stage C1) | 1 | ✅ **FAIT** — `_C_v2` reconstruit, MD5 **`5aa74f44`** ; écart samedi−dimanche du domicile ramené à **−0,02 pp** |
| 1bis | **Re-validation Step-6 complète** sur `_C_v2` | 1ter | ✅ **FAIT** (relancée par le manager sur `5aa74f44`) — GSS **69P/15W/2F** ; les 3 gates `5.2` passent FAIL → PASS ; 2 FAIL restants = `4.1.home` / `4.1.work` (backcast, D-9) |
| 1quater | 🔴 **D-11 / D-13** — promotion de `_C_v2` en source canonique 2030 | 1bis | ✅ **ACCORDÉE** — 5 conditions sur 5, mutex re-vérifié par le manager sur 5 329 152 cellules ; `7c105ef3` **intact sur disque** ; pointeurs + verrou de lockstep dans les 2 fichiers Step-7, **vu échouer** sur 2 modes de dérive |
| 2 | Cascade **Step-7** : régénérer les produits 2030 depuis `5aa74f44` + preuve de séparabilité (D-8) + ré-exécuter le validateur sur les 4 rapports (ferme §B.3.0) | 1quater | ✅ **FAIT** — 4 rapports canoniques rafraîchis (19:19, anciens archivés dans `archive_pre_20260730/`) ; **2022 42P/11W/0F**, **2030 ×3 53P/6W/1F** ; `A.12` retombe de 115,2 h à **0,0 h** sur 2030 (et WARN à juste titre sur 2022, non rebâti) ; séparabilité **structurelle** établie (D-14) ; unique FAIL = `E.3`, préexistant (D-15) |
| 2bis | 🔴 **D-15** — mécanisme de l'inversion `Office_Sales` (cons < hybrid) | 2 | ✅ **CLOS** — **bruit d'échantillonnage** (n=201, NOCS 6 seul ; injection Step-6 aveugle à la profession, vérifiée à la source). Pentes de bande identiques sur les 3 archétypes (−5,31/−5,22/**−5,58** pp) → **l'axe bureau reste interprétable pour Sales** (tendance z=−2,56, `cons−fully` z=+2,59) ; seul le pas adjacent `cons`/`hybrid` est hors puissance. Test apparié ajouté par le manager : verdict inchangé. `E.3` reste **FAIL accepté-documenté**, seuil non relâché |
| 2ter | **Révision de définition de `E.3`** — tester la *tendance* (ou tolérance fonction du SE) au lieu de chaîner des comparaisons adjacentes insensibles à la puissance | 2bis | en attente — **hors périmètre** de la cascade de calibration, demande sa propre instruction |
| 3 | **B.1.2** — gate W2 vide → `N/A` quand la strate hors-PA est vide | indépendant | ✅ **FAIT** (vérifié) |
| 4 | **B.1.3** — figures F1 (×3 canaux) et F5 pour Leg-3 | indépendant | ✅ **FAIT** (vérifié à l'image) |
| 5 | **B.1.1** — reformuler le bandeau `PR` (mauvaise attribution, seuil inchangé) | indépendant | ✅ **FAIT** |
| 6 | **B.3.2 / B.3.4** — figure Section A (barres log) et figure Section F (haltères) | indépendant | ✅ **FAIT** (vérifié à l'image) |
| 7 | **B.3.1** — relabel M.2 en WARN accepté-documenté + aligner la doc sur le code (±2 h) | indépendant | ✅ **FAIT** |
| 7bis | 🔴 **B.3.3bis** — re-spécifier R.1 / R.2 (bande-conscients, levier dérivé à l'exécution) | indépendant | ✅ **FAIT** (2022 0F, 2030 52P/7W/1F, vus dans les rapports) |
| 7ter | 🔴 **B.3.6** — réécrire R.7 (tautologie) et R.4 (pic annulé par la normalisation) + **audit de vacuité de tous les gates Step-7** | indépendant | ✅ **FAIT** (2022 43P/0F, 2030 53P/6W/1F ; audit : 11 VACUOUS / 3 SUSPECT / ~41 CAN-FAIL) |
| 7quater | 🔴 **F.1 branche 2030** — remplacer les preuves manuelles codées en dur par un vrai contrôle d'exécution de la **séparabilité** (le socle du factoriel 3×3×3) + A.4/G.1/G.2 + triage A.12/B.4/H.5/G.4 | 7ter | ✅ **FAIT** — F.1 réel, vu échouer sur 2 perturbations ; A.12 **fire vrai** (~115 h d'écart de mtime : c'est le gate qui aurait dû attraper §B.3.0) ; H.5/G.4 laissés + documentés (D-10). 2030 = **52P/7W/1F**, dont **51 réellement exercés**. ⚠️ preuve **forte** de séparabilité reportée en ligne 2 (voir D-8) |
| 8 | **B.2.2** — relabel `4.secondary.retail` (JS non fiable sur canal creux) | indépendant | ✅ **FAIT** (scorecard inchangé, INFO 19→20) |
| 9 | 🔴 **B.2.1** — biais génératif du décodeur (réentraînement / repondération) — **chiffré le 30/07 : −4,05 pp sur les heures ouvrées (ancre 2022), intouchables par la calibration, composante dominante de l'écart `all48`** | **hors périmètre calibration**, après 1 | en attente — **priorité relevée** |
| 10 | Re-simuler les **7 cellules de probe** — motif **rectifié le 30/07** (voir D-16) | 2 | ✅ **FAIT** — 7/7 `ok` exit=0 en **27,7 min** (12–18 min/cellule, 6 workers, watchdog armé) |
| 11 | Re-passer le **scorecard §P** | 10 | ✅ **FAIT** — **32P / 0W / 0F / 10 INFO** (contre 25P/0W/0F sur le cluster : +6 gates `INPUTS_HASH` réellement exercés + P4 réparé). 1 FAIL initial = **défaut de portage local**, corrigé et **vu échouer** (D-18) |
| 11bis | 🔴 **Trouvaille** : `inject_residential()` n'avait **jamais** été exécuté — les probes excluent le résidentiel **par conception**, et le smoke test enregistré (office 6 / retail 3 / hotel 3) **précédait** le câblage résidentiel | 11 | ✅ **FAIT** — smoke campagne : **27 Spaces, 27 ménages distincts** (graine 42), 54 horaires `MXU_Residential_Occ/Met_HH*`, `fallback=[]`, `ambiguous=[]`. §B **CLOS** |
| 11ter | Premier run **annuel complet** + première exécution de l'IDF **Calgary** (28 des 56 cellules n'avaient jamais touché CAN_CLG) | 11bis | ✅ **FAIT** — cellule 17 `B_central__Tall__CLG`, **6,6 min** (1 worker), 8760 lignes, `ep_return_code=0`, **0 Severe**, EPW + IDF Calgary confirmés **depuis le log** et non le manifeste, 4 canaux injectés (résidentiel 27/27). Voir D-20 |
| 12 | **Campagne 56 runs** — 2,6–3,5 h en local à 6 workers | 11 | 🔵 **LANCÉE** le 30/07 — 6 workers, watchdog 80 %, reprise activée (cellule 17 sautée) |
| 12bis | 🔴 **D-17 — arbitrage utilisateur** : harmoniser le filtre `IS_SYNTHETIC` du bras historique (2022 non filtré vs 2005/2010/2015 filtrés) ? Coût : invalide le produit 2022, son rapport Step-7 et la probe `cycle_2022` | — | **question ouverte** — n'empêche pas la campagne, affecte la *lecture* de l'axe époque |
| 12ter | Contrôle §C sur le canal **résidentiel** historique | — | ✅ **FAIT** — 48/48 bins diffèrent, max\|Δ\| 0,095 ; **les 3 canaux de l'axe époque sont vivants** (D-17) |

**Ce qui a changé par rapport au plan initial** : le point 9 (biais du décodeur) était supposé être
absorbé par le point 1. **Il ne l'est pas** — ce sont deux défauts sans recouvrement de code
(§B.2.1). Et la purification d'ancre est passée de « question ouverte » à composant du point 1
(§A.7).

---

## Progress Log

### 2026-07-30 — ouverture du document

- Doc créé. Lot A repris verbatim du relais manager du 2026-07-28 (décision utilisateur : corriger
  Step-6 d'abord).
- Gardes unidirectionnelles **re-confirmées dans le code** par le manager :
  `3rdJ_06_calibrate_C_4split.py:341` et `:427`. Le diagnostic du relais tient.
- Lot B ouvert : 10 points relevés par l'utilisateur en relisant les rapports HTML de validation
  Steps 5/6/7. Trois investigations read-only lancées en parallèle (une par étape).

### 2026-07-30 — Lot B Steps 5 et 7 exécutés (points 3 à 7), vérifiés par le manager

**Step 5** — `3rdJ_05_censusLinkage_4split_val.py` → `3rdJ_step5_validation_report_v2.html`
(1 192 461 o ; l'original de 796 798 o est **intact**, mtime inchangé ; nouveau flag `--out-suffix`).

- **W2** (`:659-684`) → `WARN`/`N/A` quand la strate hors-population-active est vide, en réutilisant
  le motif « test non exécutable » déjà présent dans le validateur. Aucun seuil touché.
  *Trouvaille collatérale* : `eSim_dynamicML_mHead_alignment.py::data_alignment()` — le script qui
  produit `Aligned_Census_2025.csv` — **n'harmonise jamais `LFTAG`** (absent de sa liste
  `harmonize_*`). Le domaine `{1,2}` est donc hérité de plus haut
  (`forecasted_population_2025_LINKED.csv`), hors périmètre de ce script : l'intentionnalité **n'est
  pas confirmable** ici. À ne pas refermer sur une supposition.
- **Bandeau PR** (`:392-396` console, `:1289-1294` HTML, + `_KNOWN_DONORLESS` et
  `_section0_cause_note()` `:231-275`) : nomme désormais les **deux** causes possibles (vrai bug de
  remap *ou* strate donneuse structurellement absente) et identifie PR = 6 comme territoire
  connu-sans-donneur. FAIL et seuil **inchangés**, aucune exemption PR = 6 ajoutée.
- **Figures** : `2f_f1_hom30` (gate 2.2), `3f_f1_wrk30` (W1), `3rf_f1_ret30` (R1), `5f_f5_hh_athome`
  (Section 5, lu directement dans le `Full_Aggregated.csv` **non-excl**).
- **Scorecard 32P/4W/3F → 31P/5W/3F** : seul W2 bascule PASS → WARN ; les 3 FAIL (PR 0.1, gate 2.2,
  gate R1) sont identiques avant/après. C'est exactement la signature attendue — rien d'autre n'a
  bougé.
- **Vérification manager** : les 11 PNG du rapport extraits du base64 et **regardés**. F1-hom30 =
  max |Δ| 6,80 pp / 19 slots hors bande ±3 pp ; F5 = 771 lignes sous 0,30 sur 30 273, soit 2,55 % —
  **conforme au cadre gelé 30 273/771**. Aucune n'est un axe vide.

**Step 7** — `3rdJ_07_bemIntegration_4split_val.py` (+ `_val.md`) → 4 × `_v2.html`, originaux intacts.

- **Section A** (`:229-320`) : `ax.table()` remplacé par des barres horizontales en échelle log,
  colorées par le verdict du gate de comptage propre à chaque canal, annotées formule + badge.
  Vérifié à l'image : Résidentiel 1 109 520 (N_HH×2×24), Bureau 432 (3×2×24×3), Commerce 288
  (3×2×48), Hôtel 2 304 (2×12×2×48).
- **Section F** (`:886-949`) : l'axe vide devient un graphe à barres groupées domicile/bureau par
  bande. Vérifié à l'image : domicile 49,9 → 53,7 → 56,2 (Δ +6,29 pp) **pendant que** bureau
  45,9 → 42,2 → 35,1 (Δ −10,75 pp). C'est précisément ce que F.4 n'affirmait qu'en texte.
- **M.2** (`:755-789` + `_val.md`) : le seul cas QC-2022 passe en `warn` avec sa justification
  empirique embarquée ; **fenêtre inchangée** (11-15 h) ; toute autre violation échoue toujours. La
  mention « ±1 slot » de la doc est corrigée pour décrire les fenêtres réellement codées (11:00-15:00
  / 12:00-17:00) — **la doc suit le code**, jamais l'inverse.
- **2022 : 42P/10W/1F → 42P/11W/0F**, exactement le relabel M.2 visé et rien d'autre.
- **B.3.3 vérifié** : amplitude du levier 0,8550 → 0,9215 → 0,9975 = 14,25 pp ; plancher nuit
  0,0017-0,0020 ≤ 0,01 ; pics AB@14 h / QC@11 h dans la fenêtre en 2030.

**Et le vrai résultat de la journée** : la régénération contre les CSV corrigés du 28/07 fait tomber
R.1 et R.2 sur les trois rapports 2030 (52P/7W/1F → **50P/7W/8F**). Ce n'est pas une régression —
c'est un **gate enfin vu échouer**. Diagnostic re-dérivé indépendamment depuis les CSV avant toute
action, décision de re-spécification prise : **§B.3.3bis**.

### 2026-07-30 — Lot A livré (point 1), **vérifié et partiellement renvoyé**

Livrable `outputs_step6\..._C_v2.csv`, 111 024 lignes, MD5 `46a539c2`. Canonique `_C` re-vérifié
**intact** (`7c105ef3`). Bidirectionnalité ajoutée à `cap_band_stageB` (:362-448) et `run_stage_C0`
(:493-576), recrutement exclusivement depuis l'état OUT (`hom==0 & wrk==0 & ret==0`), ordre
extension-de-queue → extension-de-tête → isolé, `ACT=WORK_ACT_0IDX` sur les slots levés. Nouveaux
flags `--pure-anchor` (défaut ON), `--no-pure-anchor`, `--out_tag`.

**✅ Confirmé par le manager, re-dérivé indépendamment :**

- **Le chiffre-phare du relais (−10,51 pp poolé) était le mauvais instrument.** Part d'employés en
  semaine : ancre OBS **94,27 %** (19 801/21 005) contre cadre 2030 **49,87 %** (18 456/37 008). Or
  la cible de Stage B (`:455`) *et* les lignes qu'il modifie (`:461-462`) sont toutes deux
  `DDAY_STRATA==1 & LFTAG==1`. Une métrique poolée toutes-populations **ne peut donc structurellement
  pas** mesurer ce stage. L'employé a eu raison de refuser de faire bouger ce chiffre.
- **Les 16 slots BIZ sont identiques au bit près avant/après** (−13,22 pp dans les deux cas), ce qui
  prouve indépendamment que la branche UP respecte `if t in BIZ_SET: continue`.
- Mutex : 0 conflit à chaque stage, C1 en résorbe 2 687 réels → 0 résiduel, assert final à 0.
- Déterminisme : deux exécutions seed 42 → MD5 identique.
- Amplitude inter-bandes préservée : 4,82 → 4,48 pp (semaine-employés), re-dérivée et concordante.

**🔴 Renvoyé — le titre « FAIL → PASS » ne se reproduit pas.** Écart taux-travail semaine-employés,
calculé de quatre façons naturelles directement depuis les deux CSV :

| Métrique (semaine, `LFTAG==1`) | ANCIEN | NOUVEAU | gate ≤ 2,4 pp |
|---|---|---|---|
| 48 slots, ancre complète | −7,04 | −6,38 | FAIL / FAIL |
| 32 slots non-BIZ, ancre complète | −3,96 | −2,97 | **FAIL / FAIL** |
| 32 slots non-BIZ, ancre réelle seule | −4,26 | −3,27 | FAIL / FAIL |
| 16 slots BIZ (hors périmètre Stage B) | −13,22 | −13,22 | inchangé |

Les quatre montrent une amélioration réelle et cohérente (+0,66 à +0,99 pp) : **le correctif
fonctionne**. Mais **aucune** ne tombe sur −2,62 → −1,96. La définition exacte de la métrique a été
redemandée sous forme de code exécutable.

#### ⚠️ Réconciliation — et **mon ancre était la mauvaise**

L'écart venait du **choix d'ancre**, réconcilié à 0,01 pp près. J'avais utilisé le fichier entier,
soit les quatre cycles GSS poolés (2005/2010/2015/2022, n = 14 237 réels). **C'est le mauvais
instrument** : juger une calibration ancrée sur 2022 contre une moyenne d'ère 2005-2022 fait entrer
des régimes de travail pré-COVID dans la référence. L'employé avait raison de prendre 2022 seul
(n = 2 708 réels) ; j'aurais dû filtrer `CYCLE_YEAR` avant de le contredire.

Matrice complète re-dérivée par le manager, `CYCLE_YEAR` en main :

| Ancre | Slots | ANCIEN | NOUVEAU |
|---|---|---|---|
| **2022 seul, réel** | **nonBIZ32** | **−1,91 PASS** | **−0,92 PASS** |
| 2022 seul, réel | all48 (mélange) | −2,62 FAIL | −1,96 PASS |
| 2022 seul, réel | BIZ16 | −4,05 FAIL | −4,05 FAIL (identique au bit) |
| tous cycles, réel | all48 | −7,18 | −6,52 |
| tous cycles, réel | nonBIZ32 | −4,26 | −3,27 |
| tous cycles, réel | BIZ16 | −13,02 | −13,02 |

**L'employé a ensuite sur-rétracté**, et c'est à corriger aussi : il a écrit que sur l'ancre 2022
restreinte aux slots non-BIZ le gate échouait « avant comme après ». Faux — c'est **−1,91 PASS →
−0,92 PASS**. Sur son propre périmètre et sa propre ère, le livrable était **déjà dans la tolérance
avant le correctif** et s'en éloigne deux fois moins après. Rétracter une affirmation non étayée
était juste ; rétracter au-delà de ce que disent les données est une autre forme d'erreur.

**Décision — la métrique de référence est : ancre 2022 seul, 32 slots non-BIZ**, parce que c'est
simultanément l'ère de la calibration et le périmètre du stage. `all48` est publié à côté, étiqueté
comme un **mélange** : (32 × −0,92 + 16 × −4,05)/48 = −1,963 et (32 × −1,91 + 16 × −4,05)/48 = −2,623,
soit exactement les deux chiffres observés. Le basculement FAIL → PASS sur `all48` ne vient donc
**pas** d'un progrès sur les heures ouvrées — il vient de la dilution de l'amélioration non-BIZ sur
48 slots, pendant que BIZ16 reste figé à −4,05.

**Ce qu'il faut retenir : c'est le choix d'ancre, pas le correctif, qui décide du verdict.**

**Conséquence de cadrage, corrigée** : le déficit sur les heures ouvrées que Stage B est *par
construction* interdit de toucher vaut **−4,05 pp sur l'ancre 2022** — et non les −13,02 pp que ma
lecture tous-cycles suggérait, chiffre que j'avais surestimé. Il reste la composante dominante de
l'écart `all48` et reste imputable au biais génératif du décodeur (§B.2.1, point 9), mais son ordre
de grandeur est trois fois plus petit qu'annoncé plus haut dans ce document.

**Pooling week-end (§A.7) — appliqué et vérifié** : cible poolée 0,0747 sur n = 208, SE 1,05 pp.
Samedi +1,03 → **+0,22 pp**, dimanche +0,02 → **−0,33 pp** ; les deux très à l'intérieur de la SE.
Nouveau livrable `_C_v2` MD5 `36159935`, 111 024 lignes ; canonique `_C` re-vérifié `7c105ef3`,
intact. Amplitude inter-bandes 4,82 → 4,48 pp, préservée.

### 2026-07-30 — R.1/R.2 re-spécifiés, et la vacuité découverte au passage

Gates R.1/R.2 rendus bande-conscients (`val.py:118-138` nouveau `_derive_retail_lever()`, `:517-589`),
faillibilité démontrée par perturbation en mémoire, 4 rapports régénérés. **Scorecards re-lus par le
manager directement dans le HTML** — la règle « ne pas croire un Progress Log même quand il atteint
exactement la cible annoncée » s'appliquait ici au premier degré, puisque le chiffre rendu était
précisément celui que j'avais annoncé attendre : 2022 FAIL 1 → 0, 2030 ×3 = 52P/7W/1F, FAIL survivant
= `Office band monotonicity` (préexistant, non-commerce). Conforme.

L'employé a signalé deux points ambigus **sans les corriger**, ce qui était la bonne décision : R.7
est une tautologie et R.4 est structurellement insatisfiable. Les deux vérifiés par le manager dans
le code et dans les rapports — avec une correction : **R.4 est aussi dégénéré en 2022**, donc
antérieur au levier. Voir §B.3.6, et l'audit de vacuité qui en découle.

### 2026-07-30 — Lot A CLOS après trois tours de réconciliation

Le Progress Log de `3rdJ_06_longitudinalForecasting_4split.md` porte désormais le récit complet :
revendication initiale flatteuse → contestation du manager (sur une mauvaise ancre) → sur-rétractation
de l'employé → correction bilatérale et matrice à six cellules. Décision de métrique de référence
inscrite avec sa justification code (`run_stage_B():455` tire sa cible de `CYCLE_YEAR==2022`,
`cap_band_stageB()` saute `BIZ_SET` en `:400-401`).

Dernier défaut attrapé et corrigé : le tableau PROOF 1 affichait les valeurs **week-end du build
d'avant le pooling** (−0,01 / −0,13) sous un en-tête « post-correctif `_v2` » — un seul tableau
décrivant deux builds. Rectifié en +0,22 / −0,33 avec la ligne de cible poolée (0,0747, n = 208,
SE 1,05 pp) rendue autoportante, et le tableau d'ablation étiqueté « pré-pooling » de bout en bout.
Aucun verdict ne changeait ; c'est précisément le défaut de chiffre périmé qui a déjà coûté deux
re-runs dans la journée, et il n'avait pas à être introduit par nous sur la dernière ligne.

### 2026-07-30 — B.2.2 exécuté (point 8), et une corroboration inattendue de §B.2.1

Relabel livré, scorecard gaté **inchangé** (GSS 66P/15W/5F, hôtel 17P/3W/2F ; seul l'INFO bouge
19 → 20) — exactement la signature attendue d'une correction d'étiquetage. Détail en §B.2.2.

Vérification manager : les trois taux de positifs de la **reconstruction** (76,58 / 10,11 / 2,20 %)
reproduits **exactement** sur une lecture indépendante. Ma référence observée différait (fichier
entier, n = 29 502) de la sienne (sous-ensemble 2022, n = 5 560) — la sienne est la bonne, et c'est
bien le n = 5 560 déjà établi en §B.2.3. La conclusion de rareté tient à l'identique sous les deux
références : le commerce est 35 à 42× plus creux que le domicile.

**Corroboration indépendante de §B.2.1** : le décodeur **sur-produit le domicile** (+5,16 pp) et
**sous-produit le travail** (−6,74 pp). Deux employés, deux chemins de code sans recouvrement, la
même histoire — et cohérent en signe et en ordre de grandeur avec les +8,91 / −10,99 pp de semaine
du gate 4.1. Le biais du décodeur n'est plus une hypothèse.

⚠️ *Chiffres corrigés le même jour* : ma lecture initiale donnait +10,30 / −9,28 pp parce qu'elle
comparait au fichier **entier** (4 cycles GSS poolés) au lieu du sous-ensemble 2022. Même erreur
d'ère que celle décrite en §A — les chiffres retenus sont ceux de l'employé, sur 2022 seul.

**Note de méthode.** Les trois chiffres que je tenais pour acquis en écrivant le Lot B et que
l'exécution a démentis : (a) « la section R est bonne telle quelle » — fausse, §B.3.3bis ; (b) le
scorecard Step-7 de référence 52P/7W/1F — périmé deux fois ; (c) l'hypothèse de départ du relais
manager sur 4.1.home/work — fausse (§B.2.1). Trois sur trois du côté des suppositions, zéro du côté
des chiffres re-dérivés. La règle tient.

### 2026-07-30 — D-12 exécuté, `_C_v2` PROMU, 7quater clos

**Ce que j'ai re-dérivé moi-même** (aucun de ces chiffres n'est repris d'un rapport d'employé) :

| Contrôle | Résultat | Instrument |
|---|---|---|
| Gate `5.2`, 3 bandes, avant/après | FAIL ×3 → **PASS ×3** | `verify_52.py` sur les deux livrables |
| Validateur Step-6 sur `5aa74f44` | GSS **69P/15W/2F** | relance complète, `--out-suffix _v2` |
| Identité des 2 FAIL restants | `4.1.home`, `4.1.work` | extraction des lignes FAIL du HTML |
| Mutex | **0** sur 5 329 152 cellules (`H&W`, `H&R`, `W&R`) | `verify_d12_mutex.py` |
| Écart samedi−dimanche domicile | **−0,02 pp** | idem |
| Métrique D-1 | **−0,92 pp**, inchangée par D-12 | `verify_lotA_final.py` |
| `BIZ16` | **−4,05 pp**, inchangé par les deux correctifs | idem |

**L'attente pré-enregistrée de D-12 a tenu**, ce qui est le point qui compte : je l'avais écrite
avant de connaître le résultat, et elle était falsifiable (« si 5.2 repasse FAIL, autre chose s'est
produit »). Elle n'a pas eu à être réinterprétée après coup.

**Promotion.** `7c105ef3` reste sur disque, intact, sous son nom — on a déplacé le pointeur, pas le
fichier (D-13). En le faisant, deux gates faux ont été trouvés **dans le chemin de promotion
lui-même** : l'allowlist H6 était un test de sous-chaîne (`"_C" in stem`), et `D2030_EXPECTED_MD5`
était déclaré côté validateur **sans jamais être lu**. Les deux sont maintenant réels, et le
nouveau verrou de lockstep a été **vu échouer** sur les deux modes de dérive avant d'être accepté.

**Ce que je n'ai pas fait passer pour mieux qu'il n'est.** Le nouveau F.1 n'est pas l'équivalent de
l'ancien : il prouve une condition *nécessaire* de la séparabilité, pas la séparabilité (D-8). La
preuve forte — build `--sens office` hors-diagonale + comparaison MD5 — est portée en ligne 2, où
elle coûte presque rien puisque les produits sont régénérés de toute façon. Et le compte de PASS
2030 **baisse** de 53 à 52 : c'est le prix d'arrêter de compter des gates qui ne pouvaient pas
échouer, pas une régression.

### 2026-07-30 — cascade Step-7 exécutée (ligne 2), et deux constats à contre-courant du rapport

Les 4 rapports canoniques sont rafraîchis (19:19), les anciens archivés dans
`outputs_step7/archive_pre_20260730/` (22 fichiers). `7c105ef3` re-vérifié intact après coup.

| Scénario | Avant cascade | Après | Cause |
|---|---|---|---|
| 2022 | 42P/11W/0F | **42P/11W/0F** | non rebâti (l'audit montre le stock 2022 insensible au changement de livrable) |
| 2030 ×3 | 52P/7W/1F | **53P/6W/1F** | `A.12` passe WARN → PASS : l'écart de mtime tombe de **115,2 h à 0,0 h** |

`A.12` continue de WARN sur 2022 — à juste titre, 2022 n'a pas été rebâti. Un gate qui distingue
les deux cas est un gate qui marche.

**Constat 1 — j'avais commandé un test vide.** Le rapport annonce « séparabilité CONFIRMÉE » sur la
foi de « tout identique au bit sur les 3 axes ». Mais *tout* identique — y compris l'axe visé —
c'est exactement ce qui prive le test de pouvoir discriminant. `:931-947` : `--sens X` met les
canaux hors-axe à `[]`, ils ne sont jamais écrits. Le test mesurait le périmètre d'écriture. La
preuve réelle est structurelle et je l'ai substituée : `build_retail_product_2030(retail_scenario)`,
**zéro** occurrence de `BAND` dans son corps — la bande bureau n'a pas de chemin d'entrée. Détail en
D-14. La corroboration empirique correcte existe et passe : le livrable 2030 a changé, les 6
fichiers commerce/hôtel 2030 sont restés identiques au bit.

**Constat 2 — l'unique FAIL est sur l'axe de la campagne, et il est vieux.** `E.3`,
`Office_Sales` : cons 0,4483 < hybrid 0,4630, alors que plus de télétravail devrait donner moins de
présence. Vérifié non-artefact (tient sur 24 h, +7,7 pp à 17 h) et vérifié **préexistant** (rapport
archivé : 0,4472 / 0,4616, même forme). Ni causé ni corrigé par la calibration — même classe que
D-9. Diagnostic lancé (D-15) : il bloque l'*interprétation* de l'axe bureau, pas l'exécution de la
campagne.

### 2026-07-30 — D-15 clos : ce n'était pas un défaut, et ce n'était pas non plus ce que j'avais dit

Diagnostic rendu, puis re-dérivé depuis les artefacts (`verify_d15_sales.py`,
`verify_d15_addendum.py`). **Cette fois le rapport est juste sur toute la ligne** : n = 201 contre
1 928 / 1 994, écart −1,46 pp, z = −0,33, population agrégée monotone 0,4641 / 0,4045 / 0,3585,
heure 17 plate à 0,1667 / 0,1689 / 0,1692. Tout se re-dérive au centième. Mécanisme confirmé à la
source : `NOCS` n'entre jamais dans l'appariement du donor-swap Step-6, la stratification est
emploi + classe WFH + AGEGRP. Les trois archétypes découpent une seule distribution aveugle à la
profession.

**Le contrôle que j'ai ajouté.** L'employé teste en non apparié. Si les trois bandes contenaient
les mêmes personnes, le test correct était l'apparié, et le verdict pouvait basculer de « bruit » à
« défaut ». C'était le seul angle par lequel « bruit » pouvait tomber, donc je l'ai fermé : SE
appariée 4,36 contre 4,40 non appariée. Rien. Le donor-swap re-tire le diaire entier, la corrélation
intra-personne est nulle. **Verdict robuste aux deux tests.**

**Ce que j'ai corrigé chez moi.** J'avais écrit dans D-15 que le pic à 17 h était « une anomalie de
timing de départ, pas de niveau ». Faux. À 17 h la population bureau agrégée est **plate** et les
**trois** archétypes y sont non monotones — il n'y a aucun signal de bande à cette heure, pour
personne. Ce qui sauve Knowledge et Public dans `E.3`, c'est le n dix fois plus grand sur la moyenne
9 h–17 h, pas une meilleure tenue horaire. J'avais lu une structure dans une excursion de petit
échantillon. Corrigé dans D-15 plutôt qu'effacé : c'est le genre d'erreur qui se recycle si on la
gomme.

**Ce que j'ai corrigé chez lui.** Sa conclusion — « Sales n'a pas l'échantillon pour résoudre
l'effet » — est trop faible et aurait coûté un archétype à l'interprétation de la campagne. Le test
de tendance dit l'inverse : pente **−5,58 pp/bande, z = −2,56**, et `cons − fully` z = +2,59. Sales
**résout l'effet de bout en bout**. Seul le pas adjacent `cons`/`hybrid` est hors puissance. Et les
trois pentes — −5,31 / −5,22 / −5,58 — sont indiscernables, ce qui **corrobore le mécanisme par un
angle qu'il n'avait pas utilisé** : c'est précisément ce que prédit une injection aveugle à la
profession. L'axe bureau reste lisible pour les trois archétypes.

**Disposition.** `E.3` reste FAIL accepté-documenté, seuil intact. Mais le vrai défaut n'est pas la
valeur : `E.3` chaîne des comparaisons adjacentes sans tenir compte de la puissance, donc il
échouera à chaque re-tirage sur l'archétype à n = 201, quel que soit l'état du pipeline. C'est un
gate qui mesure la taille d'échantillon en croyant mesurer le télétravail. Révision inscrite en
ligne 2ter, **non appliquée** : une redéfinition de gate ne se glisse pas dans une cascade de
calibration.

Un rapport exact peut porter une conclusion trop faible, et une conclusion trop faible coûte aussi
cher qu'une fausse — ici, un archétype abandonné à tort. Prochaine ligne : **10**, re-simuler les 7
cellules de probe.

### 2026-07-30 — ligne 10 lancée, après avoir découvert que son motif était faux (D-16)

En allant lancer la re-simulation, j'ai vérifié le motif que j'avais moi-même inscrit en ligne 10 —
« `INJ_HASH` a changé, `campaign_5670f602/` périmé ». **Faux des deux côtés.** `INJ_HASH` fingerprint
l'**injecteur** (`commercial_integration.py`) et possède le chemin de sortie ; une reconstruction de
produits Step-7 ne le déplace pas — c'est `INPUTS_HASH` qui bouge, et cette séparation *est* le
correctif du Défaut 3, déjà en place depuis le 28/07.

Ce que la vérification a fait remonter est **plus sérieux** que ce que j'avais écrit : le scorecard
§P clos à **25P/0W/0F** l'a été **sur le cluster avec l'injecteur `5670f602`**, alors que l'injecteur
local est `cf69d508` depuis le 28/07 — un correctif `classify_tag2()` résidentiel/résidentiel-commun
venu d'une session concurrente. Donc ce scorecard est périmé pour **deux motifs indépendants** :
câblage *et* produits. Je n'en avais correctement noté aucun des deux. Et le motif faux était
dangereux dans un sens précis : s'il avait laissé croire que seul `INPUTS_HASH` avait bougé, on
aurait pu conclure le câblage inchangé et sauter la re-validation du canal résidentiel — **le seul
que `classify_tag2()` touche**. Détail en D-16.

Bonne nouvelle structurelle au passage : `INJ_HASH` possédant le chemin, les résultats cluster
restent sous `campaign_5670f602/` et la re-simulation écrit sous `campaign_cf69d508/`. **Les chemins
se séparent d'eux-mêmes** — l'arborescence enregistre la divergence au lieu de la masquer, et aucun
`--allow-stale-inputs` n'est nécessaire. Dry-run : 7 cellules à faire, 0 sautée. Lancé : 6 workers,
watchdog mémoire 80 %, ~16 min/cellule.

**Et une preuve que j'avais sous-estimée.** En vérifiant quels produits les probes lisent, les mtimes
montrent que les 6 fichiers commerce/hôtel 2030 ont été **réellement réécrits** par la cascade
(19:17–19:18) — pas sautés — à partir d'un livrable résidentiel modifié, et ressortent **identiques
au md5**. La preuve structurelle de D-14 excluait une dépendance *déclarée* ; celle-ci exclut une
dépendance *cachée* (un état global au niveau module). Les deux ensemble fondent le factoriel
3×3×3 — c'est exactement ce que le test vide prétendait établir. D-14 renforcée.

Trois motifs vérifiés aujourd'hui, trois faux : la séparabilité (D-14), le mécanisme `Office_Sales`
(D-15), et celui-ci. Aucun n'a changé l'action à mener ; tous auraient mal orienté la suivante.

### 2026-07-30 — probes + scorecard clos (32P/0W/0F), et le canal résidentiel n'avait jamais tourné

**Lignes 10 et 11 faites.** 7/7 cellules `ok` exit=0 en **27,7 min** (12–18 min/cellule, 6 workers,
watchdog armé, aucune alerte mémoire). Scorecard §P : **32P / 0W / 0F / 10 INFO**, contre 25P/0W/0F
sur le cluster. Les 7 points supplémentaires sont réels, pas cosmétiques : les **6 gates
`INPUTS_HASH`** créés par le correctif du Défaut 3 sont pour la première fois **réellement
exercés** (ils confirment qu'un canal non varié garde exactement le même md5 de CSV d'une cellule à
l'autre), plus le P4 réparé.

**Le FAIL initial était un trou de portage, pas un défaut** — et je ne l'ai pas classé sans preuve.
`P4 banner` cherchait un nom de log **SLURM** qui n'existe pas en local, alors que la bannière était
bien imprimée (`_logs/fallback_retail.log:179`). Corrigé sur le **glob seul**, assertion inchangée,
puis **vu échouer** en retirant la ligne de bannière du log, puis log restauré et md5 re-vérifié
identique. Détail en D-18.

**🔴 La vraie trouvaille est ailleurs**, et elle vient d'un simple `INFO` que j'ai refusé de laisser
passer : `P1 residential -- NOT EXERCISED`. Les probes excluent le résidentiel **par conception** —
elles ne peuvent donc pas valider le canal qui est *le sujet de la recherche*. Et le smoke test
consigné au Progress Log de Step-8, celui qui atteste « chaîne complète prouvée de bout en bout »,
**précède de dix minutes** le câblage résidentiel. Exacte à sa date, fausse aujourd'hui.
`inject_residential()` n'avait donc **jamais** été exécuté — et la campagne allait être son premier
passage, sur 56 cellules et 3 heures.

Smoke campagne lancé avant tout run long : **27 Spaces, 27 ménages distincts** (graine 42, conforme
à OD-8R-L3), 54 horaires `MXU_Residential_Occ/Met_HH*`, `fallback=[]`, `ambiguous=[]`,
`n_carriers_neutralized=1` (le correctif 2J Bug A est actif). **§B est CLOS** — la doc Step-8 et la
mémoire projet qui le disaient « spécifié, non implémenté » étaient périmées. Détail en D-19.

**Reste avant la campagne** : un run **annuel complet** sur l'IDF **Calgary**, jamais exercé — 28
des 56 cellules en dépendent (ligne 11ter, en cours). L'item ouvert n° 2 (EPW Calgary taggé `_6B`
vs `Z7A`) est **déjà tranché avec chiffres** au Progress Log Step-8 : HDD18 4933/4852, cas
limite NECB 6/7A réel, fichier délibérément non renommé — pas un blocage.

Une preuve de fumée n'atteste que du code à l'instant où elle tourne. Quand le câblage change
ensuite, elle ne devient pas fausse — elle devient un piège, et d'autant plus efficace qu'elle est
authentique.

**Ce que je retiens des deux.** Le rapport de l'employé était exact sur chaque chiffre et faux sur
les deux verdicts qui comptaient : « séparabilité confirmée » (le test ne pouvait pas la confirmer)
et « pas un nouveau défaut, donc rien à signaler » (vrai, et c'est justement pourquoi il faut le
signaler). Les chiffres se re-dérivent ; les verdicts se re-instruisent.

### 2026-07-30 — ligne 11ter close, campagne lancée (D-20)

**Cellule Calgary — vérifiée sur l'artefact, pas sur la ligne de statut.** Le fichier de sortie de
la tâche de fond est revenu **vide** malgré `exit=0` : le statut ne prouvait rien. Re-dérivé depuis
le manifeste et le log EnergyPlus.

| Contrôle | Valeur |
|---|---|
| Durée | **6,6 min** (1 worker, sans contention) |
| `hourly_meters` / `channel_hourly` | **8760 / 8760** lignes |
| `ep_return_code` | **0** — « Completed Successfully », **0 Severe** |
| IDF | `CAN_CLG/TallBuilding_…_Z7A_v242.idf` — **lu dans le log**, pas dans le manifeste |
| EPW | `CAN_AB_Calgary-Canadian.Olympic.Park.Upper.712350_TMYx_6B.epw`, sizing « CALGARY-CANADIAN.OLYMPIC.PARK.UPPER » |
| Canaux | office 6 / retail 3 / hotel 3 / **résidentiel 27 Spaces, 27 ménages distincts** |
| `fallback` / `ambiguous` / `banner_lines` | `[]` / `[]` / `[]` |

Le manifeste ne consigne **pas** le fichier météo. Un manifeste propre sur une cellule `CLG` aurait
donc l'air identique si l'EPW de Montréal avait été utilisé par erreur — c'est le log qui ferme la
question, et c'est pour cela qu'il fallait l'ouvrir. *À corriger un jour : le chemin EPW mérite
d'être dans le manifeste.*

**Les 105 267 351 « Warnings » du bandeau final ne sont pas 105 M problèmes** — c'est le cumul
récurrent d'EnergyPlus compté par pas de temps. Le fichier ne contient que **478** lignes `** Warning **`
distinctes, dominées par du dimensionnement bénin (débit d'air minimal de zone 75, `GetOAControllerInputs`
62, `CalcEquipmentFlowRates` 47). 0 Severe. Vérifié plutôt que supposé, parce qu'un nombre à 9 chiffres
mérite qu'on l'ouvre.

**Ce que le run a appris en plus de ce qu'on lui demandait** : voir **D-20**. Le décompte de valeurs
distinctes par colonne montre que le résidentiel ne pilote **que** les personnes, là où les trois
canaux commerciaux pilotent aussi éclairage et prises. C'est `OD-7D`, verrouillé — mais la
conséquence (asymétrie de voies vers l'énergie, défavorable au canal qui est le sujet de la thèse)
n'était énoncée nulle part comme réserve de lecture. Elle l'est maintenant.

**Calgary n'est pas plus lente que Montréal** : 6,6 min seule contre 15,5–18,3 min par cellule à
6 workers pour les probes — soit un facteur de contention ≈ 2,7×, pas un surcoût climatique.
L'hypothèse de la doc Step-8 (« appliquer le même chiffre aux cellules CLG qu'à MTL ») est donc sûre,
et l'estimation 2,6–3,5 h tient.

**Campagne 56 runs LANCÉE** — 6 workers, watchdog mémoire à 80 %, reprise activée : 55 à exécuter,
la cellule 17 réutilisée telle quelle. Tous les bloqueurs documentés sont levés (§A, §B, §C clos ;
item ouvert n° 2 réglé ; D-16/D-18/D-19 traités). Reste ouvert, sans bloquer : **12bis / D-17**
(arbitrage utilisateur sur le filtre `IS_SYNTHETIC`) et la ligne **9** (biais génératif du décodeur).

**Ce que je retiens.** Deux fois de suite, le signal utile n'était pas dans le verdict mais dans une
colonne à côté : hier un `INFO` (« residential NOT EXERCISED ») qui cachait un canal jamais exécuté,
aujourd'hui un `nuniq` qui révèle une asymétrie de câblage sur une cellule par ailleurs parfaitement
valide. Un artefact qui passe tous ses gates a encore des choses à dire.
