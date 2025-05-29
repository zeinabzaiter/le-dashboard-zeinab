import streamlit as st
import pandas as pd
import plotly.express as px

st.title("🦠 Résistance - Tests antibiotiques")

df = pd.read_csv("tests_par_semaine_antibiotiques_2024.csv")

semaines_selectionnees = st.sidebar.multiselect(
    "Filtrer par semaines :", 
    options=df['semaine'].unique(),
    default=df['semaine'].unique()
)

df_filtre = df[df['semaine'].isin(semaines_selectionnees)]

df_filtre['moyenne_mobile'] = df_filtre.groupby('antibiotique')['resistance'].transform(lambda x: x.rolling(8, 1).mean())
df_filtre['std_mobile'] = df_filtre.groupby('antibiotique')['resistance'].transform(lambda x: x.rolling(8, 1).std())
df_filtre['upper_IC95'] = df_filtre['moyenne_mobile'] + 1.96 * df_filtre['std_mobile']

fig = px.line(df_filtre, x='semaine', y='moyenne_mobile', color='antibiotique', markers=True)

for ab in df_filtre['antibiotique'].unique():
    seuil = df_filtre[df_filtre['antibiotique'] == ab]['upper_IC95'].mean()
    fig.add_hline(y=seuil, line_dash="dot", line_color="red")

st.plotly_chart(fig, use_container_width=True)

st.subheader("🚨 Alertes :")
for ab in df_filtre['antibiotique'].unique():
    dernier = df_filtre[df_filtre['antibiotique'] == ab].iloc[-1]
    if dernier['moyenne_mobile'] > dernier['upper_IC95']:
        st.error(f"Alerte : {ab} dépasse le seuil à la semaine {dernier['semaine']}")
