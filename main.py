import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import folium_static

st.set_page_config(layout="wide")
st.title("🔌 Carte – Consommation électrique des 100 plus grandes communes françaises")

@st.cache_data
def get_top_communes(n=100):
    url = "https://geo.api.gouv.fr/communes?fields=nom,code,centre,population&format=json&geometry=centre"
    response = requests.get(url)
    communes_data = {}
    if response.status_code == 200:
        all_communes = response.json()
        sorted_communes = sorted(
            [c for c in all_communes if "centre" in c and c.get("population")],
            key=lambda x: x["population"], reverse=True
        )[:n]
        for c in sorted_communes:
            name = c["nom"]
            code = c["code"]
            lon, lat = c["centre"]["coordinates"]
            communes_data[name] = {"code": code, "lat": lat, "lon": lon}
    return communes_data

def get_commune_data(code_insee, nom_commune, annee="2023"):
    url = "https://data.enedis.fr/api/records/1.0/search/"
    params = {
        "dataset": "consommation-electrique-par-secteur-dactivite-commune",
        "q": nom_commune,
        "rows": 100
    }
    try:
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
    except:
        return None
    return None

# Charger les communes dynamiquement
communes = get_top_communes(100)

# Agréger les données Enedis
data = []
with st.spinner("🔍 Récupération des données Enedis..."):
    for name, info in communes.items():
        total = get_commune_data(info["code"], name)
        if total:
            data.append({
                "Commune": name,
                "Code_INSEE": info["code"],
                "Latitude": info["lat"],
                "Longitude": info["lon"],
                "Consommation_Totale_MWh": total
            })

if data:
    df = pd.DataFrame(data)
    df_sorted = df.sort_values(by="Consommation_Totale_MWh", ascending=False)

    st.success("✅ Données récupérées pour les communes suivantes :")
    st.dataframe(df_sorted[["Commune", "Consommation_Totale_MWh"]])

    # Carte avec fond type Jawg Streets
    m = folium.Map(location=[46.5, 2.5], zoom_start=6, tiles="CartoDB positron")

    for _, row in df_sorted.iterrows():
        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=max(row["Consommation_Totale_MWh"] ** 0.5 / 10, 3),
            color="#0078FF",
            fill=True,
            fill_opacity=0.6,
            popup=folium.Popup(f"<b>{row['Commune']}</b><br>{int(row['Consommation_Totale_MWh'])} MWh", max_width=200)
        ).add_to(m)

    folium_static(m)

else:
    st.warning("⚠️ Aucune donnée récupérée via Enedis.")
