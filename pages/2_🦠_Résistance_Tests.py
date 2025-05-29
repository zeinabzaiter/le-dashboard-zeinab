import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.title("🦠 Résistance - Tests antibiotiques")

# Charger les données
df = pd.read_csv("tests_par_semaine_antibiotiques_2024.csv")
df.columns = df.columns.str.strip()

# Sélection de la colonne Semaine
semaines_selectionnees = st.sidebar.multiselect(
    "Filtrer par semaines :", 
    options=df['Semaine'].unique(),
    default=df['Semaine'].unique()
)
df_filtre = df[df['Semaine'].isin(semaines_selectionnees)]

# Détection des colonnes de %R
colonnes_resistance = [col for col in df.columns if col.startswith('%')]

# Sélecteur d'antibiotique
antibio = st.selectbox("Choisir un antibiotique :", colonnes_resistance)

# Calculs
df_filtre['moyenne_mobile'] = df_filtre[antibio].rolling(8, 1).mean()
df_filtre['std_mobile'] = df_filtre[antibio].rolling(8, 1).std()
df_filtre['upper_IC95'] = df_filtre['moyenne_mobile'] + 1.96 * df_filtre['std_mobile']

# Dernier point
dernier = df_filtre.iloc[-1]
alerte = dernier['moyenne_mobile'] > dernier['upper_IC95']

# Création du graphique
fig = go.Figure()

# Courbe moyenne mobile
fig.add_trace(go.Scatter(
    x=df_filtre['Semaine'],
    y=df_filtre['moyenne_mobile'],
    mode='lines+markers',
    name='Moyenne mobile',
    line=dict(color='blue')
))

# Ligne de seuil IC95%
fig.add_hline(
    y=df_filtre['upper_IC95'].mean(),
    line_dash="dot",
    line_color="red",
    annotation_text="Seuil IC95%",
    annotation_position="top left"
)

# 🔴 Point rouge s’il y a alerte
if alerte:
    fig.add_trace(go.Scatter(
        x=[dernier['Semaine']],
        y=[dernier['moyenne_mobile']],
        mode='markers',
        marker=dict(size=16, color='darkred'),
        name='ALERTE'
    ))
    st.error(f"🚨 Alerte : {antibio} dépasse le seuil à la semaine {dernier['Semaine']}")

# Affichage
fig.update_layout(title=f"{antibio} - Résistance avec seuil IC95%", xaxis_title="Semaine", yaxis_title="Moyenne mobile")
st.plotly_chart(fig, use_container_width=True)
