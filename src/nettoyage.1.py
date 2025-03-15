import pandas as pd
import numpy as np

df = pd.read_csv("produits_1.csv")

#pour ensuite compter les manquants par ligne
df['prix'] = df['prix'].replace('Prix non disponible', 'Non disponible')
df = df.replace('Non disponible', np.nan)
#Si plus d une case vide ou égale à NaN par ligne, on supprime la ligne
df = df[df.apply(lambda row: (row.isna().sum() + (row == '').sum()) <= 1, axis=1)]


#colonne prix
df['prix'] = df['prix'].str.replace('€', '').str.replace('\u202f', '').str.replace(',', '.').str.strip()
df['prix'] = df['prix'].replace('.', np.nan)
df['prix'] = df['prix'].astype('float64')
df['prix'] = pd.to_numeric(df['prix'], downcast='integer')


#convertir To en Go et supprimer toutes lettres
def convert_storage_to_numeric(storage):
    if pd.isna(storage):
        return np.nan
    storage = storage.replace('To', '1024').replace('Go', '').replace('GB', '').replace('TB', '1024').strip()
    try:
        return int(storage)
    except ValueError:
        return np.nan

df['disque_dur'] = df['disque_dur'].apply(convert_storage_to_numeric)

#enlever 'Pouces' et convertir la colonne en numerique
df['taille_ecran'] = df['taille_ecran'].str.replace('Pouces', '').str.strip()
df['taille_ecran'] = pd.to_numeric(df['taille_ecran'], errors='coerce')


#extraire dans une nouvele colonne le nom de la marque seule du processeur
def extract_processor_brand(processor):
    if pd.isna(processor) or processor == 'Non disponible':
        return np.nan
    brands = ['Intel', 'Celeron', 'Ryzen', 'MediaTek', 'Snapdragon', 'Apple', 'Pentium']
    for brand in brands:
        if brand in processor:
            return brand
    return 'Inconnu'


df['short_processeur'] = df['processeur'].apply(extract_processor_brand)

print(df.dtypes)


df.to_csv('produits_nettoyes.1.csv', sep=';', index=False)

