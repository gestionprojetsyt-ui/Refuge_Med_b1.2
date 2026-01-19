import streamlit as st
import pandas as pd
import re

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Refuge Médéric - Association Animaux du Grand Dax", 
    layout="centered", 
    page_icon="🐾"
)

# --- 2. CONFIGURATION DU LOGO (A REMPLACER PAR TON LIEN) ---
# J'utilise une image de patte de chien par défaut pour le test
URL_LOGO = "https://cdn-icons-png.flaticon.com/512/620/620851.png" 

# --- 3. STYLE CSS (FORCE LE LOGO EN VRAI BACKGROUND) ---
st.markdown(f"""
    <style>
    /* LE LOGO : Position fixed pour sortir de tout container */
    .background-logo {{
        position: fixed;
        top: 15vh;
        left: -180px; /* Coupe environ la moitié à 35% de largeur */
        width: 500px;
        opacity: 0.35; /* Ton réglage à 35% */
        z-index: -1; /* Passe derrière absolument TOUT */
        pointer-events: none;
        user-select: none;
    }}

    /* On force le fond de l'application à être transparent pour voir l'image derrière */
    .stApp {{
        background: transparent;
    }}

    /* On s'assure que le contenu reste lisible */
    .stMain {{
        background-color: rgba(255, 255, 255, 0.4); /* Voile très léger pour le contraste */
    }}

    h1 {{ color: #FF0000 !important; }}
    
    [data-testid="stImage"] img {{ 
        border: 10px solid white !important; 
        border-radius: 5px !important; 
        box-shadow: 0px 4px 12px rgba(0,0,0,0.15) !important;
        object-fit: cover;
        height: 300px;
    }}
    
    .btn-contact {{ 
        text-decoration: none !important; color: white !important; background-color: #2e7d32; 
        padding: 12px; border-radius: 8px; display: block; text-align: center; font-weight: bold; margin-top: 10px;
    }}

    .footer-container {{
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        margin-top: 50px;
        text-align: center;
        border: 2px solid #FF0000;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    }}
    </style>
    
    <img src="{URL_LOGO}" class="background-logo">
    """, unsafe_allow_html=True)

# --- 4. FONCTIONS TECHNIQUES ---
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

# --- 5. CONTENU DE L'APP ---
try:
    URL_SHEET = st.secrets["gsheets"]["public_url"]
    df = load_all_data(URL_SHEET)

    if not df.empty:
        df_dispo = df[df['Statut'] != "Adopté"].copy()

        st.title("🐾 Refuge Médéric")
        st.markdown("#### Association Animaux du Grand Dax")

        c1, c2 = st.columns(2)
        with c1:
            liste_especes = ["Tous"] + sorted(df_dispo['Espèce'].dropna().unique().tolist())
            choix_espece = st.selectbox("🐶 Espèce", liste_especes)
        with c2:
            liste_ages = ["Tous", "Moins d'un an (Junior)", "1 à 5 ans (Jeune Adulte)", "5 à 10 ans (Adulte)", "10 ans et plus (Senior)"]
            choix_age = st.selectbox("🎂 Tranche d'âge", liste_ages)

        df_filtre = df_dispo.copy()
        if choix_espece != "Tous": df_filtre = df_filtre[df_filtre['Espèce'] == choix_espece]
        if choix_age != "Tous": df_filtre = df_filtre[df_filtre['Tranche_Age'] == choix_age]

        st.write(f"**{len(df_filtre)}** protégé(s) à l'adoption")
        st.markdown("---")

        for _, row in df_filtre.iterrows():
            with st.container(border=True):
                col_img, col_txt = st.columns([1, 1.2])
                with col_img:
                    url_photo = format_image_url(row['Photo'])
                    st.image(url_photo if url_photo.startswith('http') else "https://via.placeholder.com/300", use_container_width=True)
                with col_txt:
                    st.subheader(row['Nom'])
                    st.write(f"**{row['Espèce']}** | {row['Sexe']} | **{row['Âge']} ans**")
                    t_hist, t_carac = st.tabs(["📖 Histoire", "📋 Caractère"])
                    with t_hist: st.write(row['Histoire'])
                    with t_carac: st.write(row['Description'])
                    st.markdown(f"""<a href="tel:0558736882" class="btn-contact">📞 Appeler le refuge</a>""", unsafe_allow_html=True)

    # PIED DE PAGE
    st.markdown("""
        <div class="footer-container">
            <b style="color:#FF0000;">Refuge Médérique - Association Animaux du Grand Dax</b><br>
            182 chemin Lucien Viau, 40990 St-Paul-lès-Dax<br>
            📞 05 58 73 68 82 | ⏰ 14h00 - 18h00
        </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error("Lien 'public_url' non configuré.")
