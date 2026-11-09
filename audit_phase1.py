"""Phase 1 — audit des données (tâches 1.1 à 1.12 du tableau).

Porteurs et enchaînement :
    P1 : 1.1 -> 1.8
    P2 : 1.2 -> 1.3 -> 1.5 -> 1.10
    P3 : 1.6 -> 1.4 (attend 1.3) -> 1.9
    P4 : 1.7 -> 1.11 -> 1.12

Usage :
    python audit_phase1.py              # toutes les tâches -> docs/audit_phase1.md
    python audit_phase1.py 1.4 1.7      # seulement ces tâches, affichées dans la console
"""
import sys
import time
from functools import cache
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import train_test_split

RACINE = Path(__file__).resolve().parent
DATA = RACINE / "data"
RAPPORT = RACINE / "docs" / "audit_phase1.md"
CIBLE, ID = "TARGET", "ID"
GRAINE = 42             # graine unique du projet : même découpage pour tout le monde
PART_VALIDATION = 0.20  # protocole : découpage stratifié 80 / 20
PLANCHER = 0.6890       # AUC de la règle métier, donnée par l'énoncé
SENTINELLES = (-999999, 9999999999)
FAMILLES = ("saldo", "imp", "num", "ind", "delta")

TACHES = {}
DUREES = {}  # temps de chargement de chaque table, mesuré au premier accès


def tache(numero, titre):
    def enregistrer(f):
        TACHES[numero] = (titre, f)
        return f
    return enregistrer


# ---------------------------------------------------------------- outils
def _lire(nom):
    t0 = time.perf_counter()
    df = pd.read_csv(DATA / nom)
    DUREES[nom] = time.perf_counter() - t0
    return df


@cache
def train():
    return _lire("train.csv")


@cache
def a_decider():
    return _lire("a_decider.csv")


def variables(df):
    return [c for c in df.columns if c not in (ID, CIBLE)]


def famille(col):
    if col in (ID, CIBLE):
        return col
    debut = col.split("_")[0]
    return debut if debut in FAMILLES else "isolée"


def tableau(df, index=True):
    """DataFrame -> tableau Markdown (sans dépendance à tabulate)."""
    d = df.rename_axis(df.index.name or "").reset_index() if index else df
    lignes = ["| " + " | ".join(map(str, d.columns)) + " |",
              "|" + "---|" * len(d.columns)]
    for r in d.itertuples(index=False):
        lignes.append("| " + " | ".join(_fmt(v) for v in r) + " |")
    return "\n".join(lignes)


def _fmt(v):
    if isinstance(v, (float, np.floating)):
        return f"{v:,.4f}".replace(",", " ") if abs(v) < 1e6 else f"{v:,.0f}".replace(",", " ")
    if isinstance(v, (int, np.integer)):
        return f"{v:,}".replace(",", " ")
    return str(v)


def pct(x):
    return f"{100 * x:.2f} %"


def auc_sym(y, x):
    """AUC d'une variable prise seule comme score, quel que soit son sens."""
    a = roc_auc_score(y, x)
    return max(a, 1 - a)


@cache
def decoupage():
    """Protocole de validation : 80 / 20 stratifié sur TARGET, graine fixe."""
    df = train()
    i_app, i_val = train_test_split(df.index, test_size=PART_VALIDATION,
                                    stratify=df[CIBLE], random_state=GRAINE)
    return i_app, i_val


@cache
def regle_plancher():
    """Meilleure règle à une variable : sens choisi sur l'apprentissage, AUC mesurée sur la validation."""
    df = train()
    i_app, i_val = decoupage()
    lignes = []
    for c in variables(df):
        x_app = df.loc[i_app, c]
        if x_app.nunique() < 2:
            continue
        sens = 1 if roc_auc_score(df.loc[i_app, CIBLE], x_app) >= 0.5 else -1
        auc_val = roc_auc_score(df.loc[i_val, CIBLE], sens * df.loc[i_val, c])
        lignes.append((c, sens, auc_val))
    res = pd.DataFrame(lignes, columns=["variable", "sens", "AUC validation"])
    return res.sort_values("AUC validation", ascending=False).set_index("variable")


