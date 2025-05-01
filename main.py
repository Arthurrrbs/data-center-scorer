import streamlit as st
import pandas as pd
import folium
import requests
from streamlit_folium import folium_static

st.set_page_config(layout="wide")
st.title("Scoring des départements pour l'implantation de Data Centers")

# --- État initial : réinitialisation sliders ---
if "reset_weights" not in st.session_state:
    st.session_state.reset_weights = False

# --- Bouton de rechargement ---
if st.button("🔄 Recharger la carte"):
    st.rerun()

# --- Chargement CSV ---
@st.cache_data
def load_data():
    df = pd.read_csv("score_variables_departements_101.csv", sep=",")
    df = df.dropna(subset=["Département"])
    df = df[~df["Département"].str.strip().eq("")]
    df = df.drop_duplicates(subset=["Département"])
    df["Département"] = df["Département"].str.strip()
    return df

df = load_data()

# --- Chargement GeoJSON ---
geojson_url = "https://france-geojson.gregoiredavid.fr/repo/departements.geojson"
geojson_data = requests.get(geojson_url).json()

# --- Vérification noms GeoJSON vs CSV ---
geojson_depts = [f['properties']['nom'].strip() for f in geojson_data['features']]
csv_depts = df["Département"].unique().tolist()
missing = sorted(set(geojson_depts) - set(csv_depts))
if missing:
    st.warning(f"❌ Départements présents dans le GeoJSON mais absents du CSV : {missing}")

# --- Variables clés ---
variables = [
    "PIB_milliards", "Prix_Electricité", "Couverture_Fibre_%",
    "Densite_pop_hab_km2", "Surface_disponible_km2", "Nb_entreprises",
    "Nb_DataCenters_existants", "Taux_urbanisation_%",
    "Acces_Eau_industrielle", "Indice_canicule"
]

# --- Vérification colonnes présentes ---
missing_cols = [v for v in variables if v not in df.columns]
if missing_cols:
    st.error(f"🚨 Colonnes manquantes : {missing_cols}")
    st.stop()

# --- Sidebar : sliders de pondération + bouton reset ---
st.sidebar.title("Pondération des variables")

# Bouton reset
if st.sidebar.button("🔁 Réinitialiser les pondérations"):
    st.session_state.reset_weights = True
else:
    st.session_state.reset_weights = False

# Création sliders
weights = {}
for var in variables:
    default = 10 if st.session_state.reset_weights else st.session_state.get(f"weight_{var}", 10)
    weights[var] = st.sidebar.slider(var, 0, 100, default, key=f"weight_{var}")

# Vérifier pondération totale
total_weight = sum(weights.values())
if total_weight == 0:
    st.error("⚠️ La somme des pondérations est nulle. Merci d’augmenter au moins une variable.")
    st.stop()

# --- Normalisation des variables ---
for var in variables:
    if var in ["Prix_Electricité", "Indice_canicule"]:  # Moins = mieux
        df[f"{var}_norm"] = (df[var].max() - df[var]) / (df[var].max() - df[var].min())
    else:  # Plus = mieux
        df[f"{var}_norm"] = (df[var] - df[var].min()) / (df[var].max() - df[var].min())

# --- Score pondéré final ---
df["Score_Global"] = sum(
    (weights[v] / total_weight) * df[f"{v}_norm"] for v in variables
)

# --- Carte Folium ---
m = folium.Map(
    location=[46.5, 2.5],
    zoom_start=6,
    tiles="https://{s}.tile.jawg.io/jawg-streets/{z}/{x}/{y}.png?access-token=a2M0eqrxFjzsE65ulr9u79m0wK99KM0SNI7qtzuJD4rUV55RwBF35BYbcfWE98xo",
    attr='Jawg Maps'
)

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

# --- Ajouter les scores dans le GeoJSON pour le tooltip
for feature in geojson_data['features']:
    dept_name = feature["properties"]["nom"].strip()
    row = df[df["Département"] == dept_name]
    if not row.empty:
        feature["properties"]["Score_Global"] = round(row.iloc[0]["Score_Global"], 2)
    else:
        feature["properties"]["Score_Global"] = "N/A"

# --- Tooltip interactif
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

# --- Affichage final dans Streamlit
folium_static(m)
# --- Récupération du top 5 et flop 5
top5 = df[["Département", "Score_Global"]].sort_values(by="Score_Global", ascending=False).head(5).reset_index(drop=True)
worst5 = df[["Département", "Score_Global"]].sort_values(by="Score_Global", ascending=True).head(5).reset_index(drop=True)

# --- Affichage en colonnes côte à côte
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏆 Top 5 des départements les mieux notés")
    for i, row in top5.iterrows():
        st.markdown(
            f"""
            <div style='margin-bottom: 8px; font-size:16px'>
                <span style="font-weight:600; color:#2E8B57">{i+1}.</span>
                <span style="font-weight:500;">{row['Département']}</span>
                — <span style="color: #555;">{row['Score_Global']:.2f}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

with col2:
    st.markdown("### ⚠️ Top 5 des départements les moins bien notés")
    for i, row in worst5.iterrows():
        st.markdown(
            f"""
            <div style='margin-bottom: 8px; font-size:16px'>
                <span style="font-weight:600; color:#B22222">{i+1}.</span>
                <span style="font-weight:500;">{row['Département']}</span>
                — <span style="color: #555;">{row['Score_Global']:.2f}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
