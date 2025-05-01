import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")
st.title("🔌 Test API Enedis – Agrégation multi-communes par filtrage local (2023)")

communes = {
    "Saint-Pair-sur-Mer": "50532",
    "Le Parc": "50535",
    "Montpellier": "34172",
    "Lyon": "69385",
    "Marseille": "13055"
}

annee = "2023"
data = []

def get_commune_data(code_insee, commune_name, annee):
    url = "https://data.enedis.fr/api/records/1.0/search/"
    params = {
        "dataset": "consommation-electrique-par-secteur-dactivite-commune",
        "q": commune_name,
        "rows": 100
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        records = response.json().get("records", [])
        total_conso = 0
        for rec in records:
            fields = rec.get("fields", {})
            if str(fields.get("code_commune")) == code_insee and str(fields.get("annee")) == annee:
                conso = fields.get("conso_totale_mwh", 0)
                if conso:
                    total_conso += conso
        return total_conso
    return None

with st.spinner("🔍 Agrégation des données Enedis pour plusieurs communes (filtrage local)..."):
    for name, code in communes.items():
        total = get_commune_data(code, name, annee)
        if total:
            data.append({"Commune": name, "Consommation_Totale_MWh": total})

if data:
    df = pd.DataFrame(data)
    df_sorted = df.sort_values(by="Consommation_Totale_MWh", ascending=False)
    st.success("✅ Données agrégées pour les communes :")
    st.dataframe(df_sorted)
else:
    st.warning("⚠️ Aucune commune n'a pu être scorée avec succès.")
