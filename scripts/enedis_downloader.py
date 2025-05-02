# scripts/enedis_downloader.py

import requests
from datetime import datetime
import os

# Créer dossier /data
os.makedirs("data", exist_ok=True)

# Nom de fichier avec date du jour
today = datetime.now().strftime("%Y-%m-%d")
filename = f"data/enedis_conso_communes_{today}.csv"

# URL Enedis
url = "https://data.enedis.fr/explore/dataset/consommation-electrique-par-secteur-dactivite-commune/download/?format=csv&timezone=Europe/Berlin&use_labels_for_header=true"

print("📥 Téléchargement des données Enedis...")

try:
    response = requests.get(url, timeout=60)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"✅ Données enregistrées dans {filename}")
    else:
        print(f"❌ Erreur HTTP : {response.status_code}")
except Exception as e:
    print(f"❌ Exception : {e}")
