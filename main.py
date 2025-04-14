import streamlit as st
import pandas as pd
import folium
import requests
from streamlit_folium import folium_static

# --- 1. Titre principal ---
st.title("Carte de Scoring des Communes pour Data Centers en France")

# --- 2. Bouton pour Recharger la Carte ---
if st.button('🔄 Recharger la Carte'):
    st.rerun()

# --- 3. Charger les données Communes ---
@st.cache_data
def load_data():
    df = pd.read_csv('communes-france-2025.csv', sep=',')
    return df

df = load_data()

st.write("Colonnes disponibles :", df.columns.tolist())

# --- 4. Calculer un Score basé sur la densité ---
df['Score'] = (df['densite'] - df['densite'].min()) / (df['densite'].max() - df['densite'].min())

st.write("Aperçu des Scores :", df[['nom_standard', 'code_insee', 'densite', 'Score']].head())

# --- 5. Charger la carte GeoJSON des Communes ---
geojson_url = 'https://france-geojson.gregoiredavid.fr/repo/communes.geojson'
geojson_data = requests.get(geojson_url).json()

# --- 6. Créer la carte Folium ---
m = folium.Map(location=[46.5, 2.5], zoom_start=6)

# --- 7. Ajouter le Choropleth ---
folium.Choropleth(
    geo_data=geojson_data,
    name='choropleth',
    data=df,
    columns=['code_insee', 'Score'],  # Attention ici aussi !
    key_on='feature.properties.code',
    fill_color='YlGnBu',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Score d\'Attractivité par Commune'
).add_to(m)

# --- 8. Afficher la carte dans Streamlit ---
folium_static(m)
