# Audit des données — phase 1

Généré par `python audit_phase1.py` le 2026-11-09 09:48. Découpage : 80 / 20 stratifié, graine 42.

## 1.1 — Inventorier les tables

| fichier | Mo | lignes | colonnes |
|---|---|---|---|
| a_decider.csv | 15.1 | 15 204 | 370 |
| train.csv | 60.5 | 60 816 | 371 |

- Colonnes présentes seulement dans `train.csv` : ['TARGET']
- Colonnes présentes seulement dans `a_decider.csv` : aucune

**Familles de colonnes (train.csv)**

|  | mesuré | énoncé | écart |
|---|---|---|---|
| ID | 1 | 1 | 0 |
| TARGET | 1 | 1 | 0 |
| delta | 26 | 26 | 0 |
| imp | 49 | 49 | 0 |
| ind | 75 | 75 | 0 |
| isolée | 5 | 6 | -1 |
| num | 143 | 143 | 0 |
| saldo | 71 | 71 | 0 |

- Variables isolées : var3, var15, var36, var21, var38. Les familles de l'énoncé totalisent 372 colonnes pour 371 : l'énoncé compte une variable isolée de trop.

*(0.8 s)*

## 1.2 — Charger et compter

- Chargement des deux tables : **0.7 s** (mémoire : 181 Mo + 45 Mo)
- `train.csv` : 60 816 lignes × 371 colonnes ✓
- `a_decider.csv` : 15 204 lignes × 370 colonnes ✓
- Mécontents dans `train.csv` : **2 406** sur 60 816 = **3.96 %**
- Total des deux tables : 76 020 clients (énoncé : 76 020)
- `ID` : train de 1 à 151838, a_decider de 13 à 151813

*(0.0 s)*

## 1.3 — Typer

**Types lus par pandas, par famille**

| famille | float64 | int64 |
|---|---|---|
| delta | 10 | 16 |
| imp | 39 | 10 |
| ind | 0 | 75 |
| isolée | 1 | 4 |
| num | 0 | 143 |
| saldo | 61 | 10 |

- Colonnes lues en `float` mais qui ne contiennent que des entiers : **0**
- Colonnes texte (`object`) : aucune — tout est numérique
- Colonnes `ind_` qui ne sont pas 0/1 : aucune
- Mémoire en réduisant les types : 226 Mo → **94 Mo**

*(2.3 s)*

## 1.4 — Cardinalité

- Constantes sur les 4 000 premières lignes de train : **115** (énoncé : 97)
- Constantes sur tout `train.csv` : **36**
- Constantes sur train + a_decider : **34**
- Constantes dans train mais **variables dans a_decider** : ['imp_reemb_var17_hace3', 'num_reemb_var17_hace3']
- Quasi constantes (une valeur ≥ 99,9 % des lignes, hors constantes) : **110**

**Nombre de valeurs distinctes (train), par famille**

| famille | 1 (constante) | 2 | 3 à 10 | 11 à 100 | > 100 |
|---|---|---|---|---|---|
| delta | 0 | 12 | 12 | 2 | 0 |
| imp | 7 | 2 | 10 | 11 | 19 |
| ind | 9 | 66 | 0 | 0 | 0 |
| isolée | 0 | 0 | 1 | 2 | 2 |
| num | 14 | 24 | 65 | 39 | 1 |
| saldo | 6 | 5 | 7 | 13 | 40 |

*(1.2 s)*

## 1.5 — Valeurs impossibles

Sentinelles cherchées : (-999999, 9999999999). Une valeur négative est impossible pour un comptage (`num_`) ou un indicateur (`ind_`).

