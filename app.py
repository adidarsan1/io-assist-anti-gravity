import streamlit as st
import time
import os

st.set_page_config(
    page_title="IO-Assist | Anti-Gravity",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- ADVANCED UI CSS (Anti-Gravity Theme) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    /* Main Background & Text */
    .stApp {
        background-color: #0A0A0B;
        color: #E2E8F0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Glowing Title */
    .glowing-title {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00E5FF 0%, #0052FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 4px 20px rgba(0, 229, 255, 0.4);
        margin-bottom: 5px;
        text-align: center;
        padding-top: 20px;
    }
    
    .subtitle {
        text-align: center;
        color: #94A3B8;
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 40px;
        letter-spacing: 0.5px;
    }

    /* Glassmorphic Containers */
    .glass-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    }
    
    .step-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: #00E5FF;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Inputs */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        color: #F8FAFC !important;
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: #00E5FF !important;
        box-shadow: 0 0 0 1px #00E5FF !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00E5FF 0%, #0052FF 100%);
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        padding: 0.6rem 2rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 229, 255, 0.2) !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 229, 255, 0.4) !important;
    }
    
    /* Checkbox & Expander */
    .streamlit-expanderHeader {
        background-color: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        color: #E2E8F0 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SYSTEM PROMPT (The "Defense-Proofing Engine") ---
SYSTEM_PROMPT = """
**Role:** You are an Expert Tamil Legal Assistant for an Investigating Officer (IO).
**Goal:** Convert raw field notes (in Tanglish, English, or rough Tamil) into a formal, highly professional "Observation Mahazar" in legal Tamil, ready for CCTNS upload.

**CRITICAL INSTRUCTIONS (Defense-Proofing Engine):**
1. **Source of Light (வெளிச்சம்):** You MUST explicitly mention the source of light in the Mahazar (e.g., Natural sunlight, street light, torch light, room light). If the user notes don't specify, you must infer a reasonable source based on context (e.g., day time = natural light) or explicitly state that it was bright enough to observe. NEVER omit this.
2. **Witness Presence (பஞ்சாயத்தார்கள்):** You MUST state that the observation was conducted "in the presence of the following panchayatdars" (சாட்சிகள் முன்னிலையில்).
3. **Boundaries (எல்லைகள்):** You MUST clearly format the four boundaries (East, West, North, South) of the crime scene if provided. If not provided, add placeholders for them.
4. **Tone and Language:** Use formal, authoritative, and precise legal Tamil (நீதிமன்ற தமிழ்). Avoid colloquialisms.
5. **Structure:** The output must be structured logically:
   - Date, Time, and Place of Observation (பார்வையிட்ட நாள், நேரம் மற்றும் இடம்)
   - Presence of Witnesses (சாட்சிகள்)
   - Source of Light (வெளிச்சம்)
   - Boundaries (எல்லைகள்)
   - Detailed Observation (பார்வையிட்ட விவரம்) - *Convert raw notes into formal sentences here.*
   - Seized Items (கைப்பற்றப்பட்ட பொருட்கள்) - *If any.*

**Input:** Raw field notes from the IO.
**Output Requirement:** ONLY provide the translated and formatted Legal Tamil text. Do not add any conversational filler or introductory text.
"""

# --- INITIALIZE SESSION STATE ---
# Auto-load API key from Streamlit Secrets if available (no manual entry needed)
if "api_key" not in st.session_state:
    try:
        st.session_state.api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        st.session_state.api_key = ""
if "generated_mahazar" not in st.session_state:
    st.session_state.generated_mahazar = ""

# --- GEMINI PROCESSING FUNCTION (REST-based, no gRPC streaming) ---
def generate_mahazar(raw_notes, api_key):
    import requests
    
    if not api_key:
        return "🚨 Error: Please provide your Gemini API Key."
    
    # Direct REST call — works on every mobile browser without gRPC/asyncio
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"parts": [{"text": raw_notes}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 8192,
            "candidateCount": 1
        }
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=90)
        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                return candidates[0]["content"]["parts"][0]["text"]
            return "🚨 Error: Empty response from Gemini. Try adding more notes."
        elif resp.status_code == 400:
            return "🚨 API Key Error: Invalid API key. Please re-enter it in the Settings box."
        elif resp.status_code == 429:
            return "🚨 Quota Error: Rate limit hit. Wait 1 minute and try again."
        elif resp.status_code == 404:
            return f"🚨 Model Error (404): Model not found. API Response: {resp.text[:200]}"
        else:
            return f"🚨 API Error ({resp.status_code}): {resp.text[:300]}"
    except requests.exceptions.Timeout:
        return "🚨 Timeout: Server took too long. Check your internet and try again."
    except Exception as e:
        return f"🚨 Connection Error: {str(e)}"

# --- MAIN UI ---
st.markdown('<div class="glowing-title">IO-Assist</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Anti-Gravity Legal Mahazar Generator</div>', unsafe_allow_html=True)

# API Key Input (Glass Card)
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
with st.expander("⚙️ System Configuration (API Key)", expanded=not st.session_state.api_key):
    st.session_state.api_key = st.text_input(
        "Google Gemini API Key", 
        type="password", 
        value=st.session_state.api_key,
        help="Paste your API key to activate the engine."
    )
    if not st.session_state.api_key:
        st.warning("⚠️ API Key required to establish AI uplink.")
st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.api_key:
    st.stop()

# Input Section (Glass Card)
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="step-header">🎤 Step 1: Data Ingestion</div>', unsafe_allow_html=True)

st.info("💡 Note: Use your mobile keyboard's built-in microphone 🎙️ for the highest accuracy Tamil voice-typing.")

raw_text_input = st.text_area(
    "",
    height=180,
    placeholder="Draft your raw notes here...\n\nExample: Scene paathom, east adutha veedu, west road, blood stains irundhuchu near the door. Rendu witness vandhanga, Ramu um Somu um..."
)
st.markdown('</div>', unsafe_allow_html=True)

# Processing Section
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="step-header">⚙️ Step 2: Protocol Execution</div>', unsafe_allow_html=True)

if st.button("🚀 ENGAGE ANTI-GRAVITY PROTOCOL", use_container_width=True, type="primary"):
    if not raw_text_input.strip():
        st.error("Please provide field data to process.")
    else:
        with st.spinner("⚖️ Activating Defense-Proofing Engine... Formatting Legal Tamil..."):
            st.session_state.generated_mahazar = generate_mahazar(raw_text_input, st.session_state.api_key)
st.markdown('</div>', unsafe_allow_html=True)

# Output Section
if st.session_state.generated_mahazar:
    st.markdown('<div class="glass-card" style="border-color: #00E5FF; box-shadow: 0 0 20px rgba(0, 229, 255, 0.1);">', unsafe_allow_html=True)
    st.markdown('<div class="step-header" style="color: #00E5FF;">📄 Step 3: CCTNS Ready Payload</div>', unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8; font-size: 0.9rem; margin-bottom: 10px;'>Use the copy icon on the top right of the code block below.</p>", unsafe_allow_html=True)
    st.code(st.session_state.generated_mahazar, language="markdown")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='text-align: center; color: #475569; font-size: 0.8rem; margin-top: 20px;'>🔒 Defense-Shield Active: Validates Light Source, Boundaries & Witnesses</div>", unsafe_allow_html=True)
