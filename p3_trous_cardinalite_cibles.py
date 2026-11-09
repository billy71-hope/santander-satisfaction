"""P3 — Trous (1.6) -> Cardinalité (1.4, après le typage 1.3) -> Cibles (1.9).

Mesure, puis décide. Chaque décision est écrite avec le chiffre qui la justifie.

Usage :
    python p3_trous_cardinalite_cibles.py      # -> docs/P3_trous_cardinalite_cibles.md
"""
import time

import numpy as np
import pandas as pd
from scipy.stats import binomtest
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import KFold

from audit_phase1 import (CIBLE, GRAINE, ID, PLANCHER, RACINE, a_decider, decoupage, famille,
                          pct, regle_metier, tableau, train, variables)

RAPPORT = RACINE / "docs" / "P3_trous_cardinalite_cibles.md"
DELTA_INFINI = 9999999999     # code des colonnes delta_ : variation depuis une base nulle
VAR3_MANQUANT = -999999
VAR36_CODE = 99
SEUIL_QUASI = 0.999           # une valeur occupe au moins 99,9 % des lignes
SEUIL_P = 0.01                # test binomial : en dessous, la valeur rare a un effet réel


def nb(x):
    return f"{int(x):,}".replace(",", " ")


def taux(y):
    return f"{pct(y.mean())} ({nb(len(y))} clients)"


def profil_taux(groupes, nom):
    """Tableau taux de mécontents / clients, taux en pourcentage."""
    t = groupes.agg(["mean", "size"])
    return pd.DataFrame({"taux de mécontents": [pct(v) for v in t["mean"]], "clients": t["size"].to_numpy()},
                        index=pd.Index(t.index, name=nom))


