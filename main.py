import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")
st.title("🔌 Test API Enedis – Agrégation pour plusieurs communes (2023)")

communes = [
    "Saint-Pair-sur-Mer",
    "Le Parc",
    "Montpellier",
    "Lyon",
    "Marseille"
]
annee = "2023"
data = []

def get_commune_data(commune, annee):
    url = "https://data.enedis.fr/api/records/1.0/search/"
    params = {
        "dataset": "consommation-electrique-par-secteur-dactivite-commune",
        "q": commune,
        "rows": 100
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        records = response.json().get("records", [])
        total_conso = 0
        for rec in records:
            fields = rec.get("fields", {})
            if fields.get("nom_commune", "").lower() == commune.lower() and str(fields.get("annee")) == annee:
                conso = fields.get("conso_totale_mwh", 0)
                if conso:
                    total_conso += conso
        return total_conso
    return None

with st.spinner("🔍 Agrégation des données Enedis pour plusieurs communes..."):
    for commune in communes:
        total = get_commune_data(commune, annee)
        if total:
            data.append({"Commune": commune, "Consommation_Totale_MWh": total})

if data:
    df = pd.DataFrame(data)
    df_sorted = df.sort_values(by="Consommation_Totale_MWh", ascending=False)
    st.success("✅ Données agrégées pour les communes :")
    st.dataframe(df_sorted)
else:
    st.warning("⚠️ Aucune commune n'a pu être scorée avec succès.")
