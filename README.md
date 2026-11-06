# Sujet 05 — Identifier le client qui va se plaindre (Santander Satisfaction)

Classification binaire très déséquilibrée : **3,96 %** de clients mécontents (`TARGET = 1`).
La métrique n'est pas l'exactitude (96 % en ne prédisant jamais « mécontent ») : on juge sur l'**AUC** et sur le **seuil** de décision.
Plancher (règle métier) : **AUC 0,6890**.

Énoncé complet : [`docs/enonce.md`](docs/enonce.md)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Placer `train.csv` et `a_decider.csv` (Drive du cours, dossier `Sujet_05_Santander_Satisfaction/`) dans `data/`.
**Les données ne sont pas versionnées** (`*.csv` ignoré).

## Déposer des fichiers

**Depuis le site GitHub** (le plus simple) : ouvrir le dossier voulu → **Add file → Upload files** → glisser les fichiers → **Commit changes**.

**Depuis son ordinateur, avec git :**

```bash
# une seule fois
git clone https://github.com/billy71-hope/santander-satisfaction.git
cd santander-satisfaction
git config user.name "votre-login-github"
git config user.email "votre-email-github"

# à chaque fois
git pull                      # récupérer le travail des autres d'abord
git add <fichiers>
git commit -m "ce que j'ai fait"
git push
```

Si `git push` demande un mot de passe : utiliser `gh auth login` (GitHub CLI) ou un *personal access token*, pas le mot de passe du compte.

**Ne jamais déposer les `.csv`** (données du cours) : ils restent dans `data/` sur chaque machine.

## Structure

| Dossier | Contenu |
|---|---|
| `data/` | données du cours (non versionnées) |
| `carnets/` | carnet de démarrage |
| `docs/` | énoncé, note de 3 pages, model card, fiche de données |
| `sorties/` | prédictions `ID,TARGET` (non versionnées) |

## Livrables

1. Pipeline exécutable `a_decider.csv` → `ID,TARGET` (< 10 min sur CPU, scikit-learn seul)
2. Protocole de validation justifié
3. Journal des essais (y compris les échecs) avec leur score
4. Note de 3 pages
5. Model card
6. Fiche de données
