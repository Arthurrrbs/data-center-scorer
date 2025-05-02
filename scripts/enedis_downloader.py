import requests
from datetime import datetime
import os

# Créer le dossier /data s'il n'existe pas
os.makedirs("data", exist_ok=True)

# Date du jour
today = datetime.now().strftime("%Y-%m-%d")
filename = f"data/enedis_conso_communes_{today}.csv"

# URL officielle Enedis
url = "https://data.enedis.fr/explore/dataset/consommation-electrique-par-secteur-dactivite-commune/download/?format=csv&timezone=Europe/Berlin&use_labels_for_header=true"

print("📥 Démarrage du téléchargement Enedis en streaming...", flush=True)

try:
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    print("⬇️", end="", flush=True)

    print(f"\n✅ Données enregistrées dans {filename}", flush=True)

except Exception as e:
    print(f"\n❌ Erreur pendant le téléchargement : {e}", flush=True)
