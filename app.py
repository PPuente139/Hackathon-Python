import re
import streamlit as st
from google import genai

# ==========================================
# 1. PAGE CONFIG & EFFZEH STYLING
# ==========================================
st.set_page_config(
    page_title="1. FC Köln Content Generator",
    page_icon="🐐",
    layout="wide"
)

# Custom CSS für den FC Köln Look (Rot/Weiß/Dunkel)
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #FFFFFF;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #AAAAAA;
        margin-bottom: 1.8rem;
    }
    /* Effzeh-Rot für den Primärbutton */
    .stButton>button {
        background-color: #ED1C24 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        width: 100% !important;
        box-shadow: 0 4px 10px rgba(237, 28, 36, 0.3);
    }
    .stButton>button:hover {
        background-color: #C11219 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. GEMINI API SETUP
# ==========================================
@st.cache_resource
def get_gemini_client():
    """Lädt den Client sicher aus den Streamlit Secrets."""
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("⚠️ Keinen 'GEMINI_API_KEY' in den Streamlit Secrets gefunden! Bitte unter Settings -> Secrets hinterlegen.")
        st.stop()
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


def generate_fc_content(kategorie, tonfall, thema_wunsch):
    """Ruft die Gemini API für FC Köln Content auf."""
    client = get_gemini_client()

    prompt = f"""
    Du bist der offizielle und leidenschaftliche Content- und Newsletter-Generator für den 1. FC Köln.
    Erstelle einen mitreißenden Content-Beitrag / Newsletter-Karte.

    VORGABEN:
    - Kategorie: {kategorie}
    - Tonfall: {tonfall}
    - Spezifisches Thema / Wunsch: {thema_wunsch if thema_wunsch else "Kein spezieller Wunsch, wähle etwas Passendes zur Kategorie"}

    OUTPUT-FORMAT:
    Antworte AUSSCHLIESSLICH mit folgendem XML-Schema, damit die Daten sauber geparst werden können:

    <newsletter>
        <titel>Eine knackige, emotionale Überschrift mit Effzeh-Bezug</titel>
        <intro>Eine mitreißende Einleitung (2-3 Sätze)</intro>
        <hauptteil>Der Hauptinhalt in gut lesbaren Absätzen. Erwähne historische Details, Anekdoten oder Fakten wenn passend.</hauptteil>
        <funfact>Ein lustiger oder überraschender Funfact zum FC Köln oder dem Thema</funfact>
        <call_to_action>Ein motivierender Aufruf an die Fans (z. B. 'Come on, FC!')</call_to_action>
    </newsletter>
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        st.error(f"Fehler bei der API-Anfrage: {e}")
        return None


# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
def parse_xml_tag(text, tag_name):
    """Extrahiert Inhalte aus den XML-Tags."""
    match = re.search(f"<{tag_name}>(.*?)</{tag_name}>", text, re.DOTALL)
    return match.group(1).strip() if match else ""


def build_html_card(titel, intro, hauptteil, funfact, cta):
    """Baut eine schicke rot-weiße HTML-Newsletter-Karte."""
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; border: 2px solid #ED1C24; border-radius: 12px; padding: 25px; background-color: #ffffff; color: #222222; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
        <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid #f0f0f0; padding-bottom: 12px; margin-bottom: 15px;">
            <h2 style="color: #ED1C24; margin: 0; font-size: 22px; font-weight: 800;">{titel}</h2>
            <span style="font-size: 24px;">🐐</span>
        </div>
        <p style="font-size: 15px; color: #333333; line-height: 1.5; font-weight: 600;">{intro}</p>
        <hr style="border: 0; border-top: 1px solid #eeeeee; margin: 15px 0;">
        <div style="font-size: 14px; color: #444444; line-height: 1.6;">{hauptteil}</div>
        
        {f'<div style="background-color: #fff0f0; border-left: 4px solid #ED1C24; padding: 12px; margin: 20px 0; font-size: 13px; color: #990000;"><strong>💡 Wusstest du schon?</strong> {funfact}</div>' if funfact else ''}
        
        <div style="text-align: center; margin-top: 25px;">
            <a href="#" style="background-color: #ED1C24; color: white; padding: 10px 22px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 14px; display: inline-block;">{cta}</a>
        </div>
    </div>
    """


# ==========================================
# 4. STREAMLIT UI
# ==========================================
st.markdown('<div class="main-header">🐐 1. FC Köln Content Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Interaktives Tool für den Fachbereich – Generierung via Gemini (ohne API-Key im Frontend)</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    kategorie = st.selectbox(
        "Kategorie:",
        [
            "Vereinsgeschichte & Tradition",
            "Spieltags-Vorschau & Analyse",
            "Fan-Aktionen & Kurvennews",
            "Jugend- & Nachwuchsförderung"
        ]
    )

with col2:
    tonfall = st.selectbox(
        "Tonfall:",
        ["Humorvoll", "Leidenschaftlich & Emotional", "Sachlich & Analytisch", "Kölsch & Locker"]
    )

thema_wunsch = st.text_input(
    "Spezifisches Thema / Wunsch (optional):",
    placeholder="z. B. Maniche, Podolski, Müngersdorf, Aufstieg 1978..."
)

st.write("") # Abstand
btn_generate = st.button("🚀 Newsletter-Karte generieren")

st.markdown("---")

# --- ERGEBNIS-ANZEIGE ---
if btn_generate:
    with st.spinner("Geißbock Gemini durchsucht die Annalen des Effzeh..."):
        raw_response = generate_fc_content(kategorie, tonfall, thema_wunsch)
        
        if raw_response:
            titel = parse_xml_tag(raw_response, "titel") or "1. FC Köln News"
            intro = parse_xml_tag(raw_response, "intro")
            hauptteil = parse_xml_tag(raw_response, "hauptteil")
            funfact = parse_xml_tag(raw_response, "funfact")
            cta = parse_xml_tag(raw_response, "call_to_action") or "Come on, FC!"
            
            html_code = build_html_card(titel, intro, hauptteil, funfact, cta)
            st.session_state["generated_html"] = html_code

if "generated_html" in st.session_state:
    st.subheader("Generierte Newsletter-Karte:")
    
    # Rendered HTML Card
    st.components.v1.html(st.session_state["generated_html"], height=480, scrolling=True)
    
    # Download Button
    st.download_button(
        label="💾 HTML-Vorlage herunterladen",
        data=st.session_state["generated_html"],
        file_name="fc_koeln_newsletter.html",
        mime="text/html"
    )
