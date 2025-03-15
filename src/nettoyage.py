import pandas as pd
import numpy as np
import re

df = pd.read_csv("produits (4).csv")

print(df.shape)  # Affiche (nombre de lignes, nombre de colonnes)
print(df.columns)  # Affiche les noms des colonnes
print(df.head())  # Affiche les 5 premières lignes
print(df.info())  # Affiche des infos sur le type des colonnes et les valeurs manquantes

df = df[df['prix'] != 'Prix non disponible']
df['prix'] = df['prix'].str.replace('€', '').str.replace('\u202f', '').str.replace(',', '.').str.strip().astype('float64').astype('int64')
print(df['prix'].dtype)  #affiche le type de donnees de la colonne
print(df['prix'].describe())  #affiche stats


print(df['marque'].unique())

print(df['marque'].value_counts())

# Correction des marques
df['marque'] = df['marque'].replace('HEWLETT', 'HP')
allowed_brands = ['ACEMAGIC', 'TECLAST', 'AOC', 'ACER', 'Lenovo', 'Dell', 'HP', 'Asus', 'Apple', 'MSI', 'NiPoGi', 'Samsung', 'UMIDIGI', 'BMAX', 'Blackview', 'LG']
df['marque'] = df['marque'].apply(lambda x: x if x in allowed_brands else np.nan)

# Nombre de NaN dans la colonne 'marque' avant la recherche dans la description
num_nan = df['marque'].isna().sum()
total = len(df)
print(f"Nombre de NaN dans marque avant recherche dans description: {num_nan} / {total}")

# Création du pattern regex insensible à la casse pour les marques
brand_pattern = '|'.join(allowed_brands)

# Mise à jour de la colonne "marque" en utilisant la description
df['marque'] = df.apply(lambda row: re.search(brand_pattern, row['description'], re.IGNORECASE).group(0)
if pd.isna(row['marque']) and re.search(brand_pattern, row['description'], re.IGNORECASE)
else row['marque'], axis=1)


# Fonctions d'extraction corrigées
def extract_screen_size(description):
    # Recherche d'une taille d'écran plausible (entre 10 et 17 pouces)
    match = re.search(r'(\d{1,2}[,.]\d{1,2})["\']?\s*[Pp]ouces?|(\d{1,2})["\']?\s*[Pp]ouces?', description)
    if match:
        # Si un match est trouvé, retourne la valeur en float
        screen_size = match.group(1) if match.group(1) else match.group(2)
        # Remplacer les virgules par des points pour la conversion en float
        screen_size = screen_size.replace(',', '.')
        return float(screen_size)
    return np.nan


def extract_os(description):
    os_keywords = ['Windows 11', 'Windows 10', 'Chrome OS', 'Linux', 'Mac OS']
    for os in os_keywords:
        if os in description:
            return os
    # Cas spécial pour Chrome OS avec des variations
    if re.search(r'Chrome\s*OS', description, re.IGNORECASE):
        return 'Chrome OS'
    return np.nan


def extract_ram(description):
    # Liste des tailles de RAM standard pour les ordinateurs portables
    standard_ram_sizes = [2, 4, 6, 8, 12, 16, 24, 32, 64]

    # Recherche d'abord les mentions très explicites de RAM
    explicit_ram_patterns = [
        r'(\d{1,2})\s*Go\s+RAM',  # 16 Go RAM
        r'(\d{1,2})\s*Go\s+de\s+RAM',  # 16 Go de RAM
        r'RAM\s+(\d{1,2})\s*Go',  # RAM 16 Go
        r'(\d{1,2})\s*Go\s+DDR\d',  # 16 Go DDR4
        r'(\d{1,2})Go\s+DDR\d',  # 16Go DDR4
        r'(\d{1,2})\s*Go\s+LPDDR\d',  # 16 Go LPDDR4
        r'(\d{1,2})Go\s+LPDDR\d',  # 16Go LPDDR4
    ]

    for pattern in explicit_ram_patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            ram_size = int(match.group(1))
            if ram_size in standard_ram_sizes:
                return ram_size

    # Recherche de patterns très spécifiques comme "RAM 16 Go"
    specific_ram_pattern = re.search(r'RAM\s+(\d{1,2})', description, re.IGNORECASE)
    if specific_ram_pattern:
        ram_size = int(specific_ram_pattern.group(1))
        if ram_size in standard_ram_sizes:
            return ram_size

    # Recherche de patterns comme "8+256Go" qui indiquent souvent "8Go RAM + 256Go SSD"
    ram_ssd_pattern = re.search(r'(\d{1,2})\s*\+\s*\d+\s*Go', description, re.IGNORECASE)
    if ram_ssd_pattern:
        ram_size = int(ram_ssd_pattern.group(1))
        if ram_size in standard_ram_sizes:
            return ram_size

    # Vérification pour les modèles avec "mémoire" ou "memory"
    memory_pattern = re.search(r'(\d{1,2})\s*Go\s+de\s+mémoire', description, re.IGNORECASE)
    if memory_pattern:
        ram_size = int(memory_pattern.group(1))
        if ram_size in standard_ram_sizes:
            return ram_size

    # Recherche d'un autre pattern commun
    ram_pattern = re.search(r'RAM\s+(\d{1,2})\s*Go', description, re.IGNORECASE)
    if ram_pattern:
        ram_size = int(ram_pattern.group(1))
        if ram_size in standard_ram_sizes:
            return ram_size

    # Si aucune des recherches précédentes n'a abouti, on cherche une occurrence isolée
    # de "X Go" ou "X GB" dans un contexte qui suggère la RAM
    isolated_pattern = re.search(r'(\d{1,2})\s*Go(?!\s*SSD|\s*HDD|\s*eMMC|\s*ROM)', description, re.IGNORECASE)
    if isolated_pattern:
        # Vérifier que ce n'est pas dans un contexte qui suggère autre chose que la RAM
        match_pos = isolated_pattern.start()
        context_before = description[max(0, match_pos - 30):match_pos]

        # Mots-clés qui suggèrent qu'il ne s'agit pas de RAM
        non_ram_keywords = ['ssd', 'disque', 'stockage', 'gpu', 'graphique', 'vidéo', 'batterie', 'core', 'cœur']

        if not any(keyword in context_before.lower() for keyword in non_ram_keywords):
            ram_size = int(isolated_pattern.group(1))
            if ram_size in standard_ram_sizes:
                return ram_size

    return np.nan


