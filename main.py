import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")
st.title("🔌 Test API Enedis – Commune de Montpellier (via code INSEE)")

# Code INSEE de Montpellier
code_insee = "34172"
annee = "2022"
data = []

with st.spinner("🔍 Récupération des données Enedis pour Montpellier (tous secteurs)..."):
    url = "https://data.enedis.fr/api/records/1.0/search/"
    params = {
        "dataset": "consommation-electrique-par-secteur-dactivite-commune",
        "refine.annee": annee,
        "refine.code_insee_commune": code_insee,
        "rows": 100
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            records = response.json().get("records", [])
            total_conso = 0
            secteurs = []
            for rec in records:
                fields = rec.get("fields", {})
                conso = fields.get("consommation_mwh", None)
                secteur = fields.get("secteur_d_activite", "")
                if conso:
                    total_conso += conso
                    secteurs.append({"Secteur": secteur, "Conso_MWh": conso})
            if total_conso > 0:
                data.append({"Commune": "Montpellier", "Consommation_Totale_MWh": total_conso})
                secteurs_df = pd.DataFrame(secteurs)
        else:
            st.error(f"❌ Erreur API pour Montpellier")
    except Exception as e:
        st.error(f"❌ Exception pour Montpellier : {e}")

if data:
    df = pd.DataFrame(data)
    st.success("✅ Données agrégées pour la commune :")
    st.dataframe(df)
    st.subheader("🔎 Détail par secteur :")
    st.dataframe(secteurs_df)
else:
    st.warning("⚠️ Aucune donnée récupérée pour Montpellier.")
