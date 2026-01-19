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

# --- 2. LOGO EN FILIGRANE (OPACITÉ 0.03) ---
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

# --- 3. STYLE MINIMALISTE (LOGO DISCRET UNIQUEMENT) ---
st.markdown(f"""
    <style>
    /* LOGO À 0.03 D'OPACITÉ EN FOND */
    .logo-bg {{
        position: fixed;
        top: 25%;
        left: -10vh;
        width: 60vh;
        opacity: 0.03;
        z-index: -1;
        pointer-events: none;
    }}
    
    /* BOUTONS CONTACT VERT (On garde juste le style des boutons pour l'action) */
    .btn-contact {{ 
        text-decoration: none !important; color: white !important; background-color: #2e7d32; 
        padding: 12px; border-radius: 8px; display: block; text-align: center; font-weight: bold; margin-top: 10px;
    }}
    
    .btn-reserve {{ 
        text-decoration: none !important; color: white !important; background-color: #ff8f00; 
        padding: 12px; border-radius: 8px; display: block; text-align: center; font-weight: bold; margin-top: 10px;
    }}

    /* PIED DE PAGE DISCRET */
    .footer-container {{
        text-align: center;
        margin-top: 50px;
        padding: 20px;
        border-top: 1px solid #ccc;
    }}
    </style>
    
    <img src="data:image/png;base64,{logo_b64 if logo_b64 else ''}" class="logo-bg">
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
        if match: return f"https://drive.google.com/uc?export=view&id={match.group(1)}"
    return url

# --- 5. INTERFACE (NATIF STREAMLIT) ---

try:
    URL_SHEET = st.secrets["gsheets"]["public_url"]
    df = load_all_data(URL_SHEET)

    if not df.empty:
        df_dispo = df[df['Statut'] != "Adopté"].copy()

        st.title("🐾 Refuge Médéric")
        st.subheader("Association Animaux du Grand Dax")

        c1, c2 = st.columns(2)
        with c1:
            choix_espece = st.selectbox("🐶 Espèce", ["Tous"] + sorted(df_dispo['Espèce'].dropna().unique().tolist()))
        with c2:
            choix_age = st.selectbox("🎂 Tranche d'âge", ["Tous", "Moins d'un an (Junior)", "1 à 5 ans (Jeune Adulte)", "5 à 10 ans (Adulte)", "10 ans et plus (Senior)"])

        if st.button("🔄 Actualiser le catalogue"):
            st.cache_data.clear()
            st.rerun()

        st.info("🛡️ **Engagement Santé :** Tous nos protégés sont **vaccinés**, **identifiés** (puce électronique) et **stérilisés** avant leur départ du refuge pour une adoption responsable.")
        
        df_filtre = df_dispo.copy()
        if choix_espece != "Tous": df_filtre = df_filtre[df_filtre['Espèce'] == choix_espece]
        if choix_age != "Tous": df_filtre = df_filtre[df_filtre['Tranche_Age'] == choix_age]

        st.divider() # Ligne native Streamlit

        for _, row in df_filtre.iterrows():
            # Utilisation de st.container sans border=True pour un look 100% natif
            with st.container():
                col_img, col_txt = st.columns([1, 1.2])
                with col_img:
                    url_photo = format_image_url(row['Photo'])
                    st.image(url_photo if url_photo.startswith('http') else "https://via.placeholder.com/300", use_container_width=True)
                with col_txt:
                    st.header(row['Nom'])
                    statut = str(row['Statut']).strip()
                    st.caption(f"Statut actuel : {statut}")

                    st.write(f"**{row['Espèce']}** | {row['Sexe']} | **{row['Âge']} ans**")
                    
                    with st.expander("En savoir plus"):
                        st.write("**Son Histoire :**")
                        st.write(row['Histoire'])
                        st.write("**Son Caractère :**")
                        st.write(row['Description'])
                    
                    if "Réservé" in statut:
                        st.warning("🧡 Animal déjà réservé")
                    else:
                        st.markdown(f'<a href="tel:0558736882" class="btn-contact">📞 Appeler le refuge</a>', unsafe_allow_html=True)
                        st.markdown(f'<a href="mailto:animauxdugranddax@gmail.com?subject=Adoption de {row["Nom"]}" class="btn-contact">📩 Envoyer un Mail</a>', unsafe_allow_html=True)
            st.divider()

    # --- 6. PIED DE PAGE ---
    st.markdown("""
        <div class="footer-container">
            <p><b>Refuge Médéric - Association Animaux du Grand Dax</b><br>
            182 chemin Lucien Viau, 40990 St-Paul-lès-Dax<br>
            📞 05 58 73 68 82 | ⏰ 14h00 - 18h00 (Mercredi au Dimanche)</p>
            <p style="font-size:0.8em; color:gray;">
                Développé par Firnaeth avec passion pour nos amis à quatre pattes.
            </p>
        </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error("Impossible de charger les données.")
