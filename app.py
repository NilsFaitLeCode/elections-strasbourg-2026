import streamlit as st
import pandas as pd
import requests
import time
import plotly.express as px

# Configuration de la page
st.set_page_config(page_title="Suivi Élections Strasbourg 2026", layout="wide")

st.title("🗳️ Évolution du 2nd Tour - Municipales Strasbourg 2026")
st.markdown("Ce graphique suit l'évolution des voix cumulées au fur et à mesure du dépouillement.")

# --- CONFIGURATION ---
URL_API = "https://data.strasbourg.eu/api/explore/v2.1/catalog/datasets/resultats-du-second-tour-des-elections-municipales-2026-version-detaillee/records"
# On augmente la limite pour être sûr de récupérer tous les bureaux à chaque fois
# (149 bureaux * nombre de listes = environ 450-600 lignes à récupérer)
PARAMS = {"limit": 100} 
REFRESH_INTERVAL = 30  # Secondes entre chaque mise à jour

# --- INITIALISATION DE L'HISTORIQUE ---
if 'history' not in st.session_state:
    # On crée un DataFrame vide pour stocker les résultats cumulés au fil du temps
    st.session_state.history = pd.DataFrame(columns=['Update', 'Liste', 'Voix'])
    st.session_state.update_index = 0

# --- FONCTION DE RÉCUPÉRATION ---
def fetch_current_data():
    try:
        response = requests.get(URL_API, params=PARAMS)
        response.raise_for_status()
        data = response.json()
        
        if 'results' in data:
            df_current = pd.DataFrame(data['results'])
            
            # 1. On groupe par liste pour avoir le total actuel des voix dépouillées
            summary = df_current.groupby('lib_liste_affichee')['nb_voix'].sum().reset_index()
            summary.columns = ['Liste', 'Voix']
            
            # 2. On ajoute l'index de la mise à jour
            summary['Update'] = st.session_state.update_index
            
            return summary
        return None
    except Exception as e:
        st.error(f"Erreur lors de l'appel API : {e}")
        return None

# --- LOGIQUE DE MISE À JOUR ---
placeholder = st.empty()

# Appel de l'API
current_summary = fetch_current_data()

if current_summary is not None:
    # Vérification pour ne pas ajouter de doublons si les données n'ont pas changé
    # (Optionnel : on peut comparer avec la dernière entrée de l'historique)
    
    # Ajout à l'historique dans session_state
    st.session_state.history = pd.concat([st.session_state.history, current_summary], ignore_index=True)
    st.session_state.update_index += 1

# --- AFFICHAGE ---
with placeholder.container():
    if not st.session_state.history.empty:
        # Création du graphique avec Plotly
        fig = px.line(
            st.session_state.history, 
            x="Update", 
            y="Voix", 
            color="Liste",
            markers=True,
            title="Cumul des voix par mise à jour de l'API",
            labels={"Update": "Nombre de rafraîchissements", "Voix": "Total des suffrages"},
            template="plotly_white"
        )
        
        # Personnalisation des axes
        fig.update_layout(xaxis_type='linear')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Affichage des dernières stats
        cols = st.columns(len(current_summary))
        for i, row in current_summary.iterrows():
            cols[i].metric(label=row['Liste'], value=f"{int(row['Voix'])} v.")
            
    else:
        st.info("En attente des premières données...")