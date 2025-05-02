import streamlit as st
import pandas as pd
import requests
import folium
import json
from streamlit_folium import folium_static

st.set_page_config(layout="wide")
st.title("📡 Carte des Consommations Électriques par Commune – Données API Enedis (2023)")

# Étape 1 – Télécharger les 100 premières communes (code INSEE + nom)
@st.cache_data
def load_communes(n=100):
    url = "https://geo.api.gouv.fr/communes?fields=nom,code,centre&format=json&geometry=centre"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return pd.DataFrame(data[:n])
    else:
        return pd.DataFrame()

communes_df = load_communes(100)
st.success(f"✅ {len(communes_df)} communes chargées.")

# Étape 2 – Récupération des consommations depuis l’API Enedis
@st.cache_data
def get_consumption_data(communes_df, annee="2023"):
    base_url = "https://data.enedis.fr/api/records/1.0/search/"
    results = []
    for _, row in communes_df.iterrows():
        code = row["code"]
        nom = row["nom"]
        try:
            params = {
                "dataset": "consommation-electrique-par-secteur-dactivite-commune",
                "q": nom,
                "rows": 100
            }
            r = requests.get(base_url, params=params)
            if r.status_code == 200:
                total = 0
                records = r.json().get("records", [])
                for rec in records:
                    fields = rec.get("fields", {})
                    if str(fields.get("code_commune")) == code and str(fields.get("annee")) == annee:
                        total += fields.get("conso_totale_mwh", 0)
                if total > 0:
                    results.append({"code_commune": code, "nom_commune": nom, "consommation_mwh": total})
        except:
            continue
    return pd.DataFrame(results)

with st.spinner("🔌 Récupération des données de consommation..."):
    df_conso = get_consumption_data(communes_df)

if df_conso.empty:
    st.warning("⚠️ Aucune donnée récupérée.")
    st.stop()

# Étape 3 – Charger le GeoJSON en ligne depuis GitHub
url_geojson = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/communes.geojson"
geojson_data = requests.get(url_geojson).json()

# Étape 4 – Ajouter les consommations dans le GeoJSON
for feature in geojson_data["features"]:
    code = feature["properties"]["code"]
    match = df_conso[df_conso["code_commune"] == code]
    if not match.empty:
        feature["properties"]["conso"] = int(match["consommation_mwh"].values[0])
    else:
        feature["properties"]["conso"] = None

# Étape 5 – Affichage de la carte
m = folium.Map(location=[46.8, 2.5], zoom_start=6, tiles="CartoDB positron")

folium.Choropleth(
    geo_data=geojson_data,
    data=df_conso,
    columns=["code_commune", "consommation_mwh"],
    key_on="feature.properties.code",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    nan_fill_color="lightgrey",
    legend_name="Consommation électrique (MWh)"
).add_to(m)

folium.GeoJson(
    geojson_data,
    style_function=lambda feature: {
        "fillOpacity": 0,
        "color": "transparent",
        "weight": 0
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["nom", "conso"],
        aliases=["Commune :", "Consommation (MWh) :"],
        localize=True,
        sticky=True
    )
).add_to(m)

folium_static(m)
