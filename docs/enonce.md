# Projet — Identifier le client qui va se plaindre

> **Type de tâche** — **classification binaire fortement déséquilibrée**. Deux classes — **mécontent** ou **satisfait** — et **3,96 %** de mécontents. Une exactitude de 96 % s'obtient en ne prédisant jamais « mécontent » : c'est pourquoi la métrique n'est pas l'exactitude.


**Équipe de 3 · 6 semaines · rendu par dépôt**

---

## Le contexte

Une banque veut savoir, **parmi ses clients actuels**, lesquels risquent de partir en se plaignant.
Elle a un budget d'appels limité : elle ne peut pas rappeler tout le monde, et elle veut rappeler les
bons.

## La question à laquelle le projet répond

> Peut-on repérer, dans le dossier d'un client, ceux qui vont se plaindre — et de combien une méthode
> soignée bat-elle le tri que la banque applique aujourd'hui sans modèle ?

## Ce que vous recevez

| Fichier | Contenu |
|---|---|
| `train.csv` | **60 816 clients** dont l'issue est connue — 371 colonnes, dont `TARGET` (1 = mécontent) |
| `a_decider.csv` | **15 204 clients** — les 370 mêmes colonnes, **sans `TARGET`** |

**3,96 % des clients de `train.csv` sont mécontents** (3 008 sur 76 020 au total).

**Deux avertissements :**

- **toutes les variables sont anonymisées** (`var3`, `var15`, `imp_op_var39_comer_ult1`, …). Il n'y a
  pas de sens métier à retrouver : votre travail est de **mesurer**, pas d'interpréter. La connaissance
  du domaine ne vous aidera pas ; l'analyse, si ;
- **beaucoup de variables de montant sont nulles la plupart du temps.** C'est une information en soi.

Aucune donnée ne permet d'identifier une personne : `ID` est un numéro interne.


## Ce que contient chaque colonne

| Famille | Nombre | Ce que c'est |
|---|---|---|
| `ID` | 1 | identifiant du client |
| `saldo_` | **71** | **soldes** : montants détenus, à différentes dates |
| `imp_` | **49** | **imports** : montants des opérations |
| `num_` | **143** | **nombres** : comptages d'opérations, de produits, de contrats |
| `ind_` | **75** | **indicateurs** : présence/absence, 0 ou 1 |
| `delta_` | **26** | **variations** entre deux dates |
| `var3`, `var15`, `var21`… | 6 | quelques variables isolées, hors famille |
| `TARGET` | 1 | **la cible** : 1 = client mécontent |

**Trois faits mesurés sur les données livrées, et ils comptent :**

- **97 colonnes sur 370 sont constantes** sur un échantillon de 4 000 lignes : elles ne séparent rien.
  À vous de vérifier lesquelles, et de décider ce que vous en faites ;
- **`var3` contient la valeur `-999999`** dans une petite minorité de lignes : c'est une **sentinelle**
  de valeur manquante, pas un montant ;
- aucune valeur n'est vide au sens `NaN` : une valeur manquante est **codée**, et il faut la reconnaître.


**Ce que Kaggle documente, et ce qu'il ne documente pas.** La page *Data* de cette compétition ne
publie **aucune description par colonne** : les variables sont anonymisées et la compétition ne donne
que leurs familles. **Les lignes ci-dessus sont donc tout ce qui est documenté** — vous ne trouverez
pas, en ligne, à quoi correspond une variable précise. C'est une contrainte du sujet, et elle est
volontaire : votre travail est de **mesurer** ce que chaque variable apporte, pas de l'interpréter.

## Ce que vous rendez

**Un dépôt de code**, pas un notebook :

1. un **pipeline exécutable** qui prend `a_decider.csv` et produit `ID,TARGET` — une **décision** ;
2. le **protocole de validation** retenu, justifié ;
3. les **essais**, y compris ceux qui ont échoué, avec leur score ;
4. une **note de 3 pages** : décision, métrique et seuil, méthode, résultat chiffré, ce qui a échoué ;
5. une **model card** ;
6. la **fiche de données** du S13.

Le pipeline doit tourner **en moins de 10 minutes sur CPU**, sans GPU, avec `scikit-learn` seul.

## Ce que l'enseignant garde — et ce que vous pouvez demander

**Vous recevez toutes les lignes, sauf mention contraire ci-dessous.** Ce qui reste chez l'enseignant
n'est **jamais** une partie des données : c'est **la cible** des lignes que vous devez estimer, et elle
seule. Sans elle, il n'y aurait rien à prédire.

| | |
|---|---|
| Fichier retenu | **`verite.csv`** |
| Lignes | **15 204** |
| Colonnes | `ID`, `TARGET` |
| Contenu | l'issue réelle des clients de `a_decider.csv` |

**Vous n'y avez pas accès, et aucune copie ne doit circuler.** C'est l'enseignant qui mesure votre
rendu contre ce fichier.

### La table source complète est disponible sur demande