# ================================================================ 1.6 Trous
def trous():
    tr, de = train(), a_decider()
    y = tr[CIBLE]
    out = ["## 1.6 — Trous", "",
           f"**Valeurs vides (`NaN`) : {int(tr.isna().sum().sum()) + int(de.isna().sum().sum())}** dans les deux tables. "
           "Les trous existent pourtant : ils sont **codés**. Quatre codes trouvés, quatre décisions.", ""]

    # var3
    m = tr["var3"] == VAR3_MANQUANT
    mode = tr.loc[~m, "var3"].mode()[0]
    out += ["### `var3 = -999999` — un vrai manquant", "",
            f"- {int(m.sum())} clients dans train, {int((de['var3'] == VAR3_MANQUANT).sum())} dans a_decider.",
            f"- Taux de mécontents : {taux(y[m])} contre {taux(y[~m])}.",
            f"- La valeur `{mode}` occupe {pct((tr['var3'] == mode).mean())} des clients.",
            f"- **Décision : remplacer par `{mode}`**, la valeur dominante. Un indicateur « manquant » reposerait "
            f"sur {int(y[m].sum())} mécontent(s) : il n'apprendrait rien de fiable.", ""]

    # delta_
    dcols = [c for c in variables(tr) if famille(c) == "delta"]
    exemple = "delta_imp_aport_var13_1y3"
    s = tr[exemple] == DELTA_INFINI
    base, recent = "imp_aport_var13_hace3", "imp_aport_var13_ult1"
    fini = pd.concat([tr[dcols], de[dcols]]).replace(DELTA_INFINI, np.nan)
    lignes_inf = (tr[dcols] == DELTA_INFINI).any(axis=1)
    lignes_moins1 = (tr[dcols] == -1).any(axis=1)
    out += ["### `delta_ = 9999999999` — pas un manquant : une apparition", "",
            f"- Code présent dans {int(((tr[dcols] == DELTA_INFINI).sum() > 0).sum())} colonnes `delta_` sur {len(dcols)}, "
            f"chez {int(lignes_inf.sum())} clients de train.",
            f"- Vérification sur `{exemple}` ({int(s.sum())} lignes codées) : `{base}` vaut **toujours 0** "
            f"(max {tr.loc[s, base].max():.0f}) et `{recent}` est **toujours positif** (min {tr.loc[s, recent].min():.0f}). "
            "La variation part de zéro : division par zéro, codée « infini ».",
            f"- Symétriquement, `-1` = le montant a **disparu** (base > 0, récent = 0) : {int(lignes_moins1.sum())} clients.",
            f"- Plus grande variation finie, toutes colonnes `delta_` : **{np.nanmax(fini.to_numpy()):.2f}**.",
            f"- Taux de mécontents : {taux(tr.loc[lignes_inf, CIBLE])} chez les clients avec une apparition, "
            f"contre {taux(tr.loc[~lignes_inf, CIBLE])}.",
            f"- **Décision : remplacer `9999999999` par `{np.nanmax(fini.to_numpy()) + 1:.0f}`** (juste au-dessus de la plus "
            "grande variation finie). L'ordre est gardé (une apparition reste la plus forte hausse) sans écraser "
            "l'échelle pour les modèles linéaires. Ce n'est **pas** un trou : aucune imputation.", ""]

    # var38
    vc = tr["var38"].value_counts()
    v38 = vc.index[0]
    m38 = tr["var38"] == v38
    out += ["### `var38 = 117310.979016…` — un trou déguisé", "",
            f"- `var38` a {nb(tr['var38'].nunique())} valeurs différentes, mais **une seule** revient chez "
            f"**{nb(m38.sum())} clients ({pct(m38.mean())})**. La suivante revient {int(vc.iloc[1])} fois. "
            "Un montant à six décimales partagé par un client sur cinq n'est pas un montant : c'est une valeur "
            "de remplissage (probablement une moyenne).",
            f"- Taux de mécontents : {taux(y[m38])} contre {taux(y[~m38])} — **pas de différence nette**.",
            "- **Décision : garder `var38` telle quelle** pour le premier pipeline. **Essai à journaliser au bloc 2** : "
            "remplacer la valeur par un manquant + indicateur `var38_rempli`, et mesurer si l'AUC bouge.", ""]

    # var36
    t36 = profil_taux(tr.groupby("var36")[CIBLE], "var36")
    out += ["### `var36 = 99` — un code d'absence qui parle", "",
            tableau(t36), "",
            f"- `99` concerne {pct((tr['var36'] == VAR36_CODE).mean())} des clients et porte le **plus fort** taux de "
            "mécontents. Lu comme un nombre, 99 serait « très loin » de 3 : c'est faux, c'est une **catégorie**.",
            "- **Décision : encoder `var36` en catégories** (une colonne 0/1 par valeur). Ne pas l'imputer : "
            "l'absence est elle-même une information.", ""]

    # zéros
    v = variables(tr)
    non_nuls = (tr[v] != 0).sum(axis=1)
    par_classe = profil_taux(tr.groupby(pd.qcut(non_nuls, 5, duplicates="drop"), observed=True)[CIBLE], "valeurs non nulles")
    par_classe.index = [f"{int(i.left) + 1} à {int(i.right)}" for i in par_classe.index]
    out += ["### Les zéros — pas des trous", "",
            f"- {int(((tr[v] == 0).mean() > 0.99).sum())} colonnes sur {len(v)} sont nulles à plus de 99 %. "
            "Un zéro dit « pas de produit, pas d'opération » : c'est une **mesure**, pas un manque. "
            "Les remplacer par une moyenne détruirait l'information.",
            "- Le **nombre de valeurs non nulles** d'un client sépare déjà les mécontents :", "",
            tableau(par_classe.rename_axis("valeurs non nulles")), "",
            "- **Décision : garder les zéros.** **Essai proposé au constructeur** : ajouter la variable "
            "« nombre de valeurs non nulles » et mesurer son apport.", ""]
    return out


