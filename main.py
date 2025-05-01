import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import folium_static

st.set_page_config(layout="wide")
st.title("📍 Carte API Enedis – Consommation électrique par commune (2023)")

communes = {
    "Saint-Pair-sur-Mer": {"code": "50532", "lat": 48.8026, "lon": -1.5471},
    "Le Parc": {"code": "50535", "lat": 48.7544, "lon": -1.2952},
    "Montpellier": {"code": "34172", "lat": 43.6111, "lon": 3.8777},
    "Lyon": {"code": "69385", "lat": 45.75, "lon": 4.85},
    "Marseille": {"code": "13055", "lat": 43.2965, "lon": 5.3698}
}

annee = "2023"
data = []

# Récupération des données depuis Enedis
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
    for name, props in communes.items():
        total = get_commune_data(props["code"], name, annee)
        if total:
            data.append({"Commune": name, "Code": props["code"], "Lat": props["lat"], "Lon": props["lon"], "Conso": total})

if data:
    df = pd.DataFrame(data)
    df_sorted = df.sort_values(by="Conso", ascending=False)
    st.success("✅ Données agrégées pour les communes :")
    st.dataframe(df_sorted)

    # Création de la carte
    m = folium.Map(location=[46.5, 2.5], zoom_start=5)

    for _, row in df_sorted.iterrows():
        folium.CircleMarker(
            location=[row["Lat"], row["Lon"]],
            radius=7,
            color="blue",
            fill=True,
            fill_opacity=0.6,
            popup=f"{row['Commune']} : {row['Conso']:.0f} MWh"
        ).add_to(m)

    folium_static(m)

else:
    st.warning("⚠️ Aucune commune n'a pu être scorée avec succès.")
