import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.title("🧫 Résistance - Autres antibiotiques")

# Charger les données
df = pd.read_excel("other Antibiotiques staph aureus.xlsx")
df.columns = df.columns.str.strip()

# Si une colonne "Semaine" existe, on filtre par semaine
if "Semaine" in df.columns:
    semaines = df['Semaine'].unique()
    selected = st.sidebar.multiselect("Filtrer par semaines :", options=semaines, default=semaines)
    df = df[df['Semaine'].isin(selected)]

# Sélection des colonnes de type %R
colonnes_res = [col for col in df.columns if col.startswith('%')]

if colonnes_res:
    ab = st.selectbox("Choisir un antibiotique :", colonnes_res)

    # Forcer en numérique
    df[ab] = pd.to_numeric(df[ab], errors='coerce')

    # Vérification s’il y a des données
    if df[ab].dropna().empty:
        st.warning(f"Aucune donnée exploitable pour {ab}.")
    else:
        # Calcul statistique
        df['moyenne_mobile'] = df[ab].rolling(8, 1).mean()
        df['std_mobile'] = df[ab].rolling(8, 1).std()
        df['upper_IC95'] = df['moyenne_mobile'] + 1.96 * df['std_mobile']

        # Points en alerte
        points_alerte = df[df['moyenne_mobile'] > df['upper_IC95']]

        fig = go.Figure()

        # Courbe principale
        fig.add_trace(go.Scatter(
            x=df['Semaine'] if 'Semaine' in df.columns else df.index,
            y=df['moyenne_mobile'],
            mode='lines+markers',
            name='Moyenne mobile'
        ))

        # Seuil IC95%
        fig.add_hline(
            y=df['upper_IC95'].mean(),
            line_dash="dot",
            line_color="red",
            annotation_text="Seuil IC95%",
            annotation_position="top left"
        )

        # Affichage des points rouges si dépassement
        if not points_alerte.empty:
            fig.add_trace(go.Scatter(
                x=points_alerte['Semaine'] if 'Semaine' in df.columns else points_alerte.index,
                y=points_alerte['moyenne_mobile'],
                mode='markers',
                marker=dict(size=16, color='darkred'),
                name="⚠️ Alerte"
            ))
            st.error(f"🚨 Alerte : {len(points_alerte)} points au-dessus du seuil IC95% détectés.")

        # Affichage du graphique
        fig.update_layout(
            title=f"{ab} - Résistance avec IC95%",
            xaxis_title="Semaine" if "Semaine" in df.columns else "Index",
            yaxis_title="% Résistance"
        )

        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Aucune colonne de type '%R ...' trouvée dans le fichier.")