# ================================================================ 1.4 Cardinalité
def cardinalite():
    tr, de = train(), a_decider()
    v = variables(tr)
    y = tr[CIBLE]
    n_tr, n_de = tr[v].nunique(), de[v].nunique()
    constantes = sorted(n_tr[n_tr == 1].index)
    seulement_train = sorted(n_tr[(n_tr == 1) & (n_de > 1)].index)

    out = ["## 1.4 — Cardinalité", "",
           "Préalable (1.3) : toutes les colonnes sont numériques (`int64` / `float64`), les `ind_` valent 0 ou 1. "
           "On peut donc compter les valeurs distinctes sans conversion.", "",
           "### Colonnes constantes", "",
           f"- Sur les 4 000 premières lignes : {int((tr[v].head(4000).nunique() == 1).sum())} constantes. "
           f"Sur **tout** train : **{len(constantes)}**. L'énoncé (97, sur un échantillon de 4 000) surestime : "
           "un échantillon rend constantes des colonnes qui ne le sont pas. **On décide sur la table entière.**",
           f"- {len(seulement_train)} d'entre elles varient dans a_decider ({', '.join(seulement_train)}) : "
           "le modèle n'en a jamais vu qu'une valeur, il ne peut rien en apprendre.",
           f"- **Décision : supprimer les {len(constantes)} colonnes constantes sur train.**", "",
           "<details><summary>Liste des colonnes supprimées</summary>", "", ", ".join(f"`{c}`" for c in constantes),
           "", "</details>", ""]

    # quasi-constantes
    lignes = []
    for c in v:
        if n_tr[c] == 1:
            continue
        dominante = tr[c].value_counts().index[0]
        rare = tr[c] != dominante
        if 1 - rare.mean() >= SEUIL_QUASI:
            k_rare = int(y[rare].sum())
            p_val = binomtest(k_rare, int(rare.sum()), y.mean()).pvalue
            lignes.append((c, int(rare.sum()), k_rare, pct(y[rare].mean()), p_val))
    q = pd.DataFrame(lignes, columns=["colonne", "clients rares", "mécontents parmi eux", "taux", "p"]).set_index("colonne")
    seuil = SEUIL_P / len(q)   # correction de Bonferroni : on teste toutes les colonnes à la fois
    gardees = q[q["p"] < seuil]
    supprimees = q[q["p"] >= seuil]
    plafond = int((1 - SEUIL_QUASI) * len(tr))
    repartition = q["mécontents parmi eux"].value_counts().sort_index()
    out += ["### Colonnes quasi constantes", "",
            f"- **{len(q)}** colonnes ont une valeur qui occupe au moins 99,9 % des lignes : au plus "
            f"{plafond} clients s'en écartent. À {pct(y.mean())}, on attend **≈ {plafond * y.mean():.1f} mécontents** parmi eux.",
            "- Mécontents trouvés parmi ces clients « rares », colonne par colonne : "
            + ", ".join(f"{n} → {c} colonnes" for n, c in repartition.items()) + ".",
            f"- Test binomial (le taux des clients rares diffère-t-il de {pct(y.mean())} ?) : **{len(gardees)} colonnes** "
            f"ont un écart réel (p < {SEUIL_P} / {len(q)} = {seuil:.0e}, correction de Bonferroni puisqu'on teste "
            f"{len(q)} colonnes à la fois) :", "",
            tableau(gardees.assign(p=[f"{v:.1e}" for v in gardees["p"]])) if len(gardees) else "(aucune)", "",
            f"- Ces clients rares sont **{gardees['mécontents parmi eux'].div(gardees['clients rares']).min() / y.mean():.0f} à "
            f"{gardees['mécontents parmi eux'].div(gardees['clients rares']).max() / y.mean():.0f} fois plus souvent mécontents** "
            "que la moyenne : supprimer ces colonnes "
            "jetterait un vrai signal, même s'il ne repose que sur une poignée de mécontents.",
            f"- Pour les {len(supprimees)} autres, l'écart n'est pas distinguable du hasard : du bruit que le modèle "
            "risque d'apprendre par cœur.",
            f"- **Décision : supprimer {len(supprimees)} quasi constantes, garder les {len(gardees)} qui ont un effet "
            f"mesuré.** **Essai à journaliser** : AUC avec et sans les {len(supprimees)}, et temps gagné.", ""]

    # profil de cardinalité
    restantes = [c for c in v if c not in constantes and c not in supprimees.index]
    classes = pd.cut(n_tr[restantes], [1, 2, 10, 100, np.inf], labels=["2 (binaire)", "3 à 10", "11 à 100", "> 100"])
    profil = pd.crosstab(pd.Series([famille(c) for c in restantes], index=restantes, name="famille"),
                         classes.rename("valeurs distinctes"))
    num = [c for c in v if famille(c) == "num"]
    mult3 = sum(bool((tr[c] % 3 == 0).all()) for c in num)
    out += ["### Ce qui reste, et comment le traiter", "",
            f"Après suppression : **{len(restantes)} variables** sur {len(v)}.", "",
            tableau(profil), "",
            f"- **Variables isolées** : `var15` ({n_tr['var15']} valeurs, de {tr['var15'].min()} à {tr['var15'].max()} : "
            f"un âge) et `var38` ({nb(n_tr['var38'])} valeurs) sont continues. `var36` ({n_tr['var36']} valeurs) est une "
            f"catégorie (voir 1.6). `var3` a {n_tr['var3']} valeurs, mais `2` en occupe {pct((tr['var3'] == 2).mean())} "
            f"({pct(y[tr['var3'] == 2].mean())} de mécontents, contre {pct(y[tr['var3'] != 2].mean())} pour les autres "
            f"valeurs). `var21` : {n_tr['var21']} valeurs, nulle à {pct((tr['var21'] == 0).mean())}.",
            f"- **{mult3} colonnes `num_` sur {len(num)} ne contiennent que des multiples de 3** : les comptages sont "
            "codés × 3. Sans effet sur les arbres et sur l'AUC ; à savoir avant d'interpréter un comptage.",
            "- **Décision : `var36` en catégories, tout le reste en numérique.** Aucune variable à forte "
            "cardinalité n'est une catégorie déguisée : pas d'encodage cible à risque de fuite.",
            "- Les colonnes strictement identiques entre elles relèvent de **1.7 Doublons (P4)**.", ""]
    return out, constantes, list(supprimees.index), list(gardees.index)


