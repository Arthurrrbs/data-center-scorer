import streamlit as st
import pandas as pd
import folium
import requests
from streamlit_folium import folium_static

st.title("Scoring Multi-Variable des Départements pour Data Centers")

# --- Bouton de rechargement ---
if st.button("🔄 Recharger la carte"):
    st.rerun()

# --- Charger les données ---
@st.cache_data
def load_data():
    df = pd.read_csv("score_variables_departements.csv")
    return df

df = load_data()

st.write("🧪 Première ligne du fichier :", df.iloc[0])


# --- Vérification des noms de colonnes réels ---
st.write("✅ Colonnes détectées :", df.columns.tolist())

# --- Liste officielle attendue ---
variables = [
    "PIB_milliards", "Prix_Electricité", "Couverture_Fibre_%",
    "Densite_pop_hab_km2", "Surface_disponible_km2", "Nb_entreprises",
    "Nb_DataCenters_existants", "Taux_urbanisation_%",
    "Acces_Eau_industrielle", "Indice_canicule"
]

# --- Identifier les variables manquantes ---
missing_vars = [v for v in variables if v not in df.columns]
if missing_vars:
    st.error(f"🚨 Les colonnes suivantes sont absentes du fichier CSV : {missing_vars}")
    st.stop()


# --- Debug temporaire ---
st.write("📌 Colonnes détectées :", df.columns.tolist())
st.write("🔍 Aperçu du fichier :", df.head())

# --- Liste des variables à normaliser ---
variables = [
    "PIB_milliards", "Prix_Electricité", "Couverture_Fibre_%",
    "Densite_pop_hab_km2", "Surface_disponible_km2", "Nb_entreprises",
    "Nb_DataCenters_existants", "Taux_urbanisation_%",
    "Acces_Eau_industrielle", "Indice_canicule"
]

# --- Normalisation ---
for var in variables:
    if var in ["Prix_Electricité", "Indice_canicule"]:  # Moins = mieux
        df[f"{var}_norm"] = (df[var].max() - df[var]) / (df[var].max() - df[var].min())
    else:  # Plus = mieux
        df[f"{var}_norm"] = (df[var] - df[var].min()) / (df[var].max() - df[var].min())

# --- Calcul du score global (moyenne des normalisées) ---
df["Score_Global"] = df[[f"{v}_norm" for v in variables]].mean(axis=1)

st.subheader("Scores multi-variables par département")
st.dataframe(df[["Département", "Score_Global"] + [f"{v}_norm" for v in variables]])

# --- Charger GeoJSON des départements ---
geojson_url = "https://france-geojson.gregoiredavid.fr/repo/departements.geojson"
geojson_data = requests.get(geojson_url).json()

# --- Créer carte Folium ---
m = folium.Map(location=[46.5, 2.5], zoom_start=6)

# --- Ajouter le choropleth ---
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

# --- Affichage dans Streamlit ---
folium_static(m)