Les données de ce sujet viennent d'une **compétition publique**. Si vous voulez travailler sur la
**table d'origine entière** — plus de lignes, plus de variables, ou les fichiers annexes — **demandez-la
à l'enseignant** : il l'a, et il peut vous la fournir pour un usage d'étude. Précisez dans votre
journal ce que vous en avez fait, et **restez sur la même découpe** : le rendu final porte sur les
lignes de `a_estimer.csv` / `a_decider.csv` / `horizon.csv`, pas sur la table complète.

## Les trois rôles, et comment ils tournent

Vous êtes trois, et le projet ne se juge pas sur des **tâches** (« les features », « le modèle », « les
slides ») mais sur des **décisions**. Chacune a un responsable nommé, qui doit pouvoir la défendre
**seul**, sans ses coéquipiers.

| Rôle | La question qu'il porte | Ce qu'il produit | La question qu'on lui posera |
|---|---|---|---|
| **Le mesureur** | *Sur quoi juge-t-on ?* | le découpage, le plancher, le protocole d'essai, le tableau des essais | « pourquoi cette métrique, et pas l'exactitude ? » |
| **Le constructeur** | *Avec quoi, et en combien de temps ?* | le chargement, les variables, le pipeline reproductible, les **trois mutations nommées** | « montre-moi la mutation qui casse le découpage » |
| **L'interprète** | *Que vaut le résultat, et que dit-il du monde ?* | l'analyse d'erreurs, la model card, le test de robustesse | « qui rates-tu le plus, et combien ça coûte ? » |

Découper par tâche donne trois exécutants dont aucun ne peut défendre une décision. Découper par
question donne trois responsables — et c'est ce que l'oral vérifie.

**Sur ce sujet, le rôle dominant est le mesureur** — parce que 3,96 % de mécontents : une exactitude de **96,04 %** s'obtient en ne prédisant jamais « mécontent » — et n'attrape alors **aucun** des 602 clients réellement mécontents. Seuls l'AUC et le seuil disent quelque chose.

### La rotation aux trois actes

Les trois actes sont **S5**, **S9** et **S13-S14**. À chaque acte, les rôles **tournent** : personne ne
tient deux fois le même, et **le responsable du dépôt change**. Au bout des trois, chacun a porté les
trois questions une fois.

**Acte 1 (S5).** *Awa* est **mesureur** : découpage stratifié, plancher à **AUC 0,6890**. *Brice* est **constructeur** : pipeline sur 371 colonnes, dont 97 constantes à repérer. *Chloé* est **interprète** : à quoi ressemble un client mécontent. **Awa signe.**

**Acte 2 (S9).** *Brice* passe **mesureur** : il démontre que l'exactitude est un piège et chiffre ce qu'un seuil bas attrape. *Chloé* passe **constructeur** : les trois mutations. *Awa* passe **interprète** : les mécontents ratés. **Brice signe.**

**Acte 3 (S13-S14).** *Chloé* **mesureur**, *Awa* **constructeur**, *Brice* **interprète**. **Chloé signe.**

**Ce que la rotation empêche.** Le piège classique : trois personnes optimisent l'exactitude pendant cinq semaines et découvrent au S13 que le modèle ne sert à rien. La rotation met **chacun** devant la métrique avant la fin.

### Et si quelqu'un disparaît deux semaines ?

Son rôle est **doublé** par celui qui l'a tenu à l'acte précédent — c'est précisément à cela que sert la
rotation : au S9, chacun a déjà vu un autre rôle de l'intérieur. Le carnet de bord note la date de
reprise, ce qui a été suspendu, et qui a signé à la place. Une équipe qui n'a pas doublé son rôle
critique **avant** le S9 perdra du temps qu'elle ne rattrapera pas.

## Travailler : récupérer les données, coder, sauvegarder

Les données du cours sont sur le **Drive du cours**, en lecture seule — **dossier du sujet :**
**(lien du Drive communiqué par l’enseignant)**. Vous téléchargez **le dossier de votre sujet** — pas les autres — et vous choisissez
ensuite **où coder**. Le lien est rappelé au **premier écran du carnet de démarrage**.

Le dossier contient **trois choses** : cet énoncé, le **carnet de démarrage** (`Carnet_de_demarrage.ipynb`)
et les fichiers de données.

### 1. Récupérer votre dossier

| | |
|---|---|
| Dossier du sujet | **`Sujet_05_Santander_Satisfaction/`** |
| Poids attendu | **75,6 Mo** |
| Contenu | les fichiers listés dans « Ce que vous recevez » |

Après téléchargement, vérifiez que rien n'est tronqué : le poids du dossier doit correspondre, et
chaque `csv` doit s'ouvrir avec le bon nombre de lignes.

### 2. Option A — travailler en local, dans VS Code

C'est la voie la plus simple : vos fichiers sont sur votre disque, rien ne disparaît.

```
python -m venv .venv
```

```
source .venv/bin/activate
```

*(sous Windows : `.venv\Scripts\activate`)*

```
pip install pandas scikit-learn
```

Ouvrez le dossier dans VS Code, écrivez votre pipeline — `pipeline.py` par exemple — et lancez-le :