# ================================================================ 1.9 Cibles
def cibles():
    tr = train()
    y = tr[CIBLE]
    n, k = len(y), int(y.sum())
    p = k / n
    marge = 1.96 * np.sqrt(p * (1 - p) / n)
    out = ["## 1.9 — Cibles", "",
           "### La cible", "",
           f"- `TARGET` vaut 0 ou 1, jamais vide. **{nb(k)} mécontents sur {nb(n)} = {pct(p)}** "
           f"(intervalle à 95 % : {pct(p - marge)} à {pct(p + marge)}).",
           f"- **1 mécontent pour {(n - k) / k:.0f} satisfaits.** Prédire « satisfait » pour tous : "
           f"{pct(1 - p)} d'exactitude, zéro mécontent trouvé.",
           f"- Attendus dans a_decider au même taux : **≈ {round(p * len(a_decider()))}** (énoncé : 602).", ""]

    age = profil_taux(tr.groupby(pd.cut(tr["var15"], [0, 22, 25, 30, 40, 50, 60, 120]), observed=True)[CIBLE], "âge")
    age.index = ["22 ans et moins"] + [f"{int(i.left) + 1} à {int(i.right)}" for i in age.index[1:-1]] + ["61 et plus"]
    sans_montant = (tr[[c for c in variables(tr) if famille(c) in ("saldo", "imp")]] == 0).all(axis=1)
    out += ["### À quoi ressemble un mécontent", "",
            "**Par âge (`var15`)**", "", tableau(age.rename_axis("âge")), "",
            f"- **Aucun** mécontent jusqu'à 22 ans ({nb(age.iloc[0, 1])} clients), moins de 1 % de 23 à 25 ans, "
            "puis le taux est multiplié par 8 après 40 ans.",
            f"- Clients **sans aucun montant** (`saldo_` et `imp_` tous nuls, {pct(sans_montant.mean())} des clients) : "
            f"**{pct(y[sans_montant].mean())}** de mécontents, contre {pct(y[~sans_montant].mean())} pour les autres.",
            f"- `var36 = 99` : {pct(y[tr['var36'] == VAR36_CODE].mean())} (voir 1.6).",
            "- Portrait : un client **de plus de 30 ans, avec peu de produits et des comptes vides**.", ""]

    v = variables(tr)
    groupes = tr.groupby(v, sort=False)[CIBLE]
    nb_cibles = groupes.transform("nunique")
    ambigus = nb_cibles > 1
    out += ["### La part que personne ne peut prédire", "",
            f"- **{nb(ambigus.sum())} clients** ont un dossier identique à au moins un autre client **de cible "
            f"opposée** ; ils comptent **{int(y[ambigus].sum())} mécontents** ({pct(y[ambigus].sum() / k)} des mécontents). "
            "À dossier égal, aucun modèle ne peut les départager : c'est du **bruit de cible** irréductible.",
            "- Conséquence : l'AUC maximale atteignable est **inférieure à 1** ; ne pas s'acharner sur ces lignes.", ""]

    # précision de la mesure
    _, i_val = decoupage()
    var, sens = regle_metier()
    yv = y[i_val].to_numpy()
    sv = sens * tr.loc[i_val, var].to_numpy()
    rng = np.random.default_rng(GRAINE)
    tirages = []
    for _ in range(300):
        i = rng.integers(0, len(yv), len(yv))
        if yv[i].min() != yv[i].max():
            tirages.append(roc_auc_score(yv[i], sv[i]))
    ecart = float(np.std(tirages))
    plis = [int(y.iloc[i_test].sum()) for g in range(20)
            for _, i_test in KFold(5, shuffle=True, random_state=g).split(tr)]
    out += ["### Ce que le petit nombre de mécontents fait à la mesure", "",
            f"- La validation (20 %, graine {GRAINE}) ne contient que **{int(yv.sum())} mécontents**.",
            f"- AUC de la règle métier (`{var}`) sur la validation : {roc_auc_score(yv, sv):.4f}, "
            f"avec un **écart-type de ±{ecart:.4f}** (300 rééchantillonnages bootstrap).",
            f"- **Conséquence pour le protocole** : un écart de moins de ~{2 * ecart:.3f} entre deux essais n'est pas "
            f"distinguable du hasard. Battre le plancher ({PLANCHER}) de 0,005 ne prouve rien. Le mesureur devrait "
            "comparer les essais en **validation croisée stratifiée** (5 plis, même graine) pour réduire ce bruit.",
            f"- Sans stratification, sur 20 tirages de 5 plis (`KFold` mélangé), le nombre de mécontents par pli va de "
            f"**{min(plis)} à {max(plis)}** (attendu {k / 5:.0f}) : des plis plus ou moins « faciles », qui ajoutent du bruit "
            "à la comparaison.",
            "- **Décision : stratifier tout découpage sur `TARGET`** (chaque pli garde exactement 3,96 % de mécontents).", ""]
    return out


