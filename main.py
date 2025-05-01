import streamlit as st
import pandas as pd
import folium
import requests
from streamlit_folium import folium_static
import unicodedata

st.title("Scoring Multi-Variable des Départements pour Data Centers")

# --- Bouton de rechargement ---
if st.button("🔄 Recharger la carte"):
    st.rerun()

# --- Charger les données avec le bon séparateur ---
@st.cache_data
def load_data():
    df = pd.read_csv("score_variables_departements_101.csv", sep=",")
    return df

df = load_data()

st.write(f"✅ Nombre de lignes dans le CSV : {len(df)}")

geojson_depts = [feature['properties']['nom'] for feature in geojson_data['features']]
csv_depts = df["Département"].unique().tolist()

missing_in_csv = sorted(set(geojson_depts) - set(csv_depts))
st.warning(f"🛑 Départements présents dans le GeoJSON mais absents du CSV : {missing_in_csv}")

# --- Afficher les colonnes pour vérification ---
st.write("📌 Colonnes détectées :", df.columns.tolist())
st.write("🔍 Aperçu du fichier :", df.head())

# --- Liste des variables à normaliser ---
variables = [
    "PIB_milliards", "Prix_Electricité", "Couverture_Fibre_%",
    "Densite_pop_hab_km2", "Surface_disponible_km2", "Nb_entreprises",
    "Nb_DataCenters_existants", "Taux_urbanisation_%",
    "Acces_Eau_industrielle", "Indice_canicule"
]

# --- Vérification des colonnes présentes ---
missing_vars = [v for v in variables if v not in df.columns]
if missing_vars:
    st.error(f"🚨 Colonnes manquantes dans le CSV : {missing_vars}")
    st.stop()

df = df.dropna(subset=["Département"])  # supprime les lignes vides
df = df.drop_duplicates(subset=["Département"])  # garde un seul département par nom


# --- Normalisation des variables ---
for var in variables:
    if var in ["Prix_Electricité", "Indice_canicule"]:  # Moins = mieux
        df[f"{var}_norm"] = (df[var].max() - df[var]) / (df[var].max() - df[var].min())
    else:  # Plus = mieux
        df[f"{var}_norm"] = (df[var] - df[var].min()) / (df[var].max() - df[var].min())

# --- Calcul du score global (moyenne des scores normalisés) ---
df["Score_Global"] = df[[f"{v}_norm" for v in variables]].mean(axis=1)

st.subheader("📊 Scores multi-variables par département")
st.dataframe(df[["Département", "Score_Global"] + [f"{v}_norm" for v in variables]])

# --- Charger GeoJSON des départements ---
geojson_url = "https://france-geojson.gregoiredavid.fr/repo/departements.geojson"
geojson_data = requests.get(geojson_url).json()

# --- Debug : affichage des noms pour comparaison ---
geojson_depts = [feature['properties']['nom'] for feature in geojson_data['features']]
csv_depts = df["Département"].unique().tolist()
st.write("🗺️ Noms dans GeoJSON :", geojson_depts)
st.write("📊 Noms dans CSV (après nettoyage) :", csv_depts)

# --- Carte Folium ---
m = folium.Map(location=[46.5, 2.5], zoom_start=6)

# --- Choropleth avec correspondance sur les noms nettoyés ---
folium.Choropleth(
    geo_data=geojson_data,
    name="choropleth",
    data=df,
    columns=["Département", "Score_Global"],
    key_on="feature.properties.nom",
    fill_color="YlGnBu",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Score d'Attractivité Global"
).add_to(m)

# --- Afficher la carte dans Streamlit ---
folium_static(m)