def regle_metier():
    """Hypothèse : la règle de la banque est la règle à une variable dont l'AUC est la plus proche du plancher."""
    r = regle_plancher()
    var = (r["AUC validation"] - PLANCHER).abs().idxmin()
    return var, int(r.loc[var, "sens"])


# ---------------------------------------------------------------- tâches
@tache("1.1", "Inventorier les tables")
def t1_1():
    out = []
    lignes = []
    for f in sorted(DATA.glob("*.csv")):
        with open(f, encoding="utf-8") as h:
            entete = h.readline().strip().split(",")
            n = sum(1 for _ in h)
        lignes.append((f.name, f"{f.stat().st_size / 1e6:.1f}", n, len(entete)))
    out.append(tableau(pd.DataFrame(lignes, columns=["fichier", "Mo", "lignes", "colonnes"]), index=False))
    tr, de = set(train().columns), set(a_decider().columns)
    out.append(f"\n- Colonnes présentes seulement dans `train.csv` : {sorted(tr - de)}")
    out.append(f"- Colonnes présentes seulement dans `a_decider.csv` : {sorted(de - tr) or 'aucune'}")
    fam = pd.Series([famille(c) for c in train().columns]).value_counts()
    attendu = {"saldo": 71, "imp": 49, "num": 143, "ind": 75, "delta": 26, "isolée": 6, ID: 1, CIBLE: 1}
    comp = pd.DataFrame({"mesuré": fam, "énoncé": pd.Series(attendu)}).fillna(0).astype(int)
    comp["écart"] = comp["mesuré"] - comp["énoncé"]
    out.append("\n**Familles de colonnes (train.csv)**\n\n" + tableau(comp))
    isolees = [c for c in train().columns if famille(c) == "isolée"]
    out.append(f"\n- Variables isolées : {', '.join(isolees)}. Les familles de l'énoncé totalisent "
               f"{sum(attendu.values())} colonnes pour {train().shape[1]} : l'énoncé compte une variable isolée de trop.")
    return out


@tache("1.2", "Charger et compter")
def t1_2():
    tr, de = train(), a_decider()
    out = [f"- Chargement des deux tables : **{sum(DUREES.values()):.1f} s** "
           f"(mémoire : {tr.memory_usage(deep=True).sum() / 1e6:.0f} Mo + "
           f"{de.memory_usage(deep=True).sum() / 1e6:.0f} Mo)"]
    for nom, df, attendu in (("train.csv", tr, (60816, 371)), ("a_decider.csv", de, (15204, 370))):
        ok = "✓" if df.shape == attendu else f"✗ (attendu {attendu})"
        out.append(f"- `{nom}` : {df.shape[0]:,} lignes × {df.shape[1]} colonnes {ok}".replace(",", " "))
    n1 = int(tr[CIBLE].sum())
    out.append(f"- Mécontents dans `train.csv` : **{n1:,}** sur {len(tr):,} = **{pct(n1 / len(tr))}**".replace(",", " "))
    out.append(f"- Total des deux tables : {len(tr) + len(de):,} clients (énoncé : 76 020)".replace(",", " "))
    out.append(f"- `ID` : train de {tr[ID].min()} à {tr[ID].max()}, a_decider de {de[ID].min()} à {de[ID].max()}")
    return out


@tache("1.3", "Typer")
def t1_3():
    df = pd.concat([train().drop(columns=CIBLE), a_decider()])
    v = variables(df)
    types = pd.DataFrame({"famille": [famille(c) for c in v], "type": [str(df[c].dtype) for c in v]})
    out = ["**Types lus par pandas, par famille**\n", tableau(pd.crosstab(types["famille"], types["type"]))]
    flottants_entiers = [c for c in v if df[c].dtype.kind == "f" and (df[c] % 1 == 0).all()]
    out.append(f"\n- Colonnes lues en `float` mais qui ne contiennent que des entiers : **{len(flottants_entiers)}**"
               + (f" ({', '.join(flottants_entiers[:10])}{'…' if len(flottants_entiers) > 10 else ''})" if flottants_entiers else ""))
    objets = [c for c in v if df[c].dtype == object]
    out.append(f"- Colonnes texte (`object`) : {objets or 'aucune'} — tout est numérique")
    ind_non_binaires = [c for c in v if famille(c) == "ind" and not set(df[c].unique()) <= {0, 1}]
    out.append(f"- Colonnes `ind_` qui ne sont pas 0/1 : {ind_non_binaires or 'aucune'}")
    avant = df.memory_usage(deep=True).sum()
    reduit = df.copy()
    for c in v:
        kind = "integer" if reduit[c].dtype.kind == "i" or c in flottants_entiers else "float"
        reduit[c] = pd.to_numeric(reduit[c], downcast=kind)
    apres = reduit.memory_usage(deep=True).sum()
    out.append(f"- Mémoire en réduisant les types : {avant / 1e6:.0f} Mo → **{apres / 1e6:.0f} Mo**")
    return out


