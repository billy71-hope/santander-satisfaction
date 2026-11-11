from sklearn.metrics import roc_auc_score, roc_curve
import numpy as np
import matplotlib.pyplot as plt

CIBLE = "TARGET"
y = train[CIBLE]

# === 1.11a : Distribution de la cible ===
print("Distribution de TARGET :")
print(y.value_counts())
print(f"\nTaux de mécontents : {y.mean()*100:.2f} %")


# === 1.11b : Modèle naïf vs aléatoire ===
y_pred_naif = np.zeros(len(y))
exactitude_naif = (y == 0).mean()

np.random.seed(42)
y_pred_aleatoire = np.random.rand(len(y))
auc_aleatoire = roc_auc_score(y, y_pred_aleatoire)

print(f"Modèle naïf (prédit toujours 0) :")
print(f"  Exactitude : {exactitude_naif*100:.2f} %  ← chiffre trompeur")
print(f"  AUC        : 0.5000              ← pas mieux que le hasard")
print(f"\nModèle aléatoire :")
print(f"  AUC        : {auc_aleatoire:.4f}  ← converge vers 0.5")
print(f"\nPlancher métier (règle de la banque sans modèle) : AUC = 0.6890")


# === 1.11c : Courbe ROC de référence ===
fig, ax = plt.subplots(figsize=(7, 5))

ax.plot([0, 1], [0, 1], 'k--', label='Hasard (AUC = 0.50)')
ax.axhline(y=0.6890, color='orange', linestyle=':', label='Plancher métier : AUC = 0.6890')

ax.set_xlabel("Taux de faux positifs (FPR)")
ax.set_ylabel("Taux de vrais positifs (TPR)")
ax.set_title("Courbe ROC — références")
ax.legend()
ax.set_xlim([0, 1])
ax.set_ylim([0, 1])
plt.tight_layout()
plt.show()


# === 1.11d : Bilan ===
print("=== BILAN 1.11 — La métrique ===")
print("  Métrique choisie : AUC-ROC")
print("  Pourquoi : l'exactitude est trompeuse sur données déséquilibrées (3.96 % mécontents)")
print("  L'AUC mesure la capacité à ordonner, indépendamment du seuil de décision")
print(f"  Plancher à battre : AUC = 0.6890 (règle métier de la banque)")
print("  Un modèle utile doit dépasser ce plancher.")
