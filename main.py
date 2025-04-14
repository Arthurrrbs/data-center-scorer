import streamlit as st
import pandas as pd
import folium
import requests
from streamlit_folium import folium_static

# --- 1. Titre principal ---
st.title("Carte de Scoring des Communes pour Data Centers en France")

# --- 2. Bouton pour Recharger la Carte ---
if st.button('🔄 Recharger la Carte'):
    st.experimental_rerun()

# --- 3. Charger les données Communes ---
@st.cache_data
def load_data():
    df = pd.read_csv('communes-france-2025.csv', sep=',')
    return df

df = load_data()

st.write("Aperçu des données chargées :", df.head())

# --- 4. Nettoyage des colonnes ---
df.rename(columns={'Densité (hab/km²)': 'Densite', 'Code INSEE': 'Code_INSEE'}, inplace=True)

# --- 5. Normaliser la Densité pour créer un Score ---
df['Score'] = (df['Densite'] - df['Densite'].min()) / (df['Densite'].max() - df['Densite'].min())

st.write("Aperçu des Scores :", df[['Nom', 'Code_INSEE', 'Densite', 'Score']].head())

# --- 6. Charger la carte GeoJSON des Communes ---
geojson_url = 'https://france-geojson.gregoiredavid.fr/repo/communes.geojson'
geojson_data = requests.get(geojson_url).json()

# --- 7. Créer la carte Folium ---
m = folium.Map(location=[46.5, 2.5], zoom_start=6)

# --- 8. Ajouter Choropleth ---
folium.Choropleth(
    geo_data=geojson_data,
    name='choropleth',
    data=df,
    columns=['Code_INSEE', 'Score'],
    key_on='feature.properties.code',
    fill_color='YlGnBu',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Score d\'Attractivité par Commune'
).add_to(m)

# --- 9. Afficher la carte dans Streamlit ---
folium_static(m)