@tache("1.4", "Cardinalité")
def t1_4():
    tr, de = train(), a_decider()
    v = variables(tr)
    n_tr, n_de = tr[v].nunique(), de[v].nunique()
    n_tout = pd.concat([tr[v], de[v]]).nunique()
    n_4000 = tr[v].head(4000).nunique()
    out = [f"- Constantes sur les 4 000 premières lignes de train : **{(n_4000 == 1).sum()}** (énoncé : 97)",
           f"- Constantes sur tout `train.csv` : **{(n_tr == 1).sum()}**",
           f"- Constantes sur train + a_decider : **{(n_tout == 1).sum()}**",
           f"- Constantes dans train mais **variables dans a_decider** : {list(n_tr[(n_tr == 1) & (n_de > 1)].index) or 'aucune'}"]
    dominante = tr[v].apply(lambda s: s.value_counts(normalize=True).iloc[0])
    out.append(f"- Quasi constantes (une valeur ≥ 99,9 % des lignes, hors constantes) : **{((dominante >= 0.999) & (n_tr > 1)).sum()}**")
    classes = pd.cut(n_tr, [0, 1, 2, 10, 100, np.inf], labels=["1 (constante)", "2", "3 à 10", "11 à 100", "> 100"])
    par_fam = pd.crosstab(pd.Series([famille(c) for c in v], index=v, name="famille"), classes.rename("valeurs distinctes"))
    out.append("\n**Nombre de valeurs distinctes (train), par famille**\n\n" + tableau(par_fam))
    return out


@tache("1.5", "Valeurs impossibles")
def t1_5():
    df = pd.concat([train().drop(columns=CIBLE), a_decider()])
    v = variables(df)
    lignes = []
    for c in v:
        s = df[c]
        sent = int(s.isin(SENTINELLES).sum())
        neg = int((s < 0).sum()) if famille(c) in ("num", "ind") else 0
        if sent or neg:
            lignes.append((c, famille(c), sent, neg, s.min(), s.max()))
    res = pd.DataFrame(lignes, columns=["colonne", "famille", "sentinelles", "négatifs (num/ind)", "min", "max"])
    out = [f"Sentinelles cherchées : {SENTINELLES}. Une valeur négative est impossible pour un comptage (`num_`) "
           "ou un indicateur (`ind_`).\n"]
    out.append(tableau(res.sort_values("sentinelles", ascending=False).head(30), index=False) if len(res) else "Aucune.")
    if len(res) > 30:
        out.append(f"\n… {len(res) - 30} autres colonnes")
    out.append(f"\n- `var3` = -999999 : **{int((df['var3'] == -999999).sum())}** lignes")
    out.append(f"- `var15` : de {df['var15'].min()} à {df['var15'].max()} (à vérifier si c'est un âge)")
    neg_saldo = [c for c in v if famille(c) == "saldo" and (df[c] < 0).any()]
    out.append(f"- Soldes `saldo_` négatifs (possibles : découvert) : {len(neg_saldo)} colonnes")
    return out


