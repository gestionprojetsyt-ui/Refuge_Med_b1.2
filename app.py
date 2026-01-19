import streamlit as st
import pandas as pd
import re
import requests
import base64

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Refuge Médéric - Association Animaux du Grand Dax", 
    layout="centered", 
    page_icon="🐾"
)

# --- 2. LOGO ---
URL_LOGO_HD = "https://drive.google.com/uc?export=view&id=1M8yTjY6tt5YZhPvixn-EoFIiolwXRn7E" 

@st.cache_data
def get_base64_image(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode()
        return None
    except:
        return None

logo_b64 = get_base64_image(URL_LOGO_HD)

# --- 3. STYLE CSS (CONTRASTE FORCE) ---
if logo_b64:
    st.markdown(f"""
        <style>
        /* On force le fond de l'appli en très clair pour le contraste */
        .stApp {{
            background-color: #F0F2F6 !important;
        }}
        
        /* Logo de fond */
        .custom-bg {{
            position: fixed;
            top: 25%;
            left: -15vh;
            width: 60vh;
            opacity: 0.30;
            z-index: 0;
            pointer-events: none;
        }}

        /* STYLE DES FICHES : FOND BLANC ET TEXTE NOIR FORCE */
        .fiche-animal {{
            background-color: white !important;
            color: #1A1A1A !important;
            padding: 20px;
            border-radius: 15px;
            border: 2px solid #E0E0E0;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            position: relative;
            z-index: 10;
        }}

        /* On force la couleur noire sur TOUT le texte dans les fiches */
        .fiche-animal p, .fiche-animal span, .fiche-animal h3, .fiche-animal div {{
            color: #1A1A1A !important;
        }}

        h1 {{ color: #FF0000 !important; font-weight: 800; }}
        
        /* Boutons */
        .btn-call {{ 
            text-decoration: none !important; color: white !important; background-color: #2e7d32; 
            padding: 12px; border-radius: 8px; display: block; text-align: center; font-weight: bold; margin-top: 10px;
        }}
        .btn-mail {{ 
            text-decoration: none !important; color: white !important; background-color: #1976d2; 
            padding: 12px; border-radius: 8px; display: block; text-align: center; font-weight: bold; margin-top: 10px;
        }}

        .footer {{
            background-color: white; padding: 20px; border-radius: 15px; margin-top: 40px; text-align: center; border: 2px solid #FF0000; color: #1A1A1A;
        }}
        </style>
        
        <img src="data:image/png;base64,{logo_b64}" class="custom-bg">
        """, unsafe_allow_html=True)

# --- 4. FONCTIONS ---
@st.cache_data(ttl=60)
def load_all_data(url):
    try:
        csv_url = url.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit#gid=', '/export?format=csv&gid=')
        df = pd.read_csv(csv_url, engine='c', low_memory=False)
        def categoriser_age(age):
            try:
                age = float(str(age).replace(',', '.'))
                if age < 1: return "Moins d'un an"
                elif 1 <= age <= 5: return "1 à 5 ans"
                elif 5 < age < 10: return "5 à 10 ans"
                else: return "10 ans et plus"
            except: return "Non précisé"
        df['Tranche_Age'] = df['Âge'].apply(categoriser_age)
        return df
    except: return pd.DataFrame()

def format_image_url(url):
    url = str(url).strip()
    if "drive.google.com" in url:
        match = re.search(r"/d/([^/]+)", url)
        if match:
            id_photo = match.group(1)
            return f"https://drive.google.com/uc?export=view&id={id_photo}"
    return url

# --- 5. INTERFACE ---
try:
    URL_SHEET = st.secrets["gsheets"]["public_url"]
    df = load_all_data(URL_SHEET)

    if not df.empty:
        df_dispo = df[df['Statut'] != "Adopté"].copy()
        st.title("🐾 Refuge Médéric")
        st.write("Association Animaux du Grand Dax")

        # Filtres simples
        choix_espece = st.selectbox("🐶 Espèce", ["Tous"] + sorted(df_dispo['Espèce'].dropna().unique().tolist()))
        
        st.info("🛡️ **Engagement Santé :** Vaccinés, identifiés et stérilisés.")
        
        df_filtre = df_dispo.copy()
        if choix_espece != "Tous": df_filtre = df_filtre[df_filtre['Espèce'] == choix_espece]

        for _, row in df_filtre.iterrows():
            # ON EMBALLE CHAQUE FICHE DANS NOTRE CLASSE CSS PERSONNALISÉE
            st.markdown(f'<div class="fiche-animal">', unsafe_allow_html=True)
            
            col_img, col_txt = st.columns([1, 1.2])
            with col_img:
                url_photo = format_image_url(row['Photo'])
                st.image(url_photo if url_photo.startswith('http') else "https://via.placeholder.com/300", use_container_width=True)
            
            with col_txt:
                st.subheader(row['Nom'])
                st.write(f"**{row['Espèce']}** | {row['Sexe']} | **{row['Âge']} ans**")
                
                # Statut
                statut = str(row['Statut']).strip()
                if "Urgence" in statut: st.error(statut)
                elif "Réservé" in statut: st.warning(statut)
                else: st.info(statut)
                
                # Histoire et Caractère simplifiés pour mobile
                with st.expander("Voir son histoire"):
                    st.write(row['Histoire'])
                
                if "Réservé" in statut:
                    st.markdown('<div style="background-color:#ff8f00; color:white; padding:10px; border-radius:8px; text-align:center;">Réservé</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<a href="tel:0558736882" class="btn-call">📞 Appeler</a>', unsafe_allow_html=True)
                    st.markdown(f'<a href="mailto:animauxdugranddax@gmail.com?subject=Adoption {row["Nom"]}" class="btn-mail">📩 Mail</a>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

    # PIED DE PAGE
    st.markdown(f'''
        <div class="footer">
            <b>📍 Adresse :</b> 182 chemin Lucien Viau, Saint-Paul-lès-Dax<br>
            <b>📞 Tél :</b> 05 58 73 68 82<br>
            © 2026 - Développé par Firnaeth.
        </div>
    ''', unsafe_allow_html=True)

except Exception as e:
    st.error("Erreur de données.")
