# Prompt EMPLOYÉ — 3J Leg-3 Step 8, armement : étapes 1 + 2 (vérif stock v242 + AUDIT-W)
**Date : 2026-07-28 · Manager → Employé (Sonnet) · un seul handoff**

**Tu es l'employé. Exécute la tâche ci-dessous et ajoute une entrée `Progress Log` à la fin.**

Lis d'abord `CLAUDE.md` (racine repo) — règles cluster ABSOLUES. Puis
`3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/3rdJ_08_simulation_4split.md` (§2 8A–8E, §6b, §7)
et `..._4split_val.md` (§P). Ne lis PAS les gros CSV/IDF dans ton contexte — les scripts les lisent.

---

## État verrouillé (ne pas re-débattre)

- Steps 1–7 DONE ; Step 7 PRODUCT phase ACCEPTÉE.
- **Architecture Step 8 = B, tour mixte unique.** `TallBuilding_...v242.idf` **EST** la tour mixte :
  les 4 canaux y sont des `Space` natifs avec Tag 2 encodé sur l'objet `Space` → `classify_tag2()`
  matche en exact, **aucun greffage**. (Cadrage A = UBEM par archétype : rejeté, ne pas y revenir.)
- **Step 8 n'est PAS lancé.** Toi tu fais l'armement : étapes 1 et 2. Tu ne soumets AUCUNE campagne.

## Ta mission (3 tâches, dans l'ordre)

### A — Vérifier le stock v242 sur le scratch (login node OK)

Le stock transitionné v22.1→v24.2 a été produit en Leg-2 (job `1016780`, 2026-06-29) et vit sur le
scratch, pas dans le repo local. Doc §8B : « reuse Leg-2 transition — **verify, don't redo** ».
Si les 4 fichiers sont là et en Version 24.2 → 8B est PASS, **tu ne relances aucune transition**.

**Sur le cluster** (une ligne, `ls` = autorisé login node) :

```
ls -la /speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/outputs_step8/office_idfs_v242/CAN_MTL /speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/outputs_step8/office_idfs_v242/CAN_CLG
```

Attendu — 4 fichiers, ~29 juin 10:55–12:24 :
`CAN_MTL/{Tall,SuperTall}Building_90.1-2019_6A_Buffalo_NECB17_Z6_v242.idf`,
`CAN_CLG/{Tall,SuperTall}Building_90.1-2019_6A_Buffalo_NECB17_Z7A_v242.idf`.

Puis **un `grep` mono-fichier par IDF** (4 commandes séparées, autorisé) pour confirmer l'objet
Version : `grep -A2 -i "^  Version" <chemin_idf> | head -5` → doit montrer `24.2`.
Reporte taille + mtime + version dans un petit tableau (4 lignes).

**Si un fichier manque ou n'est pas en 24.2 → STOP, remonte au manager. N'improvise pas une
transition.** (Le v221 local existe, mais re-transitionner est hors périmètre de ce handoff.)

### B — AUDIT-W contre le VRAI IDF v242 (sbatch obligatoire)

Objectif : prouver que l'injection câble les schedules modulés sur le **bon champ** et que les
séries modulées **diffèrent** du baseline. C'est le garde-fou du bug Leg-2 où 7 scénarios bureau
simulaient byte-identique en silence. **W-FAIL bloque le Step 8 inconditionnellement.**

**B1. Écrire** `3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/3rdJ_08W_audit_wiring.py` (localement).
Spéc, dans l'ordre, sortie = **un petit rapport texte**, jamais un dump d'IDF :

1. `EPLUS_IDD` lu depuis l'env (voir B3) ; import de `commercial_integration` depuis le tree uploadé.
2. **Recensement Tag-2** : parcourir les `Space` de l'IDF v242 MTL Tall, appliquer `classify_tag2()`,
   imprimer le compte par canal + total. Attendu (à confirmer, pas à forcer) :
   résidentiel 30 · bureau 33 · commerce 9 · hôtel 25 · service/MEP 63 · total 164 Spaces ;
   **`unknown` doit être 0** — tout `unknown` > 0 = WARN listé (max 10 tags distincts imprimés).
