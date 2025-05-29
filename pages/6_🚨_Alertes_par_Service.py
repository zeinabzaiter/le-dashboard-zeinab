import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Alertes par famille d'antibiotiques", layout="wide")
st.title("\U0001F6A8 Alertes par Service / Famille d'antibiotiques")

# Charger le fichier brut
try:
    df = pd.read_csv("Export_StaphAureus_COMPLET.csv", sep=None, engine="python")
except Exception as e:
    st.error(f"Erreur de lecture du fichier : {e}")
    st.stop()

# Nettoyer les colonnes
df.columns = df.columns.str.strip().str.upper()
df = df.rename(columns={"SEMAINE": "Semaine", "UF": "UF"})

if not all(col in df.columns for col in ["Semaine", "UF"]):
    st.error("Le fichier doit contenir les colonnes 'Semaine' et 'UF'")
    st.stop()

# Dictionnaire de correspondance code -> famille
code_to_famille = {
    "VAB": "Vancomycine", "VAM": "Vancomycine", "VA30": "Vancomycine", "VA5": "Vancomycine", "M.VA": "Vancomycine", "VA": "Vancomycine",
    "TP": "Teicoplanine", "TPM": "Teicoplanine", "TEC": "Teicoplanine", "TPN": "Teicoplanine",
    "GT": "Gentamycine", "GM10": "Gentamycine", "CN30": "Gentamycine", "GEN": "Gentamycine", "GHLR": "Gentamycine", "GM": "Gentamycine", "M.GE": "Gentamycine",
    "OX5": "Oxacilline", "OX": "Oxacilline",
    "DPC": "Daptomycine", "DAP": "Daptomycine",
    "DALB": "Dalbavancine",
    "CLI": "Clindamycine", "CLIN": "Clindamycine", "CC": "Clindamycine",
    "SXT1": "Cotrimoxazole", "SXT": "Cotrimoxazole", "SXTCMI": "Cotrimoxazole", "M.SXT": "Cotrimoxazole",
    "LZ": "Linezolide", "M.LZD": "Linezolide", "LNZ10": "Linezolide", "LNZ": "Linezolide"
}

# Colonnes antibiotiques
tests_ab = [col for col in df.columns if col in code_to_famille]

# Créer une structure de résultat
alertes = []

for ab in tests_ab:
    famille = code_to_famille[ab]
    temp = df[["Semaine", "UF", ab]].copy()
    temp = temp.rename(columns={ab: "%R"})
    temp["Famille"] = famille

    temp = temp.sort_values(["UF", "Famille", "Semaine"])
    temp["%R"] = pd.to_numeric(temp["%R"], errors="coerce")
    temp["moyenne_mobile"] = temp.groupby(["UF", "Famille"])["%R"].transform(lambda x: x.rolling(8, min_periods=1).mean())
    temp["std_mobile"] = temp.groupby(["UF", "Famille"])["%R"].transform(lambda x: x.rolling(8, min_periods=1).std())
    temp["upper_IC95"] = temp["moyenne_mobile"] + 1.96 * temp["std_mobile"]

    temp["Alerte"] = temp["%R"] > temp["upper_IC95"]
    temp["Type Alerte"] = temp["Alerte"].apply(lambda x: f"🚨 Résistance élevée {famille}" if x else None)
    alertes.append(temp[["Semaine", "UF", "Famille", "Type Alerte"]])

# Concaténer toutes les alertes
df_alertes = pd.concat(alertes)
df_alertes = df_alertes[df_alertes["Type Alerte"].notna()]

# Regrouper
resume = df_alertes.groupby(["Semaine", "UF", "Famille", "Type Alerte"]).size().reset_index(name="Nombre d’alertes")

# Filtres interactifs
with st.expander("🔍 Filtres"):
    semaines = st.multiselect("Semaine :", sorted(df["Semaine"].dropna().unique()), default=sorted(df["Semaine"].dropna().unique()))
    services = st.multiselect("Services UF :", sorted(df["UF"].dropna().unique()), default=sorted(df["UF"].dropna().unique()))
    resume = resume[resume["Semaine"].isin(semaines) & resume["UF"].isin(services)]

# Affichage du tableau
st.subheader("📋 Tableau des alertes")
st.dataframe(resume, use_container_width=True)

# Export CSV
st.download_button("🗕️ Exporter CSV", data=resume.to_csv(index=False).encode('utf-8'), file_name="alertes_famille.csv", mime="text/csv")

# Affichage du graphique
st.subheader("📊 Graphique des alertes par semaine et service")
if not resume.empty:
    fig = px.scatter(
        resume,
        x="Semaine",
        y="UF",
        size="Nombre d’alertes",
        color="Famille",
        hover_data=["Type Alerte"],
        title="Alertes par famille d'antibiotiques (taille = nombre d’alertes)",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Aucune alerte correspondant aux filtres actuels.")
