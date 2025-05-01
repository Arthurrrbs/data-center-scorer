import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import folium_static

st.set_page_config(layout="wide")
st.title("🏙️ Scoring Communal via API Enedis – Consommation électrique")

# -------------------------
# Fonction API Enedis avec recherche par nom exact de commune

def get_consommation(commune, annee="2022"):
    url = "https://data.enedis.fr/api/records/1.0/search/"
    params = {
        "dataset": "consommation-electrique-par-secteur-dactivite-commune",
        "refine.annee": annee,
        "refine.nom_commune": commune,
        "rows": 1
    }
    try:
        response = requests.get(url, params=params)
        records = response.json().get("records", [])
        if records:
            return records[0]["fields"].get("consommation_mwh", None)
        return None
    except Exception as e:
        print(f"[Erreur API Enedis pour {commune}] {e}")
        return None

# -------------------------
# Fonction API Geo pour récupérer coordonnées GPS d'une commune

def get_coords(commune_name):
    url = f"https://geo.api.gouv.fr/communes?nom={commune_name}&fields=centre&format=json"
    try:
        r = requests.get(url)
        items = r.json()
        if items:
            return items[0]["centre"]["coordinates"][1], items[0]["centre"]["coordinates"][0]
    except:
        pass
    return None, None

# -------------------------
# Slider de pondération
poids = st.slider("🏠 Pondération de la variable consommation (entre 0 et 1)", 0.0, 1.0, 1.0, step=0.1)

# -------------------------
# Liste de communes testées avec noms correspondant à l'API Enedis
communes_list = [
    "Montpellier", "Nantes", "Strasbourg", "Angers", "Dijon",
    "Grenoble", "Brest", "Le Mans", "Reims", "Tours"
]

data = []

with st.spinner("🚀 Récupération des données Enedis en cours..."):
    for name in communes_list:
        conso = get_consommation(name)
        lat, lon = get_coords(name)
        if conso is not None and lat is not None:
            data.append({
                "Commune": name,
                "Conso_MWh": conso,
                "Lat": lat,
                "Lon": lon
            })

df = pd.DataFrame(data)

if not df.empty:
    # Normalisation
    df["Conso_norm"] = (df["Conso_MWh"].max() - df["Conso_MWh"]) / (df["Conso_MWh"].max() - df["Conso_MWh"].min())
    df["Score"] = poids * df["Conso_norm"]

    # -------------------------
    # Carte Folium
    m = folium.Map(location=[46.6, 2.5], zoom_start=6)

    for _, row in df.iterrows():
        folium.CircleMarker(
            location=[row["Lat"], row["Lon"]],
            radius=8,
            color="blue",
            fill=True,
            fill_opacity=0.6,
            popup=f"{row['Commune']}<br>Score: {row['Score']:.2f}"
        ).add_to(m)

    # Affichage carte
    folium_static(m)

    # -------------------------
    # Top 5 et Flop 5
    st.markdown("---")
    st.subheader("📊 Classement des communes")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🏆 Top 5")
        st.dataframe(df.sort_values("Score", ascending=False)[["Commune", "Score"]].head(5), use_container_width=True)

    with col2:
        st.markdown("### 🍾 Flop 5")
        st.dataframe(df.sort_values("Score")[["Commune", "Score"]].head(5), use_container_width=True)
else:
    st.warning("Aucune commune n'a pu être scorée avec succès.")
