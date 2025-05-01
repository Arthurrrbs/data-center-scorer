import requests

def get_consommation_residentielle(commune: str, annee="2022"):
    url = "https://data.enedis.fr/api/records/1.0/search/"
    params = {
        "dataset": "consommation-electrique-par-secteur-dactivite-commune",
        "refine.nom_commune": commune,
        "refine.annee": annee,
        "refine.secteur_d_activite": "Résidentiel",
        "rows": 1
    }
    try:
        response = requests.get(url, params=params)
        records = response.json()["records"]
        if records:
            return records[0]["fields"]["consommation_mwh"]
        else:
            return None
    except Exception as e:
        print("Erreur Enedis:", e)
        return None
