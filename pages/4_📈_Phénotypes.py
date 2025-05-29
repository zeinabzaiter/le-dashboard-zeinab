import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.title("📈 Phénotypes - Évolution")

# Charger les données
df = pd.read_excel("staph_aureus_pheno_final.xlsx")
df.columns = df.columns.str.strip()

if all(col in df.columns for col in ['Semaine', 'Phénotype', '%Présence']):

    semaines = df['Semaine'].unique()
    selected_sem = st.sidebar.multiselect("Filtrer par semaines :", options=semaines, default=semaines)
    df = df[df['Semaine'].isin(selected_sem)]

    phenos = df['Phénotype'].unique()
    selected_pheno = st.selectbox("Choisir un phénotype :", phenos)

    df_pheno = df[df['Phénotype'] == selected_pheno]
    df_pheno['%Présence'] = pd.to_numeric(df_pheno['%Présence'], errors='coerce')

    # Calculs
    df_pheno['moyenne_mobile'] = df_pheno['%Présence'].rolling(8, 1).mean()
    df_pheno['std_mobile'] = df_pheno['%Présence'].rolling(8, 1).std()
    df_pheno['upper_IC95'] = df_pheno['moyenne_mobile'] + 1.96 * df_pheno['std_mobile']

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_pheno['Semaine'],
        y=df_pheno['moyenne_mobile'],
        mode='lines+markers',
        name='Moyenne mobile'
    ))

    fig.add_hline(
        y=df_pheno['upper_IC95'].mean(),
        line_dash="dot",
        line_color="red",
        annotation_text="Seuil IC95%",
        annotation_position="top left"
    )

    # 🧠 Cas spécial : VRSA
    if selected_pheno.upper() == "VRSA":
        if (df_pheno['%Présence'] > 0).any():
            last_case = df_pheno[df_pheno['%Présence'] > 0].iloc[-1]
            fig.add_trace(go.Scatter(
                x=[last_case['Semaine']],
                y=[last_case['moyenne_mobile']],
                mode='markers',
                marker=dict(size=16, color='darkred'),
                name="⚠️ Alerte"
            ))
            st.error(f"🚨 Alerte VRSA : au moins 1 cas détecté à la semaine {last_case['Semaine']}")

    # Autres phénotypes : règles classiques
    else:
        alertes = df_pheno[df_pheno['moyenne_mobile'] > df_pheno['upper_IC95']]
        if not alertes.empty:
            fig.add_trace(go.Scatter(
                x=alertes['Semaine'],
                y=alertes['moyenne_mobile'],
                mode='markers',
                marker=dict(size=16, color='darkred'),
                name="⚠️ Alerte"
            ))
            st.error(f"🚨 Alerte : {len(alertes)} point(s) au-dessus du seuil IC95% pour {selected_pheno}")

    fig.update_layout(
        title=f"Évolution du phénotype : {selected_pheno}",
        xaxis_title="Semaine",
        yaxis_title="% Présence"
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("❗ Ce fichier doit contenir les colonnes : 'Semaine', 'Phénotype', '%Présence'")
