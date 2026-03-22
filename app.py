import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

# Configuration de la page
st.set_page_config(page_title="Live Strasbourg 2026", layout="wide")
st.title("🗳️ Résultats en direct - Strasbourg (2nd tour)")

# URL de l'API Open Data Strasbourg (Dataset 2026)
API_URL = "https://data.strasbourg.eu/api/records/1.0/search/"
params = {
    "dataset": "elections-municipales-2026-2e-tour",
    "q": "",
    "rows": 100 # Pour récupérer tous les bureaux ou le cumul
}

placeholder = st.empty()

while True:
    try:
        # Récupération des données
        response = requests.get(API_URL, params=params)
        data = response.json()
        
        # Extraction et formatage (à adapter selon les champs précis de l'API ce soir)
        records = [r['fields'] for r in data['records']]
        df = pd.DataFrame(records)
        
        # Exemple de traitement : Somme des voix par candidat
        # Les colonnes types sont souvent 'nom_candidat' et 'nb_voix'
        results = df.groupby('liste')['voix'].sum().reset_index()
        results = results.sort_values(by='voix', ascending=False)

        with placeholder.container():
            # Affichage du graphique
            fig = px.bar(results, x='liste', y='voix', 
                         color='liste', title="Répartition des voix en temps réel")
            st.plotly_chart(fig, use_container_width=True)
            
            # Affichage de l'heure de mise à jour
            st.write(f"Dernière mise à jour : {time.strftime('%H:%M:%S')}")
            
    except Exception as e:
        st.error(f"En attente des premières données... ({e})")
    
    # Pause de 60 secondes avant le prochain update
    time.sleep(60)