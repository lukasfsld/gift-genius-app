import streamlit as st
from openai import OpenAI
import json

# --- 1. SETUP ---
st.set_page_config(page_title="GiftGenius", page_icon="🎁", layout="wide")

# --- 2. PREMIUM CSS DESIGN (Glassmorphism) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    
    /* Animierter Hintergrund */
    .stApp {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Titel Styling - Weiß damit es auf dem bunten Hintergrund knallt */
    .main-title {
        color: white;
        font-weight: 800; font-size: 3.5rem; text-align: center; margin-bottom: 0;
        text-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .subtitle { text-align: center; color: rgba(255,255,255,0.9); font-size: 1.2rem; margin-bottom: 3rem; }
    
    /* GLASSMORPHISM KARTEN */
    .gift-card {
        background: rgba(255, 255, 255, 0.95); /* Fast weiß, leicht transparent */
        backdrop-filter: blur(10px); /* Der Milchglas-Effekt */
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px; 
        padding: 30px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.18);
        height: 100%;
        display: flex; 
        flex-direction: column; 
        justify-content: space-between;
        transition: transform 0.3s ease;
        text-align: center; /* Zentrierter Inhalt sieht edler aus */
    }
    
    .gift-card:hover { 
        transform: translateY(-10px); 
    }
    
    .emoji-icon { font-size: 4rem; margin-bottom: 10px; }
    .card-title { color: #2D3436; font-size: 1.3rem; font-weight: 700; margin-bottom: 10px; }
    .card-desc { color: #555; font-size: 0.95rem; line-height: 1.6; margin-bottom: 25px; }
    
    /* Button */
    .buy-btn {
        display: inline-block; 
        background: #2D3436; /* Schwarz/Dunkelgrau wirkt Premium */
        color: white !important; 
        padding: 12px 30px; 
        border-radius: 50px;
        text-decoration: none; 
        font-weight: 600; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s;
    }
    .buy-btn:hover { 
        background: #000; 
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    /* Sidebar transparenter machen */
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.9);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. SEITENLEISTE (Inputs) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4213/4213958.png", width=80)
    st.markdown("### ⚙️ Deine Suche")
    
    if "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
    else:
        st.error("API Key fehlt!")
        st.stop()
    
    relation = st.text_input("Für wen?", placeholder="z.B. Beste Freundin, Opa...")
    occasion = st.text_input("Anlass?", placeholder="z.B. Geburtstag, Jahrestag...")
    
    age = st.slider("Alter", 1, 99, 25)
    budget = st.select_slider("Budget", options=["Kleinigkeit", "20-50€", "50-100€", "Luxus (>100€)"])
    interests = st.text_area("Interessen & Typ", height=100, placeholder="z.B. Mag Pflanzen, Yoga und Wein...")
    
    st.markdown("---")
    start_search = st.button("✨ Magie starten", use_container_width=True, type="primary")


# --- 4. HAUPTBEREICH ---
st.markdown('<div class="main-title">GiftGenius AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Das perfekte Geschenk. In Sekunden.</div>', unsafe_allow_html=True)

if start_search:
    if not relation or not interests:
         st.warning("⚠️ Ich brauche ein paar Infos, um kreativ zu sein!")
    else:
        client = OpenAI(api_key=api_key)
        
        with st.spinner('🎨 Die KI durchsucht das Internet...'):
            try:
                # Prompt jetzt mit EMOJI-Anforderung
                prompt = f"""
                Rolle: Kreativer Geschenk-Scout.
                Person: {relation}, {age} Jahre. Anlass: {occasion}.
                Interessen: {interests}. Budget: {budget}.
                
                Aufgabe: 3 KONKRETE Markenprodukte.
                Format JSON: 
                {{ "items": [ 
                    {{ 
                        "emoji": "Ein passendes Emoji für dieses Produkt",
                        "title": "Exakter Produktname", 
                        "text": "Kurze, knackige Begründung.", 
                        "search": "Marke Modellnummer" 
                    }} 
                ] }}
                """
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}]
                )
                
                data = json.loads(response.choices[0].message.content.replace("```json", "").replace("```", ""))
                
                st.markdown("<br>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                cols = [col1, col2, col3]

                for i, item in enumerate(data["items"]):
                    search_query = item['search'].replace(' ', '+')
                    amazon_url = f"https://www.amazon.de/s?k={search_query}"
                    
                    with cols[i]:
                        st.markdown(f"""
                        <div class="gift-card">
                            <div class="emoji-icon">{item['emoji']}</div>
                            <div class="card-title">{item['title']}</div>
                            <div class="card-desc">{item['text']}</div>
                            <a href="{amazon_url}" target="_blank" class="buy-btn">
                                Zum Produkt ➔
                            </a>
                        </div>
                        """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Fehler: {e}")
