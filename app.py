import streamlit as st
import time
import re
import streamlit as st
from google import genai

# --- SEITEN-SETUP ---
st.set_page_config(page_title="FC Köln Newsletter Generator", page_icon="🐐", layout="centered")

st.title("🐐 1. FC Köln Content Generator")
st.caption("Interaktives Tool für den Fachbereich – Generierung via Gemini (ohne API-Key)")

# --- INPUTS ---
col1, col2 = st.columns(2)
with col1:
    kategorie = st.selectbox("Kategorie:", ["Vereinsgeschichte & Tradition", "Aktuelle Saison", "Taktik & Analysen", "Kurioses"])
with col2:
    tonfall = st.selectbox("Tonfall:", ["Begeisternd & Fan-nah", "Professionell & Analytisch", "Humorvoll"])

spezifisches_thema = st.text_input("Spezifisches Thema / Wunsch (optional):", placeholder="z. B. Hennes, Das Stadion, Meisterjahr 1978")

# --- PLAYWRIGHT AUTOMATION ---
def generate_with_playwright(kategorie, tonfall, thema):
    prompt_text = f"""Generiere einen spannenden Beitrag über den 1. FC Köln.
Kategorie: {kategorie}
Tonfall: {tonfall}
Thema: {thema if thema else 'Wähle einen überraschenden Fakt'}

Gib das Ergebnis AUSSCHLIESSLICH als XML-Codeblock im folgenden Schema aus (OHNE deinen eigenen Senf davor/danach, verwende keine & Zeichen):

<funfact>
  <titel>Prägnanter Titel</titel>
  <kategorie>{kategorie}</kategorie>
  <fakt>Ausführlicher, spannender Text im gewünschten Tonfall.</fakt>
  <fazit>Ein kurzes Fazit oder eine Pointe.</fazit>
</funfact>"""

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir="./browser_profile",
            headless=False  # Auf True setzen, wenn der Browser unsichtbar im Hintergrund laufen soll!
        )
        page = context.new_page()
        page.goto("https://gemini.google.com")
        
        input_selector = ".ql-editor, div[contenteditable='true']"
        page.wait_for_selector(input_selector, timeout=30000)
        
        page.focus(input_selector)
        page.fill(input_selector, prompt_text)
        time.sleep(1)
        page.keyboard.press("Enter")
        
        # Warten auf Generierung
        time.sleep(22)
        
        code_elements = page.query_selector_all("pre, code, .code-block")
        found_xml = ""
        
        for elem in reversed(code_elements):
            text = elem.inner_text()
            if "<funfact>" in text and "Prägnanter Titel" not in text:
                found_xml = text
                break
                
        if not found_xml:
            full_text = page.inner_text("body")
            matches = re.findall(r'<funfact>.*?</funfact>', full_text, re.DOTALL)
            for m in reversed(matches):
                if "Prägnanter Titel" not in m:
                    found_xml = m
                    break
                    
        context.close()
        return found_xml

# --- GENERATIONS-BUTTON ---
if st.button("🚀 Newsletter-Karte generieren", type="primary"):
    with st.spinner("🤖 Playwright öffnet Gemini und generiert den Inhalt... Bitte warten..."):
        try:
            xml_response = generate_with_playwright(kategorie, tonfall, spezifisches_thema)
            
            if xml_response:
                def get_tag(tag, default=""):
                    m = re.search(f'<{tag}>(.*?)</{tag}>', xml_response, re.DOTALL)
                    return m.group(1).strip() if m else default

                titel = get_tag('titel', '1. FC Köln Update')
                kat = get_tag('kategorie', kategorie)
                fakt = get_tag('fakt', 'Kein Text generiert.')
                fazit = get_tag('fazit', '')

                # HTML-Karte zusammenbauen
                html_code = f"""
                <div style="background: white; border-radius: 16px; border: 1px solid #e2e8f0; max-width: 500px; margin: 20px auto; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.08); font-family: sans-serif;">
                    <div style="background: linear-gradient(135deg, #e11d48 0%, #9f1239 100%); color: white; padding: 24px; text-align: center;">
                        <span style="background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; text-transform: uppercase;">{kat}</span>
                        <h2 style="margin: 12px 0 0 0; font-size: 22px; color: white;">🐐 {titel}</h2>
                    </div>
                    <div style="padding: 28px; line-height: 1.6; color: #334155;">
                        <p style="font-size: 16px;">{fakt}</p>
                        {'<div style="background: #fff7ed; border-left: 4px solid #f97316; padding: 12px; margin-top: 15px; border-radius: 0 8px 8px 0; color: #c2410c;">💡 <strong>Fazit:</strong> ' + fazit + '</div>' if fazit else ''}
                    </div>
                    <div style="text-align: center; padding: 12px; background: #f1f5f9; font-size: 12px; color: #64748b;">
                        Generiert für den Fachbereich
                    </div>
                </div>
                """
                
                st.success("Erfolgreich generiert!")
                st.markdown(html_code, unsafe_allow_html=True)
                
                st.download_button(
                    label="📥 HTML-Karte herunterladen",
                    data=html_code,
                    file_name="fc_newsletter_card.html",
                    mime="text/html"
                )
            else:
                st.error("Es konnte kein valider Text aus Gemini ausgelesen werden. Bitte erneut versuchen.")
                
        except Exception as e:
            st.error(f"Fehler: {e}")