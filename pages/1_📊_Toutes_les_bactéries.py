import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📊 Toutes les bactéries")

# Charger les données
df = pd.read_excel("TOUS les bacteries a etudier.xlsx")

# Nettoyage
df.columns = df.columns.str.strip()

# Sélection semaine
semaines = df['semaine'].unique()
selected = st.selectbox("Choisir une semaine :", semaines)

df_filtre = df[df['semaine'] == selected]

# Bar chart
fig = px.bar(
    df_filtre, 
    x="bacterie", 
    y="nb_isolats", 
    color="bacterie", 
    title=f"Nombre d'isolats par bactérie - Semaine {selected}"
)

st.plotly_chart(fig, use_container_width=True)
