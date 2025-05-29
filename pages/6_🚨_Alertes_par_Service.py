import streamlit as st
import pandas as pd

st.set_page_config(page_title="Alertes par service", layout="wide")
st.title("🚨 Alertes par Service / Semaine")

# Charger les données
df = pd.read_csv("Export_StaphAureus_COMPLET.csv", sep=None, engine='python')
df.columns = df.columns.str.strip()

# Renommer si besoin
if 'UF' not in df.columns and 'Service' in df.columns:
    df = df.rename(columns={'Service': 'UF'})

# Vérification colonnes nécessaires
if not all(col in df.columns for col in ['Semaine', 'UF', 'Antibiotique', '%Résistance']):
    st.error("Le fichier doit contenir les colonnes : Semaine, UF, Antibiotique, %Résistance")
    st.stop()

# Conversion
df['%Résistance'] = pd.to_numeric(df['%Résistance'], errors='coerce')

# Seuils fictifs par AB (tu peux les adapter)
seuils_ic95 = df.groupby('Antibiotique')['%Résistance'].rolling(8, min_periods=1).mean().reset_index()
seuils_ic95 = seuils_ic95.rename(columns={'%Résistance': 'moyenne_mobile'})
df = df.reset_index().merge(seuils_ic95[['level_1', 'moyenne_mobile']], left_index=True, right_on='level_1', how='left')
df['upper_IC95'] = df['moyenne_mobile'] + 1.96 * df.groupby('Antibiotique')['%Résistance'].rolling(8, min_periods=1).std().reset_index(drop=True)

# Détection des alertes
df['Alerte'] = df['%Résistance'] > df['upper_IC95']
df['Type Alerte'] = df['Alerte'].apply(lambda x: "Résistance élevée" if x else None)

# Alerte spéciale VRSA (si colonne existe)
if 'Phénotype' in df.columns and 'Présence' in df.columns:
    df['Présence'] = pd.to_numeric(df['Présence'], errors='coerce')
    vrsa_rows = df[(df['Phénotype'].str.upper() == 'VRSA') & (df['Présence'] > 0)]
    vrsa_rows['Type Alerte'] = "⚠️ VRSA détecté"
    df = pd.concat([df, vrsa_rows], ignore_index=True)

# Garder uniquement alertes
alertes = df[df['Type Alerte'].notna()]

# Résumé par semaine / service / type
resume = alertes.groupby(['Semaine', 'UF', 'Type Alerte']).size().reset_index(name="Nombre d’alertes")

# Filtres
with st.expander("🔍 Filtres"):
    semaines = st.multiselect("Filtrer par semaines :", options=sorted(df['Semaine'].unique()), default=sorted(df['Semaine'].unique()))
    ufs = st.multiselect("Filtrer par services (UF) :", options=sorted(df['UF'].unique()), default=sorted(df['UF'].unique()))
    resume = resume[resume['Semaine'].isin(semaines) & resume['UF'].isin(ufs)]

# Affichage
st.dataframe(resume, use_container_width=True)

# Export
st.download_button("📥 Télécharger le tableau", data=resume.to_csv(index=False).encode('utf-8'), file_name="alertes_par_service.csv", mime="text/csv")
