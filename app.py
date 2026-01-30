import streamlit as st
import pandas as pd
import pymongo
import plotly.express as px

# Configuration de la page
st.set_page_config(page_title="Analyse Évolution Immo", layout="wide")

st.title("📈 Évolution du Marché Immobilier (2020-2024)")
st.markdown("Comparaison des prix médians au m² calculés via **PySpark**.")

# 1. CONNEXION À MONGODB
MONGO_URI = "mongodb+srv://test123:testpass123@cluster-immo.vyrieko.mongodb.net/"

@st.cache_resource
def get_data():
    client = pymongo.MongoClient(MONGO_URI)
    db = client["immo_db"]
    collection = db["tendances_communes"]
    data = list(collection.find({}, {'_id': 0})) # On exclut l'ID Mongo pour Pandas
    return pd.DataFrame(data)

try:
    df = get_data()

    # Barre latérale pour le choix du département
    st.sidebar.header("Paramètres")
    depts = sorted(df['code_dept'].unique())
    selected_dept = st.sidebar.selectbox("Choisir un département", depts)

    # Filtrage par département
    df_dept = df[df['code_dept'] == selected_dept]

    # --- SECTION 1 : TOP 10 DES PLUS FORTES HAUSSES (2020 vs 2024) ---
    st.subheader(f"🚀 Top 10 des plus fortes évolutions (2020-2024) - Dept {selected_dept}")

    # On prépare les données pour le calcul
    # On crée un pivot pour avoir une colonne par année
    df_pivot = df_dept.pivot_table(index='Commune', columns='annee', values='prix_median')

    # Vérification de la présence des deux années charnières
    if 2020 in df_pivot.columns and 2024 in df_pivot.columns:
        # Calcul du % d'évolution
        df_pivot['evolution'] = ((df_pivot[2024] - df_pivot[2020]) / df_pivot[2020]) * 100
        
        # Nettoyage : on garde les communes présentes les deux années et on trie
        df_evol = df_pivot.dropna(subset=['evolution']).sort_values('evolution', ascending=False).head(10)
        
        if not df_evol.empty:
            fig_evol = px.bar(
                df_evol.reset_index(), 
                x='Commune', 
                y='evolution',
                color='evolution',
                labels={'evolution': 'Hausse (%)'},
                color_continuous_scale='Reds',
                template="plotly_white"
            )
            st.plotly_chart(fig_evol, use_container_width=True)
        else:
            st.warning("Pas assez de données comparatives pour ce département.")
    else:
        st.info("Les données de 2020 ou 2024 sont manquantes pour ce département dans la base.")

    st.divider()

    # --- SECTION 2 : ANALYSE DÉTAILLÉE PAR VILLE ---
    st.subheader("🔍 Historique détaillé d'une commune")
    
    # Liste des villes du département
    villes = sorted(df_dept['Commune'].unique())
    selected_ville = st.selectbox("Sélectionnez une ville pour voir sa tendance", villes)

    # Filtrage pour la ville choisie
    df_ville = df_dept[df_dept['Commune'] == selected_ville].sort_values('annee')

    col_chart, col_data = st.columns([2, 1])

    with col_chart:
        if len(df_ville) > 1:
            fig_line = px.line(
                df_ville, 
                x='annee', 
                y='prix_median', 
                markers=True,
                title=f"Tendance du prix au m² à {selected_ville}",
                labels={'prix_median': 'Prix (€/m²)', 'annee': 'Année'},
                template="plotly_white"
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("Données insuffisantes pour tracer une courbe historique (besoin d'au moins 2 ans).")

    with col_data:
        st.write("Données brutes")
        st.dataframe(df_ville[['annee', 'prix_median', 'nb_ventes']].set_index('annee'), use_container_width=True)

except Exception as e:
    st.error(f"Erreur : {e}")
    st.info("Assurez-vous que MongoDB tourne et que projet.py a bien inséré les données avec la colonne 'annee'.")