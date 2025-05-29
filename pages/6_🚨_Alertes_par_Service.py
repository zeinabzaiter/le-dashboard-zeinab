import streamlit as st
import pandas as pd

st.set_page_config(page_title="Alertes par service", layout="wide")
st.title("🚨 Alertes par Service / Semaine")

# Charger les données
try:
    df = pd.read_csv("Export_StaphAureus_COMPLET.csv", sep=None, engine='python')
except Exception as e:
    st.error(f"Erreur de lecture du fichier : {e}")
    st.stop()

# Nettoyer les noms de colonnes
df.columns = df.columns.str.strip()

# Afficher noms des colonnes bruts
st.write("Colonnes détectées :", df.columns.tolist())

# Tentative de renommage intelligent
df = df.rename(columns={
    'Week': 'Semaine',
    'week': 'Semaine',
    'Résistance (%)': '%Résistance',
    'Resistance (%)': '%Résistance',
    'Résistance': '%Résistance',
    'Résistance %': '%Résistance',
    'ATB': 'Antibiotique',
    'Antibio': 'Antibiotique',
    'Service': 'UF',
    'Unité': 'UF'
})

# Vérifier les colonnes nécessaires
colonnes_requises = ['Semaine', 'UF', 'Antibiotique', '%Résistance']
missing = [col for col in colonnes_requises if col not in df.columns]

if missing:
    st.error(f"Le fichier doit contenir les colonnes : {', '.join(colonnes_requises)}. Manquantes : {', '.join(missing)}")
    st.stop()

# Conversion pour traitement
df['%Résistance'] = pd.to_numeric(df['%Résistance'], errors='coerce')

# Calcul moyenne mobile + IC95%
df['moyenne_mobile'] = df.groupby('Antibiotique')['%Résistance'].transform(lambda x: x.rolling(8, min_periods=1).mean())
df['std_mobile'] = df.groupby('Antibiotique')['%Résistance'].transform(lambda x: x.rolling(8, min_periods=1).std())
df['upper_IC95'] = df['moyenne_mobile'] + 1.96 * df['std_mobile']

# Alerte = dépassement seuil
df['Alerte'] = df['%Résistance'] > df['upper_IC95']
df['Type Alerte'] = df['Alerte'].apply(lambda x: "Résistance élevée" if x else None)

# Alerte spéciale VRSA si dispo
if 'Phénotype' in df.columns and 'Présence' in df.columns:
    df['Présence'] = pd.to_numeric(df['Présence'], errors='coerce')
    vrsa_rows = df[(df['Phénotype'].str.upper() == 'VRSA') & (df['Présence'] > 0)].copy()
    vrsa_rows['Type Alerte'] = "⚠️ VRSA détecté"
    df = pd.concat([df, vrsa_rows], ignore_index=True)

# Garder seulement lignes avec alerte
alertes = df[df['Type Alerte'].notna()]

# Résumé
resume = alertes.groupby(['Semaine', 'UF', 'Type Alerte']).size().reset_index(name="Nombre d’alertes")

# Filtres
with st.expander("🔍 Filtres"):
    semaines = st.multiselect("Filtrer par semaines :", options=sorted(df['Semaine'].dropna().unique()), default=sorted(df['Semaine'].dropna().unique()))
    ufs = st.multiselect("Filtrer par services (UF) :", options=sorted(df['UF'].dropna().unique()), default=sorted(df['UF'].dropna().unique()))
    resume = resume[resume['Semaine'].isin(semaines) & resume['UF'].isin(ufs)]

# Affichage
st.dataframe(resume, use_container_width=True)

# Export CSV
st.download_button(
    label="📥 Télécharger les alertes",
    data=resume.to_csv(index=False).encode('utf-8'),
    file_name="alertes_par_service.csv",
    mime="text/csv"
)
