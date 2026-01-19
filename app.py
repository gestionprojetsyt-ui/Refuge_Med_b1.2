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

# --- 2. CONFIGURATION DU LOGO ---
# METS TON LIEN ICI
URL_LOGO_HD = "TON_LIEN_ICI" 

@st.cache_data
def get_base64_image(url):
    try:
        # On ajoute des headers pour simuler un navigateur et éviter d'être bloqué
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode()
        else:
            return None
    except Exception as e:
        return None

logo_b64 = get_base64_image(URL_LOGO_HD)

# --- 3. STYLE CSS ---
if logo_b64:
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{logo_b64}");
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-size: 60vh; 
            background-position: -20vh 30%; 
        }}
        .stApp::before {{
            content: "";
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background-color: rgba(255, 255, 255, 0.65);
            z-index: -1;
        }}
        h1 {{ color: #FF0000 !important; font-weight: 800; }}
        [data-testid="stImage"] img {{ 
            border: 10px solid white !important; 
            border-radius: 5px !important; 
            box-shadow: 0px 4px 15px rgba(0,0,0,0.2) !important;
            height: 320px;
            object-fit: cover;
        }}
        .btn-contact {{ 
            text-decoration: none !important; color: white !important; background-color: #2e7d32; 
            padding: 12px; border-radius: 8px; display: block; text-align: center; font-weight: bold; margin-top: 10px;
        }}
        .footer {{
            background-color: rgba(255, 255, 255, 0.9);
            padding: 25px; border-radius: 15px; margin-top: 50px; text-align: center; border: 2px solid #FF0000; color: #444; line-height: 1.6;
        }}
        </style>
        """, unsafe_allow_html=True)
else:
    # Message d'erreur discret pour toi si l'image ne charge pas
    st.warning("⚠️ Le logo en arrière-plan n'a pas pu être chargé. Vérifie le lien direct de ton image.")

# --- 4. LOGIQUE DES DONNÉES ---
@st.cache_data(ttl=60)
def load_all_data(url):
    try:
        csv_url = url.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit#gid=', '/export?format=csv&gid=')
        df = pd.read_csv(csv_url, engine='c', low_memory=False)
        def categoriser_age(age):
            try:
                age = float(str(age).replace(',', '.'))
                if age < 1: return "Moins d'un an (Junior)"
                elif 1 <= age <= 5: return "1 à 5 ans (Jeune Adulte)"
                elif 5 < age < 10: return "5 à 10 ans (Adulte)"
                else: return "10 ans et plus (Senior)"
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
        st.title("🐾 Refuge Médéric")
        st.markdown("#### Association Animaux du Grand Dax")

        c1, c2 = st.columns(2)
        with c1:
            choix_espece = st.selectbox("🐶 Espèce", ["Tous"] + sorted(df['Espèce'].dropna().unique().tolist()))
        with c2:
            choix_age = st.selectbox("🎂 Tranche d'âge", ["Tous", "Moins d'un an (Junior)", "1 à 5 ans (Jeune Adulte)", "5 à 10 ans (Adulte)", "10 ans et plus (Senior)"])

        st.success("🛡️ **Engagement Santé :** Tous nos protégés sont **vaccinés**, **identifiés** (puce électronique) et **stérilisés** avant leur départ du refuge pour une adoption responsable.")
        
        # Affichage simplifié pour le test
        st.write(f"**{len(df)}** protégé(s) à l'adoption")
        st.markdown("---")

    # --- PIED DE PAGE ---
    st.markdown(f'''
        <div class="footer">
            © 2026 - Application officielle du Refuge Médérique<br>
            <b>Association Animaux du Grand Dax</b><br>
            Développé par Firnaeth. avec passion pour nos amis à quatre pattes
        </div>
    ''', unsafe_allow_html=True)

except Exception as e:
    st.error("Lien de données manquant.")
