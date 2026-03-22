import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

# Configuration de la page
st.set_page_config(page_title="Strasbourg 2026 - Résultats Live", layout="wide")

st.title("🗳️ Résultats du 2nd Tour en Direct - Strasbourg")
st.markdown("Source : *Open Data Eurométropole de Strasbourg*")

# L'URL que vous avez trouvée
URL_API = "https://data.strasbourg.eu/api/explore/v2.1/catalog/datasets/resultats-du-second-tour-des-elections-municipales-2026-version-detaillee/records?limit=100"

# Zone de rafraîchissement
placeholder = st.empty()

while True:
    try:
        # Récupération des données
        response = requests.get(URL_API)
        data = response.json()
        
        if 'results' in data and len(data['results']) > 0:
            df = pd.DataFrame(data['results'])
            
            # 1. On regroupe par candidat pour avoir le total des voix
            # Note : On vérifie les noms de colonnes typiques (nom_liste ou candidat)
            col_candidat = 'nom_liste' if 'nom_liste' in df.columns else 'candidat'
            col_voix = 'nb_voix' if 'nb_voix' in df.columns else 'voix'
            
            summary = df.groupby(col_candidat)[col_voix].sum().reset_index()
            summary = summary.sort_values(by=col_voix, ascending=False)
            
            # 2. Calcul du pourcentage
            total_voix = summary[col_voix].sum()
            summary['%'] = (summary[col_voix] / total_voix * 100).round(2)

            with placeholder.container():
                # Affichage des métriques principales (Top 3)
                cols = st.columns(len(summary))
                for i, row in enumerate(summary.itertuples()):
                    if i < 4: # On limite l'affichage des tuiles aux 4 premiers
                        cols[i].metric(row[1], f"{row[2]} voix", f"{row[3]} %")

                # Graphique Barres
                fig = px.bar(summary, x=col_candidat, y=col_voix, 
                             text='%', color=col_candidat,
                             title=f"Répartition des voix ({time.strftime('%H:%M:%S')})")
                
                fig.update_traces(texttemplate='%{text}%', textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
                
                # Tableau récapitulatif
                st.write("### Détail des scores")
                st.dataframe(summary, use_container_width=True)
                
                st.info(f"Dernière mise à jour automatique à {time.strftime('%H:%M:%S')}. "
                        f"Nombre de lignes de données traitées : {len(df)}")
        else:
            with placeholder.container():
                st.warning("🔄 Connexion établie. En attente de l'injection des premières données par la ville...")
                st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJpbmZqZ3RreXF6YnR6eW16eW16eW16eW16eW16eW16eW16&ep=v1_gifs_search&rid=giphy.gif&ct=g", width=200)

    except Exception as e:
        st.error(f"Une erreur est survenue : {e}")
    
    # Attend 30 secondes avant de recommencer
    time.sleep(30)