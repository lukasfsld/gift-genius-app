import streamlit as st
from openai import OpenAI
import json

# --- 1. SETUP ---
st.set_page_config(page_title="GiftGenius", page_icon="🎁", layout="wide")

# Initialisiere das "Gedächtnis" der App (Session State)
# Das brauchen wir, damit die App weiß, ob sie den Titel in der Mitte oder oben anzeigen soll.
if 'has_searched' not in st.session_state:
    st.session_state.has_searched = False
if 'search_results' not in st.session_state:
    st.session_state.search_results = None

# --- 2. CSS DESIGN (Clean & Elegant) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    
    /* Hintergrund: Sanft und hell statt knallig */
    .stApp {
        background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
    }
    
    /* Titel-Styling */
    .big-title {
        background: -webkit-linear-gradient(45deg, #FF512F, #DD2476);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800; 
        text-align: center;
        line-height: 1.2;
    }
    
    .subtitle { 
        text-align: center; 
        color: #666; 
        margin-bottom: 2rem;
    }

    /* Container für die Start-Ansicht (Zentriert) */
    .center-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 60vh; /* Nimmt 60% der Bildschirmhöhe ein */
        text-align: center;
        animation: fadeIn 1s ease;
    }

    /* Container für die Ergebnis-Ansicht (Oben) */
    .top-container {
        text-align: center;
        padding-top: 0px;
        padding-bottom: 30px;
        animation: slideUp 0.8s ease;
    }
    
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    @keyframes slideUp { from { transform: translateY(50px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

    /* Die Karten */
    .gift-card {
        background: white;
        border-radius: 20px; 
        padding: 30px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08); /* Weicher Schatten */
        border: 1px solid rgba(0,0,0,0.05);
        height: 100%;
        text-align: center;
        transition: transform 0.3s ease;
    }
    
    .gift-card:hover { transform: translateY(-10px); }
    
    .emoji-icon { font-size: 3.5rem; margin-bottom: 15px; display: block; }
    .card-title { color: #2D3436; font-size: 1.3rem; font-weight: 700; margin-bottom: 10px; }
    .card-desc { color: #666; font-size: 0.95rem; line-height: 1.6; margin-bottom: 25px; }
    
    /* Button */
    .buy-btn {
        display: inline-block; 
        background: #2D3436; 
        color: white !important; 
        padding: 10px 25px; 
        border-radius: 50px;
        text-decoration: none; 
        font-weight: 600; 
        font-size: 0.9rem;
        transition: all 0.3s;
    }
    .buy-btn:hover { background: #000; transform: scale(1.05); }

</style>
""", unsafe_allow_html=True)

# --- 3. SEITENLEISTE ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4213/4213958.png", width=70)
    st.markdown("### ⚙️ Deine Suche")
    
    if "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
    else:
        st.error("API Key fehlt!")
        st.stop()
    
    relation = st.text_input("Für wen?", placeholder="z.B. Beste Freundin, Opa...")
    occasion = st.text_input("Anlass?", placeholder="z.B. Geburtstag...")
    age = st.slider("Alter", 1, 99, 25)
    budget = st.select_slider("Budget", options=["Kleinigkeit", "20-50€", "50-100€", "Luxus (>100€)"])
    interests = st.text_area("Interessen", height=100, placeholder="z.B. Mag Pflanzen, Yoga...")
    
    st.markdown("---")
    
    # Der Button löst die Suche aus
    if st.button("✨ Magie starten", use_container_width=True, type="primary"):
        st.session_state.has_searched = True # Wir merken uns: Suche gestartet!
        # Wir setzen results zurück, damit neu geladen wird
        st.session_state.search_results = None 

# --- 4. LOGIK & LAYOUT ---

# FALL A: NOCH NICHT GESUCHT (Startseite)
if not st.session_state.has_searched:
    st.markdown("""
    <div class="center-container">
        <div class="big-title" style="font-size: 4.5rem;">GiftGenius AI</div>
        <div class="subtitle" style="font-size: 1.5rem;">Das perfekte Geschenk. In Sekunden.</div>
        <div style="color: #999; margin-top: 20px;">👈 Starte links deine Suche</div>
    </div>
    """, unsafe_allow_html=True)

# FALL B: SUCHE WURDE GESTARTET (Ergebnisseite)
else:
    # Kleinerer Titel oben
    st.markdown("""
    <div class="top-container">
        <div class="big-title" style="font-size: 2.5rem;">GiftGenius AI</div>
        <div class="subtitle">Hier sind deine Vorschläge</div>
    </div>
    """, unsafe_allow_html=True)

    # Prüfen ob wir schon Ergebnisse im Cache haben oder neu suchen müssen
    if st.session_state.search_results is None:
        if not relation or not interests:
            st.warning("⚠️ Bitte gib links ein paar Infos ein, sonst kann ich nicht zaubern!")
            st.session_state.has_searched = False # Reset
        else:
            client = OpenAI(api_key=api_key)
            with st.spinner('🎨 Die KI durchsucht das Internet...'):
                try:
                    prompt = f"""
                    Rolle: Kreativer Geschenk-Scout.
                    Person: {relation}, {age} Jahre. Anlass: {occasion}.
                    Interessen: {interests}. Budget: {budget}.
                    Aufgabe: 3 KONKRETE Markenprodukte.
                    Format JSON: {{ "items": [ {{ "emoji": "Emojisymbol", "title": "Produktname", "text": "Kurze Begründung", "search": "Marke Modellnummer" }} ] }}
                    """
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}]
                    )
                    # Wir speichern das Ergebnis im Session State
                    st.session_state.search_results = json.loads(response.choices[0].message.content.replace("```json", "").replace("```", ""))
                
                except Exception as e:
                    st.error(f"Fehler: {e}")

    # Ergebnisse anzeigen (wenn vorhanden)
    if st.session_state.search_results:
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]

        for i, item in enumerate(st.session_state.search_results["items"]):
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
        
        # Button zum Zurücksetzen
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🔄 Neue Suche"):
            st.session_state.has_searched = False
            st.session_state.search_results = None
            st.rerun()
