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

# --- 3. STYLE CSS (FORCE LE NOIR ET BLANC) ---
st.markdown(f"""
    <style>
    /* Fond de l'application */
    .stApp {{ background-color: #F0F2F5 !important; }}
    
    /* Logo stable en haut à gauche */
    .fixed-logo {{
        position: absolute;
        top: -40px;
        left: -10px;
        width: 120px;
        opacity: 0.8;
        z-index: 10;
    }}

    /* FICHE ANIMAL : BLANC TOTAL, TEXTE NOIR TOTAL */
    .fiche-animal {{
        background-color: #FFFFFF !important;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #E0E0E0;
        margin-bottom: 20px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }}
    
    /* On force la couleur noire sur chaque type de texte HTML */
    .fiche-animal h2 {{ color: #FF0000 !important; font-weight: bold; margin: 0; }}
    .fiche-animal p {{ color: #000000 !important; font-size: 16px !important; margin: 5px 0; }}
    .fiche-animal b {{ color: #000000 !important; }}
    
    /* Badge de statut manuel (évite le bug du blanc sur blanc) */
    .custom-status {{
        display: inline-block;
        padding: 5px 12px;
        border-radius: 5px;
        color: white !important;
        font-weight: bold;
        margin: 10px 0;
    }}

    .btn-call {{ 
        text-decoration: none !important; color: white !important; background-color: #2e7d32; 
        padding: 12px; border-radius: 8px; display: block; text-align: center; font-weight: bold; margin-top: 10px;
    }}
    .btn-mail {{ 
        text-decoration: none !important; color: white !important; background-color: #1976d2; 
        padding: 12px; border-radius: 8px; display: block; text-align: center; font-weight: bold; margin-top: 10px;
    }}

    /* Cache les éléments Streamlit inutiles */
    #MainMenu, footer, header {{ visibility: hidden; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. CHARGEMENT DES DONNÉES ---
@st.cache_data(ttl=60)
def load_data(url):
    try:
        csv_url = url.replace('/edit?usp=sharing', '/export?format=csv')
        df = pd.read_csv(csv_url)
        # Supprime les lignes vides pour éviter les "nan" des captures d'écran
        return df.dropna(subset=['Nom'])
    except: return pd.DataFrame()

def format_img(url):
    if "drive.google.com" in str(url):
        m = re.search(r"/d/([^/]+)", str(url))
        if m: return f"https://drive.google.com/uc?export=view&id={m.group(1)}"
    return url

# --- 5. AFFICHAGE ---
try:
    # Affichage du logo
    if logo_b64:
        st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="fixed-logo">', unsafe_allow_html=True)

    URL_SHEET = st.secrets["gsheets"]["public_url"]
    df = load_data(URL_SHEET)

    if not df.empty:
        st.markdown("<h1 style='text-align:center; color:#FF0000; margin-top:20px;'>Refuge Médéric</h1>", unsafe_allow_html=True)
        
        # Filtre simple
        especes = ["Tous"] + sorted(df['Espèce'].unique().tolist())
        choix = st.selectbox("Filtrer par espèce", especes)
        
        df_filtre = df[df['Statut'] != "Adopté"]
        if choix != "Tous":
            df_filtre = df_filtre[df_filtre['Espèce'] == choix]

        for _, row in df_filtre.iterrows():
            statut = str(row['Statut'])
            couleur_statut = "#1976d2" # Bleu adoption
            if "Urgence" in statut: couleur_statut = "#d32f2f" # Rouge
            if "Réservé" in statut: couleur_statut = "#f57c00" # Orange

            # BLOC HTML POUR TOUT LE TEXTE (Protection contre le mode sombre)
            st.markdown(f"""
                <div class="fiche-animal">
                    <h2>{row['Nom']}</h2>
                    <div class="custom-status" style="background-color: {couleur_statut};">{statut}</div>
                    <p><b>Espèce :</b> {row['Espèce']}</p>
                    <p><b>Sexe :</b> {row['Sexe']} | <b>Âge :</b> {row['Âge']} ans</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Photo et Boutons
            c1, c2 = st.columns([1, 1])
            with c1:
                st.image(format_img(row['Photo']), use_container_width=True)
            with c2:
                # Histoire en texte noir forcé
                with st.expander("📖 Voir son histoire"):
                    st.markdown(f"<p style='color:black !important;'>{row['Histoire']}</p>", unsafe_allow_html=True)
                
                if "Réservé" not in statut:
                    st.markdown(f'<a href="tel:0558736882" class="btn-call">📞 Appeler</a>', unsafe_allow_html=True)
                    st.markdown(f'<a href="mailto:animauxdugranddax@gmail.com?subject=Adoption {row["Nom"]}" class="btn-mail">📩 Mail</a>', unsafe_allow_html=True)
            
            st.markdown("<hr style='border:1px solid #ddd; margin:30px 0;'>", unsafe_allow_html=True)

    # PIED DE PAGE FIXE AVEC COORDONNÉES
    st.markdown("""
        <div style="background-color:white; padding:20px; border-radius:15px; border:2px solid red; text-align:center; color:black !important;">
            <p style="margin:0; font-weight:bold; color:black !important;">📍 Refuge Médéric</p>
            <p style="margin:5px 0; color:black !important;">182 chemin Lucien Viau, Saint-Paul-lès-Dax</p>
            <p style="margin:0; font-weight:bold; color:black !important;">📞 05 58 73 68 82</p>
            <hr style="margin:10px 0;">
            <p style="font-size:12px; color:black !important;">Développé par Firnaeth. avec passion</p>
        </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.info("Mise à jour des fiches...")