```
python pipeline.py
```

**La contrainte des 10 minutes s'applique à votre machine.** Mesurez-la : elle fait partie du
livrable, et un pipeline qui tourne en 40 minutes sur votre portable ne sera pas accepté.

### 3. Option B — travailler dans un carnet Kaggle

Kaggle ne voit pas votre disque : il faut **lui donner vos fichiers**, en créant votre propre jeu de
données. C'est vous qui le déposez, pour votre usage — le jeu est **privé par défaut**.

1. **kaggle.com/datasets** → **New Dataset**.
2. Déposez les fichiers du dossier `Sujet_05_Santander_Satisfaction/` (glisser-déposer), nommez le jeu de données
   `esgc-vak-sujet-05-…`, puis **Create**.
3. Dans votre carnet : **Add Input** → onglet **Datasets** → filtre **Your Datasets** → sélectionnez
   le vôtre → **Add**.
4. Les fichiers apparaissent dans **`/kaggle/input/<nom-de-votre-jeu>/`**, en **lecture seule**.
   Vérifiez avant d'écrire du code :

```
!ls /kaggle/input/<nom-de-votre-jeu>/
```

5. Réglez la session : **Session options** → **Accelerator : None** — le projet tient sur CPU, c'est
   la contrainte du cours. Laissez **Internet désactivé**.

> **La compétition d'origine n'est pas la source.** Ne cherchez pas à l'ajouter : ses fichiers
> diffèrent des vôtres — pas d'horizon sans cible, pas de jeu à estimer — et plusieurs de ces
> compétitions ne sont plus rejoignables.

### 4. Sauvegarder, et réutiliser votre travail

**En local (Option A).** Votre dossier de travail **est** la sauvegarde. Gardez les sorties dans un
sous-dossier `sorties/`, et versionnez avec `git` si vous le souhaitez.

**Sur Kaggle (Option B).** `/kaggle/input` est en **lecture seule** : écrivez dans
**`/kaggle/working/`**.

```python
import os
os.makedirs("/kaggle/working/sorties", exist_ok=True)
prediction.to_csv("/kaggle/working/sorties/prediction.csv", index=False)
```

- **Sauvegarder** : bouton **Save Version** → **Save & Run All (Commit)**. Le carnet est **ré-exécuté
  de bout en bout** dans un conteneur propre, et **tout ce qui reste dans `/kaggle/working/` est
  conservé** comme sortie de cette version.
- **Reprendre ces sorties dans un autre carnet** : **Add Input** → onglet **Notebook Output** →
  votre carnet, la version voulue → le contenu apparaît dans `/kaggle/input/<nom-du-carnet>/`.
- **⚠️ `/kaggle/working` est éphémère** : une session inactive est coupée au bout de 20 minutes. Sans
  **Save Version**, tout est perdu.

**Quel que soit votre choix**, le livrable est le même : un **dépôt de code** reproductible, dont le
pipeline tourne en moins de 10 minutes sur CPU.

## Les trois temps du projet

### Bloc 1 — avant la séance 5 · *la décision et la mesure*

- **La métrique** : laquelle, et **ce qu'elle récompense**. Une métrique peut être satisfaite par un
  modèle qui ne trouve personne.
- **Le coût** : ce que coûte un client mécontent qu'on n'a pas rappelé, et ce que coûte un appel
  inutile. Les deux n'ont pas le même prix.
- **La règle métier** : comment la banque trie-t-elle ses clients aujourd'hui, sans modèle ?
  Mesurez-le. C'est votre plancher.
- **Le protocole de validation** : comment vous découpez `train.csv`, et pourquoi ce découpage-là.

### Bloc 2 — avant la séance 9 · *le pipeline*

- Le pipeline complet, exécutable d'un bout à l'autre.
- **Au moins huit essais**, dont ceux qui ont échoué, chacun avec son score.
- **La sélection de variables** : il y en a 369. Les garder toutes coûte du temps — mesurez-le, et
  décidez.
- **L'analyse d'erreurs** : sur quels clients vous vous trompez.

### Bloc 3 — avant la séance 13 · *le dépôt et la robustesse*

- Le dépôt propre, la note de 3 pages, la model card, la fiche de données.
- **Trois mutations nommées**, chacune applicable en **une cellule**.
- Le test de robustesse, et la décision finale sur les 15 204 clients.

## Comment vous êtes évalués

Voir la grille du cours. Trois points pèsent particulièrement ici :

- **la métrique et le seuil** : un modèle qui ne trouve personne peut afficher un score flatteur ;
- **le chiffre contre le plancher** : votre score se rapporte à la règle métier, pas à zéro ;
- **la vérité du journal** : le journal consigne les essais, y compris ceux qui ont échoué.

## Deux règles du cours

**Pas de fuite.** Une information inconnue **au moment où le dossier est ouvert** ne peut pas entrer
dans le modèle.

**Le code doit rester réparable.** On doit pouvoir passer d'une version à l'autre en changeant une
cellule, pas en réécrivant le pipeline.
