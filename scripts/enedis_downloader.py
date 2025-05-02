# scripts/enedis_downloader.py

import requests
from datetime import datetime
import os

# Crée un dossier 'data' s'il n'existe pas
os.makedirs("data", exist_ok=True)

# Nom du fichier (avec date)
today = datetime.now().strftime("%Y-%m-%d")
filename = f"data/enedis_conso_communes_{today}.csv"

# URL vers les données Enedis (full dataset)
url = "https://data.enedis.fr/explore/dataset/consommation-electrique-par-secteur-dactivite-commune/download/?format=csv&timezone=Europe/Berlin&use_labels_for_header=true"

print("📥 Téléchargement des données Enedis...")
response = requests.get(url)

if response.status_code == 200:
    with open(filename, "wb") as f:
        f.write(response.content)
    print(f"✅ Données enregistrées dans {filename}")
else:
    print(f"❌ Erreur lors du téléchargement : {response.status_code}")