if __name__ == "__main__":
    t0 = time.perf_counter()
    b_trous = trous()
    b_card, constantes, quasi, quasi_gardees = cardinalite()
    b_cibles = cibles()
    synthese = ["# P3 — Trous, cardinalité, cibles", "",
                f"Enchaînement : **1.6 Trous → 1.4 Cardinalité (après 1.3 Typer) → 1.9 Cibles**. "
                f"Généré par `python p3_trous_cardinalite_cibles.py` le {time.strftime('%Y-%m-%d %H:%M')}, sur "
                f"`train.csv` ({nb(len(train()))} lignes) et `a_decider.csv` ({nb(len(a_decider()))} lignes), "
                "tables entières.", "",
                "## Les décisions, en une page", "",
                "| # | Constat mesuré | Décision |", "|---|---|---|",
                "| 1 | `var3 = -999999` : vrai manquant, 88 clients de train | remplacer par 2, la valeur dominante |",
                "| 2 | `delta_ = 9999999999` : variation depuis une base nulle (apparition) | remplacer par la plus grande variation finie + 1 ; pas d'imputation |",
                "| 3 | `var38` : une valeur de remplissage chez 20 % des clients, sans effet sur le taux | garder ; essai « manquant + indicateur » au bloc 2 |",
                "| 4 | `var36 = 99` : code d'absence chez 40 % des clients, taux de mécontents le plus haut | encoder en catégories |",
                "| 5 | les zéros sont des mesures (pas d'opération) | garder ; essai « nombre de valeurs non nulles » |",
                f"| 6 | {len(constantes)} colonnes constantes sur train (et non 97) | les supprimer |",
                f"| 7 | {len(quasi) + len(quasi_gardees)} quasi constantes (≤ 60 clients hors valeur dominante) ; "
                f"{len(quasi_gardees)} ont un effet réel (24 à 28 % de mécontents, test binomial) | supprimer les {len(quasi)} autres ; "
                f"garder {', '.join(f'`{c}`' for c in quasi_gardees)} ; essai avec / sans |",
                "| 8 | 3,96 % de mécontents, validation à ~481 mécontents | stratifier tout découpage ; comparer les essais en validation croisée |",
                "| 9 | des dossiers identiques de cibles opposées | bruit irréductible : AUC max < 1 |",
                ""]
    texte = "\n".join(synthese + b_trous + b_card + b_cibles)
    RAPPORT.write_text(texte + f"\n*Calculé en {time.perf_counter() - t0:.0f} s.*\n", encoding="utf-8")
    print(texte)
    print(f"\nRapport écrit : {RAPPORT.relative_to(RACINE)}")
