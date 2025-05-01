import streamlit as st
import pandas as pd
import folium
import requests
from streamlit_folium import folium_static

# --- Titre principal ---
st.title("Scoring des Départements pour Data Centers en France")

# --- Bouton pour recharger ---
if st.button('🔄 Recharger la Carte'):
    st.rerun()

# --- Charger les données CSV ---
@st.cache_data
def load_data():
    pib = pd.read_csv('pib_departements.csv')
    elec = pd.read_csv('prix_electricite_departements.csv')
    df = pd.merge(pib, elec, on="Département")
    return df

df = load_data()

st.write("Données fusionnées :", df.head())

# --- Normalisation ---
df["PIB_norm"] = (df["PIB_milliards"] - df["PIB_milliards"].min()) / (df["PIB_milliards"].max() - df["PIB_milliards"].min())
df["Electricite_norm"] = (df["Prix_Electricité"].max() - df["Prix_Electricité"]) / (df["Prix_Electricité"].max() - df["Prix_Electricité"].min())

# --- Score composite (50/50) ---
df["Score"] = 0.5 * df["PIB_norm"] + 0.5 * df["Electricite_norm"]

st.subheader("Scores par Département")
st.dataframe(df[["Département", "Score"]])

# --- Carte GeoJSON des départements ---
geojson_url = 'https://france-geojson.gregoiredavid.fr/repo/departements.geojson'
geojson_data = requests.get(geojson_url).json()

# --- Créer carte Folium ---
m = folium.Map(location=[46.5, 2.5], zoom_start=6)

# --- Ajouter Choropleth ---
folium.Choropleth(
    geo_data=geojson_data,
    name='choropleth',
    data=df,
    columns=['Département', 'Score'],
    key_on='feature.properties.nom',
    fill_color='YlGnBu',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Score d\'Attractivité'
).add_to(m)

# --- Afficher la carte ---
folium_static(m)
