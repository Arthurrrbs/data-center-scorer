import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")
st.title("🔌 Test API Enedis – Connexion de test brute")

data = []

with st.spinner("🔍 Connexion brute à l'API Enedis..."):
    url = "https://data.enedis.fr/api/records/1.0/search/"
    params = {
        "dataset": "consommation-electrique-par-secteur-dactivite-commune",
        "rows": 5
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            records = response.json().get("records", [])
            st.success("✅ Connexion réussie. Voici 5 enregistrements :")
            st.write(records)
        else:
            st.error(f"❌ Erreur API : {response.status_code}")
    except Exception as e:
        st.error(f"❌ Exception lors de l'appel API : {e}")
