import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")
st.title("🔌 Test API Enedis – 20 plus grandes communes")

# Liste des 20 plus grandes communes françaises avec leur code INSEE
communes_insee = {
    "Paris": "75056",
    "Marseille": "13055",
    "Lyon": "69385",
    "Toulouse": "31555",
    "Nice": "06088",
    "Nantes": "44109",
    "Montpellier": "34172",
    "Strasbourg": "67482",
    "Bordeaux": "33063",
    "Lille": "59350",
    "Rennes": "35238",
    "Reims": "51454",
    "Le Havre": "76351",
    "Saint-Étienne": "42218",
    "Toulon": "83137",
    "Grenoble": "38185",
    "Dijon": "21231",
    "Angers": "49007",
    "Nîmes": "30189",
    "Villeurbanne": "69266"
}

annee = "2022"
data = []

with st.spinner("🔍 Récupération des données Enedis pour 20 communes..."):
    for nom, insee in communes_insee.items():
        url = "https://data.enedis.fr/api/records/1.0/search/"
        params = {
            "dataset": "consommation-electrique-par-secteur-dactivite-commune",
            "refine.annee": annee,
            "refine.code_insee_commune": insee,
            "rows": 1
        }
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                records = response.json().get("records", [])
                if records:
                    fields = records[0]["fields"]
                    conso = fields.get("consommation_mwh", None)
                    secteur = fields.get("secteur_d_activite", "")
                    if conso:
                        data.append({"Commune": nom, "INSEE": insee, "Consommation_MWh": conso, "Secteur": secteur})
            else:
                st.error(f"❌ Erreur API pour {nom} ({insee})")
        except Exception as e:
            st.error(f"❌ Exception pour {nom} ({insee}) : {e}")

if data:
    df = pd.DataFrame(data)
    st.success("✅ Données récupérées pour les communes suivantes :")
    st.dataframe(df)
else:
    st.warning("⚠️ Aucune donnée récupérée pour les 20 communes.")