3. **Injection** via `inject_mixed_use()` (`eSim_bem_utils/commercial_integration.py` L284) :
   - `idf_path` = `CAN_MTL/TallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v242.idf`
   - `output_path` = `$SCRATCH8/audit_w/TallBuilding_Z6_v242_injected.idf`
   - `channels` = `{"office": {"csv": office_presence_multiplier_2022.csv, "archetype": "Office_Knowledge", "band": "observed"}, "retail": {"csv": retail_presence_multiplier_2022.csv, "pr": "QC"}, "hotel": {"csv": hotel_schedule_multiplier_2022.csv, "pr": "QC"}}`
     (**`band="observed"` est la seule bande présente dans le CSV 2022** — vérifié ; ne pas inventer
     `hybrid`. MTL → `PR="QC"`.)
   - `building_meta` = `{"building": "Tall", "city": "MTL", "cz": "Z6", "purpose": "W-audit"}`
   - Imprimer `n_spaces` par canal + `fallback` + `ambiguous`. **`fallback` non vide = FAIL** (les
     3 CSV sont censés être là ; un fall-back silencieux, c'est exactement le piège W5/P4).
4. **W2** : rouvrir l'IDF injecté et appeler `assert_wiring(idf, expected_channels, verbose=True)`.
   `assert_wiring` ne lit que `expected_channels.values()` → passe un dict dont les **valeurs** sont
   les noms de schedules modulés retournés par l'injection (`result["modulated_schedule_names"]`).
   Attendu : 0 violation, N objets PEOPLE audités (imprimer N).
5. **W3 — à implémenter DANS TON SCRIPT, pas dans le module.** ⚠️ Le docstring d'`assert_wiring`
   (L437-446) annonce W2 **et** W3, mais le code L447-461 ne fait que W2 : la comparaison
   « série modulée ≠ baseline » n'existe pas. **Ne modifie pas `commercial_integration.py`** —
   implémente W3 dans l'audit et signale l'écart au manager dans le Progress Log.
   W3 = pour chaque schedule modulé, comparer les valeurs du `Schedule:Compact` injecté à celles du
   `Schedule:Compact` baseline (relire l'IDF source non injecté) ; imprimer par canal
   `n_slots_differents / n_slots_total` et `max|Δ|`. **Un canal avec 0 slot différent = W3 FAIL.**
6. **W6 (bonus, gratuit)** : compter les occurrences des noms de champs pré-v24.2
   (`_PRE_V242_FIELD_NAMES` = `Zone_or_ZoneList_Name`, `Zone_Name`) sur les objets touchés → doit
   être 0. Non bloquant, à reporter.
7. Terminer par un **scorecard** `W2/W3/W6 + Tag-2 census` : `n PASS / n WARN / n FAIL`, et
   `exit(1)` si un FAIL. Écrire le rapport dans `$SCRATCH8/logs/8W_audit_<jobid>.out` (via la
   redirection `--wrap`) — pas de fichier binaire, pas de dump.

**B2. Uploader** (localement, une ligne chacune ; `SCRATCH8=/speed-scratch/o_iseri/step8_4split`) :

```
scp "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\eSim_bem_utils\commercial_integration.py" o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/step8_4split/upload/eSim_bem_utils/
```
```
scp "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg3_4-split\Step7_docs\outputs_step7\office_presence_multiplier_2022.csv" "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg3_4-split\Step7_docs\outputs_step7\retail_presence_multiplier_2022.csv" "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg3_4-split\Step7_docs\outputs_step7\hotel_schedule_multiplier_2022.csv" o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/step8_4split/upload/3J_docs_occ_nTemp/Leg3_4-split/Step7_docs/outputs_step7/
```
```
scp "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg3_4-split\Step8_docs\3rdJ_08W_audit_wiring.py" o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/step8_4split/upload/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/
```

(Crée les dossiers d'abord si besoin : `mkdir -p` en une ligne sur le cluster — autorisé.)

**§6b — inventaire md5 aux DEUX bouts AVANT de soumettre** : md5 local vs cluster pour les 3 CSV +
`commercial_integration.py` + le script d'audit. Local : `certutil -hashfile <f> MD5` (PowerShell).
Cluster : `md5sum <f>` mono-fichier. **Un md5 divergent = re-upload, pas de soumission.**

**B3. Soumettre** (sur le cluster, UNE ligne, `sbatch` fire-and-forget, `-t 7-00:00:00`) :

```
sbatch -p ps --mem=16G -t 7-00:00:00 --job-name=3J_8W_audit --wrap "cd /speed-scratch/o_iseri/step8_4split/upload/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs && mkdir -p /speed-scratch/o_iseri/step8_4split/logs /speed-scratch/o_iseri/step8_4split/audit_w && setenv EPLUS_IDD /home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/Energy+.idd && setenv PYTHONPATH /speed-scratch/o_iseri/step8_4split/upload && /speed-scratch/o_iseri/envs/step4/bin/python 3rdJ_08W_audit_wiring.py > /speed-scratch/o_iseri/step8_4split/logs/8W_audit.out"
```

- Le shell du `--wrap` est **tcsh** sur Speed → `setenv VAR val` (PAS `export`), séparateurs `&&`.
  Si tcsh renâcle sur la chaîne, bascule sur un `.sh` `#!/bin/bash` avec en-têtes `#SBATCH`
  (`-t 7-00:00:00`, `--output=/speed-scratch/o_iseri/step8_4split/logs/8W_audit_%j.out`) et
  `sbatch ce_fichier.sh` — **jamais** un wrapper dans `/tmp` (noexec sur les nœuds de calcul).
- Vérifie d'abord que l'IDD existe (`ls` mono-chemin) ; s'il n'est pas là, cherche-le sous
  `/home/o/o_iseri/ep_install/` (`ls`, profondeur bornée) et remonte le chemin trouvé.
- Python cluster : `/speed-scratch/o_iseri/envs/step4/bin/python` (eppy + pandas). Si `import eppy`
  échoue **dans le job**, remonte au manager — n'installe rien, ne teste rien sur le login node.
- Note le job id, puis **attends**. Relecture du log : `tail -60 <log>` mono-fichier, **≥ 30 min
  d'espacement**, pas de boucle de polling.

### C — Journaliser

Ajoute un `Progress Log` daté à la fin de `Step8_docs/3rdJ_08_simulation_4split.md` :
tableau des 4 IDF v242 (taille/mtime/version), job id de l'audit-W, recensement Tag-2 observé vs
attendu, scorecard W2/W3/W6, et l'écart `assert_wiring` W3-non-implémenté. Coche 8B dans la
checklist si PASS.

## Livrables

1. Tableau de vérification des 4 `*_v242.idf` (existence + Version 24.2) → verdict 8B PASS/FAIL.
2. `3rdJ_08W_audit_wiring.py` (nouveau) + job id + scorecard W2/W3/W6 + recensement Tag-2.
3. Entrée Progress Log.
4. Ligne finale : **GO / NO-GO pour les probes §P** (étape 3), avec la raison en une phrase.

## Garde-fous (non négociables)

- 🔴 `sbatch` uniquement, fire-and-forget. **Zéro `python`/`python3` sur le login node**, même un
  `-c` d'une ligne. Autorisé login node : `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `cd`,
  `ls`, `mkdir`, `scp`, `module load`, `tail`/`head`/`grep`/`wc -l`/`cat` **mono-fichier**.
- 🔴 `-t 7-00:00:00` sur CHAQUE soumission, même pour un audit de 30 s.
- Commandes cluster = **une seule ligne**, `cd`-first, labellisées « localement » / « sur le cluster ».
- **Ne JAMAIS assouplir un seuil** pour effacer un FAIL → relabel + documente avec preuve.
- **Ne modifie pas** `commercial_integration.py` (W3 va dans ton script), ni les fichiers ML protégés
  (`eSim_datapreprocessing.py`, `eSim_dynamicML_mHead.py`, `eSim_dynamicML_mHead_alignment.py`).
- **Ne lance NI les probes §P NI la campagne 56 runs.** Ce handoff s'arrête à l'audit-W.
- Blocage ou résultat inattendu → remonte au manager, n'improvise pas de contournement.