@tache("1.6", "Trous")
def t1_6():
    df = pd.concat([train().drop(columns=CIBLE), a_decider()])
    v = variables(df)
    out = [f"- Valeurs vides (`NaN`) : **{int(df[v].isna().sum().sum())}**",
           f"- Valeurs manquantes **codées** (sentinelles {SENTINELLES}) : "
           f"**{int(df[v].isin(SENTINELLES).sum().sum())}** cellules, dans "
           f"{int((df[v].isin(SENTINELLES).sum() > 0).sum())} colonnes (détail en 1.5)"]
    zeros = (df[v] == 0).mean()
    par_fam = zeros.groupby([famille(c) for c in v]).describe()[["count", "mean", "50%", "min"]]
    par_fam.columns = ["colonnes", "part de zéros moyenne", "médiane", "minimum"]
    out.append("\n**Part de zéros par famille** (un zéro n'est pas un trou : c'est souvent « pas d'opération »)\n\n" + tableau(par_fam))
    out.append(f"\n- Colonnes nulles à plus de 99 % : **{int((zeros > 0.99).sum())}** sur {len(v)}")
    tr = train()
    montants = [c for c in variables(tr) if famille(c) in ("saldo", "imp")]
    vide = (tr[montants] == 0).all(axis=1)
    out.append(f"- Clients de train sans aucun montant (`saldo_` et `imp_` tous nuls) : {pct(vide.mean())} ; "
               f"taux de mécontents chez eux : **{pct(tr.loc[vide, CIBLE].mean())}** contre {pct(tr.loc[~vide, CIBLE].mean())} chez les autres")
    return out


@tache("1.7", "Doublons")
def t1_7():
    tr, de = train(), a_decider()
    v = variables(tr)
    out = [f"- `ID` en double : train {int(tr[ID].duplicated().sum())}, a_decider {int(de[ID].duplicated().sum())}, "
           f"communs aux deux tables {len(set(tr[ID]) & set(de[ID]))}"]
    dup = tr.duplicated(subset=v, keep=False)
    out.append(f"- Lignes de train dont toutes les variables (hors ID) existent ailleurs dans train : **{int(dup.sum())}**")
    conflits = tr[dup].groupby(v, sort=False)[CIBLE].nunique()
    groupes = tr[dup].groupby(v, sort=False)[CIBLE].transform("nunique") > 1
    out.append(f"- Groupes de lignes identiques **avec des cibles différentes** : **{int((conflits > 1).sum())}** "
               f"groupes, {int(groupes.sum())} lignes — même dossier, issues opposées : aucun modèle ne peut les séparer")
    cles_tr = pd.util.hash_pandas_object(tr[v], index=False)
    cles_de = pd.util.hash_pandas_object(de[v], index=False)
    out.append(f"- Clients de a_decider dont le dossier est identique à un dossier de train : **{int(cles_de.isin(set(cles_tr)).sum())}**")
    tout = pd.concat([tr[v], de[v]])
    non_constantes = [c for c in v if tout[c].nunique() > 1]
    hachages = pd.Series({c: pd.util.hash_pandas_object(tout[c], index=False).sum() for c in non_constantes})
    jumelles = hachages[hachages.duplicated(keep=False)]
    groupes_col = jumelles.groupby(jumelles).apply(lambda s: list(s.index))
    out.append(f"- Colonnes non constantes strictement identiques à une autre : **{int(hachages.duplicated().sum())}** "
               f"colonnes en trop, réparties en {len(groupes_col)} groupes (les constantes sont traitées en 1.4)")
    for g in groupes_col.head(8):
        out.append(f"  - {', '.join(g)}")
    return out


@tache("1.8", "Fuites")
def t1_8():
    tr, de = train(), a_decider()
    v = [c for c in variables(tr) if tr[c].nunique() > 1]
    auc = pd.Series({c: auc_sym(tr[CIBLE], tr[c]) for c in v}).sort_values(ascending=False)
    out = ["**AUC de chaque variable prise seule (train entier)** — une valeur proche de 1 signalerait une fuite\n",
           tableau(auc.head(12).rename("AUC").to_frame())]
    suspectes = auc[auc > 0.80]
    out.append(f"\n- Variables à AUC > 0,80 : {list(suspectes.index) or 'aucune'}")
    out.append(f"- AUC de l'`ID` seul : {auc_sym(tr[CIBLE], tr[ID]):.4f} (≈ 0,5 attendu : l'ordre des dossiers ne doit rien dire)")
    y = np.r_[np.zeros(len(tr)), np.ones(len(de))]
    derive = pd.Series({c: auc_sym(y, pd.concat([tr[c], de[c]])) for c in v}).sort_values(ascending=False)
    out.append("\n**Train contre a_decider, variable par variable** (AUC ≈ 0,5 : les deux tables se ressemblent)\n")
    out.append(tableau(derive.head(5).rename("AUC train/a_decider").to_frame()))
    out.append("\nRègle du cours : aucune information inconnue à l'ouverture du dossier. Les colonnes `delta_` "
               "(variations entre deux dates) sont à vérifier en priorité : leurs deux dates doivent précéder la plainte.")
    return out