| colonne | famille | sentinelles | négatifs (num/ind) | min | max |
|---|---|---|---|---|---|
| delta_imp_aport_var13_1y3 | delta | 370 | 0 | -1.0000 | 9 999 999 999 |
| delta_num_aport_var13_1y3 | delta | 370 | 0 | -1.0000 | 9 999 999 999 |
| var3 | isolée | 116 | 0 | -999 999.0000 | 238.0000 |
| delta_num_compra_var44_1y3 | delta | 70 | 0 | -1.0000 | 9 999 999 999 |
| delta_imp_compra_var44_1y3 | delta | 70 | 0 | -1.0000 | 9 999 999 999 |
| delta_num_venta_var44_1y3 | delta | 42 | 0 | -1.0000 | 9 999 999 999 |
| delta_imp_venta_var44_1y3 | delta | 42 | 0 | -1.0000 | 9 999 999 999 |
| delta_imp_aport_var17_1y3 | delta | 39 | 0 | -1.0000 | 9 999 999 999 |
| delta_num_aport_var17_1y3 | delta | 39 | 0 | -1.0000 | 9 999 999 999 |
| delta_num_reemb_var13_1y3 | delta | 38 | 0 | 0.0000 | 9 999 999 999 |
| delta_imp_reemb_var13_1y3 | delta | 38 | 0 | 0.0000 | 9 999 999 999 |
| delta_num_reemb_var17_1y3 | delta | 20 | 0 | -1.0000 | 9 999 999 999 |
| delta_imp_reemb_var17_1y3 | delta | 20 | 0 | -1.0000 | 9 999 999 999 |
| delta_num_trasp_var33_in_1y3 | delta | 5 | 0 | -1.0000 | 9 999 999 999 |
| delta_imp_trasp_var33_in_1y3 | delta | 5 | 0 | -1.0000 | 9 999 999 999 |
| delta_imp_trasp_var17_in_1y3 | delta | 4 | 0 | -1.0000 | 9 999 999 999 |
| delta_num_trasp_var17_out_1y3 | delta | 4 | 0 | 0.0000 | 9 999 999 999 |
| delta_imp_trasp_var17_out_1y3 | delta | 4 | 0 | 0.0000 | 9 999 999 999 |
| delta_num_trasp_var17_in_1y3 | delta | 4 | 0 | -1.0000 | 9 999 999 999 |
| delta_imp_amort_var18_1y3 | delta | 2 | 0 | 0.0000 | 9 999 999 999 |
| delta_imp_amort_var34_1y3 | delta | 2 | 0 | 0.0000 | 9 999 999 999 |
| delta_imp_reemb_var33_1y3 | delta | 1 | 0 | 0.0000 | 9 999 999 999 |
| delta_imp_aport_var33_1y3 | delta | 1 | 0 | -1.0000 | 9 999 999 999 |
| delta_num_aport_var33_1y3 | delta | 1 | 0 | -1.0000 | 9 999 999 999 |
| delta_imp_trasp_var33_out_1y3 | delta | 1 | 0 | 0.0000 | 9 999 999 999 |
| delta_num_reemb_var33_1y3 | delta | 1 | 0 | 0.0000 | 9 999 999 999 |
| delta_num_trasp_var33_out_1y3 | delta | 1 | 0 | 0.0000 | 9 999 999 999 |