def extract_processor(description):
    # Liste de processeurs connus avec leurs modèles
    intel_processors = [
        r'Intel\s+Core\s+i\d+-\d{4,5}[A-Z]*',  # Ex: Intel Core i5-1235U, Intel Core i7-1255U
        r'Intel\s+Core\s+i\d+\s+\d{4,5}[A-Z]*',  # Ex: Intel Core i5 1235U
        r'Intel\s+Core\s+i\d+',  # Ex: Intel Core i5, Intel Core i7
        r'Intel\s+i\d+-\d{4,5}[A-Z]*',  # Ex: Intel i7-10850H
        r'Intel\s+i\d+',  # Ex: Intel i5, Intel i7
        r'Intel\s+Celeron\s+N\d{3,4}',  # Ex: Intel Celeron N4500
        r'Intel\s+Celeron\s+J\d{3,4}',  # Ex: Intel Celeron J4125
        r'Celeron\s+N\d{3,4}',  # Ex: Celeron N5095
        r'Celeron\s+J\d{3,4}',  # Ex: Celeron J4105
        r'ln-tel\s+([A-Za-z]+\s+)?N-?\d{2,3}',  # Pour capturer les variantes mal orthographiées
    ]

    amd_processors = [
        r'AMD\s+Ryzen\s+\d+\s+\d{4}[A-Z]*',  # Ex: AMD Ryzen 7 5825U
        r'AMD\s+Ryzen\s+\d+',  # Ex: AMD Ryzen 7, AMD Ryzen 5
        r'AMD\s+R\d+',  # Ex: AMD R3
    ]

    # Exclusion des modèles d'ordinateurs portables souvent confondus avec des processeurs
    exclusion_patterns = [
        r'^\s*[A-Z]\d+\s*$',  # Modèles comme G7, M3, etc.
        r'^\s*[A-Z]\d+[A-Z]\d+\s*$',  # Modèles comme T490, X1650
        r'^\s*[A-Z]\d{3,4}(-\d+)?\s*$',  # Modèles comme A315, T460
    ]

    # Recherche des processeurs Intel
    for pattern in intel_processors:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            result = match.group(0)
            # Vérifie si le résultat pourrait être un faux positif
            if not any(re.match(excl, result.strip()) for excl in exclusion_patterns):
                return result

    # Recherche des processeurs AMD
    for pattern in amd_processors:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            result = match.group(0)
            if not any(re.match(excl, result.strip()) for excl in exclusion_patterns):
                return result

    # Recherche de processeurs Celeron/Pentium sans le préfixe Intel
    processor_match = re.search(r'N\d{3,4}\s+Celeron|Celeron\s+N\d{3,4}|Celeron\s+J\d{3,4}', description)
    if processor_match:
        return processor_match.group(0)

    # Recherche les processeurs indiqués par des patterns comme "N5095 Processeur"
    processor_keyword_match = re.search(r'([A-Z]\d{3,4})\s+[Pp]rocesseur', description)
    if processor_keyword_match:
        return processor_keyword_match.group(1)

    return np.nan


