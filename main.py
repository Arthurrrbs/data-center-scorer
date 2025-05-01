import streamlit as st
import requests

st.set_page_config(layout="wide")
st.title("🔌 Test API Enedis – Vérification simple")

# Code commune INSEE à tester
code_insee_test = "34172"  # Montpellier
annee = "2022"

# Requête API Enedis
url = "https://data.enedis.fr/api/records/1.0/search/"
params = {
    "dataset": "consommation-electrique-par-secteur-dactivite-commune",
    "refine.annee": annee,
    "refine.code_insee_commune": code_insee_test,
    "rows": 1
}

with st.spinner("🔍 Requête Enedis en cours..."):
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            records = response.json().get("records", [])
            if records:
                fields = records[0]["fields"]
                st.success("✅ Données trouvées !")
                st.json(fields)
            else:
                st.warning("⚠️ Aucune donnée trouvée pour ce code INSEE.")
        else:
            st.error(f"❌ Erreur {response.status_code} : {response.text}")
    except Exception as e:
        st.error(f"❌ Exception levée : {e}")
