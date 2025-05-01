import streamlit as st
import pandas as pd
import folium
import requests
from streamlit_folium import folium_static

st.set_page_config(layout="wide")
st.title("📍 Scoring Multi-Variable des Départements pour Data Centers")

# --- Recharger ---
if st.button("🔄 Recharger la carte"):
    st.rerun()

# --- Charger CSV ---
@st.cache_data
def load_data():
    df = pd.read_csv("score_variables_departements_101.csv", sep=",")
    df = df.dropna(subset=["Département"])
    df = df[~df["Département"].str.strip().eq("")]
    df = df.drop_duplicates(subset=["Département"])
    df["Département"] = df["Département"].str.strip()
    return df

df = load_data()

# --- Charger GeoJSON ---
geojson_url = "https://france-geojson.gregoiredavid.fr/repo/departements.geojson"
geojson_data = requests.get(geojson_url).json()

# --- Vérif noms départements ---
geojson_depts = [f['properties']['nom'].strip() for f in geojson_data['features']]
csv_depts = df["Département"].unique().tolist()
missing = sorted(set(geojson_depts) - set(csv_depts))
if missing:
    st.warning(f"❌ Départements présents dans le GeoJSON mais absents du CSV : {missing}")

# --- Variables utilisées ---
variables = [
    "PIB_milliards", "Prix_Electricité", "Couverture_Fibre_%",
    "Densite_pop_hab_km2", "Surface_disponible_km2", "Nb_entreprises",
    "Nb_DataCenters_existants", "Taux_urbanisation_%",
    "Acces_Eau_industrielle", "Indice_canicule"
]

# --- Vérifier colonnes ---
missing_cols = [v for v in variables if v not in df.columns]
if missing_cols:
    st.error(f"🚨 Colonnes manquantes : {missing_cols}")
    st.stop()

# --- Sliders de pondération ---
st.sidebar.title("⚖️ Pondération des variables")
weights = {}
for var in variables:
    weights[var] = st.sidebar.slider(var, 0, 100, 10)

total_weight = sum(weights.values())
if total_weight == 0:
    st.error("⚠️ La somme des pondérations est nulle. Augmente au moins une variable.")
    st.stop()

# --- Normalisation ---
for var in variables:
    if var in ["Prix_Electricité", "Indice_canicule"]:  # Moins = mieux
        df[f"{var}_norm"] = (df[var].max() - df[var]) / (df[var].max() - df[var].min())
    else:
        df[f"{var}_norm"] = (df[var] - df[var].min()) / (df[var].max() - df[var].min())

# --- Score pondéré ---
df["Score_Global"] = sum(
    (weights[v] / total_weight) * df[f"{v}_norm"] for v in variables
)

# --- Carte ---
m = folium.Map(location=[46.5, 2.5], zoom_start=6)

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

# --- Ajouter score dans GeoJSON
for feature in geojson_data['features']:
    dept_name = feature["properties"]["nom"].strip()
    row = df[df["Département"] == dept_name]
    if not row.empty:
        feature["properties"]["Score_Global"] = round(row.iloc[0]["Score_Global"], 2)
    else:
        feature["properties"]["Score_Global"] = "N/A"

# --- Tooltip
folium.GeoJson(
    geojson_data,
    style_function=lambda feature: {
        'fillColor': 'transparent',
        'color': 'transparent',
        'weight': 0
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["nom", "Score_Global"],
        aliases=["Département :", "Score :"],
        sticky=True,
        labels=True
    )
).add_to(m)

# --- Afficher carte
folium_static(m)
