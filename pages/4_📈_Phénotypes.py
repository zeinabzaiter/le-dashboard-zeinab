import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.title("📈 Phénotypes - Taux et Occurrences")

# Chargement du fichier
df = pd.read_excel("staph_aureus_pheno_final.xlsx")
df.columns = df.columns.str.strip()

# Renommer si besoin
if 'Week' in df.columns:
    df = df.rename(columns={'Week': 'Semaine'})

# Liste des phénotypes (toutes colonnes sauf 'Semaine')
phenos = [col for col in df.columns if col != 'Semaine']

# Calcul total par semaine pour % (évite division par 0)
df['total'] = df[phenos].sum(axis=1)

# Interface
selected = st.selectbox("Choisir un phénotype :", phenos)

# Calcul %
df['%'] = df[selected] / df['total'] * 100

# Calcul moyenne mobile & IC95%
df['moyenne_mobile'] = df['%'].rolling(8, 1).mean()
df['std_mobile'] = df['%'].rolling(8, 1).std()
df['upper_IC95'] = df['moyenne_mobile'] + 1.96 * df['std_mobile']

# Alerte VRSA
is_vrsa = selected.upper() == "VRSA"
alerte_rows = df[df['moyenne_mobile'] > df['upper_IC95']] if not is_vrsa else df[df[selected] > 0]

# Graphique
fig = go.Figure()

# Courbe % mobile
fig.add_trace(go.Scatter(
    x=df['Semaine'],
    y=df['moyenne_mobile'],
    mode='lines+markers',
    name='% Mobile',
    line=dict(color='blue')
))

# Occurrences en bulles
fig.add_trace(go.Scatter(
    x=df['Semaine'],
    y=df['moyenne_mobile'],
    mode='markers+text',
    marker=dict(size=12, color='lightblue'),
    text=df[selected].astype(str),
    textposition='top center',
    name='Occurrences'
))

# Ligne IC95%
fig.add_hline(
    y=df['upper_IC95'].mean(),
    line_dash="dot",
    line_color="red",
    annotation_text="Seuil IC95%",
    annotation_position="top left"
)

# Points rouges pour alertes
if not alerte_rows.empty:
    fig.add_trace(go.Scatter(
        x=alerte_rows['Semaine'],
        y=alerte_rows['moyenne_mobile'],
        mode='markers',
        marker=dict(size=16, color='darkred'),
        name='⚠️ Alerte'
    ))
    st.error(f"🚨 Alerte détectée pour {selected} à {len(alerte_rows)} semaine(s)")

# Layout
fig.update_layout(
    title=f"Évolution du phénotype : {selected}",
    xaxis_title="Semaine",
    yaxis_title="% Présence (moyenne mobile)",
    legend_title="Indicateurs"
)

st.plotly_chart(fig, use_container_width=True)
