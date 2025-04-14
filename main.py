import streamlit as st
import pandas as pd
import folium
import requests
from streamlit_folium import folium_static

# --- 1. Titre ---
st.title("Carte des Départements - Scoring PIB et Prix Électricité")

# --- 2. Bouton pour Recharger la Carte ---
if st.button('🔄 Recharger la Carte'):
    st.experimental_rerun()

# --- 3. Charger les données ---
@st.cache_data
def load_data():
    pib = pd.read_csv('pib_departements.csv')
    elec = pd.read_csv('prix_electricite_departements.csv')
    df = pd.merge(pib, elec, on="Département")
    return df

df = load_data()

st.write("Données fusionnées :", df.head())

# --- 4. Normaliser PIB et Prix Electricité ---
df["PIB_norm"] = (df["PIB_milliards"] - df["PIB_milliards"].min()) / (df["PIB_milliards"].max() - df["PIB_milliards"].min())
df["Prix_Electricité_norm"] = (df["Prix_Electricité"].max() - df["Prix_Electricité"]) / (df["Prix_Electricité"].max() - df["Prix_Electricité"].min())

# --- 5. Calculer Score composite (50% PIB + 50% Prix Electricité) ---
df["Score"] = 0.5 * df["PIB_norm"] + 0.5 * df["Prix_Electricité_norm"]

st.write("Scores calculés :", df[["Département", "Score"]])

# --- 6. Charger la carte GeoJSON des départements français ---
geojson_url = 'https://france-geojson.gregoiredavid.fr/repo/departements.geojson'
geojson_data = requests.get(geojson_url).json()

# --- 7. Créer la carte Folium ---
m = folium.Map(location=[46.5, 2.5], zoom_start=6)

# --- 8. Ajouter le Choropleth ---
folium.Choropleth(
    geo_data=geojson_data,
    name='choropleth',
    data=df,
    columns=['Département', 'Score'],
    key_on='feature.properties.nom',
    fill_color='YlGnBu',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Score d\'Attractivité (PIB + Electricité)'
).add_to(m)

# --- 9. Afficher la carte dans Streamlit ---
folium_static(m)