def extract_storage(description):
    # Liste des tailles standard de stockage
    standard_storage_sizes = [32, 64, 128, 256, 512, 1024, 2048]

    # Patrons pour SSD explicites
    ssd_patterns = [
        r'(\d+)\s*(?:Go|GB|To|TB)\s+SSD',  # 512 Go SSD, 1 To SSD
        r'SSD\s+(\d+)\s*(?:Go|GB|To|TB)',  # SSD 512 Go
        r'(\d+)(?:Go|GB|To|TB)\s+SSD',  # 512Go SSD
        r'SSD\s+de\s+(\d+)\s*(?:Go|GB|To|TB)',  # SSD de 512 Go
        r'(\d+)\s*(?:Go|GB|To|TB)\s+M\.2\s+SSD',  # 512 Go M.2 SSD
        r'Disque\s+SSD\s+(\d+)\s*(?:Go|GB|To|TB)',  # Disque SSD 512 Go
        r'(\d+)\s*(?:Go|GB|To|TB)\s+NVMe',  # 512 Go NVMe
    ]

    #patrons pour eMMC
    emmc_patterns = [
        r'(\d+)\s*(?:Go|GB)\s+eMMC',  # 128 Go eMMC
        r'eMMC\s+(\d+)\s*(?:Go|GB)',  # eMMC 128 Go
    ]

    #patrons pour HDD
    hdd_patterns = [
        r'(\d+)\s*(?:Go|GB|To|TB)\s+HDD',  # 1 To HDD
        r'HDD\s+(\d+)\s*(?:Go|GB|To|TB)',  # HDD 1 To
        r'Disque\s+dur\s+(\d+)\s*(?:Go|GB|To|TB)',  # Disque dur 1 To
    ]

    #patrons pour stockage non spécifié (mais probablement SSD)
    generic_storage_patterns = [
        r'(\d+)\s*(?:Go|GB|To|TB)\s+de\s+stockage',  # 512 Go de stockage
        r'stockage\s+(\d+)\s*(?:Go|GB|To|TB)',  # stockage 512 Go
        r'(\d+)\s*(?:Go|GB|To|TB)\s+de\s+SSD',  # 512 Go de SSD
    ]

    #recherche des patrons de stockage SSD
    for pattern in ssd_patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            size = int(match.group(1))
            # Conversion To en Go si nécessaire
            if "To" in description[match.start():match.end()] or "TB" in description[match.start():match.end()]:
                size *= 1024

            # Vérification si la taille est standard
            if size in standard_storage_sizes or size % 128 == 0:
                return f"{size} Go SSD"

    # Recherche des patrons eMMC
    for pattern in emmc_patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            size = int(match.group(1))
            return f"{size} Go eMMC"

    # Recherche des patrons HDD
    for pattern in hdd_patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            size = int(match.group(1))
            # Conversion To en Go si nécessaire
            if "To" in description[match.start():match.end()] or "TB" in description[match.start():match.end()]:
                size *= 1024

            return f"{size} Go HDD"

    # Recherche des patrons génériques de stockage
    for pattern in generic_storage_patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            size = int(match.group(1))
            # Conversion To en Go si nécessaire
            if "To" in description[match.start():match.end()] or "TB" in description[match.start():match.end()]:
                size *= 1024

            # Vérification si la taille est standard
            if size in standard_storage_sizes or size % 128 == 0:
                return f"{size} Go SSD"  # Supposer SSD par défaut

    # Chercher des patterns comme "8+256Go" qui indiquent souvent "8Go RAM + 256Go SSD"
    ram_ssd_pattern = re.search(r'\d{1,2}\s*\+\s*(\d+)\s*Go', description, re.IGNORECASE)
    if ram_ssd_pattern:
        size = int(ram_ssd_pattern.group(1))
        if size in standard_storage_sizes or size % 128 == 0:
            return f"{size} Go SSD"

    # Recherche de nombres suivis de Go/GB qui pourraient être du stockage
    # Exclure les contextes qui suggèrent clairement la RAM
    storage_pattern = re.search(r'(\d+)\s*(?:Go|GB)(?!\s*RAM|\s*de\s*RAM|\s*DDR)', description, re.IGNORECASE)
    if storage_pattern:
        size = int(storage_pattern.group(1))
        # Vérifier si la taille est plausible pour le stockage (pour éviter de confondre avec RAM)
        if size >= 128 and (size in standard_storage_sizes or size % 128 == 0):
            return f"{size} Go SSD"  # Supposer SSD par défaut pour les ordinateurs modernes

    # Si aucun pattern n'a été trouvé
    return np.nan

# Application des fonctions
df['screen_size'] = df['description'].apply(extract_screen_size)
df['os'] = df['description'].apply(extract_os)
df['ram'] = df['description'].apply(extract_ram)
df['processor'] = df['description'].apply(extract_processor)
df['storage'] = df['description'].apply(extract_storage)

print(df['marque'].unique())
print(df['marque'].value_counts())

print(df['processor'].unique())
print(df['processor'].value_counts())

print(df['screen_size'].unique())
print(df['screen_size'].value_counts())

print(df['os'].unique())
print(df['os'].value_counts())

print(df['ram'].unique())
print(df['ram'].value_counts())

print(df['storage'].unique())
print(df['storage'].value_counts())

# Comptage des valeurs NaN et total des lignes pour chaque colonne
columns_to_check = ['marque', 'screen_size', 'os', 'ram', 'processor', 'storage']
for column in columns_to_check:
    num_nan = df[column].isna().sum()
    total = len(df)
    print(f"Nombre de NaN dans la colonne {column}: {num_nan} / {total}")

#df.to_csv('produits_nettoyes.csv', sep=';', index=False)

df_complete = df.dropna(subset=['screen_size', 'os', 'ram', 'processor', 'storage'])
print(df_complete.shape)
df_complete.to_csv('produits_complets.csv', sep=';', index=False)



