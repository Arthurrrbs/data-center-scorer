import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import folium_static

st.set_page_config(layout="wide")
st.title("🏙️ Scoring Communal via API Enedis – Consommation électrique")

# -------------------------
# Fonction API Geo pour communes
def get_communes_france(limit=20):
    url = "https://geo.api.gouv.fr/communes"
    params = {
        "fields": "nom,population,centre",
        "format": "json",
        "geometry": "centre"
    }
    response = requests.get(url, params=params)
    data = response.json()
    # Trier par population descendante et garder les n plus grandes
    data = sorted([c for c in data if "population" in c and c["population"] is not None], key=lambda x: -x["population"])
    return data[:limit]

# -------------------------
# Fonction API Enedis
def get_consommation(commune, annee="2022"):
    url = "https://data.enedis.fr/api/records/1.0/search/"
    params = {
        "dataset": "consommation-electrique-par-secteur-dactivite-commune",
        "refine.nom_commune": commune,
        "refine.annee": annee,
        "refine.secteur_d_activite": "Résidentiel",
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
# Slider de pondération
poids = st.slider("🏠 Pondération de la variable consommation (entre 0 et 1)", 0.0, 1.0, 1.0, step=0.1)

# -------------------------
# Chargement des 20 communes les plus peuplées
communes_data = get_communes_france(20)
data = []

with st.spinner("🚀 Récupération des données Enedis en cours..."):
    for c in communes_data:
        conso = get_consommation(c["nom"])
        if conso is not None:
            data.append({
                "Commune": c["nom"],
                "Conso_MWh": conso,
                "Lat": c["centre"]["coordinates"][1],
                "Lon": c["centre"]["coordinates"][0]
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