@tache("1.9", "Cibles")
def t1_9():
    y = train()[CIBLE]
    n, k = len(y), int(y.sum())
    p = k / n
    marge = 1.96 * np.sqrt(p * (1 - p) / n)
    out = [f"- Valeurs prises par `TARGET` : {sorted(int(v) for v in y.unique())}, manquantes : {int(y.isna().sum())}",
           f"- Mécontents : **{k:,}** / {n:,} = **{pct(p)}** (intervalle à 95 % : {pct(p - marge)} – {pct(p + marge)})".replace(",", " "),
           f"- Satisfaits : {n - k:,}. Rapport : **1 mécontent pour {(n - k) / k:.0f} satisfaits**".replace(",", " ")]
    i_app, i_val = decoupage()
    out.append(f"- Découpage 80 / 20 stratifié (graine {GRAINE}) : {int(y[i_app].sum())} mécontents en apprentissage, "
               f"**{int(y[i_val].sum())}** en validation ({pct(y[i_val].mean())})")
    out.append(f"- Attendu dans `a_decider.csv` au même taux : ≈ {round(p * len(a_decider()))} mécontents (énoncé : 602)")
    out.append("- Conséquence : prédire « satisfait » pour tout le monde donne **" + pct(1 - p) + "** d'exactitude et ne trouve personne")
    return out


@tache("1.10", "Le plancher")
def t1_10():
    regles = regle_plancher()
    meilleure = regles.index[0]
    out = [f"Protocole : 80 / 20 stratifié, graine {GRAINE}. Pour chaque variable, le **sens** (grand = mécontent "
           "ou l'inverse) est choisi sur l'apprentissage, l'AUC est mesurée sur la validation.\n",
           tableau(regles.head(8)),
           f"\n- Meilleure règle à une variable : **`{meilleure}`**, AUC validation **{regles.iloc[0, 1]:.4f}**",
           f"- Plancher de l'énoncé : **{PLANCHER}**"]
    proches = regles[(regles["AUC validation"] - PLANCHER).abs() < 0.005]
    out.append(f"- Règles à moins de 0,005 du plancher : {list(proches.index) or 'aucune'}")
    var, sens = regle_metier()
    out.append(f"- **Hypothèse retenue pour la règle métier : `{var}`** (la plus proche de {PLANCHER}, AUC "
               f"{regles.loc[var, 'AUC validation']:.4f}, {'grand' if sens > 0 else 'petit'} = plus de risque). "
               "À confirmer auprès de l'enseignant. Tout modèle doit battre ce chiffre sur la même validation.")
    return out


@tache("1.11", "La métrique")
def t1_11():
    df = train()
    _, i_val = decoupage()
    y = df.loc[i_val, CIBLE].to_numpy()
    var, sens = regle_metier()
    score = sens * df.loc[i_val, var].to_numpy()
    lignes = [("Personne n'est mécontent", 1 - y.mean(), 0.5, y.mean(), 0.0),
              (f"Règle métier ({var})", np.nan, roc_auc_score(y, score), average_precision_score(y, score), np.nan)]
    out = []
    ordre = np.argsort(-score, kind="stable")
    for budget in (0.05, 0.10, 0.20):
        k = int(budget * len(y))
        lignes.append((f"Règle métier, on rappelle les {int(budget * 100)} % les plus à risque", np.nan, np.nan, np.nan,
                       y[ordre[:k]].sum() / y.sum()))
    res = pd.DataFrame(lignes, columns=["règle", "exactitude", "AUC ROC", "AUC précision-rappel", "mécontents trouvés"])
    out.append(tableau(res.astype(object).fillna("—"), index=False))
    out.append("\n- **L'exactitude récompense le silence** : 96 % sans trouver un seul mécontent.")
    out.append("- **AUC ROC** (métrique retenue, celle du plancher) : probabilité qu'un mécontent soit classé devant un "
               "satisfait. Insensible au déséquilibre et au seuil : elle juge le **classement**.")
    out.append("- **AUC précision-rappel** en contrôle : son niveau de base est le taux de mécontents "
               f"({pct(y.mean())}), elle montre à quel point les premiers rappels sont justes.")
    out.append("- Le classement ne suffit pas à décider : le **seuil** (combien on rappelle) se fixe avec le coût des erreurs (1.12).")
    return out


