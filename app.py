import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Refuge de Douai", layout="centered")

# --- 2. LIEN GOOGLE SHEET ---
# REMPLACE CE LIEN par le tien (celui obtenu via le bouton Partager)
URL_SHEET = "https://docs.google.com/spreadsheets/d/1XZXKwCfJ_922HAkAANzpXyyZL97uJzcu84viFWdtgpA/edit?usp=sharing"

# Transformation automatique du lien pour lecture directe
def get_csv_url(url):
    if "docs.google.com" in url:
        return url.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit#gid=', '/export?format=csv&gid=')
    return url

URL_CSV = get_csv_url(URL_SHEET)

# --- 3. STYLE CSS (Grandes photos & Design) ---
st.markdown("""
    <style>
    .stAlert { padding: 5px; border-radius: 10px; }
    [data-testid="stImage"] img {
        border-radius: 15px;
        max-height: 350px; 
        object-fit: cover;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🐾 Nos protégés")

try:
    # --- 4. CHARGEMENT DES DONNÉES ---
    # On ajoute st.cache_data pour que l'app soit rapide
    @st.cache_data(ttl=600) # Recharge les données toutes les 10 min
    def load_data(url):
        return pd.read_csv(url)

    df = load_data(URL_CSV)

    # --- 5. FILTRE AUTOMATIQUE ---
    if not df.empty:
        # On récupère les espèces uniques (Chien, Chat...)
        liste_especes = ["Tous"] + sorted(df['Espèce'].dropna().unique().tolist())
        espece_choisie = st.selectbox("Quel animal recherchez-vous ?", liste_especes)
    else:
        espece_choisie = "Tous"

    st.markdown("---")

    # Filtrage
    df_filtre = df[df['Espèce'] == espece_choisie] if espece_choisie != "Tous" else df

    # --- 6. AFFICHAGE DE LA LISTE ---
    for index, row in df_filtre.iterrows():
        with st.container(border=True):
            col1, col2 = st.columns([1.5, 2])
            
            with col1:
                photo = str(row['Photo']).strip()
                # Vérifie si c'est un lien Web ou un fichier local
                if photo.startswith('http'):
                    st.image(photo, use_container_width=True)
                elif os.path.exists(photo):
                    st.image(photo, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/300?text=Photo+introuvable")

            with col2:
                st.header(row['Nom'])
                
                # Statuts avec couleurs
                statut = str(row['Statut'])
                if "Adopté" in statut:
                    st.success(f"✅ {statut}")
                elif "Urgence" in statut:
                    st.error(f"🚨 {statut}")
                else:
                    st.warning(f"🏠 {statut}")

                st.write(f"**{row['Espèce']}** | {row['Sexe']} | **{row['Âge']} ans**")
                st.caption(f"📅 Arrivé le : {row['Date_Entree']}")
                
                tab1, tab2 = st.tabs(["📖 Histoire", "📋 Caractère"])
                with tab1:
                    st.write(row['Histoire'])
                with tab2:
                    st.write(row['Description'])

except Exception as e:
    st.error(f"Erreur de connexion au Google Sheet.")
    st.info("Vérifie que ton lien est public ('Tous les utilisateurs disposant du lien').")
