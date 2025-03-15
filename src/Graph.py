import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("produits_nettoyes.1.csv", sep=";")


plt.figure("1")
sns.histplot(df["prix"], bins=30, kde=True)
plt.title("Répartition des prix des produits")
plt.xlabel("prix")
plt.ylabel("quantité")
plt.grid(True)
plt.show()
plt.savefig("Histogramme_des_prix.png", format="png", dpi=300)

plt.figure("2")
sns.scatterplot(data=df, x="taille_ecran", y="prix")
plt.title("Prix vs Taille de l’écran")
plt.xlabel("Taille de l’écran (pouces)")
plt.ylabel("Prix (€)")
plt.grid(True)
plt.savefig("Nuage_de_points_Prix_vs_Taille_ecran.png", format="png", dpi=300)
plt.show()

plt.figure("3")
sns.countplot(data=df, y="short_processeur", order=df["short_processeur"].value_counts().index)
plt.title("Nombre de produits par type de processeur")
plt.xlabel("Nombre de produits")
plt.ylabel("Type de processeur")
plt.grid(True)
plt.savefig("Nombre_de_produits_par_processeur.png", format="png", dpi=300)
plt.show()

plt.figure("4")
sns.scatterplot(data=df, x="stock_disponible", y="prix")
plt.title("Prix vs Stock disponible")
plt.xlabel("Stock disponible")
plt.ylabel("Prix (€)")
plt.grid(True)
plt.savefig("Prix_vs_Stock_disponible.png", format="png", dpi=300)
plt.show()

plt.figure("5")
sns.scatterplot(data=df, x="avis", y="prix")
plt.title("Prix vs Nombre d’avis")
plt.xlabel("Nombre d’avis")
plt.ylabel("Prix (€)")
plt.grid(True)
plt.savefig("Prix_vs_Nombre_d_avis.png", format="png", dpi=300)
plt.show()

plt.figure("6")
sns.boxplot(data=df, y="prix")
plt.title("Répartition des prix avec détection des outliers")
plt.ylabel("Prix (€)")
plt.grid(True)
plt.savefig("Boxplot_Prix_Outliers.png", format="png", dpi=300)
plt.show()