@tache("1.12", "Le coût des erreurs")
def t1_12():
    df = train()
    _, i_val = decoupage()
    y = df.loc[i_val, CIBLE].to_numpy()
    var, sens = regle_metier()
    score = sens * df.loc[i_val, var].to_numpy()
    ordre = np.argsort(-score, kind="stable")
    trouves = np.r_[0, np.cumsum(y[ordre])]          # mécontents trouvés en rappelant les k premiers
    k = np.arange(len(y) + 1)
    lignes = []
    for r in (2, 5, 10, 25, 50):
        # coût en « appels » : un appel inutile coûte 1, un mécontent non rappelé coûte r
        cout = (k - trouves) + r * (y.sum() - trouves)
        kb = int(np.argmin(cout))
        lignes.append((r, f"{1 / (1 + r):.3f}", kb, pct(kb / len(y)), int(trouves[kb]), int(y.sum() - trouves[kb]),
                       int(cout[kb]), int(r * y.sum()), int(len(y) - y.sum())))
    res = pd.DataFrame(lignes, columns=["mécontent raté / appel inutile", "seuil de probabilité 1/(1+r)",
                                        "appels", "part rappelée", "trouvés", "ratés", "coût", "coût sans appel", "coût tout appeler"])
    out = ["Les deux erreurs n'ont pas le même prix : **appel inutile** = 1 (unité), **mécontent raté** = r. "
           f"La banque doit fixer r ; en attendant, voici la décision optimale avec la règle métier (`{var}`) sur la validation "
           f"({len(y)} clients, {int(y.sum())} mécontents).\n",
           tableau(res, index=False),
           "\n- Avec des probabilités bien calibrées, le seuil optimal est **p > 1/(1+r)** : à r = 10, on rappelle "
           "dès 9 % de risque.",
           "- Si le budget d'appels est fixé (ex. 10 % des clients), le seuil est imposé par le budget : "
           "on rappelle les plus à risque jusqu'à épuisement."]
    return out


# ---------------------------------------------------------------- lancement
def lancer(numeros):
    blocs = []
    for num in numeros:
        titre, f = TACHES[num]
        t0 = time.perf_counter()
        corps = "\n".join(f())
        blocs.append(f"## {num} — {titre}\n\n{corps}\n\n*({time.perf_counter() - t0:.1f} s)*\n")
        print(blocs[-1])
    return blocs


if __name__ == "__main__":
    for f in ("train.csv", "a_decider.csv"):
        if not (DATA / f).is_file():
            sys.exit(f"{f} manquant dans {DATA} : téléchargez le dossier Sujet_05 du Drive du cours.")
    demandes = sys.argv[1:] or list(TACHES)
    inconnues = [n for n in demandes if n not in TACHES]
    if inconnues:
        sys.exit(f"Tâches inconnues : {inconnues}. Disponibles : {list(TACHES)}")
    blocs = lancer(demandes)
    if not sys.argv[1:]:
        RAPPORT.write_text("# Audit des données — phase 1\n\n"
                           f"Généré par `python audit_phase1.py` le {time.strftime('%Y-%m-%d %H:%M')}. "
                           f"Découpage : 80 / 20 stratifié, graine {GRAINE}.\n\n" + "\n".join(blocs), encoding="utf-8")
        print(f"Rapport écrit : {RAPPORT.relative_to(RACINE)}")
