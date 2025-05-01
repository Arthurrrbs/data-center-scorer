import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")
st.title("🔌 Test API Enedis – 2 communes")

# Liste réduite à 2 communes
communes = [
    "Montpellier",
    "Dijon"
]

annee = "2022"
data = []

with st.spinner("🔍 Récupération des données Enedis pour 2 communes..."):
    for nom in communes:
        url = "https://data.enedis.fr/api/records/1.0/search/"
        params = {
            "dataset": "consommation-electrique-par-secteur-dactivite-commune",
            "q": nom,
            "refine.annee": annee,
            "rows": 10
        }
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                records = response.json().get("records", [])
                for rec in records:
                    fields = rec.get("fields", {})
                    if fields.get("nom_commune", "").lower() == nom.lower():
                        conso = fields.get("consommation_mwh", None)
                        secteur = fields.get("secteur_d_activite", "")
                        if conso:
                            data.append({"Commune": nom, "Consommation_MWh": conso, "Secteur": secteur})
                        break
            else:
                st.error(f"❌ Erreur API pour {nom}")
        except Exception as e:
            st.error(f"❌ Exception pour {nom} : {e}")

if data:
    df = pd.DataFrame(data)
    st.success("✅ Données récupérées pour les communes suivantes :")
    st.dataframe(df)
else:
    st.warning("⚠️ Aucune donnée récupérée pour les communes testées.")
