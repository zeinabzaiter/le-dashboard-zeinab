import streamlit as st
import pandas as pd
import plotly.express as px

st.title("🦠 Résistance - Tests antibiotiques")

df = pd.read_csv("tests_par_semaine_antibiotiques_2024.csv")

semaines_selectionnees = st.sidebar.multiselect(
    "Filtrer par semaines :", 
    options=df['Semaine'].unique(),
    default=df['Semaine'].unique()
)

df_filtre = df[df['Semaine'].isin(semaines_selectionnees)]

# Exemple avec 1 antibiotique : Vancomycin
df_filtre['moyenne_mobile'] = df_filtre['%R Vancomycin'].rolling(8, 1).mean()
df_filtre['std_mobile'] = df_filtre['%R Vancomycin'].rolling(8, 1).std()
df_filtre['upper_IC95'] = df_filtre['moyenne_mobile'] + 1.96 * df_filtre['std_mobile']

fig = px.line(df_filtre, x='Semaine', y='moyenne_mobile', markers=True, title="%R Vancomycin - Moyenne mobile")
fig.add_hline(y=df_filtre['upper_IC95'].mean(), line_dash="dot", line_color="red", annotation_text="Seuil IC95%")

st.plotly_chart(fig, use_container_width=True)

dernier = df_filtre.iloc[-1]
if dernier['moyenne_mobile'] > dernier['upper_IC95']:
    st.error(f"Alerte : %R Vancomycin dépasse le seuil à la semaine {dernier['Semaine']}")
