# === 1.7a : Doublons de lignes ===
n_doublons_lignes = train.duplicated().sum()
print(f"Lignes dupliquées : {n_doublons_lignes}")

if n_doublons_lignes > 0:
    print("\nExemple de doublons :")
    masque = train.duplicated(keep=False)
    display(train[masque].head(6))
else:
    print("Aucune ligne dupliquée — le jeu est propre sur ce point.")


# === 1.7b : Doublons de colonnes ===
colonnes = [c for c in train.columns if c != "TARGET"]
groupes_doublons = {}
deja_vu = {}

for col in colonnes:
    h = hash(train[col].values.tobytes())
    if h in deja_vu:
        ref = deja_vu[h]
        if ref not in groupes_doublons:
            groupes_doublons[ref] = []
        groupes_doublons[ref].append(col)
    else:
        deja_vu[h] = col

if groupes_doublons:
    print(f"{sum(len(v) for v in groupes_doublons.values())} colonne(s) dupliquée(s) :")
    for ref, copies in groupes_doublons.items():
        print(f"  '{ref}' == {copies}")
else:
    print("Aucune colonne dupliquée.")


# === 1.7c : Bilan ===
colonnes_a_supprimer = [col for copies in groupes_doublons.values() for col in copies]

print("=== BILAN 1.7 — Doublons ===")
print(f"  Lignes dupliquées     : {n_doublons_lignes}")
print(f"  Colonnes dupliquées   : {len(colonnes_a_supprimer)}")
if colonnes_a_supprimer:
    print(f"  → Colonnes supprimables sans perte d'info : {colonnes_a_supprimer}")
else:
    print("  → Aucune suppression nécessaire.")
