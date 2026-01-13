import streamlit as st
import pandas as pd
import re

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Refuge Médérique (Association Animaux du Grand Dax)", layout="centered", page_icon="🐾")

# --- 2. RÉCUPÉRATION DU LIEN SÉCURISÉ ---
try:
    URL_SHEET = st.secrets["gsheets"]["public_url"]
except:
    st.error("Lien de la base de données non configuré dans les Secrets Streamlit.")
    st.stop()

# --- 3. FONCTIONS TECHNIQUES ---

def format_image_url(url):
    url = str(url).strip()
    if "drive.google.com" in url:
        match = re.search(r"/d/([^/]+)", url)
        if match:
            id_photo = match.group(1)
            return f"https://drive.google.com/uc?export=view&id={id_photo}"
    return url

def get_csv_url(url):
    if "docs.google.com" in url:
        return url.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit#gid=', '/export?format=csv&gid=')
    return url

# --- 4. STYLE CSS ---
st.markdown("""
    <style>
    [data-testid="stImage"] img { border-radius: 15px; object-fit: cover; }
    .footer { text-align: center; color: #888; font-size: 0.8em; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. CHARGEMENT ET AFFICHAGE ---
try:
    df = pd.read_csv(get_csv_url(URL_SHEET))
    
    st.title("🐾 Refuge Médérique")
    st.subheader("Association Animaux du Grand Dax")

    if not df.empty:
        liste_especes = ["Tous"] + sorted(df['Espèce'].dropna().unique().tolist())
        espece_choisie = st.selectbox("Quel animal recherchez-vous ?", liste_especes)
        
        df_filtre = df[df['Espèce'] == espece_choisie] if espece_choisie != "Tous" else df
        st.write(f"Affichage de **{len(df_filtre)}** protégés")
        st.markdown("---")

        for _, row in df_filtre.iterrows():
            with st.container(border=True):
                col1, col2 = st.columns([1.5, 2])
                
                with col1:
                    url_photo = format_image_url(row['Photo'])
                    if url_photo.startswith('http'):
                        st.image(url_photo, use_container_width=True)
                    else:
                        st.image("https://via.placeholder.com/300?text=Photo+à+venir")

                with col2:
                    st.header(row['Nom'])
                    
                    statut = str(row['Statut'])
                    if "Adopté" in statut: st.success(f"✅ {statut}")
                    elif "Urgence" in statut: st.error(f"🚨 {statut}")
                    else: st.warning(f"🏠 {statut}")

                    st.write(f"**{row['Espèce']}** | {row['Sexe']} | **{row['Âge']} ans**")
                    st.markdown(f"📅 **Arrivé le :** {row['Date_Entree']}")
                    
                    st.write(f"**Description :** {row['Description']}")
                    
                    with st.expander("Lire son histoire complète"):
                        st.write(row['Histoire'])

    else:
        st.info("Le catalogue est vide pour le moment.")

    # --- PIED DE PAGE ---
    st.markdown(f'''
        <div class="footer">
            © 2026 - Application officielle du Refuge Médérique<br>
            <b>Association Animaux du Grand Dax</b><br>
            Développé par Firnaeth.
        </div>
    ''', unsafe_allow_html=True)

except Exception as e:
    st.error("Erreur de connexion aux données.")
