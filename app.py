import streamlit as st
import pandas as pd
import pymongo
import plotly.express as px

# Configuration de la page
st.set_page_config(page_title="Analyse Immo Spark", layout="wide")

st.title("📊 Analyse du Marché Immobilier (OpenData)")
st.markdown("Données traitées avec **PySpark** et stockées sur **MongoDB**.")

# 1. CONNEXION À MONGODB
@st.cache_resource # Pour éviter de se reconnecter à chaque clic
def get_data():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["immo_db"]
    collection = db["tendances_communes"]
    # On récupère tout et on transforme en DataFrame Pandas
    data = list(collection.find())
    return pd.DataFrame(data)

try:
    df = get_data()

    # 2. FILTRES DANS LA BARRE LATÉRALE
    st.sidebar.header("Filtres")
    depts = sorted(df['code_dept'].unique())
    selected_dept = st.sidebar.selectbox("Choisir un département", depts)

    # Filtrage du DataFrame
    df_filtered = df[df['code_dept'] == selected_dept]

    # 3. AFFICHAGE DES CHIFFRES CLÉS
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Prix Médian Global", f"{int(df_filtered['prix_median'].mean())} €/m²")
    with col2:
        st.metric("Nombre de Communes", len(df_filtered))

    # 4. GRAPHIQUE INTERACTIF (Plotly)
    st.subheader(f"Top 15 des communes les plus chères - Dept {selected_dept}")
    top_10 = df_filtered.sort_values("prix_median", ascending=False).head(15)
    
    fig = px.bar(top_10, x="Commune", y="prix_median", 
                 color="prix_median",
                 labels={'prix_median': 'Prix au m² (€)'},
                 template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    # 5. TABLEAU DES DONNÉES
    st.subheader("Détail des données")
    st.dataframe(df_filtered[['code_dept', 'Commune', 'prix_median', 'nb_ventes']], use_container_width=True)

except Exception as e:
    st.error(f"Impossible de se connecter à MongoDB : {e}")
    st.info("Assurez-vous que MongoDB est lancé et que le script Spark a été exécuté.")