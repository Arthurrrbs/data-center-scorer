import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")
st.title("🔌 Test API Enedis – Saint-Pair-sur-Mer (agrégation 2023)")

commune = "Saint-Pair-sur-Mer"
annee = "2023"
data = []

with st.spinner(f"🔍 Récupération des données Enedis pour {commune} en {annee}..."):
    url = "https://data.enedis.fr/api/records/1.0/search/"
    params = {
        "dataset": "consommation-electrique-par-secteur-dactivite-commune",
        "q": commune,
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
                if fields.get("nom_commune", "").lower() == commune.lower() and str(fields.get("annee")) == annee:
                    conso = fields.get("conso_totale_mwh", 0)
                    secteur = fields.get("code_grand_secteur", "Non spécifié")
                    if conso:
                        total_conso += conso
                        secteurs.append({"Secteur": secteur, "Conso_totale_MWh": conso})
            if total_conso > 0:
                data.append({"Commune": commune, "Consommation_Totale_MWh": total_conso})
                secteurs_df = pd.DataFrame(secteurs)
        else:
            st.error(f"❌ Erreur API : {response.status_code}")
    except Exception as e:
        st.error(f"❌ Exception : {e}")

if data:
    df = pd.DataFrame(data)
    st.success("✅ Données agrégées pour la commune :")
    st.dataframe(df)
    st.subheader("🔎 Détail par secteur :")
    st.dataframe(secteurs_df)
else:
    st.warning(f"⚠️ Aucune donnée récupérée pour {commune} en {annee}.")
