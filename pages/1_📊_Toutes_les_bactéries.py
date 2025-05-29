import streamlit as st
import pandas as pd

st.title("📊 Toutes les bactéries")

# Charger les données
df = pd.read_excel("TOUS les bacteries a etudier.xlsx")
df.columns = df.columns.str.strip()

# Affichage interactif
colonnes = st.multiselect(
    "Choisir les colonnes à afficher :",
    df.columns.tolist(),
    default=df.columns.tolist()
)

st.dataframe(df[colonnes])


