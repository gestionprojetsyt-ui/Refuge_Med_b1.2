import streamlit as st
import pandas as pd
import re

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Refuge Médérique - Grand Dax", 
    layout="centered", 
    page_icon="🐾"
)

# --- 2. FONCTIONS TECHNIQUES (CACHE & URL) ---

# Cette fonction télécharge les données et les garde en mémoire (Cache)
# C'est ce qui rend le changement de filtre instantané.
@st.cache_data(ttl=3600)  # Garde en mémoire pendant 1 heure
def load_all_data(url):
    # Transformation du lien Google Sheet en lien de téléchargement CSV
    csv_url = url.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit#gid=', '/export?format=csv&gid=')
    # Lecture directe avec le moteur le plus rapide
    return pd.read_csv(csv_url, engine='c', low_memory=False)

# Transformation des liens Google Drive en images affichables
def format_image_url(url):
    url = str(url).strip()
    if "drive.google.com" in url:
        match = re.search(r"/d/([^/]+)", url)
        if match:
            id_photo = match.group(1)
            return f"https://drive.google.com/uc?export=view&id={id_photo}"
    return url

# --- 3. STYLE VISUEL (CSS) ---
st.markdown("""
    <style>
    [data-testid="stImage"] img { border-radius: 15px; object-fit: cover; height: 250px; }
    .footer { text-align: center; color: #888; font-size: 0.85em; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    .stButton>button { width: 100%; border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. CHARGEMENT ET INTERFACE ---
try:
    # Récupération sécurisée du lien
    URL_SHEET = st.secrets["gsheets"]["public_url"]
    
    # Chargement des données (Utilise le cache pour la vitesse)
    df = load_all_data(URL_SHEET)

    st.title("🐾 Refuge Médérique")
    st.markdown("#### Association Animaux du Grand Dax")

    if not df.empty:
        # Filtre par espèce (Devient instantané avec le cache)
        liste_especes = ["Tous"] + sorted(df['Espèce'].dropna().unique().tolist())
        choix = st.selectbox("Quel animal recherchez-vous ?", liste_especes)
        
        # Filtrage local (très rapide)
        df_filtre = df[df['Espèce'] == choix] if choix != "Tous" else df
        
        st.write(f"Il y a actuellement **{len(df_filtre)}** protégés à l'adoption.")
        st.markdown("---")

        # --- BOUCLE D'AFFICHAGE DES FICHES ---
        for _, row in df_filtre.iterrows():
            with st.container(border=True):
                col1, col2 = st.columns([1.5, 2])
                
                with col1:
                    # Gestion de la photo
                    url_photo = format_image_url(row['Photo'])
                    if url_photo.startswith('http'):
                        st.image(url_photo, use_container_width=True)
                    else:
                        st.image("https://via.placeholder.com/300?text=Photo+à+venir")

                with col2:
                    st.header(row['Nom'])
                    
                    # Statut (Couleurs)
                    statut = str(row['Statut'])
                    if "Adopté" in statut: st.success(f"✅ {statut}")
                    elif "Urgence" in statut: st.error(f"🚨 {statut}")
                    else: st.warning(f"🏠 {statut}")

                    # Infos clés
                    st.write(f"**{row['Espèce']}** | {row['Sexe']} | **{row['Âge']} ans**")
                    
                    # DATE D'ARRIVÉE (Juste sous l'âge)
                    st.markdown(f"📅 **Arrivé le :** {row['Date_Entree']}")
                    
                    st.write(f"**Description :** {row['Description']}")
                    
                    with st.expander("En savoir plus sur son histoire"):
                        st.write(row['Histoire'])

    # --- PIED DE PAGE ET BOUTON DE MISE À JOUR ---
    st.markdown("---")
    col_btn, col_txt = st.columns([1, 2])
    with col_btn:
        # Bouton pour vider le cache et recharger si elles modifient le Excel
        if st.button("🔄 Actualiser le catalogue"):
            st.cache_data.clear()
            st.rerun()
            
    with col_txt:
        st.markdown(f'''
            <div class="footer">
                © 2026 - Refuge Médérique<br>
                <b>Grand Dax</b>
            </div>
        ''', unsafe_allow_html=True)

except Exception as e:
    st.error("Connexion à la base de données impossible. Vérifiez le lien dans les Secrets.")
