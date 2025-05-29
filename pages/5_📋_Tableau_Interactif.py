import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tableau Interactif", layout="wide")
st.title("📋 Tableau Interactif des Données Microbio")

# Charger les données
df = pd.read_csv("Export_StaphAureus_COMPLET.csv", sep=None, engine='python')  # gère le séparateur automatiquement
df.columns = df.columns.str.strip()

# Affiche les dimensions
st.markdown(f"**{df.shape[0]:,} lignes**, **{df.shape[1]} colonnes**")

# Sélection de colonnes à afficher
colonnes_affichées = st.multiselect("🧩 Colonnes à afficher :", options=df.columns.tolist(), default=df.columns.tolist())

# Zone de filtres dynamiques
with st.expander("🔍 Filtres avancés :"):
    filtres = {}
    for col in colonnes_affichées:
        if df[col].dtype == 'object' or df[col].nunique() < 100:
            valeurs_uniques = sorted(df[col].dropna().unique())
            selected = st.multiselect(f"Filtrer '{col}' :", options=valeurs_uniques, default=valeurs_uniques)
            filtres[col] = selected

    # Appliquer les filtres
    for col, values in filtres.items():
        df = df[df[col].isin(values)]

# Affichage du tableau final
st.dataframe(df[colonnes_affichées], use_container_width=True)

# Option de téléchargement
st.download_button(
    label="📥 Télécharger les données filtrées",
    data=df[colonnes_affichées].to_csv(index=False).encode('utf-8'),
    file_name='données_filtrées.csv',
    mime='text/csv'
)
