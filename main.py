import streamlit as st
from openai import OpenAI
import json

# --- 1. SETUP ---
st.set_page_config(page_title="GiftGenius", page_icon="🎁", layout="wide")

# --- 2. CSS-STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    .gradient-text {
        background: -webkit-linear-gradient(45deg, #FF512F, #DD2476);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 600; font-size: 3rem; text-align: center; margin-bottom: 0;
    }
    .subtitle { text-align: center; color: #666; font-size: 1.1rem; margin-bottom: 3rem; }
    .gift-card {
        background: white; border-radius: 20px; padding: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08); transition: all 0.3s ease;
        border: 1px solid rgba(0,0,0,0.05); height: 100%;
        display: flex; flex-direction: column; justify-content: space-between;
    }
    .gift-card:hover { transform: translateY(-8px); box-shadow: 0 20px 40px rgba(0,0,0,0.12); border-color: #DD2476; }
    .card-title { color: #2D3436; font-size: 1.3rem; font-weight: 600; margin-bottom: 10px; }
    .card-desc { color: #636e72; font-size: 0.95rem; line-height: 1.6; margin-bottom: 20px; }
    .buy-btn {
        display: block; background: linear-gradient(90deg, #FF512F 0%, #DD2476 100%);
        color: white !important; text-align: center; padding: 12px; border-radius: 12px;
        text-decoration: none; font-weight: 500; box-shadow: 0 4px 15px rgba(221, 36, 118, 0.4);
        transition: box-shadow 0.3s;
    }
    .buy-btn:hover { box-shadow: 0 6px 20px rgba(221, 36, 118, 0.6); opacity: 0.95; }
    .stButton > button {
        background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
        color: white; border: none; border-radius: 10px; font-weight: 600; padding: 0.5rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. UI STRUKTUR ---
st.markdown('<div class="gradient-text">GiftGenius AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Entdecke Geschenke, die wirklich begeistern.</div>', unsafe_allow_html=True)

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4213/4213958.png", width=80)
    st.markdown("### Dein Profil")
    
    # --- KEY AUTOMATISCH LADEN ---
    if "OPENAI_API_KEY" in st.secrets:
        st.success("Verbindung aktiv! ✅", icon="🚀")
        api_key = st.secrets["OPENAI_API_KEY"]
    else:
        st.error("Kein API Key gefunden.")
        st.stop()
    
    st.markdown("---")
    
    relation = st.selectbox("Für wen?", ["Partner/in", "Eltern", "Bester Freund/in", "Kind", "Kollege", "Nachbar"])
    age = st.slider("Alter", 1, 99, 25)
    budget = st.select_slider("Budget", options=["Kleinigkeit", "20-50€", "50-100€", "Luxus (>100€)"])
    interests = st.text_area("Hobbys & Vorlieben", height=120, placeholder="Z.B. Mag Minimalismus, kocht gerne asiatisch, hasst Plastik...")
    
    st.markdown("---")
    start_search = st.button("✨ Magie starten", use_container_width=True)

# --- 4. LOGIK ---
if start_search:
    if not interests:
        st.warning("✍️ Bitte gib ein paar Interessen ein.")
    else:
        client = OpenAI(api_key=api_key)
        
        with st.spinner('🤖 Die KI analysiert Trends und psychologische Profile...'):
            try:
                prompt = f"""
                Rolle: Trendscout & Shopping-Assistent.
                Zielperson: {relation}, {age} Jahre.
                Budget: {budget}.
                Interessen: {interests}.
                
                Aufgabe: Finde 3 Geschenkideen.
                Format: JSON {{ "items": [ {{ "title": "...", "text": "...", "search": "..." }} ] }}
                Wichtig: Sei kreativ! Keine 08/15 Ideen.
                """
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.8
                )
                
                data = json.loads(response.choices[0].message.content.replace("```json", "").replace("```", ""))
                
                st.markdown("<br>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                cols = [col1, col2, col3]

                for i, item in enumerate(data["items"]):
                    amazon_url = f"https://www.amazon.de/s?k={item['search'].replace(' ', '+')}"
                    with cols[i]:
                        st.markdown(f"""
                        <div class="gift-card">
                            <div>
                                <div class="card-title">{item['title']}</div>
                                <div class="card-desc">{item['text']}</div>
                            </div>
                            <a href="{amazon_url}" target="_blank" class="buy-btn">
                                Zum Produkt ➔
                            </a>
                        </div>
                        """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Fehler: {e}")