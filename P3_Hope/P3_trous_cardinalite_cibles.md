# P3 — Trous, cardinalité, cibles

Enchaînement : **1.6 Trous → 1.4 Cardinalité (après 1.3 Typer) → 1.9 Cibles**. Généré par `python P3_Hope/p3_trous_cardinalite_cibles.py` le 2026-11-09 09:47, sur `train.csv` (60 816 lignes) et `a_decider.csv` (15 204 lignes), tables entières.

## Les décisions, en une page

| # | Constat mesuré | Décision |
|---|---|---|
| 1 | `var3 = -999999` : vrai manquant, 88 clients de train | remplacer par 2, la valeur dominante |
| 2 | `delta_ = 9999999999` : variation depuis une base nulle (apparition) | remplacer par la plus grande variation finie + 1 ; pas d'imputation |
| 3 | `var38` : une valeur de remplissage chez 20 % des clients, sans effet sur le taux | garder ; essai « manquant + indicateur » au bloc 2 |
| 4 | `var36 = 99` : code d'absence chez 40 % des clients, taux de mécontents le plus haut | encoder en catégories |
| 5 | les zéros sont des mesures (pas d'opération) | garder ; essai « nombre de valeurs non nulles » |
| 6 | 36 colonnes constantes sur train (et non 97) | les supprimer |
| 7 | 110 quasi constantes (≤ 60 clients hors valeur dominante) ; 4 ont un effet réel (24 à 28 % de mécontents, test binomial) | supprimer les 106 autres ; garder `imp_op_var40_efect_ult1`, `imp_op_var40_efect_ult3`, `num_op_var40_efect_ult1`, `num_op_var40_efect_ult3` ; essai avec / sans |
| 8 | 3,96 % de mécontents, validation à ~481 mécontents | stratifier tout découpage ; comparer les essais en validation croisée |
| 9 | des dossiers identiques de cibles opposées | bruit irréductible : AUC max < 1 |

## 1.6 — Trous

**Valeurs vides (`NaN`) : 0** dans les deux tables. Les trous existent pourtant : ils sont **codés**. Quatre codes trouvés, quatre décisions.

### `var3 = -999999` — un vrai manquant

- 88 clients dans train, 28 dans a_decider.
- Taux de mécontents : 1.14 % (88 clients) contre 3.96 % (60 728 clients).
- La valeur `2` occupe 97.53 % des clients.
- **Décision : remplacer par `2`**, la valeur dominante. Un indicateur « manquant » reposerait sur 1 mécontent(s) : il n'apprendrait rien de fiable.

### `delta_ = 9999999999` — pas un manquant : une apparition

- Code présent dans 26 colonnes `delta_` sur 26, chez 421 clients de train.
- Vérification sur `delta_imp_aport_var13_1y3` (291 lignes codées) : `imp_aport_var13_hace3` vaut **toujours 0** (max 0) et `imp_aport_var13_ult1` est **toujours positif** (min 300). La variation part de zéro : division par zéro, codée « infini ».
- Symétriquement, `-1` = le montant a **disparu** (base > 0, récent = 0) : 1389 clients.
- Plus grande variation finie, toutes colonnes `delta_` : **8.00**.
- Taux de mécontents : 1.90 % (421 clients) chez les clients avec une apparition, contre 3.97 % (60 395 clients).
- **Décision : remplacer `9999999999` par `9`** (juste au-dessus de la plus grande variation finie). L'ordre est gardé (une apparition reste la plus forte hausse) sans écraser l'échelle pour les modèles linéaires. Ce n'est **pas** un trou : aucune imputation.

### `var38 = 117310.979016…` — un trou déguisé

- `var38` a 46 577 valeurs différentes, mais **une seule** revient chez **12 012 clients (19.75 %)**. La suivante revient 12 fois. Un montant à six décimales partagé par un client sur cinq n'est pas un montant : c'est une valeur de remplissage (probablement une moyenne).
- Taux de mécontents : 4.06 % (12 012 clients) contre 3.93 % (48 804 clients) — **pas de différence nette**.
- **Décision : garder `var38` telle quelle** pour le premier pipeline. **Essai à journaliser au bloc 2** : remplacer la valeur par un manquant + indicateur `var38_rempli`, et mesurer si l'AUC bouge.

### `var36 = 99` — un code d'absence qui parle

| var36 | taux de mécontents | clients |
|---|---|---|
| 0 | 0.00 % | 321 |
| 1 | 3.03 % | 11 718 |
| 2 | 2.75 % | 6 955 |
| 3 | 1.63 % | 17 784 |
| 99 | 6.54 % | 24 038 |

- `99` concerne 39.53 % des clients et porte le **plus fort** taux de mécontents. Lu comme un nombre, 99 serait « très loin » de 3 : c'est faux, c'est une **catégorie**.
- **Décision : encoder `var36` en catégories** (une colonne 0/1 par valeur). Ne pas l'imputer : l'absence est elle-même une information.

### Les zéros — pas des trous

- 217 colonnes sur 369 sont nulles à plus de 99 %. Un zéro dit « pas de produit, pas d'opération » : c'est une **mesure**, pas un manque. Les remplacer par une moyenne détruirait l'information.
- Le **nombre de valeurs non nulles** d'un client sépare déjà les mécontents :

| valeurs non nulles | taux de mécontents | clients |
|---|---|---|
| 8 à 14 | 8.43 % | 12 709 |
| 15 à 29 | 2.90 % | 19 415 |
| 30 à 32 | 2.07 % | 5 468 |
| 33 à 49 | 2.47 % | 11 383 |
| 50 à 149 | 3.18 % | 11 841 |

- **Décision : garder les zéros.** **Essai proposé au constructeur** : ajouter la variable « nombre de valeurs non nulles » et mesurer son apport.

## 1.4 — Cardinalité

Préalable (1.3) : toutes les colonnes sont numériques (`int64` / `float64`), les `ind_` valent 0 ou 1. On peut donc compter les valeurs distinctes sans conversion.

### Colonnes constantes

- Sur les 4 000 premières lignes : 115 constantes. Sur **tout** train : **36**. L'énoncé (97, sur un échantillon de 4 000) surestime : un échantillon rend constantes des colonnes qui ne le sont pas. **On décide sur la table entière.**
- 2 d'entre elles varient dans a_decider (imp_reemb_var17_hace3, num_reemb_var17_hace3) : le modèle n'en a jamais vu qu'une valeur, il ne peut rien en apprendre.
- **Décision : supprimer les 36 colonnes constantes sur train.**

<details><summary>Liste des colonnes supprimées</summary>

`imp_amort_var18_hace3`, `imp_amort_var34_hace3`, `imp_reemb_var13_hace3`, `imp_reemb_var17_hace3`, `imp_reemb_var33_hace3`, `imp_trasp_var17_out_hace3`, `imp_trasp_var33_out_hace3`, `ind_var2`, `ind_var27`, `ind_var27_0`, `ind_var28`, `ind_var28_0`, `ind_var2_0`, `ind_var41`, `ind_var46`, `ind_var46_0`, `num_reemb_var13_hace3`, `num_reemb_var17_hace3`, `num_reemb_var33_hace3`, `num_trasp_var17_out_hace3`, `num_trasp_var33_out_hace3`, `num_var27`, `num_var27_0`, `num_var28`, `num_var28_0`, `num_var2_0_ult1`, `num_var2_ult1`, `num_var41`, `num_var46`, `num_var46_0`, `saldo_medio_var13_medio_hace3`, `saldo_var27`, `saldo_var28`, `saldo_var2_ult1`, `saldo_var41`, `saldo_var46`

</details>

### Colonnes quasi constantes

- **110** colonnes ont une valeur qui occupe au moins 99,9 % des lignes : au plus 60 clients s'en écartent. À 3.96 %, on attend **≈ 2.4 mécontents** parmi eux.
- Mécontents trouvés parmi ces clients « rares », colonne par colonne : 0 → 94 colonnes, 1 → 12 colonnes, 8 → 4 colonnes.
- Test binomial (le taux des clients rares diffère-t-il de 3.96 % ?) : **4 colonnes** ont un écart réel (p < 0.01 / 110 = 9e-05, correction de Bonferroni puisqu'on teste 110 colonnes à la fois) :

| colonne | clients rares | mécontents parmi eux | taux | p |
|---|---|---|---|---|
| imp_op_var40_efect_ult1 | 29 | 8 | 27.59 % | 1.2e-05 |
| imp_op_var40_efect_ult3 | 33 | 8 | 24.24 % | 3.4e-05 |
| num_op_var40_efect_ult1 | 29 | 8 | 27.59 % | 1.2e-05 |
| num_op_var40_efect_ult3 | 33 | 8 | 24.24 % | 3.4e-05 |

- Ces clients rares sont **6 à 7 fois plus souvent mécontents** que la moyenne : supprimer ces colonnes jetterait un vrai signal, même s'il ne repose que sur une poignée de mécontents.
- Pour les 106 autres, l'écart n'est pas distinguable du hasard : du bruit que le modèle risque d'apprendre par cœur.
- **Décision : supprimer 106 quasi constantes, garder les 4 qui ont un effet mesuré.** **Essai à journaliser** : AUC avec et sans les 106, et temps gagné.

### Ce qui reste, et comment le traiter

Après suppression : **227 variables** sur 369.

| famille | 2 (binaire) | 3 à 10 | 11 à 100 | > 100 |
|---|---|---|---|---|
| delta | 0 | 2 | 2 | 0 |
| imp | 0 | 0 | 4 | 19 |
| ind | 53 | 0 | 0 | 0 |
| isolée | 0 | 1 | 2 | 2 |
| num | 6 | 50 | 39 | 1 |
| saldo | 0 | 0 | 6 | 40 |

- **Variables isolées** : `var15` (99 valeurs, de 5 à 104 : un âge) et `var38` (46 577 valeurs) sont continues. `var36` (5 valeurs) est une catégorie (voir 1.6). `var3` a 195 valeurs, mais `2` en occupe 97.53 % (3.99 % de mécontents, contre 2.73 % pour les autres valeurs). `var21` : 22 valeurs, nulle à 98.87 %.
- **131 colonnes `num_` sur 143 ne contiennent que des multiples de 3** : les comptages sont codés × 3. Sans effet sur les arbres et sur l'AUC ; à savoir avant d'interpréter un comptage.
- **Décision : `var36` en catégories, tout le reste en numérique.** Aucune variable à forte cardinalité n'est une catégorie déguisée : pas d'encodage cible à risque de fuite.
- Les colonnes strictement identiques entre elles relèvent de **1.7 Doublons (P4)**.

## 1.9 — Cibles

### La cible

- `TARGET` vaut 0 ou 1, jamais vide. **2 406 mécontents sur 60 816 = 3.96 %** (intervalle à 95 % : 3.80 % à 4.11 %).
- **1 mécontent pour 24 satisfaits.** Prédire « satisfait » pour tous : 96.04 % d'exactitude, zéro mécontent trouvé.
- Attendus dans a_decider au même taux : **≈ 602** (énoncé : 602).

### À quoi ressemble un mécontent

**Par âge (`var15`)**

| âge | taux de mécontents | clients |
|---|---|---|
| 22 ans et moins | 0.00 % | 963 |
| 23 à 25 | 0.91 % | 24 536 |
| 26 à 30 | 4.24 % | 9 349 |
| 31 à 40 | 6.58 % | 11 746 |
| 41 à 50 | 7.71 % | 7 539 |
| 51 à 60 | 7.80 % | 3 757 |
| 61 et plus | 4.78 % | 2 926 |

- **Aucun** mécontent jusqu'à 22 ans (963 clients), moins de 1 % de 23 à 25 ans, puis le taux est multiplié par 8 après 40 ans.
- Clients **sans aucun montant** (`saldo_` et `imp_` tous nuls, 24.83 % des clients) : **9.14 %** de mécontents, contre 2.24 % pour les autres.
- `var36 = 99` : 6.54 % (voir 1.6).
- Portrait : un client **de plus de 30 ans, avec peu de produits et des comptes vides**.

### La part que personne ne peut prédire

- **1 994 clients** ont un dossier identique à au moins un autre client **de cible opposée** ; ils comptent **256 mécontents** (10.64 % des mécontents). À dossier égal, aucun modèle ne peut les départager : c'est du **bruit de cible** irréductible.
- Conséquence : l'AUC maximale atteignable est **inférieure à 1** ; ne pas s'acharner sur ces lignes.

### Ce que le petit nombre de mécontents fait à la mesure

- La validation (20 %, graine 42) ne contient que **481 mécontents**.
- AUC de la règle métier (`var15`) sur la validation : 0.6903, avec un **écart-type de ±0.0099** (300 rééchantillonnages bootstrap).
- **Conséquence pour le protocole** : un écart de moins de ~0.020 entre deux essais n'est pas distinguable du hasard. Battre le plancher (0.689) de 0,005 ne prouve rien. Le mesureur devrait comparer les essais en **validation croisée stratifiée** (5 plis, même graine) pour réduire ce bruit.
- Sans stratification, sur 20 tirages de 5 plis (`KFold` mélangé), le nombre de mécontents par pli va de **433 à 525** (attendu 481) : des plis plus ou moins « faciles », qui ajoutent du bruit à la comparaison.
- **Décision : stratifier tout découpage sur `TARGET`** (chaque pli garde exactement 3,96 % de mécontents).

*Calculé en 17 s.*
