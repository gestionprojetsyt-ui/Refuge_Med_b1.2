import streamlit as st
import pandas as pd
import re
import requests
import base64

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Refuge Médéric", layout="centered")

# --- 2. LOGO ---
URL_LOGO_HD = "https://drive.google.com/uc?export=view&id=1M8yTjY6tt5YZhPvixn-EoFIiolwXRn7E" 

@st.cache_data
def get_base64_image(url):
    try:
        response = requests.get(url, timeout=10)
        return base64.b64encode(response.content).decode()
    except: return None

logo_b64 = get_base64_image(URL_LOGO_HD)

# --- 3. STYLE CSS "ANTI-TEXTE BLANC" ---
st.markdown(f"""
    <style>
    /* Fond de l'application */
    .stApp {{ background-color: #F5F7F9 !important; }}
    
    /* Logo de fond fixe */
    .custom-bg {{
        position: fixed; top: 20%; left: -15vh; width: 60vh;
        opacity: 0.3; z-index: -1; pointer-events: none;
    }}

    /* FORCE LE TEXTE EN NOIR SUR TOUTE LA PAGE */
    html, body, [data-testid="stWidgetLabel"], .stMarkdown, p, h1, h2, h3, span, li {{
        color: #000000 !important;
    }}

    /* STYLE DES FICHES BLANCHES */
    .fiche-animal {{
        background-color: #FFFFFF !important;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #DDDDDD;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 25px;
    }}

    /* Boutons de contact */
    .btn-call {{ 
        text-decoration: none !important; color: white !important; background-color: #2e7d32; 
        padding: 12px; border-radius: 8px; display: block; text-align: center; font-weight: bold; margin-top: 10px;
    }}
    .btn-mail {{ 
        text-decoration: none !important; color: white !important; background-color: #1976d2; 
        padding: 12px; border-radius: 8px; display: block; text-align: center; font-weight: bold; margin-top: 10px;
    }}

    .footer {{
        background-color: white; padding: 20px; border-radius: 15px; 
        margin-top: 40px; text-align: center; border: 2px solid #FF0000;
    }}
    </style>
    <img src="data:image/png;base64,{logo_b64}" class="custom-bg">
""", unsafe_allow_html=True)

# --- 4. FONCTIONS ---
@st.cache_data(ttl=60)
def load_data(url):
    try:
        csv_url = url.replace('/edit?usp=sharing', '/export?format=csv')
        df = pd.read_csv(csv_url)
        # On supprime les lignes où le nom est vide (évite les "nan")
        df = df.dropna(subset=['Nom'])
        return df
    except: return pd.DataFrame()

def format_img(url):
    if "drive.google.com" in str(url):
        m = re.search(r"/d/([^/]+)", str(url))
        if m: return f"https://drive.google.com/uc?export=view&id={m.group(1)}"
    return url

# --- 5. CONTENU ---
try:
    URL_SHEET = st.secrets["gsheets"]["public_url"]
    df = load_data(URL_SHEET)

    if not df.empty:
        st.title("🐾 Refuge Médéric")
        
        # Filtre Espece
        especes = ["Tous"] + sorted([x for x in df['Espèce'].unique() if str(x) != 'nan'])
        choix = st.selectbox("Filtrer par espèce", especes)
        
        df_filtre = df[df['Statut'] != "Adopté"]
        if choix != "Tous":
            df_filtre = df_filtre[df_filtre['Espèce'] == choix]

        for _, row in df_filtre.iterrows():
            # Utilisation de HTML pur pour la fiche pour garantir le fond blanc
            st.markdown(f'''
                <div class="fiche-animal">
                    <h2 style="color: #FF0000 !important; margin-top:0;">{row['Nom']}</h2>
                    <p><b>{row['Espèce']}</b> | {row['Sexe']} | {row['Âge']} ans</p>
                </div>
            ''', unsafe_allow_html=True)
            
            # Affichage Photo et détails
            c1, c2 = st.columns([1, 1])
            with c1:
                st.image(format_img(row['Photo']), use_container_width=True)
            with c2:
                statut = str(row['Statut'])
                if "Urgence" in statut: st.error(statut)
                elif "Réservé" in statut: st.warning(statut)
                else: st.info(statut)
                
                with st.expander("📖 Voir son histoire"):
                    st.write(row['Histoire'])
                
                if "Réservé" not in statut:
                    st.markdown(f'<a href="tel:0558736882" class="btn-call">📞 Appeler</a>', unsafe_allow_html=True)
                    st.markdown(f'<a href="mailto:animauxdugranddax@gmail.com?subject=Adoption {row["Nom"]}" class="btn-mail">📩 Mail</a>', unsafe_allow_html=True)
            
            st.markdown("---")

    # FOOTER
    st.markdown('<div class="footer">📍 182 chemin Lucien Viau, Saint-Paul-lès-Dax<br>📞 05 58 73 68 82</div>', unsafe_allow_html=True)

except Exception as e:
    st.error("Connexion au tableau en cours...")