- `var3` = -999999 : **116** lignes
- `var15` : de 5 à 105 (à vérifier si c'est un âge)
- Soldes `saldo_` négatifs (possibles : découvert) : 14 colonnes

*(0.6 s)*

## 1.6 — Trous

- Valeurs vides (`NaN`) : **0**
- Valeurs manquantes **codées** (sentinelles (-999999, 9999999999)) : **1310** cellules, dans 27 colonnes (détail en 1.5)

**Part de zéros par famille** (un zéro n'est pas un trou : c'est souvent « pas d'opération »)

|  | colonnes | part de zéros moyenne | médiane | minimum |
|---|---|---|---|---|
| delta | 26.0000 | 0.9976 | 0.9997 | 0.9727 |
| imp | 49.0000 | 0.9680 | 0.9995 | 0.8454 |
| ind | 75.0000 | 0.9123 | 0.9957 | 0.0045 |
| isolée | 5.0000 | 0.1990 | 0.0010 | 0.0000 |
| num | 143.0000 | 0.8893 | 0.9954 | 0.0045 |
| saldo | 71.0000 | 0.9222 | 0.9963 | 0.2672 |

- Colonnes nulles à plus de 99 % : **220** sur 369
- Clients de train sans aucun montant (`saldo_` et `imp_` tous nuls) : 24.83 % ; taux de mécontents chez eux : **9.14 %** contre 2.24 % chez les autres

*(0.8 s)*

## 1.7 — Doublons

- `ID` en double : train 0, a_decider 0, communs aux deux tables 0
- Lignes de train dont toutes les variables (hors ID) existent ailleurs dans train : **4572**
- Groupes de lignes identiques **avec des cibles différentes** : **113** groupes, 1994 lignes — même dossier, issues opposées : aucun modèle ne peut les séparer
- Clients de a_decider dont le dossier est identique à un dossier de train : **1130**
- Colonnes non constantes strictement identiques à une autre : **41** colonnes en trop, réparties en 26 groupes (les constantes sont traitées en 1.4)
  - num_var37_0, num_var37
  - num_reemb_var17_hace3, num_reemb_var33_ult1, num_trasp_var33_out_ult1
  - delta_imp_trasp_var17_in_1y3, delta_num_trasp_var17_in_1y3
  - num_var32_0, num_var32
  - num_var6, num_var13_medio_0, num_var13_medio, num_var18_0, num_var18, num_var29, num_var34_0, num_var34
  - ind_var20, ind_var7_recib_ult1
  - saldo_var13_medio, saldo_medio_var13_medio_ult1
  - ind_var26_0, ind_var26

*(1.9 s)*

## 1.8 — Fuites

**AUC de chaque variable prise seule (train entier)** — une valeur proche de 1 signalerait une fuite

|  | AUC |
|---|---|
| var15 | 0.7010 |
| saldo_var30 | 0.6952 |
| num_meses_var5_ult3 | 0.6930 |
| saldo_var42 | 0.6801 |
| num_var30 | 0.6795 |
| saldo_var5 | 0.6785 |
| saldo_medio_var5_hace2 | 0.6785 |
| saldo_medio_var5_ult1 | 0.6764 |
| saldo_medio_var5_ult3 | 0.6752 |
| ind_var30 | 0.6730 |
| num_var42 | 0.6694 |
| saldo_medio_var5_hace3 | 0.6692 |

- Variables à AUC > 0,80 : aucune
- AUC de l'`ID` seul : 0.5076 (≈ 0,5 attendu : l'ordre des dossiers ne doit rien dire)

**Train contre a_decider, variable par variable** (AUC ≈ 0,5 : les deux tables se ressemblent)

|  | AUC train/a_decider |
|---|---|
| var38 | 0.5028 |
| num_var22_ult1 | 0.5028 |
| num_meses_var5_ult3 | 0.5027 |
| saldo_medio_var5_hace3 | 0.5026 |
| saldo_medio_var5_hace2 | 0.5024 |

Règle du cours : aucune information inconnue à l'ouverture du dossier. Les colonnes `delta_` (variations entre deux dates) sont à vérifier en priorité : leurs deux dates doivent précéder la plainte.

*(18.7 s)*

## 1.9 — Cibles

- Valeurs prises par `TARGET` : [0, 1], manquantes : 0
- Mécontents : **2 406** / 60 816 = **3.96 %** (intervalle à 95 % : 3.80 % – 4.11 %)
- Satisfaits : 58 410. Rapport : **1 mécontent pour 24 satisfaits**
- Découpage 80 / 20 stratifié (graine 42) : 1925 mécontents en apprentissage, **481** en validation (3.95 %)
- Attendu dans `a_decider.csv` au même taux : ≈ 602 mécontents (énoncé : 602)
- Conséquence : prédire « satisfait » pour tout le monde donne **96.04 %** d'exactitude et ne trouve personne

*(0.0 s)*

## 1.10 — Le plancher

Protocole : 80 / 20 stratifié, graine 42. Pour chaque variable, le **sens** (grand = mécontent ou l'inverse) est choisi sur l'apprentissage, l'AUC est mesurée sur la validation.

| variable | sens | AUC validation |
|---|---|---|
| saldo_var30 | -1 | 0.6936 |
| var15 | 1 | 0.6903 |
| saldo_var42 | -1 | 0.6827 |
| saldo_medio_var5_hace2 | -1 | 0.6745 |
| saldo_medio_var5_ult1 | -1 | 0.6728 |
| num_meses_var5_ult3 | -1 | 0.6721 |
| saldo_var5 | -1 | 0.6718 |
| saldo_medio_var5_ult3 | -1 | 0.6686 |

- Meilleure règle à une variable : **`saldo_var30`**, AUC validation **0.6936**
- Plancher de l'énoncé : **0.689**
- Règles à moins de 0,005 du plancher : ['saldo_var30', 'var15']
- **Hypothèse retenue pour la règle métier : `var15`** (la plus proche de 0.689, AUC 0.6903, grand = plus de risque). À confirmer auprès de l'enseignant. Tout modèle doit battre ce chiffre sur la même validation.

*(13.4 s)*

## 1.11 — La métrique

| règle | exactitude | AUC ROC | AUC précision-rappel | mécontents trouvés |
|---|---|---|---|---|
| Personne n'est mécontent | 0.9605 | 0.5000 | 0.0395 | 0.0000 |
| Règle métier (var15) | — | 0.6903 | 0.0613 | — |
| Règle métier, on rappelle les 5 % les plus à risque | — | — | — | 0.0478 |
| Règle métier, on rappelle les 10 % les plus à risque | — | — | — | 0.1289 |
| Règle métier, on rappelle les 20 % les plus à risque | — | — | — | 0.3514 |

- **L'exactitude récompense le silence** : 96 % sans trouver un seul mécontent.
- **AUC ROC** (métrique retenue, celle du plancher) : probabilité qu'un mécontent soit classé devant un satisfait. Insensible au déséquilibre et au seuil : elle juge le **classement**.
- **AUC précision-rappel** en contrôle : son niveau de base est le taux de mécontents (3.95 %), elle montre à quel point les premiers rappels sont justes.
- Le classement ne suffit pas à décider : le **seuil** (combien on rappelle) se fixe avec le coût des erreurs (1.12).

*(0.0 s)*

## 1.12 — Le coût des erreurs

Les deux erreurs n'ont pas le même prix : **appel inutile** = 1 (unité), **mécontent raté** = r. La banque doit fixer r ; en attendant, voici la décision optimale avec la règle métier (`var15`) sur la validation (12164 clients, 481 mécontents).

| mécontent raté / appel inutile | seuil de probabilité 1/(1+r) | appels | part rappelée | trouvés | ratés | coût | coût sans appel | coût tout appeler |
|---|---|---|---|---|---|---|---|---|
| 2 | 0.333 | 0 | 0.00 % | 0 | 481 | 962 | 962 | 11 683 |
| 5 | 0.167 | 0 | 0.00 % | 0 | 481 | 2 405 | 2 405 | 11 683 |
| 10 | 0.091 | 0 | 0.00 % | 0 | 481 | 4 810 | 4 810 | 11 683 |
| 25 | 0.038 | 6 070 | 49.90 % | 401 | 80 | 7 669 | 12 025 | 11 683 |
| 50 | 0.020 | 7 373 | 60.61 % | 441 | 40 | 8 932 | 24 050 | 11 683 |

- Avec des probabilités bien calibrées, le seuil optimal est **p > 1/(1+r)** : à r = 10, on rappelle dès 9 % de risque.
- Si le budget d'appels est fixé (ex. 10 % des clients), le seuil est imposé par le budget : on rappelle les plus à risque jusqu'à épuisement.

*(0.0 s)*
